# Current Project Status

## 1. Current Project Direction

The Enterprise Multimodal E-Commerce Recommendation AI System now follows a two-track real-data strategy.

| Track | Dataset | Current Purpose |
| --- | --- | --- |
| A | `RetailRocket_event-based` | Behavior and event-based recommendation |
| B | `amazon_berkeley_text_images-based` | Product metadata, text, and image-based product similarity |

The tracks are intentionally independent. RetailRocket `visitorid` and `itemid` values must not be joined to Amazon Berkeley Objects (ABO) listing or image identifiers. The project must not imply that both datasets represent one company, one catalog, or one user population.

Video, spin, 360-degree, and 3D recommendation are outside the current project scope.

## 2. Completed Work

### 2.1 Discovery and Alignment

- Added safe RetailRocket discovery using header-only reads, streaming line counts, and chunked aggregation.
- Added bounded ABO archive discovery without full extraction or image processing.
- Recorded the confirmed two-track strategy and repository alignment findings.
- Updated discovery scripts so raw-data and report paths resolve from the repository root rather than the current working directory.

Evidence reports:

- `docs/reports/retailrocket_dataset_discovery.md`
- `docs/reports/abo_dataset_discovery.md`
- `docs/reports/dataset_discovery_summary.md`
- `docs/reports/full_repository_alignment_audit.md`

### 2.2 Documentation Rebuild

Rebuilt `docs/01_project_foundation.md` through `docs/07_deployment_plan.md` around the real-data strategy. The documents now separate RetailRocket behavior recommendation from ABO text/image similarity, prohibit fabricated joins, and defer advanced systems until baseline evidence exists.

### 2.3 Sample Fixture Rebuild

Replaced the deprecated unified synthetic sample design with tiny deterministic fixtures:

```text
data/sample/
├── README.md
├── retailrocket/
└── amazon_berkeley_objects/
```

Fixtures exist for tests, examples, and Continuous Integration / Continuous Deployment (CI/CD) workflows only. They are not the primary Machine Learning (ML) datasets.

### 2.4 Loading and Validation Update

- Added track-specific RetailRocket fixture loading and validation.
- Added ABO listing, image metadata, image path, and product-image mapping validation.
- Removed active dependencies on the old unified synthetic `products/users/events` contract.

### 2.5 Deprecated Baseline Cleanup

Removed the retired synthetic popularity baseline assumptions and rebuilt the implementation around RetailRocket source fields only:

```text
timestamp, visitorid, event, itemid, transactionid
```

### 2.6 RetailRocket Baseline Protocol and Pipeline

- Added `docs/reports/retailrocket_baseline_protocol.md`.
- Implemented `RetailRocketPopularityRecommender` with provisional weights:
  - `view`: `1.0`
  - `addtocart`: `3.0`
  - `transaction`: `5.0`
- Added a chunked real-data runner that writes top RetailRocket items.
- Added a temporal baseline evaluation pipeline for `HitRate@10` and `Recall@10`.

The weights remain provisional and may be revised after evaluation review.

## 3. Current Data Assets

### 3.1 Raw Data

Raw data remains local and ignored by Git.

```text
data/raw/RetailRocket_event-based/
├── events.csv
├── item_properties_part1.csv
├── item_properties_part2.csv
└── category_tree.csv

data/raw/amazon_berkeley_text_images-based/
├── README.md
├── abo-listings.tar
└── abo-images-small.tar
```

### 3.2 Deterministic Sample Fixtures

```text
data/sample/retailrocket/
├── events_sample.csv
├── item_properties_sample.csv
└── category_tree_sample.csv

data/sample/amazon_berkeley_objects/
├── listings_sample.jsonl
├── images_sample.csv
└── image_paths_sample.txt
```

### 3.3 Processed Local Artifacts

The following generated artifacts currently exist under `data/processed/` and are ignored by Git:

- `retailrocket_baseline_top_items.csv`
- `retailrocket_baseline_evaluation.json`

These are reproducible local outputs, not committed source assets.

## 4. Current Code Status

