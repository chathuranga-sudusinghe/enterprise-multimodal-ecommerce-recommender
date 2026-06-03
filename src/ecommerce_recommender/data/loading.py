"""Fixture loading helpers for the independent recommendation dataset tracks."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import EmptyDataError

logger = logging.getLogger(__name__)


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """Load a non-empty fixture CSV file into a DataFrame.

    This helper is intended for small fixture files. Large raw datasets require
    dedicated bounded or chunked readers.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    try:
        dataframe = pd.read_csv(path)
    except EmptyDataError as exc:
        raise ValueError(f"CSV file is empty: {path}") from exc

    if dataframe.empty:
        raise ValueError(f"CSV file is empty: {path}")

    logger.debug("Loaded fixture CSV %s with %d rows", path, len(dataframe))
    return dataframe


def load_jsonl(file_path: str | Path) -> list[dict[str, Any]]:
    """Load non-empty JSON Lines fixture records from a file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"JSONL file not found: {path}")

    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"JSONL file contains invalid JSON at line {line_number}: {path}"
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"JSONL record at line {line_number} must be an object: {path}"
                )
            records.append(record)

    if not records:
        raise ValueError(f"JSONL file is empty: {path}")

    logger.debug("Loaded fixture JSONL %s with %d records", path, len(records))
    return records


def load_text_lines(file_path: str | Path) -> list[str]:
    """Load stripped, non-empty lines from a fixture text file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Text file not found: {path}")

    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    non_empty_lines = [line for line in lines if line]
    if not non_empty_lines:
        raise ValueError(f"Text file is empty: {path}")

    logger.debug("Loaded fixture text file %s with %d lines", path, len(non_empty_lines))
    return non_empty_lines


def load_retailrocket_fixtures(fixture_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Load the small RetailRocket fixture files from their track directory."""
    directory = Path(fixture_dir)
    return {
        "events": load_csv(directory / "events_sample.csv"),
        "item_properties": load_csv(directory / "item_properties_sample.csv"),
        "category_tree": load_csv(directory / "category_tree_sample.csv"),
    }


def load_amazon_berkeley_objects_fixtures(fixture_dir: str | Path) -> dict[str, object]:
    """Load the small Amazon Berkeley Objects fixture files."""
    directory = Path(fixture_dir)
    return {
        "listings": load_jsonl(directory / "listings_sample.jsonl"),
        "images": load_csv(directory / "images_sample.csv"),
        "image_paths": load_text_lines(directory / "image_paths_sample.txt"),
    }


def load_sample_fixtures(sample_dir: str | Path) -> dict[str, dict[str, object]]:
    """Load both fixture tracks without reading any raw dataset files."""
    directory = Path(sample_dir)
    return {
        "retailrocket": load_retailrocket_fixtures(directory / "retailrocket"),
        "amazon_berkeley_objects": load_amazon_berkeley_objects_fixtures(
            directory / "amazon_berkeley_objects"
        ),
    }
