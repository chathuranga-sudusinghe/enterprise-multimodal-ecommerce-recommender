"""Clean bounded Amazon Berkeley Objects listings into CLIP-ready records."""

from __future__ import annotations

import csv
import gzip
import io
import json
import logging
import tarfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator, Mapping

LOGGER = logging.getLogger(__name__)

IMAGES_METADATA_MEMBER = "images/metadata/images.csv.gz"
ENGLISH_LANGUAGE_TAGS = {
    "en_US",
    "en_GB",
    "en_IN",
    "en_SG",
    "en_CA",
    "en_AU",
}
TEXT_FIELDS = (
    "item_name",
    "brand",
    "product_type",
    "bullet_point",
    "color",
    "material",
    "style",
)
OPTIONAL_METADATA_FIELDS = (
    "item_name",
    "brand",
    "bullet_point",
    "product_type",
    "color",
    "material",
    "style",
    "main_image_id",
    "other_image_id",
)
SOURCE_DATASET = "amazon_berkeley_objects"


@dataclass(frozen=True)
class ABOCleaningSummary:
    """Counts describing one ABO cleaning run."""

    records_scanned: int = 0
    records_written: int = 0
    dropped_missing_item_id: int = 0
    dropped_unusable_text: int = 0
    dropped_missing_required_text: int = 0
    dropped_missing_image: int = 0
    duplicate_item_ids_dropped: int = 0
    missing_product_type: int = 0
    usable_text_count: int = 0
    mapped_image_count: int = 0
    clip_ready_count: int = 0
    evaluation_ready_count: int = 0

    def to_dict(self) -> dict[str, int]:
        """Return a JSON-serializable summary."""
        return asdict(self)


def flatten_multilingual_text(value: Any) -> str:
    """Flatten an ABO text value, preferring available English entries."""
    candidates = list(_iter_text_candidates(value))
    english_values = _unique_text(
        text for language_tag, text in candidates if language_tag in ENGLISH_LANGUAGE_TAGS
    )
    if english_values:
        return " ".join(english_values)

    fallback_values = _unique_text(text for _, text in candidates)
    return fallback_values[0] if fallback_values else ""


def build_combined_text(fields: Mapping[str, Any]) -> str:
    """Build deterministic product text from observed ABO fields."""
    values = [str(fields.get(field, "")).strip() for field in TEXT_FIELDS]
    return " ".join(value for value in values if value)


def normalize_metadata_value(value: Any) -> str:
    """Normalize optional metadata for evaluation grouping."""
    text = str(value or "").strip().lower()
    return " ".join(text.split())


