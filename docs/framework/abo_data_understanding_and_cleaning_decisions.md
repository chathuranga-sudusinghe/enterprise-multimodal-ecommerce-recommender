# ABO Data Understanding and Cleaning Decisions

## 1. Purpose

This document converts exploratory findings from `notebooks/03_abo_data_inspection.ipynb` into approved or proposed cleaning decisions for the Amazon Berkeley Objects (ABO) text/image similarity track.

The notebook is data understanding evidence. It is not the final data pipeline. Final cleaning must be implemented in reproducible scripts, with outputs written as controlled processed artifacts and validated through the Data Gate hardening process.

This document supports the current Data Gate Hardening milestone by connecting notebook-based inspection to explicit cleaning rules. It does not authorize FAISS, vector databases, API work, MCP integration, deployment, monitoring, or production-readiness claims.

## 2. Notebook Evidence Used

Evidence source:

- `notebooks/03_abo_data_inspection.ipynb`

The notebook inspected:

- Raw ABO file existence under `data/raw/amazon_berkeley_text_images-based/`.
- `abo-listings.tar` structure using bounded tar inspection.
- `abo-images-small.tar` structure using bounded tar inspection.
- Listing record samples from compressed listing metadata members.
- Available listing fields and nested fields.
- Product ID fields, especially `item_id`, `main_image_id`, and `other_image_id`.
- Text fields used for product similarity.
- Image fields and image archive contents.
- Missing values in important fields.
- Duplicate `item_id` values in the sampled records.
- Image mapping feasibility.
- Corrected image mapping through `images/metadata/images.csv.gz`.
- CLIP-ready estimation before and after corrected image mapping.
- Good and problematic example records.

Key notebook observations:

- The raw listing archive and small image archive existed locally during inspection.
- A bounded sample of 500 listing records was inspected.
- The sampled listing records had 28 observed top-level fields.
- Sampled `item_id` values were present and unique in the 500-record sample.
- Direct comparison of listing image IDs to image file stems produced zero mapped images.
- The image archive contained `images/metadata/images.csv.gz` with columns including `image_id` and `path`.
- Corrected mapping through `images/metadata/images.csv.gz` mapped 495 of 500 sampled `main_image_id` values to image paths that existed in the small image archive.
- Corrected CLIP-ready count in the sampled records was 495 of 500 when requiring usable text and a mapped image path.

## 3. ABO Listing Field Understanding

The notebook observed or used these fields for the ABO cleaning design:

| Field | Role | Requiredness |
|---|---|---|
| `item_id` | Primary ABO product/listing identity. | Required for identity. |
| `item_name` | Product name/title text. | Optional metadata, used for text. |
| `brand` | Product brand text. | Optional metadata, used for text. |
| `bullet_point` | Product bullet text. | Optional metadata, used for text. |
| `product_type` | Product type/category metadata. | Optional metadata, important for evaluation interpretation. |
| `color` | Product attribute text. | Optional metadata, used for text. |
| `material` | Product attribute text. | Optional metadata, used for text. |
| `style` | Product attribute text. | Optional metadata, used for text. |
| `main_image_id` | Preferred image identifier for product-image mapping. | Optional metadata, required for CLIP-ready status. |
| `other_image_id` | Additional image identifiers where available. | Optional metadata. |

`item_id` is the only required identity field in the cleaned ABO product record. All other fields are optional metadata, but missing values must be preserved or reported rather than invented.

## 4. Text Cleaning Decisions

Approved cleaning direction:

- Build `combined_text` from available `item_name`, `brand`, `bullet_point`, `product_type`, `color`, `material`, and `style` values.
- Handle multilingual, list, dictionary, and nested text values safely.
- Prefer usable English text where available if the current cleaning logic supports language-aware selection.
- Fall back to the first valid non-empty value where English text is not available.
- Treat empty strings, empty lists, null values, and missing fields as missing text components.
- Do not invent missing titles, brands, product types, bullets, colors, materials, styles, or other text.
- Keep records with missing optional text fields only when `combined_text` remains usable.

The notebook supports these decisions by profiling the target text fields and creating combined text from observed listing samples.

## 5. Image Mapping Decision

Approved image mapping rule:

```text
main_image_id -> images/metadata/images.csv.gz image_id -> path -> images/small/{path}
```

