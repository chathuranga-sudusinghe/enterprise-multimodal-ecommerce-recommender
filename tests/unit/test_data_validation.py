import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ecommerce_recommender.data.validation import (
    validate_events,
    validate_products,
    validate_users,
)


def valid_products_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": ["p1", "p2"],
            "product_name": ["Running Shoes", "Trail Backpack"],
            "category": ["Footwear", "Bags"],
            "brand": ["Stride", "Peak"],
            "price": [89.99, 59.5],
            "description": ["Lightweight running shoes", "Durable trail backpack"],
            "image_path": ["images/p1.jpg", "images/p2.jpg"],
            "stock_status": ["in_stock", "low_stock"],
            "rating": [4.5, 4.0],
            "created_at": ["2026-01-01T00:00:00", "2026-01-02T00:00:00"],
        }
    )


def valid_users_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "user_id": ["u1", "u2"],
            "age_group": ["25-34", "35-44"],
            "country": ["US", "CA"],
            "preferred_category": ["Footwear", "Bags"],
            "created_at": ["2026-01-01T00:00:00", "2026-01-02T00:00:00"],
        }
    )


def valid_events_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "event_id": ["e1", "e2"],
            "user_id": ["u1", "u2"],
            "product_id": ["p1", "p2"],
            "event_type": ["view", "purchase"],
            "timestamp": ["2026-01-03T00:00:00", "2026-01-04T00:00:00"],
        }
    )


def test_valid_products_pass() -> None:
    validate_products(valid_products_df())


def test_missing_required_product_column_fails() -> None:
    products = valid_products_df().drop(columns=["price"])

    with pytest.raises(ValueError, match="missing required columns: price"):
        validate_products(products)


def test_duplicate_product_id_fails() -> None:
    products = valid_products_df()
    products.loc[1, "product_id"] = "p1"

    with pytest.raises(ValueError, match="duplicate values in product_id"):
        validate_products(products)


def test_invalid_price_fails() -> None:
    products = valid_products_df()
    products.loc[0, "price"] = -1

    with pytest.raises(ValueError, match="price must be >= 0"):
        validate_products(products)


def test_invalid_rating_fails() -> None:
    products = valid_products_df()
    products.loc[0, "rating"] = 6

    with pytest.raises(ValueError, match="rating must be between 0 and 5"):
        validate_products(products)


def test_invalid_stock_status_fails() -> None:
    products = valid_products_df()
    products.loc[0, "stock_status"] = "backordered"

    with pytest.raises(ValueError, match="invalid stock_status"):
        validate_products(products)


def test_valid_users_pass() -> None:
    validate_users(valid_users_df())


def test_duplicate_user_id_fails() -> None:
    users = valid_users_df()
    users.loc[1, "user_id"] = "u1"

    with pytest.raises(ValueError, match="duplicate values in user_id"):
        validate_users(users)


def test_valid_events_pass() -> None:
    validate_events(valid_events_df(), valid_users_df(), valid_products_df())


def test_invalid_event_type_fails() -> None:
    events = valid_events_df()
    events.loc[0, "event_type"] = "share"

    with pytest.raises(ValueError, match="invalid event_type"):
        validate_events(events, valid_users_df(), valid_products_df())


def test_event_with_unknown_user_fails() -> None:
    events = valid_events_df()
    events.loc[0, "user_id"] = "unknown-user"

    with pytest.raises(ValueError, match="unknown user_id"):
        validate_events(events, valid_users_df(), valid_products_df())


def test_event_with_unknown_product_fails() -> None:
    events = valid_events_df()
    events.loc[0, "product_id"] = "unknown-product"

    with pytest.raises(ValueError, match="unknown product_id"):
        validate_events(events, valid_users_df(), valid_products_df())
