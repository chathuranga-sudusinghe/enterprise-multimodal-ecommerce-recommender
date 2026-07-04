"""Metadata-based proxy evaluation for ABO product similarity outputs."""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import fmean, median
from typing import Any, Mapping, Sequence


def load_product_lookup(products_path: str | Path) -> dict[str, dict[str, Any]]:
    """Load cleaned ABO JSONL records into an item_id lookup."""
    path = Path(products_path)
    if not path.is_file():
        raise FileNotFoundError(f"Cleaned ABO products file not found: {path}")

    lookup: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_number}: {path}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Expected JSON object at line {line_number}: {path}")
            item_id = _text(record.get("item_id"))
            if not item_id:
                raise ValueError(f"Cleaned ABO record is missing item_id at line {line_number}")
            lookup[item_id] = record

    if not lookup:
        raise ValueError(f"Cleaned ABO products file is empty: {path}")
    return lookup


def load_method_output(output_path: str | Path) -> dict[str, Any]:
    """Load one model output JSON object."""
    path = Path(output_path)
    if not path.is_file():
        raise FileNotFoundError(f"ABO similarity output not found: {path}")
    output = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(output, dict):
        raise ValueError(f"ABO similarity output must be a JSON object: {path}")
    return output


def extract_query_item_id(method_output: Mapping[str, Any]) -> str:
    """Extract the aligned or legacy query product identifier."""
    query_item_id = method_output.get("query_item_id", method_output.get("source_product_id"))
    value = _text(query_item_id)
    if not value:
        raise ValueError("ABO similarity output is missing query_item_id/source_product_id")
    return value


