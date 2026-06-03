import json
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from scripts.evaluate_retailrocket_baseline import (
    aggregate_train_scores_and_test_relevance,
    calculate_metrics,
    determine_split_timestamp,
    run_evaluation,
)


def write_events(path: Path) -> None:
    """Write a small temporal RetailRocket fixture for evaluator tests."""
    pd.DataFrame(
        {
            "timestamp": [10, 20, 30, 40, 90, 95, 100],
            "visitorid": [101, 102, 103, 104, 201, 202, 202],
            "event": [
                "view",
                "addtocart",
                "transaction",
                "view",
                "view",
                "view",
                "transaction",
            ],
            "itemid": [5001, 5001, 5002, 5003, 5002, 5001, 5999],
            "transactionid": [None, None, 90001, None, None, None, 90002],
        }
    ).to_csv(path, index=False)


def test_determine_split_timestamp_uses_time_range(tmp_path: Path) -> None:
    events_path = tmp_path / "events.csv"
    write_events(events_path)

    assert determine_split_timestamp(events_path, chunk_size=2, train_ratio=0.8) == 82


def test_chunked_aggregation_and_metrics_use_later_interactions(tmp_path: Path) -> None:
    events_path = tmp_path / "events.csv"
    write_events(events_path)

    scores, relevance, train_count, test_count = aggregate_train_scores_and_test_relevance(
        events_path, split_timestamp=82, chunk_size=2
    )
    hit_rate, recall = calculate_metrics([5002, 5001], relevance)

    assert scores.to_dict() == {5001: 4.0, 5002: 5.0, 5003: 1.0}
    assert relevance == {201: {5002}, 202: {5001, 5999}}
    assert train_count == 4
    assert test_count == 3
    assert hit_rate == 1.0
    assert recall == 0.75


def test_run_evaluation_writes_json_result(tmp_path: Path) -> None:
    events_path = tmp_path / "events.csv"
    output_path = tmp_path / "processed" / "evaluation.json"
    write_events(events_path)

    result = run_evaluation(
        events_path, output_path, chunk_size=2, top_k=2, train_ratio=0.8
    )

    assert result["recommended_itemids"] == [5002, 5001]
    assert result["hit_rate_at_2"] == 1.0
    assert result["recall_at_2"] == 0.75
    assert json.loads(output_path.read_text(encoding="utf-8")) == result


def test_calculate_metrics_requires_test_visitors() -> None:
    with pytest.raises(ValueError, match="at least one visitor"):
        calculate_metrics([5001], {})