def clean_abo_products(
    listings_tar_path: str | Path,
    images_tar_path: str | Path,
    max_records: int | None = None,
) -> tuple[list[dict[str, Any]], ABOCleaningSummary]:
    """Return cleaned ABO records and a cleaning summary.

    Listing metadata and image metadata are read directly from their tar archives.
    No archive members or image bytes are extracted to disk. Written records keep
    the existing CLIP-ready boundary used by downstream similarity runners.
    """
    listings_path = _require_file(listings_tar_path, "ABO listings archive")
    images_path = _require_file(images_tar_path, "ABO images archive")
    if max_records is not None and max_records <= 0:
        raise ValueError("max_records must be a positive integer or None")

    raw_records = list(_read_listing_records(listings_path, max_records=max_records))
    target_image_ids = {
        flatten_multilingual_text(record.get("main_image_id"))
        for record in raw_records
    }
    target_image_ids.discard("")

    image_id_to_path = _read_image_mapping(images_path, target_image_ids)
    resolved_paths = {
        resolved
        for csv_path in image_id_to_path.values()
        if (resolved := resolve_image_path(csv_path)) is not None
    }
    existing_image_paths = _find_existing_tar_members(images_path, resolved_paths)

    cleaned_records: list[dict[str, Any]] = []
    seen_item_ids: set[str] = set()
    dropped_missing_item_id = 0
    dropped_unusable_text = 0
    dropped_missing_required_text = 0
    dropped_missing_image = 0
    duplicate_item_ids_dropped = 0
    missing_product_type = 0
    usable_text_count = 0
    mapped_image_count = 0
    clip_ready_count = 0
    evaluation_ready_count = 0

    for raw_record in raw_records:
        flattened = {
            field: flatten_multilingual_text(raw_record.get(field))
            for field in ("item_id", *OPTIONAL_METADATA_FIELDS)
        }
        item_id = flattened["item_id"]
        if not item_id:
            dropped_missing_item_id += 1
            dropped_missing_required_text += 1
            continue

        combined_text = build_combined_text(flattened)
        has_usable_text = bool(combined_text)
        if not has_usable_text:
            dropped_unusable_text += 1
            dropped_missing_required_text += 1
            continue
        usable_text_count += 1

        main_image_id = flattened["main_image_id"]
        csv_path = image_id_to_path.get(main_image_id)
        image_path = resolve_image_path(csv_path)
        has_usable_image = bool(image_path and image_path in existing_image_paths)
        image_mapping_status = _image_mapping_status(
            main_image_id,
            csv_path,
            image_path,
            has_usable_image,
        )
        if not has_usable_image:
            dropped_missing_image += 1
            continue
        mapped_image_count += 1

        if item_id in seen_item_ids:
            duplicate_item_ids_dropped += 1
            continue

        normalized_product_type = normalize_metadata_value(flattened["product_type"])
        normalized_brand = normalize_metadata_value(flattened["brand"])
        normalized_color = normalize_metadata_value(flattened["color"])
        if not normalized_product_type:
            missing_product_type += 1

        is_clip_ready = has_usable_text and has_usable_image
        is_evaluation_ready = bool(is_clip_ready and normalized_product_type)
        clip_ready_count += int(is_clip_ready)
        evaluation_ready_count += int(is_evaluation_ready)

        seen_item_ids.add(item_id)
        cleaned_records.append(
            {
                "item_id": item_id,
                "item_name": flattened["item_name"],
                "brand": flattened["brand"],
                "product_type": flattened["product_type"],
                "bullet_point": flattened["bullet_point"],
                "color": flattened["color"],
                "material": flattened["material"],
                "style": flattened["style"],
                "combined_text": combined_text,
                "combined_text_length": len(combined_text),
                "normalized_product_type": normalized_product_type,
                "normalized_brand": normalized_brand,
                "normalized_color": normalized_color,
                "main_image_id": main_image_id,
                "other_image_id": flattened["other_image_id"],
                "image_path": image_path,
                "has_usable_text": has_usable_text,
                "has_usable_image": has_usable_image,
                "is_clip_ready": is_clip_ready,
                "is_evaluation_ready": is_evaluation_ready,
                "metadata_field_count": _metadata_field_count(flattened),
                "source_dataset": SOURCE_DATASET,
                "image_mapping_status": image_mapping_status,
                "cleaning_status": "written",
            }
        )

    summary = ABOCleaningSummary(
        records_scanned=len(raw_records),
        records_written=len(cleaned_records),
        dropped_missing_item_id=dropped_missing_item_id,
        dropped_unusable_text=dropped_unusable_text,
        dropped_missing_required_text=dropped_missing_required_text,
        dropped_missing_image=dropped_missing_image,
        duplicate_item_ids_dropped=duplicate_item_ids_dropped,
        missing_product_type=missing_product_type,
        usable_text_count=usable_text_count,
        mapped_image_count=mapped_image_count,
        clip_ready_count=clip_ready_count,
        evaluation_ready_count=evaluation_ready_count,
    )
    LOGGER.info("ABO cleaning summary: %s", summary.to_dict())
    return cleaned_records, summary