Direct comparison of `main_image_id` to image file stems inside `abo-images-small.tar` is not sufficient. The notebook showed that direct stem matching produced zero mapped images in the inspected sample, while the corrected metadata mapping found valid paths for 495 of 500 sampled records.

Cleaning scripts should therefore:

- Read `images/metadata/images.csv.gz` from `abo-images-small.tar`.
- Use the `image_id` column to map listing `main_image_id` values.
- Use the mapped `path` column to construct the expected small-image tar member path as `images/small/{path}`.
- Confirm the resolved tar member exists before marking a record image-ready.
- Avoid extracting the full image archive.

## 6. Missing Value Handling

Approved or proposed handling:

- Missing `item_id`: reject or skip the record because the cleaned product cannot be identified safely.
- Missing text fields: allow missing optional components if `combined_text` remains usable.
- Missing `product_type`: keep the record only if needed for similarity coverage, but track it as an evaluation limitation because product type is useful for proxy evaluation interpretation.
- Missing image mapping or missing image path: keep the record for text-only use if text is usable, but do not mark it CLIP-ready.
- Missing optional metadata: preserve as empty, null, or omitted according to the cleaned schema; do not infer or invent values.

Missing-value summaries must be reported by the cleaning process or validation report before Data Gate approval.

## 7. Duplicate Handling

Approved duplicate handling direction:

- Duplicate `item_id` values must be detected.
- Cleaning should preserve one deterministic record or skip duplicate records according to the current implementation.
- Duplicate handling must be reported as part of the cleaning summary.

The notebook found zero duplicate `item_id` rows in the 500-record sample, but that sample result is not full-dataset proof. Full or bounded cleaning runs still need duplicate counts in their output summaries.

## 8. CLIP-Ready Definition

A cleaned ABO product is CLIP-ready only when all of the following are true:

- It has a usable `item_id`.
- It has usable `combined_text`.
- It has a usable mapped image path derived through the corrected image metadata mapping:

```text
main_image_id -> images/metadata/images.csv.gz image_id -> path -> images/small/{path}
```

Records without usable text or without a validated mapped image path must not be counted as CLIP-ready.

## 9. Cleaning Script Expectations

Based on the notebook decisions, `scripts/clean_abo_products.py` should:

- Use bounded archive reading for ABO listing metadata and image metadata.
- Extract metadata safely from `abo-listings.tar` without loading or extracting unnecessary files.
- Normalize text fields from multilingual, list, dictionary, and nested structures.
- Build `combined_text` from approved text fields.
- Read image metadata from `images/metadata/images.csv.gz`.
- Map `main_image_id` to a resolved small-image path using `image_id` and `path`.
- Confirm mapped image paths exist in `abo-images-small.tar`.
- Write product-level cleaned records to JSONL.
- Include `item_id`, text fields, image identifiers, mapped `image_path`, text/image readiness flags, and `is_clip_ready` where supported by the cleaned schema.
- Avoid full raw image extraction.
- Report records scanned, records written, missing required text, missing image mapping, and duplicate item IDs.

The script should remain local, deterministic, and dependency-light.

## 10. Data Gate Impact

This document supports Data Gate hardening by making the notebook's exploratory evidence reviewable and by converting data understanding into explicit cleaning rules.

It helps establish:

- Why `item_id` is the identity boundary for ABO.
- Which fields should feed text cleaning.
- Why corrected image metadata mapping is required.
- How missing values and duplicates should be handled.
- What CLIP-ready means for the ABO track.

This document is local framework evidence only. It does not make the Data Gate fully GO by itself and does not replace reproducible scripts, schema validation, lineage records, checksum/source-version evidence, or evaluation hardening.

## 11. Remaining Gaps

Remaining gaps before stronger Data Gate approval:

- Source checksum and source version evidence for ABO raw archives.
- Full schema validation evidence for raw and processed ABO artifacts.
- Row-count and missing-value summary from the cleaning script for the actual processed outputs.
- Duplicate handling summary from cleaning runs.
- Representative evaluation query selection criteria.
- Clear lineage from raw archive members to processed JSONL records.
- Reproducibility evidence for processed artifacts and evaluation outputs.
- No production claims until data, evaluation, service, monitoring, and deployment gates are supported by evidence.
