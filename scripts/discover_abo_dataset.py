"""Discover Amazon Berkeley Objects archives safely without full extraction."""

from __future__ import annotations

import csv
import gzip
import io
import json
import logging
import tarfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data/raw/amazon_berkeley_text_images-based"
REPORT_PATH = PROJECT_ROOT / "docs/reports/abo_dataset_discovery.md"
SUMMARY_REPORT_PATH = PROJECT_ROOT / "docs/reports/dataset_discovery_summary.md"
SAMPLE_LIMIT = 10
LISTING_RECORD_LIMIT = 5
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
TEXT_FIELD_CANDIDATES = {
    "brand", "bullet_point", "color", "fabric_type", "item_keywords", "item_name",
    "material", "model_name", "product_type", "style",
}


@dataclass
class ArchiveSummary:
    """Streaming tar archive inspection summary."""

    path: Path
    member_count: int = 0
    file_count: int = 0
    directory_count: int = 0
    top_level_counts: Counter[str] = field(default_factory=Counter)
    suffix_counts: Counter[str] = field(default_factory=Counter)
    metadata_paths: list[str] = field(default_factory=list)
    sample_paths: list[str] = field(default_factory=list)
    image_count: int = 0
    image_suffix_counts: Counter[str] = field(default_factory=Counter)
    sample_image_paths: list[str] = field(default_factory=list)
    metadata_fields: set[str] = field(default_factory=set)
    sample_record_count: int = 0

    @property
    def size_bytes(self) -> int:
        """Return archive size in bytes."""
        return self.path.stat().st_size

    @property
    def size_mb(self) -> float:
        """Return archive size in mebibytes."""
        return self.size_bytes / (1024 * 1024)


def require_file(path: Path) -> None:
    """Raise a clear error when an expected ABO file is missing."""
    if not path.is_file():
        raise FileNotFoundError(f"ABO raw file not found: {path}")


def compound_suffix(path: PurePosixPath) -> str:
    """Return a useful lowercase suffix, preserving gzip metadata suffixes."""
    suffixes = path.suffixes
    if len(suffixes) >= 2 and suffixes[-1].lower() == ".gz":
        return "".join(suffixes[-2:]).lower()
    return path.suffix.lower() or "<no suffix>"


def read_listing_samples(archive: tarfile.TarFile, member: tarfile.TarInfo, summary: ArchiveSummary) -> None:
    """Read a bounded number of JSON-lines listing records from one gzip member."""
    extracted = archive.extractfile(member)
    if extracted is None:
        return
    with gzip.GzipFile(fileobj=extracted) as gzip_file:
        with io.TextIOWrapper(gzip_file, encoding="utf-8") as text_file:
            for _ in range(LISTING_RECORD_LIMIT):
                line = text_file.readline()
                if not line:
                    break
                record = json.loads(line)
                if isinstance(record, dict):
                    summary.metadata_fields.update(str(key) for key in record)
                    summary.sample_record_count += 1


def read_image_metadata_header(archive: tarfile.TarFile, member: tarfile.TarInfo, summary: ArchiveSummary) -> None:
    """Read only a compressed metadata header or a bounded JSON-lines sample."""
    extracted = archive.extractfile(member)
    if extracted is None:
        return
    if member.name.endswith(".csv.gz"):
        with gzip.GzipFile(fileobj=extracted) as gzip_file:
            with io.TextIOWrapper(gzip_file, encoding="utf-8") as text_file:
                summary.metadata_fields.update(csv.DictReader(text_file).fieldnames or [])
    elif member.name.endswith(".json.gz"):
        with gzip.GzipFile(fileobj=extracted) as gzip_file:
            with io.TextIOWrapper(gzip_file, encoding="utf-8") as text_file:
                for _ in range(LISTING_RECORD_LIMIT):
                    line = text_file.readline()
                    if not line:
                        break
                    record = json.loads(line)
                    if isinstance(record, dict):
                        summary.metadata_fields.update(str(key) for key in record)
                        summary.sample_record_count += 1


