# ABO Cleaning Summary Report Template

## Purpose

This template defines the required fields for a future actual ABO cleaning summary report. It should be filled by a reproducible cleaning run, not by notebook-only exploration.

## Run Metadata

| Field | Value |
|---|---|
| Command | `TODO` |
| Generated at UTC | `TODO` |
| Code version or commit | `TODO` |
| Operator or environment | `TODO` |

## Inputs and Output

| Field | Value |
|---|---|
| Raw listings input | `TODO` |
| Raw images input | `TODO` |
| Image metadata member | `images/metadata/images.csv.gz` |
| Output path | `TODO` |

## Cleaning Counts

| Metric | Count |
|---|---:|
| Records scanned | `TODO` |
| Records written | `TODO` |
| Skipped records | `TODO` |
| Missing `item_id` | `TODO` |
| Duplicate `item_id` | `TODO` |
| Missing `product_type` | `TODO` |
| Usable text count | `TODO` |
| Mapped image count | `TODO` |
| CLIP-ready count | `TODO` |
| Evaluation-ready count | `TODO` |

## Duplicate Handling

- Duplicate detection method: `TODO`
- Duplicate handling policy used: `TODO`
- Duplicate examples or sample IDs, if safe and useful: `TODO`

## Missing Value Summary

- Missing identity handling: `TODO`
- Missing text handling: `TODO`
- Missing product type handling: `TODO`
- Missing image mapping handling: `TODO`
- Optional metadata handling: `TODO`

## Image Mapping Summary

- Mapping rule: `main_image_id -> images/metadata/images.csv.gz image_id -> path -> images/small/{path}`
- Image IDs found in metadata: `TODO`
- Resolved paths found in image archive: `TODO`
- Image mapping failures by reason: `TODO`

## Readiness Summary

- Catalog records: `TODO`
- Text-ready records: `TODO`
- Image-ready records: `TODO`
- CLIP-ready records: `TODO`
- Evaluation-ready records: `TODO`

## Limitations

- `TODO`

## Data Gate Impact

State whether this cleaning run supports Data Gate hardening and what remains before Data Gate can be marked GO.

Current decision from this report:

- `TODO: GO / PARTIAL / NO-GO`

This report must not be used to claim production monitoring, production readiness, API readiness, MCP readiness, deployment readiness, or vector-search readiness by itself.
