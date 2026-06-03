import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ecommerce_recommender.data.loading import (
    load_amazon_berkeley_objects_fixtures,
    load_csv,
    load_retailrocket_fixtures,
    load_sample_fixtures,
)

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "data" / "sample"


def test_load_csv_returns_dataframe_for_valid_fixture_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "events_sample.csv"
    csv_path.write_text("timestamp,visitorid\n1430622004384,101\n", encoding="utf-8")

    dataframe = load_csv(csv_path)

    assert isinstance(dataframe, pd.DataFrame)
    assert dataframe.shape == (1, 2)
    assert dataframe.loc[0, "visitorid"] == 101


def test_load_csv_raises_file_not_found_for_missing_csv(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        load_csv(tmp_path / "missing.csv")


def test_load_csv_raises_value_error_for_empty_csv(tmp_path: Path) -> None:
    empty_path = tmp_path / "empty.csv"
    empty_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV file is empty"):
        load_csv(empty_path)


def test_load_retailrocket_fixtures() -> None:
    fixtures = load_retailrocket_fixtures(SAMPLE_DIR / "retailrocket")

    assert set(fixtures) == {"events", "item_properties", "category_tree"}
    assert set(fixtures["events"].columns) == {
        "timestamp",
        "visitorid",
        "event",
        "itemid",
        "transactionid",
    }
    assert len(fixtures["events"]) == 18


def test_load_amazon_berkeley_objects_fixtures() -> None:
    fixtures = load_amazon_berkeley_objects_fixtures(
        SAMPLE_DIR / "amazon_berkeley_objects"
    )

    assert set(fixtures) == {"listings", "images", "image_paths"}
    assert len(fixtures["listings"]) == 6
    assert len(fixtures["images"]) == 10
    assert len(fixtures["image_paths"]) == 10


def test_load_sample_fixtures_keeps_tracks_separate() -> None:
    fixtures = load_sample_fixtures(SAMPLE_DIR)

    assert set(fixtures) == {"retailrocket", "amazon_berkeley_objects"}
    assert "events" in fixtures["retailrocket"]
    assert "listings" in fixtures["amazon_berkeley_objects"]
