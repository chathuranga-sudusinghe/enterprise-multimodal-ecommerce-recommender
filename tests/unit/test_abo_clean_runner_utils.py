import io
import json
import tarfile
from pathlib import Path

import pytest

from scripts.abo_clean_runner_utils import build_image_records, extract_sample_images, load_clean_abo_products, select_query_item_id


def _record(item_id: str, image_path: str) -> dict[str, object]:
    return {"item_id": item_id, "item_name": f"Product {item_id}", "product_type": "FIXTURE", "combined_text": f"cleaned text {item_id}", "main_image_id": f"image-{item_id}", "image_path": image_path, "is_clip_ready": True}


def test_load_clean_abo_products_uses_bounded_file_order(tmp_path: Path) -> None:
    input_path = tmp_path / "products.jsonl"
    records = [_record("a", "images/small/a.jpg"), _record("b", "images/small/b.jpg")]
    input_path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")
    loaded = load_clean_abo_products(input_path, max_products=1)
    assert [record["item_id"] for record in loaded] == ["a"]
    assert select_query_item_id(loaded) == "a"


def test_load_clean_abo_products_rejects_missing_clean_fields(tmp_path: Path) -> None:
    input_path = tmp_path / "products.jsonl"
    input_path.write_text(json.dumps({"item_id": "a"}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="combined_text"):
        load_clean_abo_products(input_path)


def test_extract_sample_images_reads_only_requested_tar_members(tmp_path: Path) -> None:
    archive_path = tmp_path / "images.tar"
    requested_path = "images/small/00/requested.jpg"
    with tarfile.open(archive_path, "w") as archive:
        for member_name, content in ((requested_path, b"requested"), ("images/small/00/unrelated.jpg", b"unrelated")):
            member = tarfile.TarInfo(member_name)
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
    products = [_record("a", requested_path)]
    image_root = extract_sample_images(archive_path, products, tmp_path / "extracted")
    assert (image_root / requested_path).read_bytes() == b"requested"
    assert not (image_root / "images/small/00/unrelated.jpg").exists()
    assert build_image_records(products) == [{"image_id": "image-a", "path": requested_path}]


def test_select_query_item_id_rejects_item_outside_loaded_sample() -> None:
    with pytest.raises(ValueError, match="not present"):
        select_query_item_id([_record("a", "images/small/a.jpg")], "missing")