def extract_recommendations(method_output: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Extract aligned or legacy recommendation records."""
    recommendations = method_output.get("recommendations", method_output.get("results", []))
    if recommendations is None:
        return []
    if not isinstance(recommendations, list) or not all(
        isinstance(recommendation, dict) for recommendation in recommendations
    ):
        raise ValueError("ABO similarity recommendations must be a list of objects")
    return [dict(recommendation) for recommendation in recommendations]


def extract_query_outputs(method_output: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Extract one or more query-level similarity outputs.

    Legacy runner artifacts are a single query object. Multi-query artifacts
    should keep shared method metadata at the top level and place query records
    under ``queries``.
    """
    queries = method_output.get("queries")
    if queries is None:
        return [dict(method_output)]
    if not isinstance(queries, list) or not all(isinstance(query, dict) for query in queries):
        raise ValueError("ABO multi-query similarity output queries must be a list of objects")

    shared_fields = {
        key: value
        for key, value in method_output.items()
        if key not in {"queries", "recommendations", "results", "query_item_id", "source_product_id"}
    }
    return [{**shared_fields, **dict(query)} for query in queries]


def precision_at_k(binary_relevance: Sequence[int | bool], k: int | None = None) -> float:
    """Calculate proxy precision for a ranked binary relevance list."""
    relevance = _bounded_relevance(binary_relevance, k)
    return sum(relevance) / len(relevance) if relevance else 0.0


def average_precision_at_k(
    binary_relevance: Sequence[int | bool], k: int | None = None
) -> float:
    """Calculate proxy average precision within the observed top-K list."""
    relevance = _bounded_relevance(binary_relevance, k)
    relevant_count = sum(relevance)
    if relevant_count == 0:
        return 0.0
    precision_sum = sum(
        sum(relevance[:rank]) / rank
        for rank, is_relevant in enumerate(relevance, start=1)
        if is_relevant
    )
    return precision_sum / relevant_count


def ndcg_at_k(binary_relevance: Sequence[int | bool], k: int | None = None) -> float:
    """Calculate proxy NDCG for binary relevance within the observed top-K list."""
    relevance = _bounded_relevance(binary_relevance, k)
    if not relevance:
        return 0.0
    dcg = sum(value / math.log2(rank + 1) for rank, value in enumerate(relevance, start=1))
    ideal = sorted(relevance, reverse=True)
    idcg = sum(value / math.log2(rank + 1) for rank, value in enumerate(ideal, start=1))
    return dcg / idcg if idcg else 0.0


def evaluate_method_output(
    method_output: Mapping[str, Any],
    product_lookup: Mapping[str, Mapping[str, Any]],
    method_name: str | None = None,
) -> dict[str, Any]:
    """Evaluate one similarity output using metadata-based proxy relevance."""
    query_item_id = extract_query_item_id(method_output)
    query = product_lookup.get(query_item_id)
    if query is None:
        raise ValueError(f"Query item_id is not present in cleaned ABO products: {query_item_id}")

    recommendations = extract_recommendations(method_output)
    configured_top_k = method_output.get("top_k")
    top_k = int(configured_top_k) if configured_top_k is not None else len(recommendations)
    if top_k < 0:
        raise ValueError("top_k must not be negative")
    ranked = recommendations[:top_k]

    query_product_type = _normalized(query.get("product_type"))
    query_brand = _normalized(query.get("brand"))
    query_color = _normalized(query.get("color"))
    relevance: list[int] = []
    product_type_matches = 0
    brand_matches = 0
    color_matches = 0
    color_comparisons = 0
    scores: list[float] = []
    product_types: set[str] = set()
    brands: set[str] = set()
    missing_item_ids: list[str] = []
    seen_item_ids: set[str] = set()
    duplicate_item_ids: list[str] = []
    self_recommendation_count = 0
    known_recommendations = 0

    for recommendation in ranked:
        item_id = _text(recommendation.get("item_id", recommendation.get("product_id")))
        if item_id == query_item_id:
            self_recommendation_count += 1
        if item_id:
            if item_id in seen_item_ids:
                duplicate_item_ids.append(item_id)
            seen_item_ids.add(item_id)
        recommended_product = product_lookup.get(item_id)
        if recommended_product is None:
            missing_item_ids.append(item_id or "<missing>")
            relevance.append(0)
        else:
            known_recommendations += 1
            product_type = _normalized(recommended_product.get("product_type"))
            brand = _normalized(recommended_product.get("brand"))
            color = _normalized(recommended_product.get("color"))
            type_match = bool(query_product_type and product_type == query_product_type)
            brand_match = bool(query_brand and brand == query_brand)
            relevance.append(int(type_match))
            product_type_matches += int(type_match)
            brand_matches += int(brand_match)
            if product_type:
                product_types.add(product_type)
            if brand:
                brands.add(brand)
            if query_color and color:
                color_comparisons += 1
                color_matches += int(color == query_color)

        score = recommendation.get("score", recommendation.get("similarity_score"))
        if score is not None:
            try:
                scores.append(float(score))
            except (TypeError, ValueError):
                pass

    recommendation_count = len(ranked)
    return {
        "method_name": method_name or _text(method_output.get("method_name")) or "unknown",
        "evaluation_scope": "single_query",
        "query_item_id": query_item_id,
        "products_loaded": method_output.get("products_loaded"),
        "recommendations_evaluated": recommendation_count,
        "known_recommendations_evaluated": known_recommendations,
        "missing_recommendation_count": len(missing_item_ids),
        "missing_recommendation_item_ids": missing_item_ids,
        "self_recommendation_count": self_recommendation_count,
        "duplicate_recommendation_count": len(duplicate_item_ids),
        "duplicate_recommendation_item_ids": duplicate_item_ids,
        "top_k": top_k,
        "product_type_match_rate_at_k": product_type_matches / recommendation_count if recommendation_count else 0.0,
        "brand_match_rate_at_k": brand_matches / recommendation_count if recommendation_count else 0.0,
        "color_match_rate_at_k": color_matches / color_comparisons if color_comparisons else None,
        "color_comparisons_at_k": color_comparisons,
        "proxy_precision_at_k": precision_at_k(relevance),
        "proxy_average_precision_at_k": average_precision_at_k(relevance),
        "proxy_ndcg_at_k": ndcg_at_k(relevance),
        "mean_similarity_score_at_k": fmean(scores) if scores else 0.0,
        "unique_product_type_count_at_k": len(product_types),
        "unique_brand_count_at_k": len(brands),
    }


def evaluate_multi_query_method_output(
    method_output: Mapping[str, Any],
    product_lookup: Mapping[str, Mapping[str, Any]],
    method_name: str | None = None,
) -> dict[str, Any]:
    """Evaluate one method artifact containing one or more query outputs."""
    query_outputs = extract_query_outputs(method_output)
    if len(query_outputs) == 1 and "queries" not in method_output:
        return evaluate_method_output(query_outputs[0], product_lookup, method_name)

    per_query_metrics: list[dict[str, Any]] = []
    query_failures: list[dict[str, str]] = []
    for query_output in query_outputs:
        try:
            per_query_metrics.append(
                evaluate_method_output(query_output, product_lookup, method_name)
            )
        except ValueError as exc:
            query_failures.append(
                {
                    "query_item_id": _text(
                        query_output.get("query_item_id", query_output.get("source_product_id"))
                    )
                    or "<missing>",
                    "reason": str(exc),
                }
            )

    metric_fields = (
        "product_type_match_rate_at_k",
        "proxy_precision_at_k",
        "proxy_average_precision_at_k",
        "proxy_ndcg_at_k",
        "brand_match_rate_at_k",
        "mean_similarity_score_at_k",
        "unique_product_type_count_at_k",
        "unique_brand_count_at_k",
    )
    aggregate_metrics = {
        field: _summary_stats([metrics[field] for metrics in per_query_metrics])
        for field in metric_fields
    }
    color_values = [
        metrics["color_match_rate_at_k"]
        for metrics in per_query_metrics
        if metrics["color_match_rate_at_k"] is not None
    ]
    aggregate_metrics["color_match_rate_at_k"] = _summary_stats(color_values)

    return {
        "method_name": method_name or _text(method_output.get("method_name")) or "unknown",
        "evaluation_scope": "multi_query",
        "query_count": len(query_outputs),
        "evaluated_query_count": len(per_query_metrics),
        "query_failure_count": len(query_failures),
        "query_failures": query_failures,
        "failed_query_item_ids": [failure["query_item_id"] for failure in query_failures],
        "query_item_ids": [metrics["query_item_id"] for metrics in per_query_metrics],
        "products_loaded": method_output.get("products_loaded"),
        "top_k_values": sorted({metrics["top_k"] for metrics in per_query_metrics}),
        "recommendations_evaluated": sum(
            int(metrics["recommendations_evaluated"]) for metrics in per_query_metrics
        ),
        "known_recommendations_evaluated": sum(
            int(metrics["known_recommendations_evaluated"]) for metrics in per_query_metrics
        ),
        "missing_recommendation_count": sum(
            int(metrics["missing_recommendation_count"]) for metrics in per_query_metrics
        ),
        "self_recommendation_count": sum(
            int(metrics["self_recommendation_count"]) for metrics in per_query_metrics
        ),
        "duplicate_recommendation_count": sum(
            int(metrics["duplicate_recommendation_count"]) for metrics in per_query_metrics
        ),
        "aggregate_metrics": aggregate_metrics,
        "per_query_metrics": per_query_metrics,
    }


def _bounded_relevance(
    binary_relevance: Sequence[int | bool], k: int | None
) -> list[int]:
    if k is not None and k < 0:
        raise ValueError("k must not be negative")
    values = binary_relevance if k is None else binary_relevance[:k]
    return [int(bool(value)) for value in values]


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _normalized(value: Any) -> str:
    return _text(value).casefold()


def _summary_stats(values: Sequence[Any]) -> dict[str, float | None]:
    numeric_values = [float(value) for value in values if value is not None]
    if not numeric_values:
        return {"mean": None, "median": None, "min": None, "max": None}
    return {
        "mean": fmean(numeric_values),
        "median": float(median(numeric_values)),
        "min": min(numeric_values),
        "max": max(numeric_values),
    }
