"""Discover RetailRocket dataset structure safely with chunked reads."""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHUNK_SIZE = 100_000
RAW_DATA_DIR = PROJECT_ROOT / "data/raw/RetailRocket_event-based"
REPORT_PATH = PROJECT_ROOT / "docs/reports/retailrocket_dataset_discovery.md"
CSV_FILES = ("events.csv", "item_properties_part1.csv", "item_properties_part2.csv", "category_tree.csv")


@dataclass(frozen=True)
class CsvInventory:
    """Safe file-level CSV inventory metadata."""

    path: Path
    size_bytes: int
    records: int
    columns: tuple[str, ...]

    @property
    def size_mb(self) -> float:
        """Return file size in mebibytes."""
        return self.size_bytes / (1024 * 1024)


def require_file(path: Path) -> None:
    """Raise a clear error when an expected raw file is missing."""
    if not path.is_file():
        raise FileNotFoundError(f"RetailRocket raw file not found: {path}")


def count_records(path: Path) -> int:
    """Count records with streaming file iteration, excluding the header."""
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        return max(sum(1 for _ in csv_file) - 1, 0)


def read_columns(path: Path) -> tuple[str, ...]:
    """Read only the CSV header."""
    return tuple(str(column) for column in pd.read_csv(path, nrows=0).columns)


def inspect_inventory(path: Path) -> CsvInventory:
    """Collect basic CSV inventory data without loading the full file."""
    require_file(path)
    LOGGER.info("Inventory: %s", path)
    return CsvInventory(path, path.stat().st_size, count_records(path), read_columns(path))


def update_min_max(current_min: int | None, current_max: int | None, series: pd.Series) -> tuple[int | None, int | None]:
    """Update integer timestamp bounds from a chunk column."""
    numeric = pd.to_numeric(series, errors="coerce").dropna()
    if numeric.empty:
        return current_min, current_max
    chunk_min, chunk_max = int(numeric.min()), int(numeric.max())
    return (
        chunk_min if current_min is None else min(current_min, chunk_min),
        chunk_max if current_max is None else max(current_max, chunk_max),
    )


def inspect_events(path: Path) -> dict[str, object]:
    """Aggregate RetailRocket event statistics with chunked reads only."""
    LOGGER.info("Chunk scan: %s", path)
    event_counts: Counter[str] = Counter()
    visitor_ids: set[int] = set()
    item_ids: set[int] = set()
    timestamp_min: int | None = None
    timestamp_max: int | None = None
    transaction_non_null = 0
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        event_counts.update(chunk["event"].dropna().astype(str))
        visitor_ids.update(chunk["visitorid"].dropna().astype(int))
        item_ids.update(chunk["itemid"].dropna().astype(int))
        timestamp_min, timestamp_max = update_min_max(timestamp_min, timestamp_max, chunk["timestamp"])
        transaction_non_null += int(chunk["transactionid"].notna().sum())
    return {
        "event_counts": event_counts,
        "unique_visitors": len(visitor_ids),
        "unique_items": len(item_ids),
        "timestamp_min": timestamp_min,
        "timestamp_max": timestamp_max,
        "transaction_non_null": transaction_non_null,
    }


def inspect_item_properties(path: Path) -> dict[str, object]:
    """Aggregate one item-properties file with chunked reads only."""
    LOGGER.info("Chunk scan: %s", path)
    item_ids: set[int] = set()
    property_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    timestamp_min: int | None = None
    timestamp_max: int | None = None
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        item_ids.update(chunk["itemid"].dropna().astype(int))
        property_counts.update(chunk["property"].dropna().astype(str))
        missing_counts.update({column: int(count) for column, count in chunk.isna().sum().items()})
        timestamp_min, timestamp_max = update_min_max(timestamp_min, timestamp_max, chunk["timestamp"])
    return {
        "unique_items": len(item_ids),
        "property_counts": property_counts,
        "missing_counts": missing_counts,
        "timestamp_min": timestamp_min,
        "timestamp_max": timestamp_max,
    }


def inspect_category_tree(path: Path) -> dict[str, int]:
    """Inspect the small category tree file normally."""
    LOGGER.info("Small-file scan: %s", path)
    category_tree = pd.read_csv(path)
    return {
        "records": len(category_tree),
        "unique_categories": int(category_tree["categoryid"].nunique()),
        "missing_parentid": int(category_tree["parentid"].isna().sum()),
    }


