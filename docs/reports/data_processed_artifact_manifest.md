# Data and Processed Artifact Manifest

## Purpose

This manifest records the expected raw data inputs and the local generated artifacts used by the current Data, Baseline, and partial Evaluation checkpoint. It supports the Framework v2.1 Data and Evaluation Evidence Hardening milestone by making artifact provenance, regeneration commands, and limitations explicit.

This is a local reproducibility manifest, not a production data catalog or deployment inventory.

## Ownership

| Role | Owner |
| --- | --- |
| Project owner | Chathuranga Sudusinghe |
| Maintenance owner | Chathuranga Sudusinghe / Project Maintainer |

## Repository Data Rules

- RetailRocket and Amazon Berkeley Objects (ABO) are independent dataset tracks.
- RetailRocket `visitorid` and `itemid` values must not be joined to ABO `item_id`, `main_image_id`, `other_image_id`, or `image_id` values.
- Raw datasets remain local under `data/raw/` and are ignored by Git.
- Generated outputs remain local under `data/processed/` and are ignored by Git unless a future review explicitly approves a small evidence artifact.
- `data/sample/` contains tiny deterministic fixtures for tests and examples only.

## Raw Dataset Expectations

| Track | Expected path | Expected files | Committed status | Field expectations | Notes |
| --- | --- | --- | --- | --- | --- |
| RetailRocket behavior events | `data/raw/RetailRocket_event-based/` | `events.csv`, `item_properties_part1.csv`, `item_properties_part2.csv`, `category_tree.csv` | Ignored by Git | Events: `timestamp`, `visitorid`, `event`, `itemid`, `transactionid`; observed events include `view`, `addtocart`, `transaction`. Item properties: `timestamp`, `itemid`, `property`, `value`. Category tree: `categoryid`, `parentid`. | Use header-only, streaming, or chunked reads for large CSV files. |
| ABO product metadata and images | `data/raw/amazon_berkeley_text_images-based/` | `abo-listings.tar`, `abo-images-small.tar`, `README.md` | Ignored by Git | Listings include fields such as `item_id`, `item_name`, `brand`, `bullet_point`, `product_type`, `color`, `material`, `style`, `main_image_id`, `other_image_id`. Image metadata includes `image_id`, `path`, `height`, `width`. | Use bounded tar inspection and controlled extraction only. Do not extract all images for routine work. |

## Generated Processed Artifacts

