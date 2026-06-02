from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """Load a non-empty CSV file into a pandas DataFrame."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    try:
        df = pd.read_csv(path)
    except EmptyDataError as exc:
        raise ValueError(f"CSV file is empty: {path}") from exc

    if df.empty:
        raise ValueError(f"CSV file is empty: {path}")

    return df


def load_sample_datasets(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Load Version 1 sample products, users, and events datasets."""
    directory = Path(data_dir)

    return {
        "products": load_csv(directory / "products.csv"),
        "users": load_csv(directory / "users.csv"),
        "events": load_csv(directory / "events.csv"),
    }