| Area | Current Status |
| --- | --- |
| Fixture loaders | RetailRocket and ABO fixture loaders implemented |
| Validators | Track-specific RetailRocket and ABO validators implemented |
| RetailRocket baseline | Event-weighted popularity recommender implemented |
| RetailRocket runner | Chunked raw-event aggregation and top-item CSV output implemented |
| RetailRocket evaluator | Chunked temporal split evaluation and JSON output implemented |
| Discovery scripts | RetailRocket and ABO discovery scripts implemented with repository-root paths |
| ABO text baseline | Not implemented yet |
| ABO image similarity | Not implemented yet |
| Application Programming Interface (API) | Not implemented yet |
| Deployment stack | Not implemented yet |

Key implementation files:

- `src/ecommerce_recommender/data/loading.py`
- `src/ecommerce_recommender/data/validation.py`
- `src/ecommerce_recommender/models/baseline.py`
- `scripts/run_retailrocket_baseline.py`
- `scripts/evaluate_retailrocket_baseline.py`

## 5. Test Status

The latest relevant pytest run completed successfully:

```text
17 passed in 2.99s
```

Current unit coverage includes:

- RetailRocket and ABO fixture loading.
- RetailRocket and ABO fixture validation.
- ABO product-image mapping checks.
- RetailRocket weighted popularity ranking.
- Unsupported RetailRocket event handling.
- Deterministic RetailRocket tie-breaking.
- Chunked RetailRocket runner aggregation and output creation.
- Temporal split calculation.
- Chunked train-score and test-relevance aggregation.
- Visitor-level baseline metrics.
- Evaluation JSON output creation.

The latest evaluator tests use only temporary CSV and output files.

## 6. RetailRocket Baseline Status

The first real RetailRocket baseline is implemented and evaluated. It is intentionally simple: one global top-K ranking from event-weighted train interactions. This establishes an honest reference point for later improvements.

Latest local evaluation artifact:

```text
data/processed/retailrocket_baseline_evaluation.json
```

| Metric | Value |
| --- | ---: |
| Temporal split timestamp | `1440160551107` |
| Train ratio | `0.8` |
| Train events | `2,266,414` |
| Test events | `489,687` |
| Evaluated visitors | `275,826` |
| HitRate@10 | `0.0081645675` |
| Recall@10 | `0.0073435373` |

These metric values are acceptable for a first non-personalized popularity baseline. They provide a measurable floor rather than a production-quality target. Later RetailRocket methods must use the same evaluation protocol when claiming improvement.

## 7. Remaining Work

### 7.1 Recommended Near-Term Work

- Define an ABO text-similarity baseline protocol.
- Implement an ABO metadata/text product-similarity baseline.
- Add ABO text-similarity unit tests using deterministic fixtures.
- Define an ABO retrieval evaluation protocol and focused local evaluation path.

### 7.2 Later Work

- Add ABO image similarity after the text baseline is stable.
- Compare text, image, and later multimodal ABO methods under the same ABO protocol.
- Explore stronger RetailRocket methods only after preserving baseline comparability.
- Add API, monitoring, and deployment work only after stable baseline evidence exists.
- Consider Retrieval-Augmented Generation (RAG), agentic workflows, Model Context Protocol (MCP), and contextual bandits only when a justified enterprise use case exists.

## 8. Risks and Warnings

- Do not merge RetailRocket and ABO identifiers.
- Do not restore the deprecated unified synthetic sample design.
- Do not introduce video recommendation into the current scope.
- Do not describe fixtures as primary ML datasets.
- Do not overclaim API, deployment, advanced-model, or production readiness.
- Keep raw RetailRocket reads chunked and ABO archive inspection bounded.
- Preserve ABO attribution and license notes in future public-facing documentation.
- Compare advanced methods only against the corresponding track baseline under the same protocol.

## 9. Recommended Next Step

Build the ABO text baseline next.

Use the existing ABO fixture contract to define a small content-based product-similarity baseline from approved metadata fields such as `item_name`, `brand`, `bullet_point`, and `product_type`. Create a separate ABO protocol first, keep the implementation independent from RetailRocket, and add focused retrieval tests before processing larger ABO data.
