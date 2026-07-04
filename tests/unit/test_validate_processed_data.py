import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.validate_processed_data import (  # noqa: E402
    render_report,
    validate_abo_clean_jsonl,
    validate_processed_data,
    validate_similarity_json,
)


def test_validate_abo_clean_jsonl_counts_missing_and_duplicate_values(tmp_path: Path) -> None:
    path = tmp_path / "abo_clean.jsonl"
    records = [
        {
            "item_id": "item-1",
            "product_type": "SHOE",
            "image_path": "images/small/item-1.jpg",
            "is_clip_ready": True,
        },
        {
            "item_id": "item-1",
            "product_type": "",
            "image_path": "",
            "is_clip_ready": False,
        },
        {
            "item_id": "",
            "product_type": None,
        },
    ]
    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")

    result = validate_abo_clean_jsonl(path)

    assert result.status == "WARN"
    assert result.counters["records"] == 3
    assert result.counters["missing_item_id"] == 1
    assert result.counters["duplicate_item_id"] == 1
    assert result.counters["missing_product_type"] == 2
    assert result.counters["missing_image_path"] == 2
    assert result.counters["is_clip_ready_true"] == 1
    assert result.counters["is_clip_ready_false"] == 1


def test_validate_abo_clean_jsonl_fails_on_invalid_json_line(tmp_path: Path) -> None:
    path = tmp_path / "abo_clean.jsonl"
    path.write_text('{"item_id": "item-1"}\n{bad-json}\n', encoding="utf-8")

    result = validate_abo_clean_jsonl(path)

    assert result.status == "FAIL"
    assert result.counters["invalid_json_lines"] == 1
    assert any("invalid JSON" in issue for issue in result.issues)


def test_validate_similarity_json_warns_on_duplicate_and_self_recommendations(tmp_path: Path) -> None:
    path = tmp_path / "similarity.json"
    path.write_text(
        json.dumps(
            {
                "query_item_id": "item-1",
                "recommendations": [
                    {"item_id": "item-1", "score": 1.0},
                    {"item_id": "item-2", "score": 0.8},
                    {"item_id": "item-2", "score": 0.7},
                    {"score": 0.5},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = validate_similarity_json(path)

    assert result.status == "WARN"
    assert result.counters["recommendations"] == 4
    assert result.counters["self_recommendations"] == 1
    assert result.counters["duplicate_recommendations"] == 1
    assert result.counters["missing_recommendation_item_id"] == 1


def test_missing_processed_files_are_reported_without_failure(tmp_path: Path) -> None:
    results = validate_processed_data(tmp_path)

    assert len(results) == 7
    assert {result.status for result in results} == {"MISSING"}
    report = render_report(results, processed_dir=tmp_path, generated_at_utc="2026-07-04T00:00:00Z")
    assert "This is local validation evidence, not production monitoring." in report
    assert "## Missing Files" in report
