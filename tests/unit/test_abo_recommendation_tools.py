import json
from pathlib import Path

from ecommerce_recommender.mcp_tools.abo_recommendation_tools import (
    get_query_item_id,
    get_recommendations,
    load_product_catalog,
    load_similarity_results,
    lookup_product,
    policy_check_recommendation,
)


def test_product_catalog_loading_and_lookup(tmp_path: Path) -> None:
    path = tmp_path / "products.jsonl"
    records = [
        {"item_id": "query", "item_name": "Plate", "product_type": "PLATE"},
        {"item_id": "candidate", "item_name": "Bowl", "product_type": "BOWL"},
    ]
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")

    catalog = load_product_catalog(path)

    assert set(catalog) == {"query", "candidate"}
    assert lookup_product(catalog, "candidate")["item_name"] == "Bowl"
    assert lookup_product(catalog, "missing") is None


def test_similarity_result_loading_and_normalization(tmp_path: Path) -> None:
    path = tmp_path / "results.json"
    path.write_text(
        json.dumps(
            {
                "source_product_id": "query",
                "results": [
                    {"product_id": "candidate", "similarity_score": 0.8}
                ],
            }
        ),
        encoding="utf-8",
    )

    results = load_similarity_results(path)
    recommendations = get_recommendations(results, top_k=1)

    assert get_query_item_id(results) == "query"
    assert recommendations == [
        {
            "product_id": "candidate",
            "similarity_score": 0.8,
            "item_id": "candidate",
            "score": 0.8,
        }
    ]


def test_policy_check_rejects_same_item_id() -> None:
    check = policy_check_recommendation(
        {"item_id": "query", "product_type": "PLATE"},
        {"item_id": "query", "item_name": "Plate", "product_type": "PLATE", "score": 1.0},
    )

    assert check["approved"] is False
    assert "same_as_query_item" in check["rejection_reasons"]


def test_policy_check_approves_valid_recommendation() -> None:
    check = policy_check_recommendation(
        {"item_id": "query", "product_type": "PLATE"},
        {"item_id": "candidate", "item_name": "Plate Set", "product_type": "PLATE", "score": 0.9},
    )

    assert check["approved"] is True
    assert check["rejection_reasons"] == []
    assert check["recommendation"]["product_type_matches_query"] is True
