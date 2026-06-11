import json
import math
from pathlib import Path

import pytest

from ecommerce_recommender.evaluation.abo_proxy_similarity import (
    average_precision_at_k,
    evaluate_method_output,
    load_product_lookup,
    ndcg_at_k,
    precision_at_k,
)
from scripts.evaluate_abo_similarity_methods import run_evaluation


def _products() -> dict[str, dict[str, object]]:
    return {
        "query": {
            "item_id": "query",
            "item_name": "White ceramic plate",
            "brand": "TableHome",
            "product_type": "PLATE",
            "color": "White",
        },
        "same-type": {
            "item_id": "same-type",
            "item_name": "Blue salad plate",
            "brand": "OtherBrand",
            "product_type": "PLATE",
            "color": "Blue",
        },
        "same-brand": {
            "item_id": "same-brand",
            "item_name": "White ceramic mug",
            "brand": "TableHome",
            "product_type": "MUG",
            "color": "White",
        },
        "both": {
            "item_id": "both",
            "item_name": "White dinner plate",
            "brand": "TableHome",
            "product_type": "PLATE",
            "color": "White",
        },
    }


def _method_output(recommendations: list[dict[str, object]]) -> dict[str, object]:
    return {
        "method_name": "fixture_similarity",
        "products_loaded": 4,
        "query_item_id": "query",
        "top_k": len(recommendations),
        "recommendations": recommendations,
    }


def test_precision_at_k_with_binary_relevance() -> None:
    assert precision_at_k([1, 0, 1], k=3) == pytest.approx(2 / 3)


def test_average_precision_at_k_with_binary_relevance() -> None:
    assert average_precision_at_k([1, 0, 1], k=3) == pytest.approx((1.0 + 2 / 3) / 2)


def test_ndcg_at_k_with_binary_relevance() -> None:
    expected = (1.0 + 1 / math.log2(4)) / (1.0 + 1 / math.log2(3))
    assert ndcg_at_k([1, 0, 1], k=3) == pytest.approx(expected)


def test_product_type_and_brand_match_rates() -> None:
    output = _method_output([
        {"item_id": "same-type", "score": 0.9},
        {"item_id": "same-brand", "score": 0.8},
        {"item_id": "both", "score": 0.7},
    ])

    metrics = evaluate_method_output(output, _products())

    assert metrics["product_type_match_rate_at_k"] == pytest.approx(2 / 3)
    assert metrics["brand_match_rate_at_k"] == pytest.approx(2 / 3)
    assert metrics["color_match_rate_at_k"] == pytest.approx(2 / 3)


def test_mean_similarity_score_at_k() -> None:
    output = _method_output([
        {"item_id": "same-type", "score": 0.9},
        {"item_id": "same-brand", "score": 0.6},
    ])

    metrics = evaluate_method_output(output, _products())

    assert metrics["mean_similarity_score_at_k"] == pytest.approx(0.75)


def test_evaluation_result_structure(tmp_path: Path) -> None:
    products_path = tmp_path / "products.jsonl"
    products_path.write_text(
        "\n".join(json.dumps(record) for record in _products().values()) + "\n",
        encoding="utf-8",
    )
    method_path = tmp_path / "tfidf.json"
    method_path.write_text(
        json.dumps(_method_output([{"item_id": "both", "score": 0.9}])),
        encoding="utf-8",
    )
    output_path = tmp_path / "evaluation.json"

    result = run_evaluation(
        products_path,
        {"tfidf": method_path, "missing": tmp_path / "missing.json"},
        output_path,
        generated_at_utc="2026-06-11T00:00:00Z",
    )

    assert result["evaluation_type"] == "proxy_similarity_evaluation"
    assert result["dataset_track"] == "amazon_berkeley_text_images-based"
    assert result["evaluated_methods"] == ["tfidf"]
    assert "tfidf" in result["metrics_by_method"]
    assert result["assumptions"]
    assert result["limitations"]
    assert json.loads(output_path.read_text(encoding="utf-8")) == result


def test_missing_recommendation_product_ids_are_reported() -> None:
    output = _method_output([
        {"item_id": "missing", "score": 0.9},
        {"item_id": "both", "score": 0.8},
    ])

    metrics = evaluate_method_output(output, _products())

    assert metrics["missing_recommendation_count"] == 1
    assert metrics["missing_recommendation_item_ids"] == ["missing"]
    assert metrics["recommendations_evaluated"] == 2
    assert metrics["proxy_precision_at_k"] == 0.5


def test_empty_recommendations_do_not_crash() -> None:
    metrics = evaluate_method_output(_method_output([]), _products())

    assert metrics["recommendations_evaluated"] == 0
    assert metrics["proxy_precision_at_k"] == 0.0
    assert metrics["proxy_average_precision_at_k"] == 0.0
    assert metrics["proxy_ndcg_at_k"] == 0.0
    assert metrics["mean_similarity_score_at_k"] == 0.0
    assert metrics["color_match_rate_at_k"] is None


def test_load_product_lookup_reads_jsonl(tmp_path: Path) -> None:
    products_path = tmp_path / "products.jsonl"
    products_path.write_text(json.dumps(_products()["query"]) + "\n", encoding="utf-8")

    lookup = load_product_lookup(products_path)

    assert set(lookup) == {"query"}
