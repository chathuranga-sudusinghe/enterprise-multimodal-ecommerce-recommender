import csv
import gzip
import io
import json
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from ecommerce_recommender.data.clean_abo_products import (
    clean_abo_products,
    flatten_multilingual_text,
    write_clean_products_jsonl,
)


def _multilingual(english: str, fallback: str = "Fallback") -> list[dict[str, str]]:
    return [
        {"language_tag": "fr_FR", "value": fallback},
        {"language_tag": "en_US", "value": english},
    ]


def _listing(item_id: str = "item-1", image_id: str = "image-1") -> dict[str, object]:
    return {
        "item_id": item_id,
        "item_name": _multilingual("Ceramic Plate"),
        "brand": _multilingual("Table Home"),
        "product_type": [{"value": "DINNER_PLATE"}],
        "bullet_point": [
            {"language_tag": "en_US", "value": "Dishwasher safe"},
            {"language_tag": "en_US", "value": "Set of four"},
        ],
        "color": _multilingual("White"),
        "material": _multilingual("Ceramic"),
        "style": _multilingual("Modern"),
        "main_image_id": image_id,
    }


def _gzip_bytes(content: str) -> bytes:
    return gzip.compress(content.encode("utf-8"))


def _add_bytes(archive: tarfile.TarFile, name: str, content: bytes) -> None:
    member = tarfile.TarInfo(name)
    member.size = len(content)
    archive.addfile(member, io.BytesIO(content))


def _write_tar_fixtures(
    tmp_path: Path,
    listings: list[dict[str, object]],
    image_rows: list[dict[str, str]] | None = None,
    existing_image_paths: set[str] | None = None,
) -> tuple[Path, Path]:
    listings_tar = tmp_path / "abo-listings.tar"
    images_tar = tmp_path / "abo-images-small.tar"

    listing_jsonl = "\n".join(json.dumps(record) for record in listings) + "\n"
    with tarfile.open(listings_tar, "w") as archive:
        _add_bytes(
            archive,
            "listings/metadata/listings_0.json.gz",
            _gzip_bytes(listing_jsonl),
        )

    rows = image_rows or [
        {"image_id": "image-1", "height": "100", "width": "100", "path": "00/image-1.jpg"}
    ]
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=["image_id", "height", "width", "path"])
    writer.writeheader()
    writer.writerows(rows)

    paths = existing_image_paths
    if paths is None:
        paths = {f"images/small/{row['path']}" for row in rows}
    with tarfile.open(images_tar, "w") as archive:
        _add_bytes(
            archive,
            "images/metadata/images.csv.gz",
            _gzip_bytes(csv_buffer.getvalue()),
        )
        for image_path in sorted(paths):
            _add_bytes(archive, image_path, b"fixture-image")

    return listings_tar, images_tar


def test_flatten_multilingual_text_prefers_english_value() -> None:
    value = [
        {"language_tag": "fr_FR", "value": "Assiette"},
        {"language_tag": "en_GB", "value": "Plate"},
    ]

    assert flatten_multilingual_text(value) == "Plate"


def test_flatten_multilingual_text_falls_back_to_first_valid_value() -> None:
    value = [
        {"language_tag": "fr_FR", "value": "Assiette"},
        {"language_tag": "de_DE", "value": "Teller"},
    ]

    assert flatten_multilingual_text(value) == "Assiette"


def test_builds_combined_text_from_required_and_optional_fields(tmp_path: Path) -> None:
    listings_tar, images_tar = _write_tar_fixtures(tmp_path, [_listing()])

    records, _ = clean_abo_products(listings_tar, images_tar, max_records=10)

    assert records[0]["combined_text"] == (
        "Ceramic Plate Table Home DINNER_PLATE Dishwasher safe Set of four "
        "White Ceramic Modern"
    )


def test_maps_main_image_id_to_resolved_tar_path(tmp_path: Path) -> None:
    listings_tar, images_tar = _write_tar_fixtures(tmp_path, [_listing()])

    records, summary = clean_abo_products(listings_tar, images_tar)

    assert records[0]["image_path"] == "images/small/00/image-1.jpg"
    assert summary.records_written == 1


def test_drops_record_when_main_image_id_does_not_map(tmp_path: Path) -> None:
    listings_tar, images_tar = _write_tar_fixtures(
        tmp_path,
        [_listing(image_id="missing-image")],
    )

    records, summary = clean_abo_products(listings_tar, images_tar)

    assert records == []
    assert summary.dropped_missing_image == 1


def test_drops_record_when_required_text_is_missing(tmp_path: Path) -> None:
    listing = _listing()
    listing["brand"] = []
    listings_tar, images_tar = _write_tar_fixtures(tmp_path, [listing])

    records, summary = clean_abo_products(listings_tar, images_tar)

    assert records == []
    assert summary.dropped_missing_required_text == 1


def test_deduplicates_item_id_and_keeps_first_valid_record(tmp_path: Path) -> None:
    first = _listing()
    second = _listing()
    second["item_name"] = _multilingual("Second Plate")
    listings_tar, images_tar = _write_tar_fixtures(tmp_path, [first, second])

    records, summary = clean_abo_products(listings_tar, images_tar)

    assert len(records) == 1
    assert records[0]["item_name"] == "Ceramic Plate"
    assert summary.duplicate_item_ids_dropped == 1


def test_writes_clip_ready_jsonl_with_expected_fields(tmp_path: Path) -> None:
    listings_tar, images_tar = _write_tar_fixtures(tmp_path, [_listing()])
    records, summary = clean_abo_products(listings_tar, images_tar)
    output_path = tmp_path / "processed" / "abo_clean.jsonl"

    rows_written = write_clean_products_jsonl(records, output_path)
    saved_record = json.loads(output_path.read_text(encoding="utf-8").strip())

    assert rows_written == 1
    assert summary.to_dict() == {
        "records_scanned": 1,
        "records_written": 1,
        "dropped_missing_required_text": 0,
        "dropped_missing_image": 0,
        "duplicate_item_ids_dropped": 0,
    }
    assert set(saved_record) == {
        "item_id",
        "item_name",
        "brand",
        "product_type",
        "bullet_point",
        "color",
        "material",
        "style",
        "combined_text",
        "main_image_id",
        "image_path",
        "has_usable_text",
        "has_usable_image",
        "is_clip_ready",
    }
    assert saved_record["is_clip_ready"] is True
