# Data Quality Validation Report

## Purpose

This report records the first lightweight local validation evidence for the Data Gate Hardening milestone. It validates processed artifacts if they exist and does not modify raw data or processed artifacts.

This is local validation evidence, not production monitoring.

## Run Context

- Generated at UTC: `2026-07-04T15:38:50Z`
- Processed directory: `data/processed`
- Validator: `scripts/validate_processed_data.py`

## Pass/Warn/Fail Summary

| Status | Count |
|---|---:|
| PASS | 7 |
| WARN | 0 |
| FAIL | 0 |
| MISSING | 0 |

## Files Checked

| File | Type | Status | Summary |
|---|---|---|---|
| `data/processed/abo_clean_products_5k.jsonl` | ABO cleaned JSONL | PASS | Validated 4971 cleaned ABO product records. |
| `data/processed/abo_clean_products_sample.jsonl` | ABO cleaned JSONL | PASS | Validated 992 cleaned ABO product records. |
| `data/processed/abo_tfidf_similarity_5k_sample.json` | ABO similarity JSON | PASS | Validated 5 similarity recommendations. |
| `data/processed/abo_image_similarity_5k_sample.json` | ABO similarity JSON | PASS | Validated 5 similarity recommendations. |
| `data/processed/abo_clip_similarity_5k_sample.json` | ABO similarity JSON | PASS | Validated 5 similarity recommendations. |
| `data/processed/abo_similarity_proxy_evaluation.json` | Evaluation JSON | PASS | Evaluation JSON parsed successfully. |
| `data/processed/retailrocket_baseline_evaluation.json` | Evaluation JSON | PASS | Evaluation JSON parsed successfully. |

## Missing Files

- None.

## Schema Issues

- `data/processed/abo_tfidf_similarity_5k_sample.json` (PASS):
  - Query field present: query_item_id.
- `data/processed/abo_image_similarity_5k_sample.json` (PASS):
  - Query field present: query_item_id.
- `data/processed/abo_clip_similarity_5k_sample.json` (PASS):
  - Query field present: query_item_id.
- `data/processed/abo_similarity_proxy_evaluation.json` (PASS):
  - Top-level keys available: assumptions, dataset_track, evaluated_methods, evaluation_name, evaluation_scope, evaluation_type, generated_at_utc, limitations, metrics_by_method, products_file.
  - Nested `metrics_by_method` field is present.
- `data/processed/retailrocket_baseline_evaluation.json` (PASS):
  - Top-level keys available: baseline, evaluated_visitor_count, hit_rate_at_10, recall_at_10, recommended_itemids, split_timestamp, test_event_count, top_k, train_event_count, train_ratio.
  - Metric-like fields present: hit_rate_at_10, recall_at_10.

## Duplicate Issues

- None detected.

## Missing Value Counts

- None detected.

## Data Gate Impact

- Data Gate impact: all existing checked processed artifacts passed this lightweight validation. Missing optional local artifacts, if any, still need review before broader Data Gate approval.
- This report supports documentation and data contract hardening only.
- This report does not authorize FAISS, vector DB, API, MCP, deployment, monitoring, or production-readiness claims.
