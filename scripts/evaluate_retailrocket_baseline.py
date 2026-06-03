"""Evaluate the RetailRocket popularity baseline with a temporal split."""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

from ecommerce_recommender.models.baseline import (
    PROVISIONAL_RETAILROCKET_EVENT_WEIGHTS,
)

try:
    from scripts.run_retailrocket_baseline import build_top_items
except ModuleNotFoundError:  # Support direct execution from the scripts directory.
    from run_retailrocket_baseline import build_top_items

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS_PATH = PROJECT_ROOT / "data/raw/RetailRocket_event-based/events.csv"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data/processed/retailrocket_baseline_evaluation.json"
DEFAULT_CHUNK_SIZE = 100_000
DEFAULT_TOP_K = 10
DEFAULT_TRAIN_RATIO = 0.8
REQUIRED_COLUMNS = {"timestamp", "visitorid", "event", "itemid"}


def determine_split_timestamp(
    events_path: str | Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    train_ratio: float = DEFAULT_TRAIN_RATIO,
) -> int:
    """Return an inclusive train cutoff from the observed timestamp range."""
    path = _require_events_file(events_path)
    _validate_chunk_size(chunk_size)
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1")
    _validate_required_columns(path)

    timestamp_min: int | None = None
    timestamp_max: int | None = None
    try:
        for chunk in pd.read_csv(path, chunksize=chunk_size, usecols=["timestamp"]):
            timestamps = _numeric_integer_series(chunk["timestamp"], "timestamp")
            chunk_min, chunk_max = int(timestamps.min()), int(timestamps.max())
            timestamp_min = chunk_min if timestamp_min is None else min(timestamp_min, chunk_min)
            timestamp_max = chunk_max if timestamp_max is None else max(timestamp_max, chunk_max)
    except EmptyDataError as exc:
        raise ValueError(f"RetailRocket events CSV is empty: {path}") from exc

    if timestamp_min is None or timestamp_max is None:
        raise ValueError(f"RetailRocket events CSV contains no rows: {path}")
    if timestamp_min == timestamp_max:
        raise ValueError("RetailRocket events requires more than one timestamp for a temporal split")
    return timestamp_min + int((timestamp_max - timestamp_min) * train_ratio)


