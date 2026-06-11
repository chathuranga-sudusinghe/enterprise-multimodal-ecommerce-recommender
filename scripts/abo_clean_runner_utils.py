"""Shared bounded input helpers for cleaned ABO similarity runners."""

from __future__ import annotations

import json
import shutil
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_PATH = PROJECT_ROOT / "data/processed/abo_clean_products_5k.jsonl"
DEFAULT_IMAGES_TAR_PATH = PROJECT_ROOT / "data/raw/amazon_berkeley_text_images-based/abo-images-small.tar"
DEFAULT_MAX_PRODUCTS = 100


def load_clean_abo_products(input_path: str | Path, max_products: int = DEFAULT_MAX_PRODUCTS) -> list[dict[str, Any]]:
    """Load the first bounded set of CLIP-ready records from cleaned JSONL."""
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Cleaned ABO JSONL file not found: {path}")
    if max_products <= 0:
        raise ValueError("max_products must be greater than zero")

    products: list[dict[str, Any]] = []
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
            for field in ("item_id", "combined_text", "main_image_id", "image_path"):
                _required_text(record, field)
            products.append(record)
            if len(products) >= max_products:
                break
    if not products:
        raise ValueError(f"No cleaned ABO products found: {path}")
    return products


def select_query_item_id(products: Sequence[Mapping[str, Any]], query_item_id: str | None = None) -> str:
    """Return a validated query item ID shared by all similarity runners."""
    item_ids = [str(product["item_id"]) for product in products]
    selected = query_item_id or item_ids[0]
    if selected not in set(item_ids):
        raise ValueError(f"Query item_id is not present in the loaded sample: {selected}")
    return selected


def extract_sample_images(images_tar_path: str | Path, products: Sequence[Mapping[str, Any]], destination: str | Path) -> Path:
    """Extract only selected cleaned-product image members to a temporary root."""
    archive_path = Path(images_tar_path)
    destination_path = Path(destination)
    if not archive_path.is_file():
        raise FileNotFoundError(f"ABO images archive not found: {archive_path}")

    requested_paths = {_validated_tar_member_path(product["image_path"]) for product in products}
    extracted_paths: set[str] = set()
    with tarfile.open(archive_path, mode="r:") as archive:
        for member in archive:
            if not member.isfile() or member.name not in requested_paths:
                continue
            source = archive.extractfile(member)
            if source is None:
                continue
            target = destination_path / PurePosixPath(member.name)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as output:
                shutil.copyfileobj(source, output)
            extracted_paths.add(member.name)
            if extracted_paths == requested_paths:
                break

    missing_paths = requested_paths - extracted_paths
    if missing_paths:
        missing = ", ".join(sorted(missing_paths))
        raise FileNotFoundError(f"Cleaned ABO image paths not found in archive: {missing}")
    return destination_path


def build_image_records(products: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Build the image mapping shape expected by the RGB histogram baseline."""
    return [{"image_id": _required_text(product, "main_image_id"), "path": _required_text(product, "image_path")} for product in products]


def product_metadata(product: Mapping[str, Any]) -> dict[str, str]:
    """Return compact product metadata for runner JSON outputs."""
    return {field: str(product[field]) for field in ("item_name", "product_type") if product.get(field) not in (None, "")}


def display_path(path: str | Path) -> str:
    """Display repository paths without embedding a machine-specific prefix."""
    resolved = Path(path).resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def write_json_output(output: Mapping[str, Any], output_path: str | Path) -> None:
    """Write a stable, readable runner result artifact."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _required_text(record: Mapping[str, Any], field: str) -> str:
    value = record.get(field)
    if value is None or not str(value).strip():
        raise ValueError(f"Cleaned ABO record is missing required field: {field}")
    return str(value).strip()


def _validated_tar_member_path(value: Any) -> str:
    path = PurePosixPath(_required_text({"image_path": value}, "image_path"))
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe cleaned ABO image_path: {value}")
    return path.as_posix()
