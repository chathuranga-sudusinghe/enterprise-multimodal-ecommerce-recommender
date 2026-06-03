"""RetailRocket behavior-based baseline recommender.

The numeric event weights in this module are provisional baseline values for
implementation testing. They may change after evaluation protocol review. This
module uses RetailRocket events only and does not consume Amazon Berkeley
Objects data.
"""

from __future__ import annotations

import logging
from numbers import Integral

import pandas as pd

LOGGER = logging.getLogger(__name__)

RETAILROCKET_REQUIRED_EVENT_COLUMNS: set[str] = {
    "timestamp",
    "visitorid",
    "event",
    "itemid",
    "transactionid",
}
PROVISIONAL_RETAILROCKET_EVENT_WEIGHTS: dict[str, float] = {
    "view": 1.0,
    "addtocart": 3.0,
    "transaction": 5.0,
}


class RetailRocketPopularityRecommender:
    """Rank RetailRocket items by provisional event-weighted popularity.

    Unsupported event values are ignored with a warning so an unexpected
    source value does not break baseline generation. These weights are
    provisional baseline weights for the first RetailRocket baseline and may
    be revised after evaluation.
    """

    def __init__(self) -> None:
        """Initialize an unfitted recommender with no item scores."""
        self.item_scores_ = pd.Series(dtype="float64", name="popularity_score")

    def fit(self, events: pd.DataFrame) -> RetailRocketPopularityRecommender:
        """Compute weighted item popularity from RetailRocket event rows.

        Args:
            events: RetailRocket events using the discovered source schema.

        Returns:
            The fitted recommender instance.
        """
        self.item_scores_ = pd.Series(dtype="float64", name="popularity_score")
        # An empty history is a valid cold-start fallback, not a processing error.
        if events.empty:
            return self

        self._validate_required_columns(events)
        # Preserve service availability if the source adds an unapproved event value.
        known_events = events[
            events["event"].isin(PROVISIONAL_RETAILROCKET_EVENT_WEIGHTS)
        ].copy()
        ignored_event_count = len(events) - len(known_events)
        if ignored_event_count:
            LOGGER.warning(
                "Ignoring %d RetailRocket events with unsupported event values",
                ignored_event_count,
            )

        if known_events.empty:
            return self

        # Normalize identifiers so the public contract consistently returns integers.
        item_ids = pd.to_numeric(known_events["itemid"], errors="coerce")
        if item_ids.isna().any() or (item_ids % 1 != 0).any():
            raise ValueError("RetailRocket events contains invalid itemid values")

        known_events["itemid"] = item_ids.astype("int64")
        known_events["popularity_score"] = known_events["event"].map(
            PROVISIONAL_RETAILROCKET_EVENT_WEIGHTS
        )
        # Use itemid as a secondary key so equal scores always produce stable output.
        ranked_scores = (
            known_events.groupby("itemid", as_index=False)["popularity_score"]
            .sum()
            .sort_values(
                by=["popularity_score", "itemid"],
                ascending=[False, True],
                kind="stable",
            )
        )
        self.item_scores_ = ranked_scores.set_index("itemid")["popularity_score"]
        return self

    def recommend(self, top_k: int = 10) -> list[int]:
        """Return up to ``top_k`` RetailRocket item IDs in ranked order."""
        if not isinstance(top_k, Integral) or isinstance(top_k, bool) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")

        return [int(item_id) for item_id in self.item_scores_.head(top_k).index]

    @staticmethod
    def _validate_required_columns(events: pd.DataFrame) -> None:
        """Raise a clear error when RetailRocket event columns are missing."""
        missing_columns = RETAILROCKET_REQUIRED_EVENT_COLUMNS.difference(events.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"RetailRocket events is missing required columns: {missing}")
