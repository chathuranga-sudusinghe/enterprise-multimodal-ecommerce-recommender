"""Run TF-IDF similarity on a bounded cleaned ABO product sample."""

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
for import_root in (PROJECT_ROOT, SRC_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from ecommerce_recommender.models.abo_text_similarity import ABOTextSimilarityBaseline, build_combined_product_text  # noqa: E402
from scripts.abo_clean_runner_utils import DEFAULT_INPUT_PATH, DEFAULT_MAX_PRODUCTS, display_path, load_clean_abo_products, product_metadata, select_query_item_id  # noqa: E402

LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data/processed/abo_tfidf_similarity_5k_sample.json"
METADATA_FIELDS = ("item_name", "brand", "product_type", "color", "material", "style")


def load_abo_products(sample_path: Path) -> list[dict[str, Any]]:
    """Load small ABO fixtures from JSON, JSONL, or CSV for compatibility."""
    suffix = sample_path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        records = payload if isinstance(payload, list) else next((payload[key] for key in ("products", "listings", "items", "records") if isinstance(payload.get(key), list)), None)
        if records is None:
            raise ValueError(f"JSON sample must contain a list of product records: {sample_path}")
        return _ensure_product_records(records)
    if suffix == ".jsonl":
        return _ensure_product_records([json.loads(line) for line in sample_path.read_text(encoding="utf-8").splitlines() if line.strip()])
    if suffix == ".csv":
        with sample_path.open("r", encoding="utf-8", newline="") as handle:
            return _ensure_product_records(list(csv.DictReader(handle)))
    raise ValueError(f"Unsupported ABO sample file format: {sample_path.suffix}")


def create_sample_output(products: Sequence[Mapping[str, Any]], input_sample_path: Path, top_k: int = 3, generated_at_utc: str | None = None, query_item_id: str | None = None) -> dict[str, Any]:
    """Create aligned TF-IDF runner output."""
    generated_at_utc = generated_at_utc or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    source_product_id = select_query_item_id(products, query_item_id)
    product_lookup = {_product_id(product): product for product in products}
    if source_product_id not in product_lookup:
        raise ValueError(f"Query item_id is not present in the loaded sample: {source_product_id}")
    results = ABOTextSimilarityBaseline().fit(products).recommend_similar(source_product_id, top_k=top_k)
    return {
        "baseline_name": "abo_text_similarity_baseline",
        "method_name": "tfidf_text_similarity",
        "dataset_track": "amazon_berkeley_text_images-based",
        "method": "Text-only product-to-product similarity using TF-IDF and cosine similarity.",
        "input_file": display_path(input_sample_path),
        "input_sample_path": display_path(input_sample_path),
        "products_loaded": len(products),
        "query_item_id": source_product_id,
        "source_product_id": source_product_id,
        "source_product_metadata": _metadata_for_output(product_lookup[source_product_id]),
        "top_k": top_k,
        "generated_at_utc": generated_at_utc,
        "recommendations": [{"item_id": result.product_id, "score": round(result.similarity_score, 6), **product_metadata(product_lookup[result.product_id])} for result in results],
        "assumptions": ["ABO cleaned products only; RetailRocket data and identifiers are not used."],
        "limitations": ["This runner performs non-personalized text similarity only."],
    }


def select_source_product_id(products: Sequence[Mapping[str, Any]]) -> str:
    candidates = sorted(_product_id(product) for product in products if build_combined_product_text(product))
    if not candidates:
        raise ValueError("No ABO products with usable text were found in the sample.")
    return candidates[0]


def write_output_artifact(output: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", "--sample-path", dest="input_path", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--output", "--output-path", dest="output_path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--max-products", type=int, default=DEFAULT_MAX_PRODUCTS)
    parser.add_argument("--query-item-id", default=None)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    products = load_clean_abo_products(args.input_path, args.max_products)
    output = create_sample_output(products, args.input_path, args.top_k, query_item_id=args.query_item_id)
    write_output_artifact(output, args.output_path)
    LOGGER.info("Wrote ABO TF-IDF results to %s", args.output_path)


def _ensure_product_records(records: Sequence[Any]) -> list[dict[str, Any]]:
    products = []
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


if __name__ == "__main__":
    main()
