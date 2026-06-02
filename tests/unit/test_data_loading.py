import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ecommerce_recommender.data.loading import load_csv


def test_load_csv_returns_dataframe_for_valid_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "products.csv"
    csv_path.write_text("product_id,product_name\np1,Running Shoes\n", encoding="utf-8")

    df = load_csv(csv_path)

    assert isinstance(df, pd.DataFrame)
    assert df.shape == (1, 2)
    assert df.loc[0, "product_id"] == "p1"


def test_load_csv_raises_file_not_found_for_missing_csv(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        load_csv(missing_path)


def test_load_csv_raises_value_error_for_empty_csv(tmp_path: Path) -> None:
    empty_path = tmp_path / "empty.csv"
    empty_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV file is empty"):
        load_csv(empty_path)
