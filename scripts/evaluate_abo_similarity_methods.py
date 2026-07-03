"""Compare ABO similarity outputs with metadata-based proxy metrics."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
for import_root in (PROJECT_ROOT, SRC_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from ecommerce_recommender.evaluation.abo_proxy_similarity import (  # noqa: E402
    evaluate_multi_query_method_output,
    load_method_output,
    load_product_lookup,
)

LOGGER = logging.getLogger(__name__)
DEFAULT_PRODUCTS = PROJECT_ROOT / "data/processed/abo_clean_products_5k.jsonl"
DEFAULT_TFIDF = PROJECT_ROOT / "data/processed/abo_tfidf_similarity_5k_sample.json"
DEFAULT_IMAGE = PROJECT_ROOT / "data/processed/abo_image_similarity_5k_sample.json"
DEFAULT_CLIP = PROJECT_ROOT / "data/processed/abo_clip_similarity_5k_sample.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/processed/abo_similarity_proxy_evaluation.json"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--products", type=Path, default=DEFAULT_PRODUCTS)
    parser.add_argument("--tfidf", type=Path, default=DEFAULT_TFIDF)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--clip", type=Path, default=DEFAULT_CLIP)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def run_evaluation(
    products_path: Path,
    method_paths: dict[str, Path],
    output_path: Path,
    generated_at_utc: str | None = None,
) -> dict[str, object]:
    """Evaluate all available method outputs and write one comparison artifact."""
    product_lookup = load_product_lookup(products_path)
    metrics_by_method: dict[str, dict[str, Any]] = {}

    for method_label, method_path in method_paths.items():
        if not method_path.is_file():
            LOGGER.warning("Skipping missing %s output: %s", method_label, method_path)
            continue
        metrics_by_method[method_label] = evaluate_multi_query_method_output(
            load_method_output(method_path),
            product_lookup,
            method_name=method_label,
        )

    has_multi_query = any(
        metrics.get("evaluation_scope") == "multi_query"
        for metrics in metrics_by_method.values()
    )
    result: dict[str, object] = {
        "evaluation_name": "ABO similarity method proxy comparison",
        "evaluation_type": "proxy_similarity_evaluation",
        "evaluation_scope": "multi_query" if has_multi_query else "single_query",
        "dataset_track": "amazon_berkeley_text_images-based",
        "products_file": _display_path(products_path),
        "evaluated_methods": list(metrics_by_method),
        "metrics_by_method": metrics_by_method,
        "assumptions": [
            "ABO has no real user behavior labels.",
            "Product type match is used as binary proxy relevance.",
            "Multi-query results are metadata proxy evidence, not user satisfaction evidence.",
            "Results must not be interpreted as real click or purchase recommendation performance.",
        ],
        "limitations": [
            "Proxy relevance may overestimate or underestimate real user satisfaction.",
            "Brand and product type matching do not capture all semantic similarity.",
            "Real production evaluation needs user behavior data or human judgment.",
        ],
        "generated_at_utc": generated_at_utc or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def log_summary(metrics_by_method: dict[str, dict[str, Any]]) -> None:
    """Log a compact comparison table without adding a table dependency."""
    LOGGER.info("%-10s %8s %10s %10s %10s", "method", "queries", "type_rate", "precision", "ndcg")
    for method, metrics in metrics_by_method.items():
        if metrics.get("evaluation_scope") == "multi_query":
            aggregate = metrics["aggregate_metrics"]
            LOGGER.info(
                "%-10s %8d %10.3f %10.3f %10.3f",
                method,
                metrics["evaluated_query_count"],
                _mean_or_zero(aggregate["product_type_match_rate_at_k"]),
                _mean_or_zero(aggregate["proxy_precision_at_k"]),
                _mean_or_zero(aggregate["proxy_ndcg_at_k"]),
            )
            continue
        LOGGER.info(
            "%-10s %8d %10.3f %10.3f %10.3f",
            method,
            1,
            metrics["product_type_match_rate_at_k"],
            metrics["proxy_precision_at_k"],
            metrics["proxy_ndcg_at_k"],
        )


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    result = run_evaluation(
        args.products,
        {"tfidf": args.tfidf, "image": args.image, "clip": args.clip},
        args.output,
    )
    log_summary(result["metrics_by_method"])
    LOGGER.info("Wrote ABO proxy similarity evaluation to %s", args.output)


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path.resolve())


def _mean_or_zero(summary: dict[str, float | None]) -> float:
    return float(summary["mean"] or 0.0)


if __name__ == "__main__":
    main()
