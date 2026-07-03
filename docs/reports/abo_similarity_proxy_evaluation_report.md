# ABO Similarity Proxy Evaluation Report

## Summary

The current ABO proxy evaluation is **preliminary**. It compares TF-IDF text similarity, RGB histogram image similarity, and CLIP text-image similarity on one bounded query using product-type equality as binary proxy relevance.

Under this one-query bounded proxy sample, CLIP has the highest Product Type Match@5, Proxy Precision@5, and Proxy NDCG@5. This does not prove that CLIP is generally better, production-ready, or better for real user satisfaction.

## Dataset Track

| Item | Value |
| --- | --- |
| Dataset track | Amazon Berkeley Objects text/image similarity |
| Raw folder | `data/raw/amazon_berkeley_text_images-based/` |
| Cleaned input | `data/processed/abo_clean_products_5k.jsonl` |
| Evaluation artifact | `data/processed/abo_similarity_proxy_evaluation.json` |
| Artifact status | Local generated output; ignored by Git |

ABO is independent from RetailRocket. ABO `item_id` and image identifiers must not be joined to RetailRocket `visitorid` or `itemid` values.

## Why Proxy Evaluation Is Used

ABO does not provide user behavior labels, clicks, carts, purchases, conversions, or explicit relevance judgments in this project scope. The current evaluation therefore uses product metadata as a proxy for similarity quality.

Primary proxy relevance:

```text
recommended.product_type == query.product_type
```

This is a metadata consistency check, not a real recommendation relevance label.

## Compared Methods

| Method | Implementation | Output artifact |
| --- | --- | --- |
| TF-IDF text similarity | `src/ecommerce_recommender/models/abo_text_similarity.py` | `data/processed/abo_tfidf_similarity_5k_sample.json` |
| RGB histogram image similarity | `src/ecommerce_recommender/models/abo_image_similarity.py` | `data/processed/abo_image_similarity_5k_sample.json` |
| CLIP text-image similarity | `src/ecommerce_recommender/models/abo_clip_similarity.py` | `data/processed/abo_clip_similarity_5k_sample.json` |

## Current Query and Candidate Scope

Source: `data/processed/abo_similarity_proxy_evaluation.json`.

| Field | Value |
| --- | --- |
| Query item | `B07NQ437BB` |
| Products loaded per method | 100 |
| Top K | 5 |
| Product file | `data/processed/abo_clean_products_5k.jsonl` |
| Generated timestamp | `2026-06-11T13:48:12Z` |

This is one bounded query. It should be treated as a smoke-test-level comparison, not a representative benchmark.

## Current Metrics

| Method | Product Type Match@5 | Proxy Precision@5 | Proxy Average Precision@5 | Proxy NDCG@5 | Brand Match@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| CLIP | 0.80 | 0.80 | 0.6792 | 0.7606 | 0.40 |
| TF-IDF | 0.60 | 0.60 | 0.5889 | 0.7123 | 0.60 |
| RGB Histogram | 0.00 | 0.00 | 0.0000 | 0.0000 | 0.20 |

All three methods evaluated five known recommendations with zero missing recommendation records in the current artifact.

## Interpretation

The current result shows that CLIP performed best under the present bounded one-query proxy setup. TF-IDF also retrieved several same-product-type items. RGB histogram retrieved visually scored items but did not match the query product type under the proxy metric.

These results are consistent with the method designs:

- TF-IDF uses metadata text and may capture product terminology.
- RGB histogram captures coarse color distribution and can miss semantic product similarity.
- CLIP uses text and image features and may better align some visually/textually similar products.

This interpretation is limited to the current query and candidate sample.

## Run Commands

Generate the cleaned input:

```bash
python scripts/clean_abo_products.py --max-records 5000 --output data/processed/abo_clean_products_5k.jsonl
```

Generate method outputs:

```bash
python scripts/run_abo_text_baseline.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5
python scripts/run_abo_image_similarity.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5
python scripts/run_abo_clip_similarity.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5 --local-files-only
```

Generate proxy evaluation:

```bash
python scripts/evaluate_abo_similarity_methods.py --products data/processed/abo_clean_products_5k.jsonl --tfidf data/processed/abo_tfidf_similarity_5k_sample.json --image data/processed/abo_image_similarity_5k_sample.json --clip data/processed/abo_clip_similarity_5k_sample.json --output data/processed/abo_similarity_proxy_evaluation.json
```

## Limitations

- The evidence covers one query only.
- Product-type equality is a proxy and may not match user intent, substitute relationships, complements, or visual relevance.
- No human judgment labels are used.
- No online clicks, conversions, purchases, or satisfaction labels are used.
- CLIP may require PyTorch, Transformers, Pillow, and a local Hugging Face model cache.
- Runtime, memory, and latency are not recorded in the current artifact.
- Results are local generated evidence and are not production-quality claims.

## Open Gaps

- Define and run the multi-query proxy evaluation described in `docs/reports/abo_multi_query_proxy_evaluation_design.md`.
- Record query selection criteria and skipped-query reasons.
- Report aggregate metrics across at least 25 query products where local resources allow.
- Add failure-case review for product-type mismatches and method-specific errors.
- Collect local runtime and resource notes, especially for CLIP.
- Keep Delivery, Production, and Maintenance open until evidence and service design are separately approved.

## Production Readiness Statement

This report documents a local preliminary proxy evaluation. It does not claim production readiness, customer relevance, conversion impact, deployment readiness, or general superiority of any method.
