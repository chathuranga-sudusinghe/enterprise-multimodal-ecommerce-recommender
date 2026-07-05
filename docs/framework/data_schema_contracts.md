# Data Schema Contracts

## Purpose

This document records the current expected schemas for raw and processed artifacts used by the project. It should reflect discovered evidence and current artifacts only. It must not invent unsupported business fields or imply cross-dataset identity links.

Optional fields are marked explicitly.

## RetailRocket Raw Events

Expected source:

- `data/raw/RetailRocket_event-based/events.csv`

Expected fields:

| Field | Required | Notes |
|---|---:|---|
| `timestamp` | Yes | Event timestamp from the raw RetailRocket event log. |
| `visitorid` | Yes | RetailRocket visitor identifier. Must not be joined to ABO identifiers. |
| `event` | Yes | Known values include `view`, `addtocart`, and `transaction`. |
| `itemid` | Yes | RetailRocket item identifier. Must not be joined to ABO `item_id` or image identifiers. |
| `transactionid` | Optional | Present for transaction-related records where available. |

## RetailRocket Raw Item Properties

Expected sources:

- `data/raw/RetailRocket_event-based/item_properties_part1.csv`
- `data/raw/RetailRocket_event-based/item_properties_part2.csv`

Expected fields:

| Field | Required | Notes |
|---|---:|---|
| `timestamp` | Yes | Property observation timestamp. |
| `itemid` | Yes | RetailRocket item identifier. |
| `property` | Yes | Item property name from the raw dataset. |
| `value` | Yes | Item property value from the raw dataset. |

## RetailRocket Category Tree

Expected source:

- `data/raw/RetailRocket_event-based/category_tree.csv`

Expected fields:

| Field | Required | Notes |
|---|---:|---|
| `categoryid` | Yes | RetailRocket category identifier. |
| `parentid` | Optional | Parent category identifier. Missing values can represent root categories. |

## ABO Cleaned Product JSONL

Expected role:

- Cleaned product metadata artifact for ABO text and image similarity work.

Expected fields:

| Field | Required | Notes |
|---|---:|---|
| `item_id` | Yes | ABO product/listing identifier. Must not be joined to RetailRocket `itemid`. |
| `item_name` | Optional | Product name/title where available. |
| `brand` | Optional | Product brand where available. |
| `bullet_point` | Optional | Product bullet text where available. |
| `product_type` | Optional | Product type/category metadata. Missing values should be tracked. |
| `color` | Optional | Product color metadata where available. |
| `material` | Optional | Product material metadata where available. |
| `style` | Optional | Product style metadata where available. |
| `main_image_id` | Optional | Primary ABO image identifier where available. |
| `other_image_id` | Optional | Additional ABO image identifier or identifiers where available. |
| `combined_text` | Yes for written records | Cleaned text built only from observed ABO text fields. |
| `combined_text_length` | Yes for written records | Character length of `combined_text`. |
| `normalized_product_type` | Optional | Normalized product type for evaluation grouping. |
| `normalized_brand` | Optional | Normalized brand value where available. |
| `normalized_color` | Optional | Normalized color value where available. |
| `image_path` | Yes for written CLIP-ready records | Resolved `images/small/{path}` member from corrected image metadata mapping. |
| `has_usable_text` | Yes | Boolean readiness flag for usable `combined_text`. |
| `has_usable_image` | Yes | Boolean readiness flag for validated mapped image path. |
| `is_clip_ready` | Yes | Boolean requiring usable `item_id`, `combined_text`, and mapped image path. |
| `is_evaluation_ready` | Yes | Boolean readiness flag for the current local proxy evaluation requirements. |
| `metadata_field_count` | Yes | Count of optional metadata fields with usable values. |
| `source_dataset` | Yes | ABO provenance label. |
| `image_mapping_status` | Yes | Image mapping status such as `mapped`, `missing_main_image_id`, `image_id_not_found`, `invalid_mapped_path`, or `mapped_path_missing`. |
| `cleaning_status` | Yes | Cleaning disposition for written records. |

JSONL contract:

- One JSON object per line.
- Each line must parse as valid JSON.
- No line may contain a RetailRocket identifier mapped as an ABO identity.

## ABO TF-IDF Output JSON

Expected role:

- Local ABO text similarity baseline output.

Expected fields:

| Field | Required | Notes |
|---|---:|---|
| `query_item_id` | Yes | ABO item used as the query product, if represented per query. |
| `recommendations` | Yes | Similar ABO products for the query item. |

Expected recommendation object fields:

| Field | Required | Notes |
|---|---:|---|
| `item_id` | Yes | Recommended ABO item identifier. |
| `score` | Optional | Similarity score if emitted by the artifact. |
| `rank` | Optional | Rank if emitted by the artifact. |

If the existing artifact uses a different top-level shape, the exact shape should be documented before this contract is promoted from expected to enforced.

## ABO RGB Histogram Output JSON

Expected role:

- Local ABO image similarity baseline output using RGB histogram features.

Expected fields:

| Field | Required | Notes |
|---|---:|---|
| `query_item_id` | Optional | ABO item used as the query product if represented. |
| `query_image_id` | Optional | ABO image used as the query image if represented. |
| `recommendations` | Yes | Similar ABO products or images for the query. |

Expected recommendation object fields:

| Field | Required | Notes |
|---|---:|---|
| `item_id` | Optional | ABO product identifier if available. |
| `image_id` | Optional | ABO image identifier if available. |
| `score` | Optional | Similarity score if emitted by the artifact. |
| `rank` | Optional | Rank if emitted by the artifact. |

At least one product or image identifier should be present for each recommendation.

## ABO CLIP Output JSON

Expected role:

- Local ABO image/text-image similarity output using CLIP-derived features or scores where already produced.

Expected fields:

| Field | Required | Notes |
|---|---:|---|
| `query_item_id` | Optional | ABO query product identifier if represented. |
| `query_image_id` | Optional | ABO query image identifier if represented. |
| `recommendations` | Yes | Similar ABO products or images for the query. |

Expected recommendation object fields:

| Field | Required | Notes |
|---|---:|---|
| `item_id` | Optional | ABO product identifier if available. |
| `image_id` | Optional | ABO image identifier if available. |
| `score` | Optional | Similarity score if emitted by the artifact. |
| `rank` | Optional | Rank if emitted by the artifact. |

At least one product or image identifier should be present for each recommendation. CLIP readiness also depends on valid image paths or resolvable image identifiers.

## RetailRocket Baseline Evaluation JSON

Expected role:

- Local evaluation evidence for the RetailRocket behavior baseline.

Expected fields:

| Field | Required | Notes |
|---|---:|---|
| `dataset` | Optional | Should identify RetailRocket if present. |
| `track` | Optional | Should identify behavior recommendation if present. |
| `method` | Optional | Baseline method name if present. |
| `metrics` | Yes | Evaluation metric object. |
| `parameters` | Optional | Baseline settings if emitted. |
| `generated_at` | Optional | Run timestamp if emitted. |

Metric keys should match the approved RetailRocket evaluation protocol. Until the protocol is fully approved, metric names should be treated as local evidence rather than enterprise gate evidence.

## ABO Proxy Evaluation JSON

Expected role:

- Local proxy evaluation evidence for ABO text/image similarity baselines.

Expected fields:

| Field | Required | Notes |
|---|---:|---|
| `dataset` | Optional | Should identify ABO if present. |
| `track` | Optional | Should identify text similarity, image similarity, or multimodal similarity if present. |
| `method` | Optional | Baseline method name if present. |
| `metrics` | Yes | Proxy evaluation metric object. |
| `parameters` | Optional | Baseline settings if emitted. |
| `generated_at` | Optional | Run timestamp if emitted. |

Metric keys should match the approved ABO evaluation protocol. Proxy evaluation must not be described as production evidence unless the protocol has been approved.

## Contract Guardrails

- RetailRocket and ABO identifiers are not interchangeable.
- Processed artifacts must preserve dataset provenance.
- Missing optional fields should be measured and reported when they affect recommendation readiness.
- These contracts are documentation targets until validation code or manual gate evidence enforces them.