| Artifact | Track | Purpose | Default or observed path | Committed status | Generation command | Key schema or fields | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RetailRocket baseline top items | RetailRocket | Ranked global event-weighted item popularity output | `data/processed/retailrocket_baseline_top_items.csv` | Ignored by Git | `python scripts/run_retailrocket_baseline.py` | Expected columns include ranked `itemid` and `popularity_score`. | Global non-personalized baseline; depends on local raw `events.csv`. |
| RetailRocket baseline evaluation | RetailRocket | Temporal offline evaluation for the global popularity baseline | `data/processed/retailrocket_baseline_evaluation.json` | Ignored by Git | `python scripts/evaluate_retailrocket_baseline.py` | `baseline`, `split_timestamp`, `train_ratio`, `top_k`, `train_event_count`, `test_event_count`, `evaluated_visitor_count`, `recommended_itemids`, `hit_rate_at_10`, `recall_at_10`. | Local generated evidence only; not an online or production quality claim. |
| ABO cleaned sample | ABO | Bounded cleaned product JSONL sample | `data/processed/abo_clean_products_sample.jsonl` | Ignored by Git | `python scripts/clean_abo_products.py --max-records 1000` | Cleaned product records include `item_id`, `item_name`, `brand`, `bullet_point`, `product_type`, `color`, `material`, `style`, `main_image_id`, `image_path`, `combined_text`, `has_usable_text`, `has_usable_image`, `is_clip_ready`. | Requires local ABO raw archives; bounded sample only. |
| ABO cleaned 5k product table | ABO | Bounded cleaned product table used by the current similarity comparison | `data/processed/abo_clean_products_5k.jsonl` | Ignored by Git | `python scripts/clean_abo_products.py --max-records 5000 --output data/processed/abo_clean_products_5k.jsonl` | Same cleaned product fields as the sample output; README records 4,971 CLIP-ready records from a 5,000-listing run. | Local sample ordering and availability may differ if raw data or cleaning rules change. |
| ABO TF-IDF similarity output | ABO | Text-only product-to-product similarity output | `data/processed/abo_tfidf_similarity_5k_sample.json` | Ignored by Git | `python scripts/run_abo_text_baseline.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5` | `method_name`, `dataset_track`, `input_file`, `products_loaded`, `query_item_id`, `source_product_metadata`, `recommendations`, `top_k`, `assumptions`, `limitations`. | One bounded query in current evidence; text-only and non-personalized. |
| ABO RGB histogram similarity output | ABO | Image-only color histogram product similarity output | `data/processed/abo_image_similarity_5k_sample.json` | Ignored by Git | `python scripts/run_abo_image_similarity.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5` | `method_name`, `input_file`, `products_loaded`, `query_item_id`, `query_product`, `recommendations`, `top_k`. | Coarse image baseline; color histograms do not capture product semantics. |
| ABO CLIP similarity output | ABO | CLIP text-image product similarity output | `data/processed/abo_clip_similarity_5k_sample.json` | Ignored by Git | `python scripts/run_abo_clip_similarity.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5 --local-files-only` | `method_name`, `model_name`, `input_file`, `products_loaded`, `query_item_id`, `query_product`, `recommendations`, `top_k`. | Requires PyTorch, Transformers, Pillow, and local model cache when `--local-files-only` is used. Current evidence is one query only. |
| ABO proxy evaluation output | ABO | Metadata-proxy comparison across TF-IDF, RGB histogram, and CLIP outputs | `data/processed/abo_similarity_proxy_evaluation.json` | Ignored by Git | `python scripts/evaluate_abo_similarity_methods.py --products data/processed/abo_clean_products_5k.jsonl --tfidf data/processed/abo_tfidf_similarity_5k_sample.json --image data/processed/abo_image_similarity_5k_sample.json --clip data/processed/abo_clip_similarity_5k_sample.json --output data/processed/abo_similarity_proxy_evaluation.json` | `evaluation_name`, `evaluation_type`, `dataset_track`, `evaluated_methods`, `products_file`, `metrics_by_method`, `assumptions`, `limitations`. | Product-type equality is proxy relevance, not click, purchase, or satisfaction relevance. Current evidence covers one bounded query. |
| ABO agentic demo output | ABO | Local deterministic orchestration demo over fixed similarity results | `data/processed/abo_agentic_recommendation_demo.json` | Ignored by Git | `python scripts/run_abo_agentic_recommendation_demo.py` | `orchestrator_name`, `dataset_track`, `method_name`, `query_item_id`, `query_product`, `selected_recommendations`, `rejected_recommendations`, `policy_checks_summary`, `explanation_mode`, `assumptions`, `limitations`. | Demo only; not a production agent system, not a full MCP server/client, and not a model-quality validation. |

## Regeneration Order

1. Place RetailRocket raw files under `data/raw/RetailRocket_event-based/`.
2. Generate RetailRocket top items:

```bash
python scripts/run_retailrocket_baseline.py
```

3. Generate RetailRocket evaluation:

```bash
python scripts/evaluate_retailrocket_baseline.py
```

4. Place ABO raw archives and README under `data/raw/amazon_berkeley_text_images-based/`.
5. Generate the bounded ABO cleaned table:

```bash
python scripts/clean_abo_products.py --max-records 5000 --output data/processed/abo_clean_products_5k.jsonl
```

6. Generate ABO similarity outputs:

```bash
python scripts/run_abo_text_baseline.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5
python scripts/run_abo_image_similarity.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5
python scripts/run_abo_clip_similarity.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5 --local-files-only
```

7. Generate the ABO proxy evaluation:

```bash
python scripts/evaluate_abo_similarity_methods.py --products data/processed/abo_clean_products_5k.jsonl --tfidf data/processed/abo_tfidf_similarity_5k_sample.json --image data/processed/abo_image_similarity_5k_sample.json --clip data/processed/abo_clip_similarity_5k_sample.json --output data/processed/abo_similarity_proxy_evaluation.json
```

8. Optionally generate the local orchestration demo:

```bash
python scripts/run_abo_agentic_recommendation_demo.py
```

## Known Limitations

- This manifest does not verify raw data checksums or source download versions.
- Local processed artifacts are reproducible outputs, not immutable benchmark releases.
- ABO proxy evaluation currently uses product metadata as a relevance proxy because ABO does not provide user behavior labels.
- Current ABO evidence is a bounded one-query comparison and should not be used to claim general model superiority.
- RetailRocket baseline evaluation is global and non-personalized.
- CLIP workflows may require substantial install time, memory, and a local Hugging Face model cache.
- The basic GitHub Actions workflow is a quality gate only; it is not deployment or production operation.

## Next Manifest Improvements

- Add source download URLs and license references where publication permits.
- Add raw and processed artifact checksums when a stable local snapshot is approved.
- Add artifact generation timestamps and runtime environment details to reviewed reports.
- Extend ABO evaluation artifacts after a representative multi-query proxy protocol is approved.