def aggregate_train_scores_and_test_relevance(
    events_path: str | Path,
    split_timestamp: int,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> tuple[pd.Series, dict[int, set[int]], int, int]:
    """Aggregate train scores and later visitor-item relevance with chunked reads."""
    path = _require_events_file(events_path)
    _validate_chunk_size(chunk_size)
    _validate_required_columns(path)

    scores = pd.Series(dtype="float64", name="popularity_score")
    relevance: defaultdict[int, set[int]] = defaultdict(set)
    train_event_count = 0
    test_event_count = 0
    ignored_event_count = 0

    for chunk in pd.read_csv(path, chunksize=chunk_size, usecols=sorted(REQUIRED_COLUMNS)):
        timestamps = _numeric_integer_series(chunk["timestamp"], "timestamp")
        item_ids = _numeric_integer_series(chunk["itemid"], "itemid")
        visitor_ids = _numeric_integer_series(chunk["visitorid"], "visitorid")
        chunk = chunk.assign(timestamp=timestamps, itemid=item_ids, visitorid=visitor_ids)

        # Unsupported source values are ignored consistently with the baseline.
        known_events = chunk[
            chunk["event"].isin(PROVISIONAL_RETAILROCKET_EVENT_WEIGHTS)
        ].copy()
        ignored_event_count += len(chunk) - len(known_events)
        if known_events.empty:
            continue

        train_events = known_events[known_events["timestamp"] <= split_timestamp].copy()
        test_events = known_events[known_events["timestamp"] > split_timestamp]
        train_event_count += len(train_events)
        test_event_count += len(test_events)

        if not train_events.empty:
            train_events["popularity_score"] = train_events["event"].map(
                PROVISIONAL_RETAILROCKET_EVENT_WEIGHTS
            )
            chunk_scores = train_events.groupby("itemid")["popularity_score"].sum()
            scores = scores.add(chunk_scores, fill_value=0.0)

        # Test interactions are grouped per visitor for visitor-level metrics.
        for visitor_id, item_id in test_events[["visitorid", "itemid"]].itertuples(
            index=False, name=None
        ):
            relevance[int(visitor_id)].add(int(item_id))

    if ignored_event_count:
        LOGGER.warning(
            "Ignored %d RetailRocket events with unsupported event values",
            ignored_event_count,
        )
    if train_event_count == 0 or test_event_count == 0:
        raise ValueError("Temporal split must produce non-empty train and test events")
    return scores, dict(relevance), train_event_count, test_event_count


def calculate_metrics(
    recommended_itemids: list[int], relevance_by_visitor: dict[int, set[int]]
) -> tuple[float, float]:
    """Calculate visitor-level HitRate and Recall for one global recommendation list."""
    if not relevance_by_visitor:
        raise ValueError("Evaluation requires at least one visitor with test interactions")

    recommended = set(recommended_itemids)
    hits = 0
    recall_total = 0.0
    for relevant_items in relevance_by_visitor.values():
        matched_items = recommended.intersection(relevant_items)
        hits += bool(matched_items)
        recall_total += len(matched_items) / len(relevant_items)

    visitor_count = len(relevance_by_visitor)
    return hits / visitor_count, recall_total / visitor_count


def run_evaluation(
    events_path: str | Path = DEFAULT_EVENTS_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    top_k: int = DEFAULT_TOP_K,
    train_ratio: float = DEFAULT_TRAIN_RATIO,
) -> dict[str, object]:
    """Evaluate and save the RetailRocket popularity baseline result."""
    if top_k <= 0:
        raise ValueError("top_k must be a positive integer")

    LOGGER.info("Determining RetailRocket temporal split: %s", events_path)
    split_timestamp = determine_split_timestamp(events_path, chunk_size, train_ratio)
    LOGGER.info("Aggregating RetailRocket events with train cutoff %d", split_timestamp)
    scores, relevance, train_count, test_count = aggregate_train_scores_and_test_relevance(
        events_path, split_timestamp, chunk_size
    )
    recommended_itemids = build_top_items(scores, top_k)["itemid"].astype(int).tolist()
    hit_rate, recall = calculate_metrics(recommended_itemids, relevance)

    result: dict[str, object] = {
        "baseline": "event_weighted_popularity",
        "split_timestamp": split_timestamp,
        "train_ratio": train_ratio,
        "top_k": top_k,
        "train_event_count": train_count,
        "test_event_count": test_count,
        "evaluated_visitor_count": len(relevance),
        "recommended_itemids": recommended_itemids,
        f"hit_rate_at_{top_k}": hit_rate,
        f"recall_at_{top_k}": recall,
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    LOGGER.info("Wrote RetailRocket baseline evaluation: %s", output)
    return result


def _require_events_file(events_path: str | Path) -> Path:
    """Return an existing RetailRocket events file path or raise clearly."""
    path = Path(events_path)
    if not path.is_file():
        raise FileNotFoundError(f"RetailRocket events file not found: {path}")
    return path


def _validate_required_columns(path: Path) -> None:
    """Read only the header and reject incompatible event schemas."""
    try:
        columns = set(pd.read_csv(path, nrows=0).columns)
    except EmptyDataError as exc:
        raise ValueError(f"RetailRocket events CSV is empty: {path}") from exc
    missing = sorted(REQUIRED_COLUMNS.difference(columns))
    if missing:
        raise ValueError(f"RetailRocket events is missing required columns: {', '.join(missing)}")


def _validate_chunk_size(chunk_size: int) -> None:
    """Reject invalid chunk sizes before starting file reads."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")


def _numeric_integer_series(series: pd.Series, column: str) -> pd.Series:
    """Return validated integer source values for one required column."""
    values = pd.to_numeric(series, errors="coerce")
    if values.isna().any() or (values % 1 != 0).any():
        raise ValueError(f"RetailRocket events contains invalid {column} values")
    return values.astype("int64")


def main() -> None:
    """Run the default local RetailRocket baseline evaluation."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        run_evaluation()
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("RetailRocket baseline evaluation failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
