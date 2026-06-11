"""Run CLIP multimodal similarity on a bounded cleaned ABO product sample."""

from __future__ import annotations

import argparse
import logging
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
for import_root in (PROJECT_ROOT, SRC_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from ecommerce_recommender.models.abo_clip_similarity import ABOCLIPProduct, ABOCLIPSimilarityModel, DEFAULT_CLIP_MODEL_NAME  # noqa: E402
from scripts.abo_clean_runner_utils import DEFAULT_IMAGES_TAR_PATH, DEFAULT_INPUT_PATH, DEFAULT_MAX_PRODUCTS, display_path, extract_sample_images, load_clean_abo_products, product_metadata, select_query_item_id, write_json_output  # noqa: E402

LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data/processed/abo_clip_similarity_5k_sample.json"


def build_clip_products(records: Sequence[Mapping[str, Any]], image_root: Path) -> list[ABOCLIPProduct]:
    return [ABOCLIPProduct(product_id=str(record["item_id"]), text=str(record["combined_text"]), image_path=image_root / str(record["image_path"])) for record in records]


def run_clip_similarity(products: Sequence[ABOCLIPProduct], product_records: Sequence[Mapping[str, Any]], input_path: Path, query_item_id: str | None = None, top_k: int = 5, model_name: str = DEFAULT_CLIP_MODEL_NAME, local_files_only: bool = False) -> dict[str, Any]:
    selected_query = select_query_item_id(product_records, query_item_id)
    lookup = {str(product["item_id"]): product for product in product_records}
    results = ABOCLIPSimilarityModel(
        model_name=model_name,
        local_files_only=local_files_only,
    ).similar_items(products, selected_query, top_k)
    return {
        "method_name": "clip_multimodal_similarity",
        "model_name": model_name,
        "input_file": display_path(input_path),
        "products_loaded": len(products),
        "query_item_id": selected_query,
        "query_product": {"item_id": selected_query, **product_metadata(lookup[selected_query])},
        "top_k": top_k,
        "recommendations": [{"item_id": result.product_id, "score": round(result.score, 6), **product_metadata(lookup[result.product_id])} for result in results],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLIP runner command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--images-tar", type=Path, default=DEFAULT_IMAGES_TAR_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--max-products", type=int, default=DEFAULT_MAX_PRODUCTS)
    parser.add_argument("--query-item-id", default=None)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--model-name", default=DEFAULT_CLIP_MODEL_NAME)
    parser.add_argument(
        "--local-files-only",
        action="store_true",
        help="Load CLIP strictly from the local Hugging Face cache without network checks.",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    records = load_clean_abo_products(args.input, args.max_products)
    with tempfile.TemporaryDirectory(prefix="abo-clip-run-") as temp_dir:
        image_root = extract_sample_images(args.images_tar, records, Path(temp_dir))
        output = run_clip_similarity(
            build_clip_products(records, image_root),
            records,
            args.input,
            args.query_item_id,
            args.top_k,
            args.model_name,
            args.local_files_only,
        )
    write_json_output(output, args.output)
    LOGGER.info("Wrote ABO CLIP results to %s", args.output)


if __name__ == "__main__":
    main()
