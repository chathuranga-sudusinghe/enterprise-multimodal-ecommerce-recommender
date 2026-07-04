# Data Quality Validation Plan

## Purpose

This plan defines the validation checks needed before the Data Gate can be marked GO. It is a plan only. It does not implement validation code.

## Validation Scope

Validation must cover:

- RetailRocket raw files.
- ABO raw archives and metadata.
- ABO cleaned product JSONL.
- ABO text and image similarity outputs.
- RetailRocket and ABO evaluation output JSON.
- Repository-level controls that prevent raw data commits and cross-dataset joins.

## Required Validation Checks

| Check | Track | Target | Purpose |
|---|---|---|---|
| Required raw file presence | RetailRocket | `events.csv`, `item_properties_part1.csv`, `item_properties_part2.csv`, `category_tree.csv` | Confirm the behavior track has required local raw inputs. |
| Required raw file presence | ABO | `abo-listings.tar`, `abo-images-small.tar`, `README.md` | Confirm the text/image track has required local raw inputs. |
| Required fields | RetailRocket | Raw CSV headers | Confirm fields match the documented raw contracts without loading full files into memory. |
| Required fields | ABO | Cleaned JSONL and output JSON | Confirm required product and recommendation fields exist where expected. |
| Duplicate IDs | ABO | Cleaned product JSONL | Detect duplicate `item_id` values that could corrupt similarity evaluation. |
| Duplicate event records | RetailRocket | Raw or sampled event checks | Detect exact duplicate behavior records where feasible with memory-safe methods. |
| Missing `item_id` | ABO | Cleaned product JSONL and output JSON | Ensure product identity is present where required. |
| Missing `product_type` | ABO | Cleaned product JSONL | Measure product type coverage and decide whether missing values are acceptable for evaluation. |
| Missing `image_path` or image readiness | ABO | Image-derived artifacts | Confirm image similarity work can trace records to usable images or image identifiers. |
| CLIP readiness | ABO | CLIP output JSON and source image references | Confirm CLIP-derived outputs are traceable to valid image inputs before promotion. |
| Invalid JSONL | ABO | Cleaned product JSONL | Ensure every line parses as one JSON object. |
| Malformed output JSON | RetailRocket and ABO | Evaluation and similarity JSON artifacts | Ensure files parse and contain required top-level structures. |
| Raw data not committed | Repository | Git status and ignore rules | Confirm raw datasets under `data/raw/` remain untracked and ignored. |
| Processed artifact reproducibility | Both | Processed outputs and evaluation outputs | Confirm generation command, source inputs, code version, and run metadata are documented. |
| No cross-dataset joins | Both | Code, docs, and artifacts | Confirm RetailRocket and ABO identifiers are never treated as shared identities. |

## Memory-Safety Requirements

RetailRocket validation must avoid full-file loading for large CSVs. Allowed approaches include:

- Header-only reads.
- Streaming line counts.
- Chunked reads.
- Bounded samples.

ABO archive validation must avoid extracting all images during gate review. Allowed approaches include:

- Bounded tar inspection.
- Controlled extraction of explicitly selected small samples.
- Metadata-only checks where sufficient.

## Data Gate GO Requirements

Before marking the Data Gate GO, the project should have evidence for:

- Required raw inputs are present.
- Raw schemas match documented contracts.
- Processed schemas match documented contracts.
- Missing values are measured and accepted or remediated.
- Duplicate identifier risk is measured.
- JSONL and JSON artifacts parse successfully.
- Processed and evaluation artifacts can be reproduced.
- Raw data remains uncommitted.
- No cross-dataset joins exist.
- Source version and checksum or equivalent integrity evidence is recorded.

## Current Status

This plan is not yet implemented as validation code. Until the checks are implemented or manually evidenced, the Data Gate remains Partial and the decision remains NO-GO for retrieval/vector/API as the main work.
