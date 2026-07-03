# ABO Multi-Query Proxy Evaluation Design

## Purpose

Amazon Berkeley Objects (ABO) does not provide user sessions, clicks, carts, purchases, conversions, or explicit relevance judgments in this project scope. The current ABO evaluation therefore uses metadata-based proxy relevance to compare product-to-product similarity methods.

This design defines the next evidence-hardening step: a representative bounded multi-query proxy evaluation for ABO text, image, and CLIP similarity methods. It does not add a new model family and does not claim production readiness.

## Why Proxy Evaluation Is Needed

ABO supports catalog similarity, not behavior-based personalization. Without user labels or human relevance judgments, the project needs a transparent proxy protocol to check whether retrieved products are at least metadata-consistent with the query product.

Proxy evaluation is useful for:

- Comparing methods under the same bounded candidate pool.
- Detecting self-recommendations, duplicate recommendations, missing catalog records, and obvious category drift.
- Producing reproducible local evidence before any Delivery-stage work is considered.

Proxy evaluation is not a substitute for human review, customer behavior data, or production recommendation evaluation.

## Query Selection Criteria

The multi-query set should be selected from cleaned ABO records that meet all required conditions:

- Has stable `item_id`.
- Has non-empty `combined_text`.
- Has non-empty `product_type`.
- Has a valid `main_image_id` and resolved `image_path` when image or CLIP methods are evaluated.
- Has `is_clip_ready=true` for CLIP comparisons.
- Belongs to the bounded candidate sample used by all compared methods.

The query set should include product diversity:

- Multiple `product_type` values.
- More than one brand where available.
- Products with different text lengths and metadata completeness.
- Products whose image paths can be resolved without extracting the full ABO image archive.

## Proposed Minimum Query Count

Use at least **25 query products** for the next proxy evaluation pass.

This is large enough to reduce dependence on a single item while remaining bounded for local CPU-first development. If CLIP runtime is too heavy on the available machine, the report should document the executed query count and why it was reduced instead of silently changing the protocol.

## Candidate Pool Policy

The first multi-query evaluation should keep the candidate pool bounded and consistent across methods.

Recommended initial policy:

- Input file: `data/processed/abo_clean_products_5k.jsonl`.
- Candidate pool: first 100 to 500 CLIP-ready products, selected deterministically from the cleaned JSONL.
- Same candidate pool for TF-IDF, RGB histogram, and CLIP.
- Same `top_k` for all methods.
- Exclude the query item from its own recommendation list.
- Record skipped products and failure reasons.

Do not process all ABO images or generate full-catalog embeddings during this milestone.

## Relevance Proxy Definition

Primary binary proxy:

- A recommendation is relevant when `recommended.product_type == query.product_type`, compared after normalization.

Secondary diagnostics:

- Brand match rate where both query and candidate have a brand.
- Color match rate where both query and candidate have a color.
- Unique product-type count in top-K.
- Unique brand count in top-K.
- Missing recommendation record count.
- Self-recommendation count.
- Duplicate recommendation count.

The primary proxy should be clearly labeled as metadata consistency, not true customer relevance.

## Metrics

Report metrics per method and aggregated across all evaluated queries:

| Metric | Purpose |
| --- | --- |
| Product Type Match@K | Simple metadata-consistency rate. |
| Proxy Precision@K | Binary product-type relevance precision. |
| Proxy Average Precision@K | Ranking-aware binary proxy quality within top-K. |
| Proxy NDCG@K | Ranking-aware proxy relevance with higher rank rewarded. |
| Brand Match@K | Diagnostic, not primary relevance. |
| Color Match@K | Diagnostic where color is present. |
| Unique Product Types@K | Diversity/category drift diagnostic. |
| Unique Brands@K | Diversity diagnostic. |
| Missing Candidate Count | Output integrity check. |
| Query Failure Count | Robustness and reproducibility check. |

If feasible, include mean, median, minimum, and maximum for primary metrics across queries.

## Failure Cases to Inspect

Review and summarize examples where:

- Product-type proxy relevance is zero for all top-K recommendations.
- RGB histogram retrieves visually similar colors but unrelated product types.
- TF-IDF retrieves products because of brand or repeated generic terms.
- CLIP retrieves visually plausible but product-type mismatched items.
- Any method returns missing, duplicate, or self recommendations.
- Query products have sparse metadata or ambiguous product types.
- Image extraction or CLIP model loading fails.

## Latency and Resource Notes to Collect

Record:

- Python version and operating system.
- CPU/GPU assumption.
- Candidate pool size.
- Query count.
- `top_k`.
- Wall-clock runtime per method if measured.
- Whether CLIP used `--local-files-only`.
- Whether the Hugging Face cache was already populated.
- Any memory or install limitations observed.

Latency should be treated as local engineering evidence, not production serving latency.

## Output Expectations

A future multi-query report should include:

- Query selection method.
- Candidate pool construction.
- Commands used.
- Per-method aggregate metrics.
- Per-query result table or sample.
- Failure-case review.
- Limitations.
- Decision on whether the ABO evaluation evidence is strong enough to support Delivery-stage design work.

## Acceptance Criteria for Moving Toward Delivery Stage

The project may consider a Delivery-stage design milestone only when:

- ABO has a reviewed multi-query proxy evaluation report, not only one-query evidence.
- RetailRocket and ABO processed artifacts have documented provenance and regeneration commands.
- Baseline and advanced ABO methods are compared under the same bounded candidate and query protocol.
- Results are reported with limitations and do not claim click, purchase, satisfaction, or production performance.
- Fixture-only tests pass in a documented environment.
- Raw-data workflows are reproducible by command without committing raw data.
- Delivery remains design-only until API contracts, latency budgets, security boundaries, and fallback behavior are separately approved.

## Limitations

- Product-type equality is a weak proxy and may miss useful complementary or substitute relationships.
- ABO metadata quality varies across language, category, and record completeness.
- Multi-query proxy evaluation still cannot prove customer satisfaction.
- CLIP runtime may limit query count on local CPU machines.
- This design does not authorize full-catalog image processing, deployment, monitoring, vector databases, or FastAPI implementation.
