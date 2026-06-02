import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ecommerce_recommender.models.baseline import PopularityRecommender


def test_recommend_returns_products_in_popularity_order() -> None:
    events = pd.DataFrame(
        {
            "product_id": ["p1", "p2", "p2", "p3"],
            "event_type": ["view", "click", "purchase", "add_to_cart"],
        }
    )
    recommender = PopularityRecommender()

    recommender.fit(events)

    assert recommender.recommend() == ["p2", "p3", "p1"]


def test_fit_applies_event_weights() -> None:
    events = pd.DataFrame(
        {
            "product_id": ["p1", "p1", "p1", "p1", "p1", "p2"],
            "event_type": [
                "view",
                "click",
                "add_to_cart",
                "purchase",
                "not_interested",
                "purchase",
            ],
        }
    )
    recommender = PopularityRecommender()

    recommender.fit(events)

    assert recommender.recommend() == ["p1", "p2"]


def test_recommend_respects_top_k_limit() -> None:
    events = pd.DataFrame(
        {
            "product_id": ["p1", "p2", "p3"],
            "event_type": ["purchase", "click", "view"],
        }
    )
    recommender = PopularityRecommender()
    recommender.fit(events)

    assert recommender.recommend(top_k=2) == ["p1", "p2"]


def test_empty_events_returns_empty_recommendations() -> None:
    recommender = PopularityRecommender()

    recommender.fit(pd.DataFrame())

    assert recommender.recommend() == []


def test_missing_required_columns_raises_clear_error() -> None:
    recommender = PopularityRecommender()
    events = pd.DataFrame({"product_id": ["p1"]})

    with pytest.raises(ValueError, match="missing required columns: event_type"):
        recommender.fit(events)


def test_unknown_event_types_are_ignored() -> None:
    events = pd.DataFrame(
        {
            "product_id": ["p1", "p2", "p3"],
            "event_type": ["purchase", "share", "view"],
        }
    )
    recommender = PopularityRecommender()

    recommender.fit(events)

    assert recommender.recommend() == ["p1", "p3"]
