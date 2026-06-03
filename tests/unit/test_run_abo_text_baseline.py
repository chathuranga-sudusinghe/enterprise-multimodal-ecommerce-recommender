import json
from pathlib import Path

from scripts.run_abo_text_baseline import (
    create_sample_output,
    load_abo_products,
    write_output_artifact,
)


def _sample_products() -> list[dict[str, object]]:
    return [
        {
            "item_id": "plate-source",
            "item_name": "white ceramic dinner plate",
            "brand": "TableHome",
            "product_type": "DINNER_PLATE",
            "color": "white",
            "material": "ceramic",
            "style": "modern",
        },
        {
            "item_id": "plate-similar",
            "item_name": "white ceramic salad plate",
            "brand": "TableHome",
            "product_type": "DINNER_PLATE",
            "color": "white",
            "material": "ceramic",
            "style": "modern",
        },
        {
            "item_id": "lamp-unrelated",
            "item_name": "brass table lamp",
            "brand": "BrightRoom",
            "product_type": "TABLE_LAMP",
            "color": "brass",
            "material": "metal",
            "style": "classic",
        },
    ]


def test_runner_creates_valid_json_output_from_small_sample(tmp_path: Path) -> None:
    output = create_sample_output(
        _sample_products(),
        input_sample_path=tmp_path / "abo_sample.json",
        top_k=2,
        generated_at_utc="2026-06-03T00:00:00Z",
    )
    output_path = tmp_path / "output.json"

    write_output_artifact(output, output_path)
    saved_output = json.loads(output_path.read_text(encoding="utf-8"))

    assert saved_output["baseline_name"] == "abo_text_similarity_baseline"
    assert saved_output["dataset_track"] == "amazon_berkeley_text_images-based"
    assert saved_output["top_k"] == 2
    assert saved_output["source_product_id"] == "lamp-unrelated"
    assert len(saved_output["recommendations"]) == 2


def test_output_includes_required_metadata_fields(tmp_path: Path) -> None:
    output = create_sample_output(
        _sample_products(),
        input_sample_path=tmp_path / "abo_sample.json",
        generated_at_utc="2026-06-03T00:00:00Z",
    )

    assert "source_product_metadata" in output
    assert "recommendations" in output
    assert "assumptions" in output
    assert "limitations" in output
    assert output["source_product_metadata"] == {
        "item_name": "brass table lamp",
        "brand": "BrightRoom",
        "product_type": "TABLE_LAMP",
        "color": "brass",
        "material": "metal",
        "style": "classic",
    }
    assert set(output["recommendations"][0]) == {"product_id", "similarity_score", "metadata"}


def test_output_does_not_include_source_product_in_recommendations(tmp_path: Path) -> None:
    output = create_sample_output(
        _sample_products(),
        input_sample_path=tmp_path / "abo_sample.json",
        top_k=3,
        generated_at_utc="2026-06-03T00:00:00Z",
    )

    recommendation_ids = {recommendation["product_id"] for recommendation in output["recommendations"]}

    assert output["source_product_id"] not in recommendation_ids


def test_output_is_deterministic_for_same_input(tmp_path: Path) -> None:
    first_output = create_sample_output(
        _sample_products(),
        input_sample_path=tmp_path / "abo_sample.json",
        top_k=2,
        generated_at_utc="2026-06-03T00:00:00Z",
    )
    second_output = create_sample_output(
        _sample_products(),
        input_sample_path=tmp_path / "abo_sample.json",
        top_k=2,
        generated_at_utc="2026-06-03T00:00:00Z",
    )

    assert first_output == second_output


def test_runner_loads_small_fixture_without_raw_abo_tar_files(tmp_path: Path) -> None:
    sample_path = tmp_path / "abo_sample.jsonl"
    sample_path.write_text(
        "\n".join(json.dumps(product) for product in _sample_products()) + "\n",
        encoding="utf-8",
    )

    products = load_abo_products(sample_path)
    output = create_sample_output(
        products,
        input_sample_path=sample_path,
        top_k=1,
        generated_at_utc="2026-06-03T00:00:00Z",
    )

    assert sample_path.suffix == ".jsonl"
    assert output["input_sample_path"] == str(sample_path)
    assert len(output["recommendations"]) == 1
