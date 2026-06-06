from pathlib import Path

import numpy as np
import pytest

from ecommerce_recommender.data.loading import load_amazon_berkeley_objects_fixtures
from ecommerce_recommender.models.abo_image_similarity import (
    ABOImageSimilarityBaseline,
    extract_normalized_rgb_histogram,
    load_rgb_pixels,
)


SAMPLE_ABO_DIR = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "sample"
    / "amazon_berkeley_objects"
)


def _write_ppm(path: Path, pixels: list[tuple[int, int, int]], width: int = 1) -> Path:
    height = len(pixels) // width
    pixel_bytes = bytes(channel for pixel in pixels for channel in pixel)
    path.write_bytes(f"P6\n{width} {height}\n255\n".encode("ascii") + pixel_bytes)
    return path


def _products() -> list[dict[str, object]]:
    return [
        {
            "item_id": "source-red",
            "item_name": "Red product text",
            "product_type": "FIXTURE",
            "main_image_id": "red-source-image",
        },
        {
            "item_id": "candidate-red",
            "item_name": "Completely different text",
            "product_type": "FIXTURE",
            "main_image_id": "red-candidate-image",
        },
        {
            "item_id": "candidate-blue",
            "item_name": "Red product text",
            "product_type": "FIXTURE",
            "main_image_id": "blue-candidate-image",
        },
    ]


def _images() -> list[dict[str, str]]:
    return [
        {"image_id": "red-source-image", "path": "red_source.ppm"},
        {"image_id": "red-candidate-image", "path": "red_candidate.ppm"},
        {"image_id": "blue-candidate-image", "path": "blue_candidate.ppm"},
    ]


def test_extract_normalized_rgb_histogram_is_deterministic(tmp_path: Path) -> None:
    image_path = _write_ppm(tmp_path / "fixture.ppm", [(255, 0, 0), (0, 255, 0)], width=2)

    first_feature = extract_normalized_rgb_histogram(image_path, bins_per_channel=4)
    second_feature = extract_normalized_rgb_histogram(image_path, bins_per_channel=4)

    assert np.array_equal(first_feature, second_feature)
    assert first_feature.shape == (12,)
    assert np.linalg.norm(first_feature) == pytest.approx(1.0)


def test_fit_uses_existing_abo_image_fixtures() -> None:
    fixtures = load_amazon_berkeley_objects_fixtures(SAMPLE_ABO_DIR)

    baseline = ABOImageSimilarityBaseline().fit(
        fixtures["listings"],
        fixtures["images"],
        SAMPLE_ABO_DIR,
    )
    first_results = baseline.recommend_similar("abo_item_alpha", top_k=2)
    second_results = baseline.recommend_similar("abo_item_alpha", top_k=2)

    first_product_ids = [result.product_id for result in first_results]
    second_product_ids = [result.product_id for result in second_results]

    assert len(first_results) == 2
    assert "abo_item_alpha" not in first_product_ids
    assert first_product_ids == second_product_ids
    assert all(result.image_id for result in first_results)


def test_top_k_recommendations_exclude_source_product(tmp_path: Path) -> None:
    _write_ppm(tmp_path / "red_source.ppm", [(255, 0, 0)])
    _write_ppm(tmp_path / "red_candidate.ppm", [(255, 0, 0)])
    _write_ppm(tmp_path / "blue_candidate.ppm", [(0, 0, 255)])

    baseline = ABOImageSimilarityBaseline().fit(_products(), _images(), tmp_path)
    results = baseline.recommend_similar("source-red", top_k=2)

    assert [result.product_id for result in results] == [
        "candidate-red",
        "candidate-blue",
    ]
    assert "source-red" not in [result.product_id for result in results]


def test_similar_color_products_rank_above_different_color_products(tmp_path: Path) -> None:
    _write_ppm(tmp_path / "red_source.ppm", [(255, 0, 0)])
    _write_ppm(tmp_path / "red_candidate.ppm", [(255, 0, 0)])
    _write_ppm(tmp_path / "blue_candidate.ppm", [(0, 0, 255)])

    baseline = ABOImageSimilarityBaseline().fit(_products(), _images(), tmp_path)
    results = baseline.recommend_similar("source-red", top_k=2)

    assert results[0].product_id == "candidate-red"
    assert results[0].similarity_score > results[1].similarity_score


def test_text_metadata_is_not_used_as_similarity_signal(tmp_path: Path) -> None:
    _write_ppm(tmp_path / "red_source.ppm", [(255, 0, 0)])
    _write_ppm(tmp_path / "red_candidate.ppm", [(255, 0, 0)])
    _write_ppm(tmp_path / "blue_candidate.ppm", [(0, 0, 255)])

    baseline = ABOImageSimilarityBaseline().fit(_products(), _images(), tmp_path)
    results = baseline.recommend_similar("source-red", top_k=2)

    assert results[0].product_id == "candidate-red"
    assert results[0].metadata["item_name"] == "Completely different text"


def test_deterministic_tie_breaking_uses_product_identifier(tmp_path: Path) -> None:
    products = [
        {"item_id": "source", "main_image_id": "source-image"},
        {"item_id": "candidate-b", "main_image_id": "candidate-b-image"},
        {"item_id": "candidate-a", "main_image_id": "candidate-a-image"},
    ]
    images = [
        {"image_id": "source-image", "path": "source.ppm"},
        {"image_id": "candidate-b-image", "path": "candidate_b.ppm"},
        {"image_id": "candidate-a-image", "path": "candidate_a.ppm"},
    ]
    _write_ppm(tmp_path / "source.ppm", [(128, 128, 128)])
    _write_ppm(tmp_path / "candidate_b.ppm", [(128, 128, 128)])
    _write_ppm(tmp_path / "candidate_a.ppm", [(128, 128, 128)])

    first_run = ABOImageSimilarityBaseline().fit(products, images, tmp_path).recommend_similar(
        "source",
        top_k=2,
    )
    second_run = ABOImageSimilarityBaseline().fit(products, images, tmp_path).recommend_similar(
        "source",
        top_k=2,
    )

    assert [result.product_id for result in first_run] == ["candidate-a", "candidate-b"]
    assert [result.product_id for result in second_run] == ["candidate-a", "candidate-b"]


def test_unknown_source_product_raises_clear_error(tmp_path: Path) -> None:
    _write_ppm(tmp_path / "red_source.ppm", [(255, 0, 0)])
    baseline = ABOImageSimilarityBaseline().fit(
        [{"item_id": "known", "main_image_id": "red-source-image"}],
        [{"image_id": "red-source-image", "path": "red_source.ppm"}],
        tmp_path,
    )

    with pytest.raises(ValueError, match="Unknown Amazon Berkeley Objects product_id"):
        baseline.recommend_similar("missing")


def test_recommendation_before_fit_raises_clear_error() -> None:
    baseline = ABOImageSimilarityBaseline()

    with pytest.raises(RuntimeError, match="must be fitted before recommendations"):
        baseline.recommend_similar("item-001")


def test_load_rgb_pixels_raises_for_missing_image(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Image file not found"):
        load_rgb_pixels(tmp_path / "missing.ppm")
