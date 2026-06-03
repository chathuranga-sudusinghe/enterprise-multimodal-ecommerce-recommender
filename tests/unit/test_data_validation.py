import copy
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ecommerce_recommender.data.loading import (
    load_amazon_berkeley_objects_fixtures,
    load_retailrocket_fixtures,
)
from ecommerce_recommender.data.validation import (
    validate_abo_fixtures,
    validate_abo_image_paths,
    validate_retailrocket_events,
    validate_retailrocket_fixtures,
    validate_retailrocket_item_properties,
)

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "data" / "sample"


def retailrocket_fixtures() -> dict[str, pd.DataFrame]:
    return load_retailrocket_fixtures(SAMPLE_DIR / "retailrocket")


def abo_fixtures() -> dict[str, object]:
    return load_amazon_berkeley_objects_fixtures(
        SAMPLE_DIR / "amazon_berkeley_objects"
    )


def test_valid_retailrocket_fixtures_pass() -> None:
    validate_retailrocket_fixtures(retailrocket_fixtures())


def test_valid_abo_fixtures_pass() -> None:
    validate_abo_fixtures(abo_fixtures())


def test_invalid_retailrocket_event_value_fails() -> None:
    events = retailrocket_fixtures()["events"].copy()
    events.loc[0, "event"] = "click"

    with pytest.raises(ValueError, match="invalid event values: click"):
        validate_retailrocket_events(events)


def test_missing_required_retailrocket_column_fails() -> None:
    item_properties = retailrocket_fixtures()["item_properties"].drop(columns=["value"])

    with pytest.raises(ValueError, match="missing required columns: value"):
        validate_retailrocket_item_properties(item_properties)


def test_abo_missing_main_image_mapping_fails() -> None:
    fixtures = copy.deepcopy(abo_fixtures())
    fixtures["listings"][0]["main_image_id"] = "missing_image"

    with pytest.raises(ValueError, match="unknown main_image_id: missing_image"):
        validate_abo_fixtures(fixtures)


def test_abo_image_paths_match_images_csv() -> None:
    fixtures = abo_fixtures()

    validate_abo_image_paths(fixtures["image_paths"], fixtures["images"])


def test_abo_image_paths_mismatch_fails() -> None:
    fixtures = abo_fixtures()
    image_paths = list(fixtures["image_paths"])
    image_paths[0] = "images/small/ff/not_in_metadata.jpg"

    with pytest.raises(ValueError, match="must match paths in ABO images"):
        validate_abo_image_paths(image_paths, fixtures["images"])
