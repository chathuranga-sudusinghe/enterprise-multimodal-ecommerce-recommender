"""Run a small real CLIP similarity sample for Amazon Berkeley Objects products."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ecommerce_recommender.models.abo_clip_similarity import (  # noqa: E402
    ABOCLIPProduct,
    ABOCLIPSimilarityModel,
    DEFAULT_CLIP_MODEL_NAME,
)
from ecommerce_recommender.models.abo_text_similarity import build_combined_product_text  # noqa: E402


LOGGER = logging.getLogger(__name__)

DEFAULT_SAMPLE_PATH = PROJECT_ROOT / "data/sample/amazon_berkeley_objects/listings_sample.jsonl"
DEFAULT_IMAGE_ROOT = PROJECT_ROOT / "data/sample/amazon_berkeley_objects/images/small"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data/processed/abo_clip_similarity_sample.json"


def load_sample_products(
    sample_path: Path = DEFAULT_SAMPLE_PATH,
    image_root: Path = DEFAULT_IMAGE_ROOT,
    limit: int = 6,
) -> list[ABOCLIPProduct]:
    """Load a bounded set of ABO sample products with text and main images."""

    records = _load_jsonl_records(sample_path)
    products: list[ABOCLIPProduct] = []

    for record in records:
        product_id = _required_text(record, "item_id")
        image_id = _required_text(record, "main_image_id")
        text = build_combined_product_text(record)
        image_path = _image_path_for_id(image_root, image_id)

        if not text:
            raise ValueError(f"ABO sample product {product_id} has no usable text.")
        if not image_path.exists():
            raise FileNotFoundError(f"ABO sample image does not exist: {image_path}")

        products.append(
            ABOCLIPProduct(
                product_id=product_id,
                text=text,
                image_path=image_path,
            )
        )
        if len(products) >= limit:
            break

    if not products:
        raise ValueError(f"No usable ABO sample products found in {sample_path}")
    return products


def run_clip_similarity(
    products: Sequence[ABOCLIPProduct],
    source_product_id: str | None = None,
    top_k: int = 3,
    model_name: str = DEFAULT_CLIP_MODEL_NAME,
) -> dict[str, Any]:
    """Run real CLIP product-to-product similarity and return JSON-ready output."""

    selected_source_id = source_product_id or products[0].product_id
    model = ABOCLIPSimilarityModel(model_name=model_name)
    results = model.similar_items(products, selected_source_id, top_k=top_k)

    return {
        "model_name": model_name,
        "source_product_id": selected_source_id,
        "top_k": top_k,
        "results": [
            {
                "product_id": result.product_id,
                "score": round(result.score, 6),
            }
            for result in results
        ],
    }


def write_output(output: Mapping[str, Any], output_path: Path = DEFAULT_OUTPUT_PATH) -> None:
    """Write CLIP similarity output as stable, human-readable JSON."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample-path", type=Path, default=DEFAULT_SAMPLE_PATH)
    parser.add_argument("--image-root", type=Path, default=DEFAULT_IMAGE_ROOT)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--source-product-id", default=None)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--model-name", default=DEFAULT_CLIP_MODEL_NAME)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    products = load_sample_products(
        sample_path=args.sample_path,
        image_root=args.image_root,
        limit=args.limit,
    )
    output = run_clip_similarity(
        products,
        source_product_id=args.source_product_id,
        top_k=args.top_k,
        model_name=args.model_name,
    )
    write_output(output, args.output_path)
    LOGGER.info("Wrote ABO CLIP similarity sample output to %s", args.output_path)


def _load_jsonl_records(sample_path: Path) -> list[dict[str, Any]]:
    records = [
        json.loads(line)
        for line in sample_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not all(isinstance(record, dict) for record in records):
        raise ValueError(f"ABO sample records must be JSON objects: {sample_path}")
    return records


def _required_text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if value is None or str(value).strip() == "":
        raise ValueError(f"ABO sample record is missing required field: {field}")
    return str(value)


def _image_path_for_id(image_root: Path, image_id: str) -> Path:
    return image_root / image_id[:2] / f"{image_id}.jpg"


if __name__ == "__main__":
    main()
