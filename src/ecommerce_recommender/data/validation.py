"""Validation helpers for track-specific deterministic fixture data."""

from __future__ import annotations

from typing import Any

import pandas as pd

RETAILROCKET_EVENT_REQUIRED_COLUMNS: set[str] = {
    "timestamp",
    "visitorid",
    "event",
    "itemid",
    "transactionid",
}
RETAILROCKET_ITEM_PROPERTY_REQUIRED_COLUMNS: set[str] = {
    "timestamp",
    "itemid",
    "property",
    "value",
}
RETAILROCKET_CATEGORY_TREE_REQUIRED_COLUMNS: set[str] = {"categoryid", "parentid"}
RETAILROCKET_ALLOWED_EVENT_VALUES: set[str] = {"view", "addtocart", "transaction"}

ABO_LISTING_REQUIRED_FIELDS: set[str] = {
    "item_id",
    "item_name",
    "brand",
    "bullet_point",
    "product_type",
    "color",
    "material",
    "style",
    "main_image_id",
    "other_image_id",
}
ABO_IMAGE_REQUIRED_COLUMNS: set[str] = {"image_id", "path", "height", "width"}


def validate_required_columns(
    dataframe: pd.DataFrame, required_columns: set[str], dataset_name: str
) -> None:
    """Raise a clear error when a DataFrame is missing required columns."""
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{dataset_name} is missing required columns: {missing}")


def validate_unique_column(
    dataframe: pd.DataFrame, column: str, dataset_name: str
) -> None:
    """Raise a clear error when a required DataFrame column has duplicates."""
    if column not in dataframe.columns:
        raise ValueError(f"{dataset_name} is missing required column: {column}")

    duplicate_mask = dataframe[column].duplicated(keep=False)
    if duplicate_mask.any():
        duplicates = sorted(
            str(value) for value in dataframe.loc[duplicate_mask, column].dropna().unique()
        )
        duplicate_values = ", ".join(duplicates) if duplicates else "<empty>"
        raise ValueError(
            f"{dataset_name} has duplicate values in {column}: {duplicate_values}"
        )


def validate_retailrocket_events(events: pd.DataFrame) -> None:
    """Validate RetailRocket fixture events against discovered source fields."""
    validate_required_columns(
        events, RETAILROCKET_EVENT_REQUIRED_COLUMNS, "RetailRocket events"
    )

    invalid_events = set(events["event"].dropna()).difference(
        RETAILROCKET_ALLOWED_EVENT_VALUES
    )
    if events["event"].isna().any() or invalid_events:
        invalid = ", ".join(sorted(str(value) for value in invalid_events))
        raise ValueError(
            f"RetailRocket events contains invalid event values: {invalid or '<empty>'}"
        )

    transaction_rows = events["event"] == "transaction"
    has_transaction_id = events["transactionid"].notna()
    if (transaction_rows & ~has_transaction_id).any():
        raise ValueError("RetailRocket transaction events require transactionid values")
    if (~transaction_rows & has_transaction_id).any():
        raise ValueError("RetailRocket non-transaction events must not include transactionid values")


def validate_retailrocket_item_properties(item_properties: pd.DataFrame) -> None:
    """Validate RetailRocket fixture item-property columns."""
    validate_required_columns(
        item_properties,
        RETAILROCKET_ITEM_PROPERTY_REQUIRED_COLUMNS,
        "RetailRocket item properties",
    )


def validate_retailrocket_category_tree(category_tree: pd.DataFrame) -> None:
    """Validate RetailRocket fixture category-tree columns."""
    validate_required_columns(
        category_tree,
        RETAILROCKET_CATEGORY_TREE_REQUIRED_COLUMNS,
        "RetailRocket category tree",
    )
    validate_unique_column(category_tree, "categoryid", "RetailRocket category tree")


def validate_retailrocket_fixtures(fixtures: dict[str, pd.DataFrame]) -> None:
    """Validate all RetailRocket fixture files as one track-local contract."""
    required_keys = {"events", "item_properties", "category_tree"}
    _validate_fixture_keys(fixtures, required_keys, "RetailRocket fixtures")

    events = fixtures["events"]
    item_properties = fixtures["item_properties"]
    category_tree = fixtures["category_tree"]
    validate_retailrocket_events(events)
    validate_retailrocket_item_properties(item_properties)
    validate_retailrocket_category_tree(category_tree)

    missing_property_items = set(events["itemid"]).difference(item_properties["itemid"])
    if missing_property_items:
        missing = ", ".join(sorted(str(value) for value in missing_property_items))
        raise ValueError(f"RetailRocket events contain items without properties: {missing}")