def write_clean_products_jsonl(
    records: Iterable[Mapping[str, Any]], output_path: str | Path
) -> int:
    """Write cleaned ABO records as JSON Lines and return the row count."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(dict(record), ensure_ascii=False) + "\n")
            count += 1
    return count


def resolve_image_path(csv_path: str | None) -> str | None:
    """Resolve an images.csv.gz path to its small-image tar member path."""
    if csv_path is None or not str(csv_path).strip():
        return None

    path = PurePosixPath(str(csv_path).strip().lstrip("/"))
    if path.is_absolute() or ".." in path.parts:
        return None
    if path.parts[:2] == ("images", "small"):
        return path.as_posix()
    return (PurePosixPath("images/small") / path).as_posix()


def _read_listing_records(
    listings_tar_path: Path, max_records: int | None
) -> Iterator[dict[str, Any]]:
    records_read = 0
    metadata_members_found = 0
    with tarfile.open(listings_tar_path, mode="r:") as archive:
        for member in archive:
            if not member.isfile() or not _is_listing_metadata_member(member.name):
                continue
            metadata_members_found += 1
            extracted = archive.extractfile(member)
            if extracted is None:
                continue
            with gzip.GzipFile(fileobj=extracted) as gzip_file:
                with io.TextIOWrapper(gzip_file, encoding="utf-8") as text_file:
                    for line_number, line in enumerate(text_file, start=1):
                        if max_records is not None and records_read >= max_records:
                            return
                        if not line.strip():
                            continue
                        try:
                            record = json.loads(line)
                        except json.JSONDecodeError as exc:
                            raise ValueError(
                                f"Invalid JSON in {member.name} at line {line_number}"
                            ) from exc
                        if not isinstance(record, dict):
                            raise ValueError(
                                f"Expected a JSON object in {member.name} at line {line_number}"
                            )
                        records_read += 1
                        yield record

    if metadata_members_found == 0:
        raise ValueError(
            "No listings/metadata/listings_*.json.gz members found in ABO listings archive"
        )


def _read_image_mapping(
    images_tar_path: Path, target_image_ids: set[str]
) -> dict[str, str]:
    if not target_image_ids:
        return {}

    with tarfile.open(images_tar_path, mode="r:") as archive:
        try:
            member = archive.getmember(IMAGES_METADATA_MEMBER)
        except KeyError as exc:
            raise ValueError(
                f"Missing {IMAGES_METADATA_MEMBER} in ABO images archive"
            ) from exc
        extracted = archive.extractfile(member)
        if extracted is None:
            raise ValueError(f"Unable to read {IMAGES_METADATA_MEMBER}")

        mapping: dict[str, str] = {}
        with gzip.GzipFile(fileobj=extracted) as gzip_file:
            with io.TextIOWrapper(gzip_file, encoding="utf-8", newline="") as text_file:
                reader = csv.DictReader(text_file)
                required_columns = {"image_id", "path"}
                if not required_columns.issubset(reader.fieldnames or []):
                    raise ValueError(
                        f"{IMAGES_METADATA_MEMBER} must contain image_id and path columns"
                    )
                for row in reader:
                    image_id = (row.get("image_id") or "").strip()
                    csv_path = (row.get("path") or "").strip()
                    if image_id in target_image_ids and csv_path and image_id not in mapping:
                        mapping[image_id] = csv_path
                        if len(mapping) == len(target_image_ids):
                            break
    return mapping


def _find_existing_tar_members(
    images_tar_path: Path, candidate_paths: set[str]
) -> set[str]:
    if not candidate_paths:
        return set()

    existing: set[str] = set()
    with tarfile.open(images_tar_path, mode="r:") as archive:
        for member in archive:
            if member.isfile() and member.name in candidate_paths:
                existing.add(member.name)
                if existing == candidate_paths:
                    break
    return existing


def _image_mapping_status(
    main_image_id: str,
    csv_path: str | None,
    resolved_image_path: str | None,
    has_usable_image: bool,
) -> str:
    if not main_image_id:
        return "missing_main_image_id"
    if not csv_path:
        return "image_id_not_found"
    if not resolved_image_path:
        return "invalid_mapped_path"
    if not has_usable_image:
        return "mapped_path_missing"
    return "mapped"


def _metadata_field_count(flattened: Mapping[str, str]) -> int:
    return sum(1 for field in OPTIONAL_METADATA_FIELDS if flattened.get(field))


def _is_listing_metadata_member(member_name: str) -> bool:
    path = PurePosixPath(member_name)
    return (
        path.parent == PurePosixPath("listings/metadata")
        and path.name.startswith("listings_")
        and path.name.endswith(".json.gz")
    )


def _iter_text_candidates(value: Any) -> Iterator[tuple[str | None, str]]:
    if value is None:
        return
    if isinstance(value, str):
        text = value.strip()
        if text:
            yield None, text
        return
    if isinstance(value, (int, float, bool)):
        yield None, str(value)
        return
    if isinstance(value, list):
        for item in value:
            yield from _iter_text_candidates(item)
        return
    if isinstance(value, dict):
        if "value" in value:
            language_tag = value.get("language_tag")
            for _, text in _iter_text_candidates(value.get("value")):
                yield str(language_tag) if language_tag else None, text
            return
        for nested_value in value.values():
            yield from _iter_text_candidates(nested_value)


def _unique_text(values: Iterable[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)
    return unique


def _require_file(path: str | Path, description: str) -> Path:
    resolved = Path(path)
    if not resolved.is_file():
        raise FileNotFoundError(f"{description} not found: {resolved}")
    return resolved