def inspect_archive(path: Path) -> ArchiveSummary:
    """Stream tar headers and sample bounded metadata without extraction."""
    require_file(path)
    LOGGER.info("Streaming tar headers: %s", path)
    summary = ArchiveSummary(path=path)
    sampled_listing_metadata = False
    sampled_image_metadata = False
    with tarfile.open(path, mode="r:") as archive:
        for member in archive:
            summary.member_count += 1
            member_path = PurePosixPath(member.name)
            top_level = member_path.parts[0] if member_path.parts else member.name
            summary.top_level_counts[top_level] += 1
            if member.isdir():
                summary.directory_count += 1
                continue
            if not member.isfile():
                continue
            summary.file_count += 1
            summary.suffix_counts[compound_suffix(member_path)] += 1
            if len(summary.sample_paths) < SAMPLE_LIMIT:
                summary.sample_paths.append(member.name)
            if member_path.suffix.lower() in IMAGE_SUFFIXES:
                summary.image_count += 1
                summary.image_suffix_counts[member_path.suffix.lower()] += 1
                if len(summary.sample_image_paths) < SAMPLE_LIMIT:
                    summary.sample_image_paths.append(member.name)
            is_metadata = "metadata" in member_path.parts or member.name.lower().endswith("readme.md")
            if is_metadata and len(summary.metadata_paths) < 30:
                summary.metadata_paths.append(member.name)
            if path.name == "abo-listings.tar" and member.name.endswith(".json.gz") and not sampled_listing_metadata:
                read_listing_samples(archive, member, summary)
                sampled_listing_metadata = True
            if path.name == "abo-images-small.tar" and "metadata" in member_path.parts and member.name.endswith((".csv.gz", ".json.gz")) and not sampled_image_metadata:
                read_image_metadata_header(archive, member, summary)
                sampled_image_metadata = True
    return summary


def bullet_list(values: list[str]) -> str:
    """Render Markdown bullets or a clear empty-state bullet."""
    return "\n".join(f"- `{value}`" for value in values) or "- None discovered"


def counter_list(values: Counter[str]) -> str:
    """Render sorted Markdown bullets from a counter."""
    return "\n".join(f"- `{name}`: {count:,}" for name, count in values.most_common()) or "- None discovered"


def build_abo_report(listings: ArchiveSummary, images: ArchiveSummary, readme_path: Path) -> str:
    """Build the ABO dataset discovery report."""
    listing_fields = sorted(listings.metadata_fields)
    text_fields = sorted(TEXT_FIELD_CANDIDATES.intersection(listings.metadata_fields))
    listing_id_fields = sorted(field for field in listings.metadata_fields if field.endswith("id") or field.endswith("_id"))
    image_mapping_fields = sorted(field for field in listings.metadata_fields if "image" in field and "id" in field)
    image_metadata_fields = sorted(images.metadata_fields)
    return f"""# Amazon Berkeley Objects Dataset Discovery

This report was generated by streaming tar member headers and inspecting only a bounded sample of compressed metadata records. No archive was fully extracted, no image content was processed, and no embeddings were generated.

## Raw Archive Inventory

| File | Size MB | Purpose |
| --- | ---: | --- |
| `{listings.path.name}` | {listings.size_mb:.2f} | Multilingual product listing metadata |
| `{images.path.name}` | {images.size_mb:.2f} | Downscaled catalog images and image metadata |
| `{readme_path.name}` | {readme_path.stat().st_size / (1024 * 1024):.2f} | Dataset description and license notes |

## Listings Archive Structure

- Path: `{listings.path.as_posix()}`
- Tar members: {listings.member_count:,}
- Files: {listings.file_count:,}
- Directories: {listings.directory_count:,}
- Sampled listing records: {listings.sample_record_count:,}

### Top-Level Entries

{counter_list(listings.top_level_counts)}

### Metadata File Types

{counter_list(listings.suffix_counts)}

### Metadata Paths Sample

{bullet_list(listings.metadata_paths)}

### Metadata Sample Fields

{bullet_list(listing_fields)}

### Possible Product or Listing ID Fields

{bullet_list(listing_id_fields)}

### Available Text Fields

{bullet_list(text_fields)}

## Images Archive Structure

- Path: `{images.path.as_posix()}`
- Tar members: {images.member_count:,}
- Files: {images.file_count:,}
- Directories: {images.directory_count:,}
- Image files: {images.image_count:,}

### Top-Level Entries

{counter_list(images.top_level_counts)}

### Image File Formats

{counter_list(images.image_suffix_counts)}

### Sample Image Paths

{bullet_list(images.sample_image_paths)}

### Image Metadata Paths

{bullet_list(images.metadata_paths)}

### Image Metadata Sample Fields

{bullet_list(image_metadata_fields)}

## Product-to-Image Mapping Possibilities

The sampled listings expose image identifier fields that can link product metadata to image files:

{bullet_list(image_mapping_fields)}

Image archive paths use image IDs as filenames under sharded folders such as `images/small/00/00834536.jpg`. A later adapter can map listing `main_image_id` and `other_image_id` values to these files without merging ABO identifiers with RetailRocket identifiers.

## Baseline Signals Available

- Multilingual product names and bullet points.
- Brand, product type, color, material, style, and related listing attributes where present.
- Main and additional image identifiers.
- Downscaled catalog images for product similarity experiments.
- Candidate baseline: content-based product similarity using ABO metadata first, followed by optional image features in a later controlled step.

## Limitations

- ABO and RetailRocket are separate dataset tracks with unrelated identifiers.
- This discovery task does not join ABO products to RetailRocket events.
- Field availability varies by listing and locale.
- Spin, 360-degree, 3D, and video-style assets are outside the current project scope.
- The local subset contains listing metadata and small images only.
- This report does not train models, create embeddings, or define recommendation weights.
"""


