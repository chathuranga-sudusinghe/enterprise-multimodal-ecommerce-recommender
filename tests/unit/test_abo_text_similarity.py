import pytest

from ecommerce_recommender.models.abo_text_similarity import (
    ABOTextSimilarityBaseline,
    build_combined_product_text,
)


def test_build_combined_product_text_from_abo_metadata_fields() -> None:
    product = {
        "item_id": "item-001",
        "item_name": "Ceramic dinner plate",
        "brand": "TableHome",
        "bullet_point": ["Microwave safe", "Dishwasher safe"],
        "product_type": "DINNER_PLATE",
        "color": "White",
        "material": "Ceramic",
        "style": "Modern",
        "unsupported_field": "not included",
    }

    combined_text = build_combined_product_text(product)

    assert combined_text == (
        "Ceramic dinner plate TableHome Microwave safe Dishwasher safe "
        "DINNER_PLATE White Ceramic Modern"
    )
    assert "not included" not in combined_text



def test_build_combined_product_text_prefers_cleaned_combined_text() -> None:
    product = {
        "item_id": "item-001",
        "combined_text": "approved cleaned product text",
        "item_name": "ignored fallback name",
    }

    assert build_combined_product_text(product) == "approved cleaned product text"

def test_missing_and_empty_fields_are_handled_safely() -> None:
    product = {
        "item_id": "item-001",
        "item_name": None,
        "brand": "",
        "bullet_point": [None, "  Compact size  ", ""],
        "product_type": "STORAGE_BOX",
        "color": [],
        "material": {"primary": "Plastic", "secondary": None},
    }

    combined_text = build_combined_product_text(product)

    assert combined_text == "Compact size STORAGE_BOX Plastic"


def test_top_k_recommendations_exclude_source_product() -> None:
    baseline = ABOTextSimilarityBaseline().fit(
        [
            {"item_id": "plate-a", "item_name": "white ceramic dinner plate"},
            {"item_id": "plate-b", "item_name": "white ceramic salad plate"},
            {"item_id": "mug-a", "item_name": "blue travel coffee mug"},
        ]
    )

    results = baseline.recommend_similar("plate-a", top_k=2)

    assert [result.product_id for result in results] == ["plate-b", "mug-a"]
    assert "plate-a" not in [result.product_id for result in results]


def test_similar_text_products_rank_above_unrelated_products() -> None:
    baseline = ABOTextSimilarityBaseline().fit(
        [
            {
                "item_id": "shoe-a",
                "item_name": "women running shoe",
                "product_type": "RUNNING_SHOE",
                "material": "mesh rubber",
            },
            {
                "item_id": "shoe-b",
                "item_name": "men running shoe",
                "product_type": "RUNNING_SHOE",
                "material": "mesh rubber",
            },
            {
                "item_id": "lamp-a",
                "item_name": "brass table lamp",
                "product_type": "TABLE_LAMP",
                "material": "brass fabric",
            },
        ]
    )

    results = baseline.recommend_similar("shoe-a", top_k=2)

    assert results[0].product_id == "shoe-b"
    assert results[0].similarity_score > results[1].similarity_score


def test_deterministic_tie_breaking_uses_product_identifier() -> None:
    products = [
        {"item_id": "source", "item_name": "cotton towel"},
        {"item_id": "candidate-b", "item_name": "cotton towel"},
        {"item_id": "candidate-a", "item_name": "cotton towel"},
    ]

    first_run = ABOTextSimilarityBaseline().fit(products).recommend_similar("source", top_k=2)
    second_run = ABOTextSimilarityBaseline().fit(products).recommend_similar("source", top_k=2)

    assert [result.product_id for result in first_run] == ["candidate-a", "candidate-b"]
    assert [result.product_id for result in second_run] == ["candidate-a", "candidate-b"]


def test_top_k_is_limited_to_available_candidates() -> None:
    baseline = ABOTextSimilarityBaseline().fit(
        [
            {"item_id": "source", "item_name": "glass mixing bowl"},
            {"item_id": "candidate-a", "item_name": "glass serving bowl"},
            {"item_id": "candidate-b", "item_name": "cotton kitchen towel"},
        ]
    )

    results = baseline.recommend_similar("source", top_k=10)

    assert len(results) == 2
    assert {result.product_id for result in results} == {"candidate-a", "candidate-b"}


def test_duplicate_product_ids_raise_clear_error() -> None:
    baseline = ABOTextSimilarityBaseline()

    with pytest.raises(ValueError, match="Duplicate Amazon Berkeley Objects product_id"):
        baseline.fit(
            [
                {"item_id": "duplicate", "item_name": "glass jar"},
                {"item_id": "duplicate", "item_name": "ceramic jar"},
            ]
        )


def test_unknown_source_product_raises_clear_error() -> None:
    baseline = ABOTextSimilarityBaseline().fit(
        [{"item_id": "known", "item_name": "glass storage jar"}]
    )

    with pytest.raises(ValueError, match="Unknown Amazon Berkeley Objects product_id"):
        baseline.recommend_similar("missing")


def test_recommendation_before_fit_raises_clear_error() -> None:
    baseline = ABOTextSimilarityBaseline()

    with pytest.raises(RuntimeError, match="must be fitted before recommendations"):
        baseline.recommend_similar("item-001")
