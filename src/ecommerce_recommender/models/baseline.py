"""Simple baseline recommenders for Version 1."""

from __future__ import annotations

import logging

import pandas as pd

LOGGER = logging.getLogger(__name__)

REQUIRED_EVENT_COLUMNS: set[str] = {"product_id", "event_type"}
EVENT_WEIGHTS: dict[str, float] = {
    "view": 1.0,
    "click": 2.0,
    "add_to_cart": 3.0,
    "purchase": 5.0,
    "not_interested": -2.0,
}


class PopularityRecommender:
    """Recommend products using weighted historical interaction popularity."""

    def __init__(self) -> None:
        """Initialize an unfitted popularity recommender."""
        self._scores = pd.Series(dtype="float64", name="popularity_score")

    def fit(self, events_df: pd.DataFrame) -> None:
        """Calculate weighted popularity scores from product interaction events.

        Unknown event types are ignored so new or malformed signals do not break
        the baseline recommender.
        """
        if events_df.empty:
            self._scores = pd.Series(dtype="float64", name="popularity_score")
            return

        self._validate_required_columns(events_df)

        known_events = events_df[events_df["event_type"].isin(EVENT_WEIGHTS)].copy()
        ignored_event_count = len(events_df) - len(known_events)
        if ignored_event_count:
            LOGGER.warning("Ignoring %s events with unknown event types", ignored_event_count)

        if known_events.empty:
            self._scores = pd.Series(dtype="float64", name="popularity_score")
            return

        known_events["popularity_score"] = known_events["event_type"].map(EVENT_WEIGHTS)
        self._scores = (
            known_events.groupby("product_id", sort=False)["popularity_score"]
            .sum()
            .sort_index()
            .sort_values(ascending=False, kind="stable")
        )

    def recommend(self, top_k: int = 5) -> list[str]:
        """Return up to ``top_k`` product identifiers ordered by popularity."""
        if top_k < 0:
            raise ValueError("top_k must be greater than or equal to 0")

        return self._scores.head(top_k).index.astype(str).tolist()

    @staticmethod
    def _validate_required_columns(events_df: pd.DataFrame) -> None:
        """Raise a clear error when required event columns are missing."""
        missing_columns = REQUIRED_EVENT_COLUMNS.difference(events_df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"events is missing required columns: {missing}")