def validate_abo_listings(listings: list[dict[str, Any]]) -> None:
    """Validate required fields and basic types for ABO listing fixtures."""
    if not listings:
        raise ValueError("ABO listings must contain at least one record")

    item_ids: list[str] = []
    for index, listing in enumerate(listings, start=1):
        missing_fields = ABO_LISTING_REQUIRED_FIELDS.difference(listing)
        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(f"ABO listing {index} is missing required fields: {missing}")

        item_id = listing["item_id"]
        main_image_id = listing["main_image_id"]
        other_image_ids = listing["other_image_id"]
        if not isinstance(item_id, str) or not item_id:
            raise ValueError(f"ABO listing {index} has invalid item_id")
        if not isinstance(main_image_id, str) or not main_image_id:
            raise ValueError(f"ABO listing {index} has invalid main_image_id")
        if not isinstance(other_image_ids, list) or not all(
            isinstance(image_id, str) and image_id for image_id in other_image_ids
        ):
            raise ValueError(f"ABO listing {index} has invalid other_image_id values")
        item_ids.append(item_id)

    if len(item_ids) != len(set(item_ids)):
        raise ValueError("ABO listings contains duplicate item_id values")


def validate_abo_images(images: pd.DataFrame) -> None:
    """Validate ABO image metadata fixture columns and values."""
    validate_required_columns(images, ABO_IMAGE_REQUIRED_COLUMNS, "ABO images")
    validate_unique_column(images, "image_id", "ABO images")
    validate_unique_column(images, "path", "ABO images")

    if images["image_id"].isna().any() or images["path"].isna().any():
        raise ValueError("ABO images contains empty image_id or path values")

    for column in ("height", "width"):
        values = pd.to_numeric(images[column], errors="coerce")
        if values.isna().any() or (values <= 0).any():
            raise ValueError(f"ABO images contains invalid {column} values")


def validate_abo_image_paths(image_paths: list[str], images: pd.DataFrame) -> None:
    """Validate text fixture paths against ABO image metadata paths."""
    if not image_paths or any(not path.strip() for path in image_paths):
        raise ValueError("ABO image paths must contain non-empty lines")
    if len(image_paths) != len(set(image_paths)):
        raise ValueError("ABO image paths contains duplicate values")

    csv_paths = set(images["path"])
    text_paths = set(image_paths)
    if text_paths != csv_paths:
        raise ValueError("ABO image paths must match paths in ABO images")


def validate_abo_product_image_mappings(
    listings: list[dict[str, Any]], images: pd.DataFrame
) -> None:
    """Validate ABO listing-to-image references without using another track."""
    image_ids = set(images["image_id"])
    for listing in listings:
        item_id = listing["item_id"]
        main_image_id = listing["main_image_id"]
        if main_image_id not in image_ids:
            raise ValueError(
                f"ABO listing {item_id} references unknown main_image_id: {main_image_id}"
            )
        unknown_other_ids = set(listing["other_image_id"]).difference(image_ids)
        if unknown_other_ids:
            unknown = ", ".join(sorted(unknown_other_ids))
            raise ValueError(
                f"ABO listing {item_id} references unknown other_image_id values: {unknown}"
            )


def validate_abo_fixtures(fixtures: dict[str, object]) -> None:
    """Validate all ABO fixture files as one track-local contract."""
    required_keys = {"listings", "images", "image_paths"}
    _validate_fixture_keys(fixtures, required_keys, "ABO fixtures")

    listings = fixtures["listings"]
    images = fixtures["images"]
    image_paths = fixtures["image_paths"]
    if not isinstance(listings, list):
        raise ValueError("ABO fixtures listings must be a list")
    if not isinstance(images, pd.DataFrame):
        raise ValueError("ABO fixtures images must be a DataFrame")
    if not isinstance(image_paths, list):
        raise ValueError("ABO fixtures image_paths must be a list")

    validate_abo_listings(listings)
    validate_abo_images(images)
    validate_abo_image_paths(image_paths, images)
    validate_abo_product_image_mappings(listings, images)


def _validate_fixture_keys(
    fixtures: dict[str, object], required_keys: set[str], fixture_name: str
) -> None:
    """Raise a clear error when a fixture bundle is incomplete."""
    missing_keys = required_keys.difference(fixtures)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"{fixture_name} is missing required keys: {missing}")
