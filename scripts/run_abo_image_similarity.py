"""Run RGB histogram similarity on a bounded cleaned ABO product sample."""

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

from ecommerce_recommender.models.abo_image_similarity import ABOImageSimilarityBaseline  # noqa: E402
from scripts.abo_clean_runner_utils import DEFAULT_IMAGES_TAR_PATH, DEFAULT_INPUT_PATH, DEFAULT_MAX_PRODUCTS, build_image_records, display_path, extract_sample_images, load_clean_abo_products, product_metadata, select_query_item_id, write_json_output  # noqa: E402

LOGGER = logging.getLogger(__name__)
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data/processed/abo_image_similarity_5k_sample.json"


def run_image_similarity(products: Sequence[Mapping[str, Any]], image_root: Path, input_path: Path, query_item_id: str | None = None, top_k: int = 5) -> dict[str, Any]:
    selected_query = select_query_item_id(products, query_item_id)
    lookup = {str(product["item_id"]): product for product in products}
    results = ABOImageSimilarityBaseline().fit(products, build_image_records(products), image_root).recommend_similar(selected_query, top_k)
    return {
        "method_name": "rgb_histogram_image_similarity",
        "input_file": display_path(input_path),
        "products_loaded": len(products),
        "query_item_id": selected_query,
        "query_product": {"item_id": selected_query, **product_metadata(lookup[selected_query])},
        "top_k": top_k,
        "recommendations": [{"item_id": result.product_id, "score": round(result.similarity_score, 6), **product_metadata(lookup[result.product_id])} for result in results],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH)
    parser.add_argument("--images-tar", type=Path, default=DEFAULT_IMAGES_TAR_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--max-products", type=int, default=DEFAULT_MAX_PRODUCTS)
    parser.add_argument("--query-item-id", default=None)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    products = load_clean_abo_products(args.input, args.max_products)
    with tempfile.TemporaryDirectory(prefix="abo-image-run-") as temp_dir:
        image_root = extract_sample_images(args.images_tar, products, Path(temp_dir))
        output = run_image_similarity(products, image_root, args.input, args.query_item_id, args.top_k)
    write_json_output(output, args.output)
    LOGGER.info("Wrote ABO RGB histogram results to %s", args.output)


if __name__ == "__main__":
    main()
