"""Run the RetailRocket event-weighted popularity baseline on raw events."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError

from ecommerce_recommender.models.baseline import (
    PROVISIONAL_RETAILROCKET_EVENT_WEIGHTS,
)

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EVENTS_PATH = PROJECT_ROOT / "data/raw/RetailRocket_event-based/events.csv"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data/processed/retailrocket_baseline_top_items.csv"
DEFAULT_CHUNK_SIZE = 100_000
DEFAULT_TOP_K = 100
REQUIRED_COLUMNS = {"event", "itemid"}


def aggregate_item_scores(
    events_path: str | Path, chunk_size: int = DEFAULT_CHUNK_SIZE
) -> pd.Series:
    """Aggregate RetailRocket item popularity scores without loading all events."""
    path = Path(events_path)
    if not path.is_file():
        raise FileNotFoundError(f"RetailRocket events file not found: {path}")
    if chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")

    scores = pd.Series(dtype="float64", name="popularity_score")
    ignored_event_count = 0
    try:
        chunks = pd.read_csv(path, chunksize=chunk_size, usecols=["event", "itemid"])
        for chunk in chunks:
            # Ignore unapproved source values while preserving a visible warning.
            known_events = chunk[
                chunk["event"].isin(PROVISIONAL_RETAILROCKET_EVENT_WEIGHTS)
            ].copy()
            ignored_event_count += len(chunk) - len(known_events)
            if known_events.empty:
                continue

            item_ids = pd.to_numeric(known_events["itemid"], errors="coerce")
            if item_ids.isna().any() or (item_ids % 1 != 0).any():
                raise ValueError("RetailRocket events contains invalid itemid values")

            known_events["itemid"] = item_ids.astype("int64")
            known_events["popularity_score"] = known_events["event"].map(
                PROVISIONAL_RETAILROCKET_EVENT_WEIGHTS
            )
            chunk_scores = known_events.groupby("itemid")["popularity_score"].sum()
            # Keep only aggregated scores between chunks to bound memory usage.
            scores = scores.add(chunk_scores, fill_value=0.0)
    except EmptyDataError as exc:
        raise ValueError(f"RetailRocket events CSV is empty: {path}") from exc
    except ValueError as exc:
        if "Usecols do not match columns" in str(exc):
            missing = _missing_required_columns(path)
            raise ValueError(
                f"RetailRocket events is missing required columns: {', '.join(missing)}"
            ) from exc
        raise

    if ignored_event_count:
        LOGGER.warning(
            "Ignored %d RetailRocket events with unsupported event values",
            ignored_event_count,
        )
    return scores


def build_top_items(scores: pd.Series, top_k: int = DEFAULT_TOP_K) -> pd.DataFrame:
    """Return deterministically ranked top RetailRocket items."""
    if top_k <= 0:
        raise ValueError("top_k must be a positive integer")
    if scores.empty:
        return pd.DataFrame(columns=["itemid", "popularity_score"])

    ranked_scores = (
        scores.rename("popularity_score")
        .rename_axis("itemid")
        .reset_index()
        # Item ID is the stable secondary key for reproducible ties.
        .sort_values(
            by=["popularity_score", "itemid"],
            ascending=[False, True],
            kind="stable",
        )
        .head(top_k)
        .reset_index(drop=True)
    )
    ranked_scores["itemid"] = ranked_scores["itemid"].astype("int64")
    return ranked_scores


def run_baseline(
    events_path: str | Path = DEFAULT_EVENTS_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    top_k: int = DEFAULT_TOP_K,
) -> pd.DataFrame:
    """Aggregate raw events and save only the requested top RetailRocket items."""
    output = Path(output_path)
    LOGGER.info("Reading RetailRocket events in chunks: %s", events_path)
    top_items = build_top_items(aggregate_item_scores(events_path, chunk_size), top_k)
    output.parent.mkdir(parents=True, exist_ok=True)
    top_items.to_csv(output, index=False)
    LOGGER.info("Wrote %d ranked RetailRocket items: %s", len(top_items), output)
    return top_items


def _missing_required_columns(path: Path) -> list[str]:
    """Read only the header to describe missing runner columns clearly."""
    columns = set(pd.read_csv(path, nrows=0).columns)
    return sorted(REQUIRED_COLUMNS.difference(columns))


def main() -> None:
    """Run the default local RetailRocket baseline job."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        run_baseline()
    except (FileNotFoundError, ValueError) as exc:
        LOGGER.error("RetailRocket baseline failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
