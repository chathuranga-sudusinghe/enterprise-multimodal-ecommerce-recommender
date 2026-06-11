"""MCP-style controlled tool interfaces for ABO recommendation demos."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def load_product_catalog(products_path: str | Path) -> dict[str, dict[str, Any]]:
    """Load cleaned ABO JSONL records into an item_id catalog."""
    path = Path(products_path)
    if not path.is_file():
        raise FileNotFoundError(f"ABO product catalog not found: {path}")

    catalog: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid catalog JSON at line {line_number}: {path}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"Catalog record at line {line_number} must be an object")
            item_id = _text(record.get("item_id"))
            if not item_id:
                raise ValueError(f"Catalog record at line {line_number} is missing item_id")
            catalog.setdefault(item_id, record)

    if not catalog:
        raise ValueError(f"ABO product catalog is empty: {path}")
    return catalog


def lookup_product(
    catalog: Mapping[str, Mapping[str, Any]], item_id: str
) -> dict[str, Any] | None:
    """Return one catalog product as a detached dictionary."""
    product = catalog.get(str(item_id))
    return dict(product) if product is not None else None


def load_similarity_results(results_path: str | Path) -> dict[str, Any]:
    """Load one ABO similarity result JSON object."""
    path = Path(results_path)
    if not path.is_file():
        raise FileNotFoundError(f"ABO similarity results not found: {path}")
    try:
        results = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid similarity results JSON: {path}") from exc
    if not isinstance(results, dict):
        raise ValueError(f"Similarity results must be a JSON object: {path}")
    return results


def get_query_item_id(results: Mapping[str, Any]) -> str:
    """Extract the aligned or legacy source item identifier."""
    item_id = _text(results.get("query_item_id", results.get("source_product_id")))
    if not item_id:
        raise ValueError("Similarity results are missing query_item_id/source_product_id")
    return item_id


def get_recommendations(
    results: Mapping[str, Any], top_k: int
) -> list[dict[str, Any]]:
    """Return normalized, bounded recommendation dictionaries."""
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")
    raw = results.get("recommendations", results.get("results", []))
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError("Similarity recommendations must be a list")

    recommendations: list[dict[str, Any]] = []
    for candidate in raw[:top_k]:
        if not isinstance(candidate, dict):
            recommendations.append({"invalid_candidate": candidate})
            continue
        normalized = dict(candidate)
        if "item_id" not in normalized and "product_id" in normalized:
            normalized["item_id"] = normalized["product_id"]
        if "score" not in normalized and "similarity_score" in normalized:
            normalized["score"] = normalized["similarity_score"]
        recommendations.append(normalized)
    return recommendations


def policy_check_recommendation(
    query_product: Mapping[str, Any], recommendation: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply deterministic recommendation policy checks and return structure only."""
    query_item_id = _text(query_product.get("item_id"))
    item_id = _text(recommendation.get("item_id"))
    item_name = _text(recommendation.get("item_name"))
    product_type = _text(recommendation.get("product_type"))
    score = recommendation.get("score")

    rejection_reasons: list[str] = []
    warnings: list[str] = []
    if not item_id:
        rejection_reasons.append("missing_item_id")
    elif item_id == query_item_id:
        rejection_reasons.append("same_as_query_item")
    if score is None:
        rejection_reasons.append("missing_similarity_score")
    else:
        try:
            float(score)
        except (TypeError, ValueError):
            rejection_reasons.append("invalid_similarity_score")
    if recommendation.get("catalog_found") is False:
        rejection_reasons.append("item_not_found_in_catalog")
    if not item_name:
        warnings.append("missing_item_name")
    if not product_type:
        warnings.append("missing_product_type")

    query_product_type = _text(query_product.get("product_type"))
    product_type_matches = bool(
        query_product_type and product_type and query_product_type == product_type
    )
    checked = dict(recommendation)
    checked["item_id"] = item_id or None
    checked["product_type_matches_query"] = product_type_matches
    return {
        "approved": not rejection_reasons,
        "rejection_reasons": rejection_reasons,
        "warnings": warnings,
        "recommendation": checked,
    }


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()
