import pandas as pd

PRODUCT_REQUIRED_COLUMNS: set[str] = {
    "product_id",
    "product_name",
    "category",
    "brand",
    "price",
    "description",
    "stock_status",
    "created_at",
}

USER_REQUIRED_COLUMNS: set[str] = {
    "user_id",
    "created_at",
}

EVENT_REQUIRED_COLUMNS: set[str] = {
    "event_id",
    "user_id",
    "product_id",
    "event_type",
    "timestamp",
}

ALLOWED_EVENT_TYPES: set[str] = {
    "view",
    "click",
    "add_to_cart",
    "purchase",
    "not_interested",
}

ALLOWED_STOCK_STATUS: set[str] = {
    "in_stock",
    "low_stock",
    "out_of_stock",
}


def validate_required_columns(
    df: pd.DataFrame, required_columns: set[str], dataset_name: str
) -> None:
    """Validate that all required columns exist in a dataset."""
    missing_columns = required_columns.difference(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{dataset_name} is missing required columns: {missing}")


def validate_unique_column(df: pd.DataFrame, column: str, dataset_name: str) -> None:
    """Validate that a column contains unique values."""
    if column not in df.columns:
        raise ValueError(f"{dataset_name} is missing required column: {column}")

    duplicate_mask = df[column].duplicated(keep=False)
    if duplicate_mask.any():
        duplicates = sorted(str(value) for value in df.loc[duplicate_mask, column].dropna().unique())
        duplicate_values = ", ".join(duplicates) if duplicates else "<empty>"
        raise ValueError(
            f"{dataset_name} has duplicate values in {column}: {duplicate_values}"
        )


def validate_products(products_df: pd.DataFrame) -> None:
    """Validate the Version 1 products dataset."""
    validate_required_columns(products_df, PRODUCT_REQUIRED_COLUMNS, "products")
    validate_unique_column(products_df, "product_id", "products")

    price_values = pd.to_numeric(products_df["price"], errors="coerce")
    if price_values.isna().any() or (price_values < 0).any():
        raise ValueError("products contains invalid price values; price must be >= 0")

    if "rating" in products_df.columns:
        rating_source = products_df["rating"]
        rating_values = pd.to_numeric(rating_source, errors="coerce")
        provided_rating = rating_source.notna()
        invalid_rating = rating_values[provided_rating].isna().any() or (
            (rating_values[provided_rating] < 0) | (rating_values[provided_rating] > 5)
        ).any()
        if invalid_rating:
            raise ValueError("products contains invalid rating values; rating must be between 0 and 5")

    invalid_stock_status = set(products_df["stock_status"].dropna()).difference(
        ALLOWED_STOCK_STATUS
    )
    if products_df["stock_status"].isna().any() or invalid_stock_status:
        invalid = ", ".join(sorted(str(value) for value in invalid_stock_status))
        raise ValueError(
            f"products contains invalid stock_status values: {invalid or '<empty>'}"
        )


def validate_users(users_df: pd.DataFrame) -> None:
    """Validate the Version 1 users dataset."""
    validate_required_columns(users_df, USER_REQUIRED_COLUMNS, "users")
    validate_unique_column(users_df, "user_id", "users")


def validate_events(
    events_df: pd.DataFrame, users_df: pd.DataFrame, products_df: pd.DataFrame
) -> None:
    """Validate the Version 1 events dataset and references."""
    validate_required_columns(events_df, EVENT_REQUIRED_COLUMNS, "events")
    validate_unique_column(events_df, "event_id", "events")

    invalid_event_types = set(events_df["event_type"].dropna()).difference(
        ALLOWED_EVENT_TYPES
    )
    if events_df["event_type"].isna().any() or invalid_event_types:
        invalid = ", ".join(sorted(str(value) for value in invalid_event_types))
        raise ValueError(
            f"events contains invalid event_type values: {invalid or '<empty>'}"
        )

    unknown_users = set(events_df["user_id"]).difference(set(users_df["user_id"]))
    if unknown_users:
        unknown = ", ".join(sorted(str(user_id) for user_id in unknown_users))
        raise ValueError(f"events contains unknown user_id values: {unknown}")

    unknown_products = set(events_df["product_id"]).difference(set(products_df["product_id"]))
    if unknown_products:
        unknown = ", ".join(sorted(str(product_id) for product_id in unknown_products))
        raise ValueError(f"events contains unknown product_id values: {unknown}")


def validate_sample_datasets(datasets: dict[str, pd.DataFrame]) -> None:
    """Validate loaded Version 1 sample datasets."""
    required_keys = {"products", "users", "events"}
    missing_keys = required_keys.difference(datasets)

    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise ValueError(f"sample datasets are missing required keys: {missing}")

    products_df = datasets["products"]
    users_df = datasets["users"]
    events_df = datasets["events"]

    validate_products(products_df)
    validate_users(users_df)
    validate_events(events_df, users_df, products_df)