def format_counter(counter: Counter[str], limit: int | None = None) -> str:
    """Format counter values as Markdown bullets."""
    return "\n".join(f"- `{name}`: {count:,}" for name, count in counter.most_common(limit)) or "- None"


def build_report(inventories: list[CsvInventory], events: dict[str, object], properties: dict[str, dict[str, object]], category_tree: dict[str, int]) -> str:
    """Build the RetailRocket discovery Markdown report."""
    lines = [
        "# RetailRocket Dataset Discovery", "",
        "This report was generated with header-only reads, streaming line counts, and chunked aggregation (`chunksize=100_000`). No large raw CSV file was loaded fully into memory.", "",
        "## Raw File Inventory", "", "| File | Size MB | Records | Columns |", "| --- | ---: | ---: | --- |",
    ]
    for inventory in inventories:
        columns = ", ".join(f"`{column}`" for column in inventory.columns)
        lines.append(f"| {inventory.path.name} | {inventory.size_mb:.2f} | {inventory.records:,} | {columns} |")
    lines.extend([
        "", "## Events Overview", "",
        f"- Unique visitors: {events['unique_visitors']:,}", f"- Unique items: {events['unique_items']:,}",
        f"- Timestamp range: `{events['timestamp_min']}` to `{events['timestamp_max']}` (raw Unix milliseconds)",
        f"- Non-null transaction IDs: {events['transaction_non_null']:,}", "", "### Event Distribution", "", format_counter(events["event_counts"]),
        "", "## Item Property Overview",
    ])
    for file_name, stats in properties.items():
        missing = ", ".join(f"`{name}`={count:,}" for name, count in stats["missing_counts"].items())
        lines.extend([
            "", f"### {file_name}", "", f"- Unique items: {stats['unique_items']:,}",
            f"- Timestamp range: `{stats['timestamp_min']}` to `{stats['timestamp_max']}` (raw Unix milliseconds)",
            f"- Missing values by column: {missing}", "- Top property values by frequency:", format_counter(stats["property_counts"], limit=15),
        ])
    category_inventory = next(item for item in inventories if item.path.name == "category_tree.csv")
    lines.extend([
        "", "## Category Tree Overview", "", f"- Records: {category_tree['records']:,}",
        f"- Columns: {', '.join(f'`{column}`' for column in category_inventory.columns)}",
        f"- Unique category IDs: {category_tree['unique_categories']:,}", f"- Missing parent IDs: {category_tree['missing_parentid']:,}",
        "", "## Baseline Signals Available", "",
        "- Behavioral events: `view`, `addtocart`, and `transaction`.",
        "- Item popularity can be measured from observed interaction frequency and recency.",
        "- Visitor histories support later personalized behavior-based methods.",
        "- Item properties and the category tree may support later metadata-aware analysis after canonical mapping decisions.",
        "- Event weights remain provisional until the business task and evaluation protocol are defined.",
        "", "## Limitations", "",
        "- RetailRocket item and visitor identifiers are specific to this dataset track.",
        "- The event schema does not contain the synthetic fixture fields `event_id`, `user_id`, or `product_id`.",
        "- Item properties are stored as timestamped key-value rows and require deliberate canonicalization.",
        "- This report does not define model weights, train models, or merge RetailRocket with any other dataset.", "",
    ])
    return "\n".join(lines)


def main() -> None:
    """Run safe RetailRocket discovery and write the Markdown report."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    inventories = [inspect_inventory(RAW_DATA_DIR / file_name) for file_name in CSV_FILES]
    events = inspect_events(RAW_DATA_DIR / "events.csv")
    properties = {file_name: inspect_item_properties(RAW_DATA_DIR / file_name) for file_name in ("item_properties_part1.csv", "item_properties_part2.csv")}
    category_tree = inspect_category_tree(RAW_DATA_DIR / "category_tree.csv")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_report(inventories, events, properties, category_tree), encoding="utf-8")
    LOGGER.info("Wrote report: %s", REPORT_PATH)


if __name__ == "__main__":
    main()
