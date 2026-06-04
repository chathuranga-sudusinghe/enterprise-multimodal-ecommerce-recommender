"""Run the Amazon Berkeley Objects text similarity baseline on a small sample."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ecommerce_recommender.models.abo_text_similarity import (  # noqa: E402
    ABOTextSimilarityBaseline,
    build_combined_product_text,
)


LOGGER = logging.getLogger(__name__)

DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "docs/reports/abo_text_similarity_sample_output.json"
DEFAULT_SAMPLE_CANDIDATES = (
    PROJECT_ROOT / "data/sample/amazon_berkeley_objects/listings_sample.json",
    PROJECT_ROOT / "data/sample/amazon_berkeley_objects/listings_sample.jsonl",
    PROJECT_ROOT / "data/sample/amazon_berkeley_objects/abo_listings_sample.json",
    PROJECT_ROOT / "data/sample/amazon_berkeley_objects/abo_listings_sample.jsonl",
    PROJECT_ROOT / "data/sample/amazon_berkeley_objects/sample_listings.json",
    PROJECT_ROOT / "data/sample/amazon_berkeley_objects/sample_listings.jsonl",
    PROJECT_ROOT / "data/sample/amazon_berkeley_objects/listings.csv",
)

METADATA_FIELDS = (
    "item_name",
    "brand",
    "product_type",
    "color",
    "material",
    "style",
)


def find_default_sample_path() -> Path:
    """Return the first known small ABO sample fixture path that exists."""

    for candidate in DEFAULT_SAMPLE_CANDIDATES:
        if candidate.exists():
            return candidate

    candidates = ", ".join(str(path.relative_to(PROJECT_ROOT)) for path in DEFAULT_SAMPLE_CANDIDATES)
    raise FileNotFoundError(f"No small ABO sample fixture found. Checked: {candidates}")


def load_abo_products(sample_path: Path) -> list[dict[str, Any]]:
    """Load small ABO listing fixtures from JSON, JSONL, or CSV."""

    suffix = sample_path.suffix.lower()
    if suffix == ".json":
        return _load_json_products(sample_path)
    if suffix == ".jsonl":
        return _load_jsonl_products(sample_path)
    if suffix == ".csv":
        return _load_csv_products(sample_path)

    raise ValueError(f"Unsupported ABO sample file format: {sample_path.suffix}")


def create_sample_output(
    products: Sequence[Mapping[str, Any]],
    input_sample_path: Path,
    top_k: int = 3,
    generated_at_utc: str | None = None,
) -> dict[str, Any]:
    """Create an inspectable JSON-ready output for the ABO text baseline."""

    if generated_at_utc is None:
        generated_at_utc = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    source_product_id = select_source_product_id(products)
    product_lookup = {_product_id(product): product for product in products}
    baseline = ABOTextSimilarityBaseline().fit(products)
    recommendations = baseline.recommend_similar(source_product_id, top_k=top_k)

    return {
        "baseline_name": "abo_text_similarity_baseline",
        "dataset_track": "amazon_berkeley_text_images-based",
        "method": "Text-only product-to-product similarity using TF-IDF and cosine similarity.",
        "input_sample_path": _display_path(input_sample_path),
        "top_k": top_k,
        "generated_at_utc": generated_at_utc,
        "source_product_id": source_product_id,
        "source_product_metadata": _metadata_for_output(product_lookup[source_product_id]),
        "recommendations": [
            {
                "product_id": result.product_id,
                "similarity_score": round(result.similarity_score, 6),
                "metadata": _metadata_for_output(product_lookup[result.product_id]),
            }
            for result in recommendations
        ],
        "assumptions": [
            "This artifact uses a small Amazon Berkeley Objects sample fixture only.",
            "Recommendations are non-personalized and use product metadata text only.",
            "RetailRocket behavior data and identifiers are not used.",
        ],
        "limitations": [
            "This does not implement image similarity or multimodal recommendation.",
            "This does not use user events, API serving, deployment, RAG, agents, MCP, contextual bandits, or advanced models.",
            "Small sample output is for inspection and repeatability, not production performance claims.",
        ],
    }


def select_source_product_id(products: Sequence[Mapping[str, Any]]) -> str:
    """Select the first stable product ID with usable text."""

    candidates = sorted(
        (
            _product_id(product)
            for product in products
            if build_combined_product_text(product)
        )
    )
    if not candidates:
        raise ValueError("No ABO products with usable text were found in the sample.")
    return candidates[0]


def write_output_artifact(output: Mapping[str, Any], output_path: Path) -> None:
    """Write a deterministic, human-readable JSON artifact."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-path", type=Path, default=None)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    sample_path = args.sample_path or find_default_sample_path()
    products = load_abo_products(sample_path)
    output = create_sample_output(products, input_sample_path=sample_path, top_k=args.top_k)
    write_output_artifact(output, args.output_path)

    LOGGER.info("Wrote ABO text similarity sample output to %s", args.output_path)


def _load_json_products(sample_path: Path) -> list[dict[str, Any]]:
    payload = json.loads(sample_path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return _ensure_product_records(payload)
    if isinstance(payload, dict):
        for key in ("products", "listings", "items", "records"):
            if isinstance(payload.get(key), list):
                return _ensure_product_records(payload[key])
    raise ValueError(f"JSON sample must contain a list of product records: {sample_path}")


def _load_jsonl_products(sample_path: Path) -> list[dict[str, Any]]:
    records = [
        json.loads(line)
        for line in sample_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return _ensure_product_records(records)


def _load_csv_products(sample_path: Path) -> list[dict[str, Any]]:
    with sample_path.open("r", encoding="utf-8", newline="") as file:
        return _ensure_product_records(list(csv.DictReader(file)))


def _ensure_product_records(records: Sequence[Any]) -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, Mapping):
            raise ValueError("ABO sample records must be mapping objects.")
        _product_id(record)
        products.append(dict(record))
    return products


def _metadata_for_output(product: Mapping[str, Any]) -> dict[str, Any]:
    return {field: product[field] for field in METADATA_FIELDS if product.get(field) not in (None, "")}


def _product_id(product: Mapping[str, Any]) -> str:
    product_id = product.get("item_id", product.get("product_id"))
    if product_id is None or str(product_id).strip() == "":
        raise ValueError("ABO product record is missing item_id.")
    return str(product_id)


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
