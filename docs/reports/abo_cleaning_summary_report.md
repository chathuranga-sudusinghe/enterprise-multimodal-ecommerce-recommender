# ABO Cleaning Summary Report

## Purpose

This report records actual local ABO cleaning evidence for the Data Gate Hardening milestone. It is based on the latest local cleaning run counts and the cleaning targets defined in:

- `docs/framework/abo_cleaning_rules_contract.md`
- `docs/framework/abo_data_understanding_and_cleaning_decisions.md`
- `docs/reports/abo_cleaning_summary_report_template.md`

This is local Data Gate evidence for the ABO text/image similarity track. It is not production monitoring and does not authorize FAISS, vector databases, API implementation, MCP integration, deployment, monitoring, or production-readiness claims.

## Command Used

```bash
python scripts/clean_abo_products.py --max-records 1000 --output data/processed/abo_clean_products_sample.jsonl
```

The wrapper script calls the core cleaning logic in `src/ecommerce_recommender/data/clean_abo_products.py`.

## Raw Inputs

| Input | Path |
|---|---|
| ABO listings archive | `data/raw/amazon_berkeley_text_images-based/abo-listings.tar` |
| ABO small images archive | `data/raw/amazon_berkeley_text_images-based/abo-images-small.tar` |
| Image metadata member | `images/metadata/images.csv.gz` |

The cleaning rule for images is:

```text
main_image_id -> images/metadata/images.csv.gz image_id -> path -> images/small/{path}
```

Direct comparison of `main_image_id` to image file stems is not sufficient and is not the approved mapping rule.

## Output Artifact

| Artifact | Path |
|---|---|
| Cleaned ABO JSONL sample | `data/processed/abo_clean_products_sample.jsonl` |

The output is a JSON Lines artifact with one cleaned ABO product record per line. Existing downstream fields used by TF-IDF, RGB histogram, CLIP, and proxy evaluation scripts are preserved.

## Cleaning Counts

| Metric | Count |
|---|---:|
| Records scanned | 1000 |
| Records written | 993 |
| Skipped records | 7 |
| Dropped missing `item_id` | 0 |
| Dropped unusable text | 0 |
| Dropped missing required text | 0 |
| Dropped missing image | 7 |
| Duplicate `item_id` dropped | 0 |
| Missing `product_type` | 0 |
| Usable text count | 1000 |
| Mapped image count | 993 |
| CLIP-ready count | 993 |
| Evaluation-ready count | 993 |

## Missing Value Handling

- Missing `item_id`: 0 records were dropped for missing identity.
- Missing or unusable text: 0 records were dropped for unusable combined text.
- Missing `product_type`: 0 written records were missing product type in this run.
- Missing image mapping/path: 7 records were dropped because they were not image-ready under the corrected metadata mapping rule.
- Optional metadata: missing optional values are not invented. They remain empty, null, or omitted according to the cleaned schema.

## Duplicate Handling

- Duplicate detection target: `item_id`.
- Duplicate handling policy: deterministic first valid record wins; later duplicate `item_id` records are dropped.
- Duplicate result for this run: 0 duplicate `item_id` records were dropped.

## Image Mapping Summary

- Mapping source: `images/metadata/images.csv.gz`.
- Mapping key: listing `main_image_id` to image metadata `image_id`.
- Resolved path rule: metadata `path` is converted to `images/small/{path}`.
- Records with mapped, usable image paths: 993.
- Image mapping failures: 7 records were not written because no usable mapped image path was available.
- Full raw image extraction was not performed.

## Readiness Summary

| Readiness Category | Count |
|---|---:|
| Catalog records scanned with usable `item_id` | 1000 |
| Text-ready records | 1000 |
| Image-ready records | 993 |
| CLIP-ready records | 993 |
| Evaluation-ready records | 993 |

For this run:

- `is_clip_ready` means usable `item_id`, usable `combined_text`, and usable mapped `image_path`.
- `is_evaluation_ready` means `is_clip_ready` plus usable `normalized_product_type` for the current local proxy evaluation.

## Data Gate Impact

This report strengthens ABO Data Gate evidence by documenting the actual cleaning run counts, skipped-record reasons, image mapping rule, readiness counts, and output artifact path.

Current decision from this report:

- PARTIAL GO for continued Data Gate hardening and local validation evidence.
- NO-GO for treating ABO data readiness as sufficient to begin FAISS, vector database, API, MCP, deployment, monitoring, or production-readiness work.

Additional validation evidence is still required before broader Data Gate approval, including schema validation, source checksum/version evidence, processed artifact reproducibility evidence, and evaluation protocol hardening.

## Limitations

- This report covers a bounded local cleaning run of 1000 ABO listing records.
- It does not prove full-dataset data quality.
- It does not include raw archive checksums or source version evidence.
- It does not replace processed-data validation reports.
- It does not evaluate recommendation quality.
- It does not establish production monitoring, production readiness, API readiness, MCP readiness, deployment readiness, or vector-search readiness.
