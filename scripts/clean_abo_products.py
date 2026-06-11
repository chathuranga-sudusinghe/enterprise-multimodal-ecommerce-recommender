"""Clean a bounded ABO sample into CLIP-ready JSON Lines records."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ecommerce_recommender.data.clean_abo_products import (  # noqa: E402
    clean_abo_products,
    write_clean_products_jsonl,
)

LOGGER = logging.getLogger(__name__)

DEFAULT_RAW_DIR = PROJECT_ROOT / "data/raw/amazon_berkeley_text_images-based"
DEFAULT_LISTINGS_TAR = DEFAULT_RAW_DIR / "abo-listings.tar"
DEFAULT_IMAGES_TAR = DEFAULT_RAW_DIR / "abo-images-small.tar"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/processed/abo_clean_products_sample.jsonl"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-records", type=int, default=1000)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    """Run bounded ABO cleaning and write JSON Lines output."""
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    records, summary = clean_abo_products(
        DEFAULT_LISTINGS_TAR,
        DEFAULT_IMAGES_TAR,
        max_records=args.max_records,
    )
    rows_written = write_clean_products_jsonl(records, args.output)
    LOGGER.info("Wrote %d CLIP-ready ABO records to %s", rows_written, args.output)
    LOGGER.info("Cleaning summary: %s", summary.to_dict())


if __name__ == "__main__":
    main()
