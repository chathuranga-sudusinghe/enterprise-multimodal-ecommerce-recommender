# Data Design

## 1. Purpose

This document defines the real-data design direction for the Enterprise Multimodal E-Commerce Recommendation AI System. It records discovered source schemas, proposes canonical contracts for later approval, and separates raw datasets from tiny deterministic fixtures.

## 2. Raw Data Folder Layout

```text
data/
├── raw/
│   ├── RetailRocket_event-based/
│   │   ├── events.csv
│   │   ├── item_properties_part1.csv
│   │   ├── item_properties_part2.csv
│   │   └── category_tree.csv
│   └── amazon_berkeley_text_images-based/
│       ├── abo-listings.tar
│       ├── abo-images-small.tar
│       └── README.md
├── interim/
├── processed/
└── sample/
```

Raw data is local-only and must remain excluded from Git.

## 3. RetailRocket Discovered Schema

### 3.1 Events

| Column | Meaning | Notes |
| --- | --- | --- |
| `timestamp` | Event time | Raw Unix milliseconds |
| `visitorid` | Dataset-specific visitor identifier | RetailRocket only |
| `event` | Observed interaction type | `view`, `addtocart`, or `transaction` |
| `itemid` | Dataset-specific item identifier | RetailRocket only |
| `transactionid` | Transaction reference where available | Nullable |

### 3.2 Item Properties

Both item-property files use:

| Column | Meaning |
| --- | --- |
| `timestamp` | Property observation time in raw Unix milliseconds |
| `itemid` | RetailRocket item identifier |
| `property` | Property key |
| `value` | Property value |

Properties are timestamped key-value rows. Canonicalization requires deliberate rules rather than blind pivoting.

### 3.3 Category Tree

| Column | Meaning |
| --- | --- |
| `categoryid` | Category identifier |
| `parentid` | Parent category identifier, nullable for roots |

## 4. Amazon ABO Discovered Schema

### 4.1 Listing Metadata

ABO listing records expose optional multilingual and structured fields including:

| Field | Intended Use Direction |
| --- | --- |
| `item_id` | ABO listing identifier |
| `item_name` | Product-title text |
| `brand` | Product metadata |
| `bullet_point` | Descriptive text |
| `product_type` | Product-type consistency and filtering |
| `color` | Optional descriptive metadata |
| `material` | Optional descriptive metadata |
| `style` | Optional descriptive metadata |
| `main_image_id` | Primary ABO image mapping |
| `other_image_id` | Additional ABO image mappings |

Field availability varies by listing and locale. Future adapters must define optional-field handling explicitly.

### 4.2 Image Metadata

| Field | Meaning |
| --- | --- |
| `image_id` | ABO image identifier |
| `path` | Archive-relative image path |
| `height` | Image height |
| `width` | Image width |

## 5. Canonical Interaction Schema Direction

A future RetailRocket adapter may expose a canonical interaction schema such as:

| Canonical Field | RetailRocket Source | Notes |
| --- | --- | --- |
| `event_timestamp_ms` | `timestamp` | Preserve source unit explicitly |
| `visitor_id` | `visitorid` | Track-local identifier only |
| `item_id` | `itemid` | Track-local identifier only |
| `event_type` | `event` | Preserve observed values |
| `transaction_id` | `transactionid` | Nullable |
| `source_dataset` | Constant metadata | Record RetailRocket provenance |

This is a design direction for approval, not an implemented adapter contract.

## 6. Canonical Product Schema Direction

A future ABO adapter may expose a canonical product schema such as:

| Canonical Field | ABO Source | Notes |
| --- | --- | --- |
| `item_id` | `item_id` | ABO-local identifier only |
| `item_name` | `item_name` | May require locale-aware handling |
| `brand` | `brand` | Optional |
| `bullet_point` | `bullet_point` | Optional descriptive text |
| `product_type` | `product_type` | Optional product metadata |
| `color` | `color` | Optional |
| `material` | `material` | Optional |
| `style` | `style` | Optional |
| `main_image_id` | `main_image_id` | Optional ABO-local image mapping |
| `other_image_ids` | `other_image_id` | Optional collection |
| `source_dataset` | Constant metadata | Record ABO provenance |

This design does not imply any connection to RetailRocket `itemid` values.

## 7. Processed Data Direction

Future processed artifacts should be small, reproducible, provenance-aware, and stored separately from raw files. Likely categories include:

- RetailRocket canonical interaction partitions.
- RetailRocket approved temporal split metadata.
- ABO normalized listing records.
- ABO controlled product-to-image mappings.
- Future track-specific features or embeddings after approval.

Processed artifacts should not be committed unless they are intentionally small, safe, and reviewable.

## 8. Sample Fixture Role

`data/sample/` is reserved for tiny deterministic fixtures used by tests, examples, and CI. It is not the primary ML dataset.

Future fixture structure should be defined conceptually as:

```text
data/sample/
├── retailrocket/
└── amazon_berkeley_objects/
```

Fixture files should mirror approved canonical or discovered schemas. The old unified synthetic `products.csv`, `users.csv`, and `events.csv` contract is deprecated. Fixture files are not created in this documentation task.

## 9. Validation Expectations

RetailRocket validation should cover:

- Required columns.
- Known observed event values.
- Timestamp parsing and ordering assumptions.
- Nullable `transactionid` behavior.
- Chunk-safe ingestion.

ABO validation should cover:

- Required identifier fields.
- Optional metadata handling.
- Product-to-image mapping integrity.
- Archive member safety.
- Controlled extraction boundaries.

## 10. No Cross-Dataset ID Join Rule

RetailRocket `visitorid` and `itemid` values must never be joined to ABO `item_id`, `main_image_id`, `other_image_id`, or `image_id` values. The datasets do not represent a shared company, catalog, or identity system.

## 11. Privacy, Provenance, and Attribution

- Keep raw datasets out of Git.
- Do not log raw identifiers unnecessarily.
- Preserve dataset provenance in processed artifacts and reports.
- Preserve ABO license and attribution information in future public-facing documentation.
- Do not infer sensitive customer attributes from RetailRocket visitors.
- Document limitations when presenting results.

## 12. Future Data Extensions

Possible later extensions include track-specific feature stores, controlled image preprocessing, vector indexes, and experiment snapshots. Any extension must preserve track separation, bounded processing, and reproducibility.

## 13. Data Design Acceptance Criteria

This data design is accepted when:

1. Discovered source schemas are recorded accurately.
2. Proposed canonical fields are clearly marked as future contracts.
3. Fixture-only `data/sample/` usage is explicit.
4. Raw-data memory safety and archive safety are documented.
5. Cross-dataset joins are prohibited.
6. Provenance, privacy, and ABO attribution requirements are visible.
