import logging
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ecommerce_recommender.models.baseline import (
    RETAILROCKET_REQUIRED_EVENT_COLUMNS,
    RetailRocketPopularityRecommender,
)


def make_events(*rows: tuple[int, int, str, int, int | None]) -> pd.DataFrame:
    """Build a small in-memory RetailRocket event fixture."""
    return pd.DataFrame(
        rows,
        columns=["timestamp", "visitorid", "event", "itemid", "transactionid"],
    )


def test_recommend_returns_items_in_weighted_popularity_order() -> None:
    events = make_events(
        (1430622004384, 101, "view", 5001, None),
        (1430622064384, 101, "addtocart", 5002, None),
        (1430622124384, 102, "transaction", 5003, 90001),
        (1430622184384, 103, "view", 5002, None),
    )

    recommendations = RetailRocketPopularityRecommender().fit(events).recommend()

    assert recommendations == [5003, 5002, 5001]


def test_fit_applies_provisional_event_weights() -> None:
    # A view plus add-to-cart should remain weaker than one completed transaction.
    events = make_events(
        (1430622004384, 101, "view", 5001, None),
        (1430622064384, 101, "addtocart", 5001, None),
        (1430622124384, 102, "transaction", 5002, 90001),
    )

    recommender = RetailRocketPopularityRecommender().fit(events)

    assert recommender.item_scores_.to_dict() == {5002: 5.0, 5001: 4.0}


def test_recommend_respects_top_k_limit() -> None:
    events = make_events(
        (1430622004384, 101, "view", 5001, None),
        (1430622064384, 102, "addtocart", 5002, None),
        (1430622124384, 103, "transaction", 5003, 90001),
    )

    recommendations = RetailRocketPopularityRecommender().fit(events).recommend(top_k=2)

    assert recommendations == [5003, 5002]


def test_empty_events_returns_empty_recommendations() -> None:
    recommender = RetailRocketPopularityRecommender().fit(pd.DataFrame())

    assert recommender.recommend() == []


def test_missing_required_columns_raises_clear_error() -> None:
    events = make_events((1430622004384, 101, "view", 5001, None)).drop(
        columns=["transactionid", "visitorid"]
    )

    with pytest.raises(ValueError, match="transactionid, visitorid"):
        RetailRocketPopularityRecommender().fit(events)


def test_unsupported_event_values_are_ignored_with_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    # Unknown source values should be observable without blocking known signals.
    events = make_events(
        (1430622004384, 101, "view", 5001, None),
        (1430622064384, 102, "wishlist", 5002, None),
    )

    with caplog.at_level(logging.WARNING):
        recommendations = RetailRocketPopularityRecommender().fit(events).recommend()

    assert recommendations == [5001]
    assert "unsupported event values" in caplog.text


@pytest.mark.parametrize("top_k", [0, -1, 1.5, True])
def test_invalid_top_k_raises_value_error(top_k: object) -> None:
    recommender = RetailRocketPopularityRecommender()

    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        recommender.recommend(top_k=top_k)  # type: ignore[arg-type]


def test_ties_are_broken_by_itemid_ascending() -> None:
    # Stable tie-breaking keeps repeated offline evaluations reproducible.
    events = make_events(
        (1430622004384, 101, "view", 5003, None),
        (1430622064384, 102, "view", 5001, None),
        (1430622124384, 103, "view", 5002, None),
    )

    recommendations = RetailRocketPopularityRecommender().fit(events).recommend()

    assert recommendations == [5001, 5002, 5003]


def test_required_schema_is_retailrocket_only() -> None:
    # Guard against accidental reintroduction of the retired synthetic contract.
    assert RETAILROCKET_REQUIRED_EVENT_COLUMNS == {
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid",
    }
