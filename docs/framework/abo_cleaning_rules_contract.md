# ABO Cleaning Rules Contract

## Purpose

This contract defines the cleaned ABO product data categories and cleaning targets for the Data Gate Hardening milestone. It is based on `docs/framework/abo_data_understanding_and_cleaning_decisions.md` and converts notebook-derived understanding into explicit cleaned-data expectations.

This is a data contract document only. It does not implement FAISS, vector search, API work, MCP integration, deployment, monitoring, or new model behavior.

## 1. Required Cleaned Identity Field

| Field | Required | Rule |
|---|---:|---|
| `item_id` | Yes | Primary ABO product/listing identifier. Records without a usable `item_id` must be skipped or rejected. |

`item_id` is the identity boundary for ABO cleaned products. It must not be joined to RetailRocket `itemid`, `visitorid`, or any other non-ABO identifier.

## 2. Optional Metadata Fields

These fields may be present when observed in the raw ABO listing record. Missing values must not be invented.

| Field | Required | Cleaning Target |
|---|---:|---|
| `item_name` | No | Preserve usable title/name text. |
| `brand` | No | Preserve usable brand text. |
| `bullet_point` | No | Preserve usable bullet text, including multiple bullet values where applicable. |
| `product_type` | No | Preserve usable product type text and support normalized evaluation form. |
| `color` | No | Preserve usable color text. |
| `material` | No | Preserve usable material text. |
| `style` | No | Preserve usable style text. |
| `main_image_id` | No | Preserve preferred image identifier for corrected image mapping. |
| `other_image_id` | No | Preserve additional image identifiers where available. |

## 3. Derived Cleaned Fields

| Field | Required | Definition |
|---|---:|---|
| `combined_text` | Yes for text-ready records | Concatenated usable text built only from observed fields: `item_name`, `brand`, `bullet_point`, `product_type`, `color`, `material`, and `style`. |
| `combined_text_length` | Yes | Character length of `combined_text` after cleaning. |
| `normalized_product_type` | No | Normalized product type value for evaluation grouping and proxy relevance checks. |
| `normalized_brand` | No | Normalized brand value for analysis or proxy evaluation where available. |
| `normalized_color` | No | Normalized color value where available. |
| `image_path` | No | Resolved small-image tar path from corrected image mapping. |
| `has_usable_text` | Yes | Boolean indicating `combined_text` is non-empty and usable. |
| `has_usable_image` | Yes | Boolean indicating a validated mapped image path exists. |
| `is_clip_ready` | Yes | Boolean indicating usable `item_id`, usable `combined_text`, and usable mapped image path. |
| `is_evaluation_ready` | Yes | Boolean indicating the record has the fields needed for the current local evaluation protocol. |
| `metadata_field_count` | Yes | Count of optional metadata fields with usable values. |
| `source_dataset` | Yes | Dataset provenance label, expected to identify ABO. |
| `image_mapping_status` | Yes | Status describing image mapping result, such as mapped, missing main image ID, image ID not found, or mapped path missing. |
| `cleaning_status` | Yes | Status describing whether the record was written, skipped, or rejected and why. |

Derived fields should be deterministic and reproducible from the raw ABO listing record plus `images/metadata/images.csv.gz`.

## 4. Readiness Categories

| Category | Definition |
|---|---|
| `catalog_record` | Record has a usable `item_id` and can be represented as an ABO product record, even if it is not text-, image-, or evaluation-ready. |
| `text_ready` | Record has a usable `item_id` and usable `combined_text`. |
| `image_ready` | Record has a usable `item_id` and a validated `image_path` derived through corrected image metadata mapping. |
| `clip_ready` | Record is both text-ready and image-ready. This is equivalent to `is_clip_ready = true`. |
| `evaluation_ready` | Record satisfies the current local evaluation requirements, including fields needed by the approved or proposed ABO proxy evaluation protocol. |

Readiness categories are evidence labels. They must not be used to imply production readiness.

## 5. Cleaning Rules

### Identity

- Skip or reject records with missing, empty, or unusable `item_id`.
- Detect duplicate `item_id` values.
- Preserve one deterministic record or skip duplicates according to the current cleaning implementation.
- Report duplicate counts and handling decisions in the cleaning summary.

### Metadata

- Do not invent missing metadata.
- Preserve optional metadata when observed and usable.
- Missing optional fields may remain null, empty, or omitted according to the cleaned schema.

### Text

- Build `combined_text` only from observed ABO fields:
  - `item_name`
  - `brand`
  - `bullet_point`
  - `product_type`
  - `color`
  - `material`
  - `style`
- Handle multilingual, list, dictionary, and nested text values safely.
- Prefer usable English text where supported by current cleaning logic.
- Fall back to the first valid non-empty value when needed.
- Mark `has_usable_text = false` when `combined_text` is empty or unusable.

### Product Type

- Normalize `product_type` for evaluation through `normalized_product_type`.
- Missing `product_type` should not automatically reject a record if text or image readiness still exists.
- Missing `product_type` must be reported as an evaluation limitation because it affects proxy relevance interpretation.

### Image Mapping

- Map image paths only through:

```text
main_image_id -> images/metadata/images.csv.gz image_id -> path -> images/small/{path}
```

- Do not rely on direct comparison of `main_image_id` to image file stems.
- Do not extract the full image archive during cleaning.
- Mark image failures explicitly in `image_mapping_status`.
- Mark `has_usable_image = false` when no validated mapped image path exists.

### Readiness Flags

- `is_clip_ready` requires usable `item_id`, usable `combined_text`, and usable mapped `image_path`.
- `is_evaluation_ready` must reflect the current local evaluation protocol and should be revised if the evaluation protocol changes.
- Readiness counts must be included in the cleaning summary.

## 6. Data Gate Target

Before FAISS, vector database, vector retrieval, API, MCP, deployment, or monitoring work becomes the main implementation focus, ABO cleaned data must have:

- Cleaning summary evidence.
- Validation evidence.
- Raw input references.
- Output path references.
- Counts for records scanned, records written, skipped records, missing `item_id`, duplicate `item_id`, missing `product_type`, usable text, mapped images, CLIP-ready records, and evaluation-ready records.
- Limitations and Data Gate impact documented in a report.

Until that evidence exists and is reviewed, ABO data readiness remains partial and the project should continue Data Gate Hardening rather than advanced architecture implementation.