def build_summary_report() -> str:
    """Build the confirmed two-track dataset strategy summary."""
    return """# Dataset Discovery Summary

## Confirmed Two-Track Dataset Strategy

The project uses two independent real-world dataset tracks. They must not be merged, and their customer or product identifiers must not be treated as shared identifiers.

| Track | Dataset | Purpose | Initial Baseline Candidate |
| --- | --- | --- | --- |
| A | `RetailRocket_event-based` | Behavior and event-based recommendation | Event-weighted recent popularity recommender |
| B | `amazon_berkeley_text_images-based` | Product metadata, text, and image-based similarity recommendation | Content-based product similarity recommender |

## Dataset Separation Rule

- RetailRocket visitor and item identifiers belong only to the RetailRocket track.
- Amazon Berkeley Objects listing and image identifiers belong only to the ABO track.
- Do not create synthetic joins between tracks.
- Evaluate each track against a task-appropriate protocol before considering later system-level composition.

## Scope Boundary

Video recommendation is excluded from the current project scope. Current work focuses on behavior, text, and image-based recommendation only. ABO spin, turntable, 360-degree, and 3D assets are not part of the current implementation plan.

## Safe Baseline Direction

- RetailRocket: inspect event values, timestamp ranges, and item-property structure before selecting provisional event weights. The first candidate is an event-weighted recent popularity recommender.
- ABO: inspect multilingual listing fields and image identifier mappings before selecting metadata features. The first candidate is content-based product similarity.
- Advanced methods must be evaluated against their corresponding baseline using the same business task and evaluation protocol.

## Recommended Documentation Restructuring

1. Update system scope to describe the two-track dataset strategy.
2. Update architecture to separate behavior-based and content/image-based pipelines.
3. Update data design with discovered raw schemas and canonical mapping decisions.
4. Update evaluation planning with one protocol per dataset track and leakage controls.
5. Update security and governance notes with dataset provenance, attribution, and raw-data handling boundaries.
6. Keep model implementation paused until the discovery reports are reviewed.

## Generated Discovery Reports

- [`retailrocket_dataset_discovery.md`](retailrocket_dataset_discovery.md)
- [`abo_dataset_discovery.md`](abo_dataset_discovery.md)
"""


def main() -> None:
    """Run safe ABO discovery and write ABO plus summary reports."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    readme_path = RAW_DATA_DIR / "README.md"
    require_file(readme_path)
    listings = inspect_archive(RAW_DATA_DIR / "abo-listings.tar")
    images = inspect_archive(RAW_DATA_DIR / "abo-images-small.tar")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_abo_report(listings, images, readme_path), encoding="utf-8")
    SUMMARY_REPORT_PATH.write_text(build_summary_report(), encoding="utf-8")
    LOGGER.info("Wrote report: %s", REPORT_PATH)
    LOGGER.info("Wrote report: %s", SUMMARY_REPORT_PATH)


if __name__ == "__main__":
    main()
