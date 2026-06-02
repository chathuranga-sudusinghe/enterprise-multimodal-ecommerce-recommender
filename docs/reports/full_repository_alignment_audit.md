# Full Repository Alignment Audit

## 1. Executive Summary

The repository contains a strong early engineering foundation, but much of the original project design still follows a synthetic-data-first workflow. The confirmed direction is now a two-track real-data design:

| Track | Dataset | Purpose |
| --- | --- | --- |
| A | `RetailRocket_event-based` | Behavior and event-based recommendation |
| B | `amazon_berkeley_text_images-based` | Product metadata, text, and image-based product similarity |

The two tracks must remain independent. RetailRocket visitor and item identifiers must not be joined to Amazon Berkeley Objects (ABO) listing or image identifiers. Video recommendation is outside the current scope.

The immediate priority is documentation restructuring and fixture redesign. Model development should remain paused until the repository clearly separates the two tracks, `data/sample/` is rebuilt as tiny deterministic fixtures, and source adapters are designed from the discovered real schemas.

## 2. Current Repository Status

### Confirmed Discovery Artifacts

The repository now contains safe discovery outputs for both real-world datasets:

- `docs/reports/retailrocket_dataset_discovery.md`
- `docs/reports/abo_dataset_discovery.md`
- `docs/reports/dataset_discovery_summary.md`
- `scripts/discover_retailrocket_dataset.py`
- `scripts/discover_abo_dataset.py`

### RetailRocket Schema Ground Truth

RetailRocket events use:

```text
timestamp, visitorid, event, itemid, transactionid
```

Observed event values:

- `view`
- `addtocart`
- `transaction`

RetailRocket item properties use:

```text
timestamp, itemid, property, value
```

RetailRocket category tree data uses:

```text
categoryid, parentid
```

### ABO Schema Ground Truth

ABO listing metadata samples expose fields such as:

- `item_id`
- `item_name`
- `brand`
- `bullet_point`
- `product_type`
- `color`
- `material`
- `style`
- `main_image_id`
- `other_image_id`

ABO image metadata exposes:

- `image_id`
- `path`
- `height`
- `width`

### Empty or Incomplete Root Files

- `README.md` exists but is empty.
- `.env.example` exists but is empty.
- `pyproject.toml` is usable as a minimal package configuration.
- `requirements.txt` is usable temporarily but should later be reduced to intentional direct dependencies.

## 3. Files Aligned With the New Direction

### Keep Unchanged

| File | Reason |
| --- | --- |
| `docs/reports/retailrocket_dataset_discovery.md` | Documents the real RetailRocket schema, safe chunked-read process, event distribution, and limitations. |
| `docs/reports/abo_dataset_discovery.md` | Documents ABO archive structure, sampled metadata fields, image paths, product-to-image mapping possibilities, and scope boundaries. |
| `docs/reports/dataset_discovery_summary.md` | Correctly defines the two-track strategy, prohibits synthetic joins, excludes video recommendation, and pauses model work pending review. |

### Keep With Minor or No Immediate Change

| File | Assessment |
| --- | --- |
| `scripts/discover_retailrocket_dataset.py` | Aligned read-only discovery tool. It uses header-only reads, streaming line counts, and chunked aggregation. |
| `scripts/discover_abo_dataset.py` | Aligned read-only discovery tool. It streams tar headers, samples bounded metadata, and does not extract archives. |
| `pyproject.toml` | Minimal src-layout package configuration is suitable for the current phase. |
| `.gitignore` | Correctly ignores `data/raw/*`, processed data, virtual environments, Python metadata, and model artifacts. |
| `src/ecommerce_recommender/**/__init__.py` | Empty package markers remain safe and useful. |

## 4. Files Conflicting With the New Direction

### Agent Guidance

| File | Conflict | Required Direction |
| --- | --- | --- |
| `AGENTS.md` | Directs agents toward synthetic sample data, validation, baseline recommenders, and FastAPI before real-data restructuring. It states that Version 1 uses synthetic data only. | Rebuild to enforce the two-track strategy, data-discovery-first sequencing, no cross-dataset ID joins, no video scope, fixture-only `data/sample/`, and no model weights before protocol review. |

### Foundation Documentation

The following documents should be rebuilt from scratch because synthetic-first assumptions are woven through their structure rather than isolated to a few lines:

| File | Main Conflict |
| --- | --- |
| `docs/01_project_foundation.md` | Broad foundation remains useful conceptually, but it does not define the confirmed two-track dataset strategy, no-merge rule, or video exclusion. |
| `docs/02_system_scope.md` | Defines synthetic `products.csv`, `users.csv`, and `events.csv` as the Version 1 data foundation. |
| `docs/03_architecture.md` | Starts the Version 1 pipeline with synthetic e-commerce data and assumes one unified product/user/event flow. |
| `docs/04_data_design.md` | Entire document is centered on synthetic `products.csv`, `users.csv`, `events.csv`, shared identifiers, and fictional event types. |
| `docs/05_evaluation_plan.md` | Has useful metric principles, but it does not define separate task-appropriate protocols for RetailRocket and ABO or prohibit cross-track comparisons and synthetic joins. |
| `docs/06_security_governance.md` | States that Version 1 uses synthetic data only and does not cover raw dataset provenance, ABO attribution, or real-data handling boundaries. |
| `docs/07_deployment_plan.md` | Treats local synthetic sample data as the expected data source and does not describe fixture data versus ignored raw dataset tracks. |

### Root-Level Project Files

| File | Conflict | Required Direction |
| --- | --- | --- |
| `README.md` | Empty. | Rebuild after documentation restructuring with the two-track strategy, setup, discovery reports, and scope boundaries. |
| `.env.example` | Empty. | Add safe placeholders later for fixture paths and track-specific raw paths if configuration is introduced. |
| `requirements.txt` | Appears to be an environment snapshot including transitive packages. | Keep temporarily. Later replace with intentional direct dependencies after package policy is decided. |

## 5. Files Likely to Break After Sample Rebuild

`data/sample/` should become tiny deterministic fixtures that mirror the real dataset tracks rather than a fictional unified commerce dataset. The following files depend directly on the old fixture contract and will break or become misleading after that rebuild.

### Sample CSV Files to Replace

| File | Current Problem | Recommended Replacement Direction |
| --- | --- | --- |
| `data/sample/products.csv` | Uses fictional unified product fields such as `product_id`, price, stock, rating, and image path. | Replace with small ABO listing and image-metadata fixture files using discovered ABO fields. |
| `data/sample/users.csv` | Uses fictional demographic users with `user_id`, age group, country, and category preference. RetailRocket does not provide this schema. | Remove or replace with a tiny RetailRocket visitor-oriented fixture only if needed. Do not invent customer profile fields. |
| `data/sample/events.csv` | Uses `event_id`, `user_id`, `product_id`, and synthetic event values such as `click`, `add_to_cart`, `purchase`, and `not_interested`. | Replace with a RetailRocket-shaped fixture using `timestamp`, `visitorid`, `event`, `itemid`, and `transactionid`, with observed events `view`, `addtocart`, and `transaction`. |

### Source Files to Replace or Split

| File | Breakage Risk | Recommended Direction |
| --- | --- | --- |
| `src/ecommerce_recommender/data/loading.py` | `load_sample_datasets()` assumes one directory containing `products.csv`, `users.csv`, and `events.csv`. `load_csv()` performs unrestricted full DataFrame reads and must not be used on large raw CSVs. | Split fixture loaders from safe raw-track adapters. Require chunked reads for RetailRocket raw data and bounded tar metadata access for ABO. |
| `src/ecommerce_recommender/data/validation.py` | Assumes unified synthetic products, users, events, shared IDs, prices, ratings, stock statuses, and fictional event types. | Replace with separate RetailRocket and ABO validators. Keep fixture validation aligned to discovered schemas. |
| `src/ecommerce_recommender/models/baseline.py` | Assumes `product_id`, `event_type`, and locked synthetic event weights. RetailRocket uses `itemid`, `event`, and different observed event values. | Pause implementation. Rebuild later only after the RetailRocket business task, recency policy, provisional weights, and evaluation protocol are approved. |

### Tests to Replace or Split

| File | Breakage Risk | Recommended Direction |
| --- | --- | --- |
| `tests/unit/test_data_loading.py` | Tests generic CSV loading with synthetic product columns only. | Retain generic loader tests where useful, then add track-specific fixture loader tests. |
| `tests/unit/test_data_validation.py` | Entire suite validates fictional unified synthetic schemas. | Replace with separate RetailRocket fixture validation tests and ABO fixture validation tests. |
| `tests/unit/test_baseline_recommender.py` | Encodes locked synthetic weights and event names before RetailRocket protocol approval. | Remove or quarantine until the redesigned RetailRocket baseline contract is approved. Rebuild afterward using RetailRocket-shaped fixtures. |

## 6. Recommended Files to Rebuild

Rebuild these files in a controlled documentation-first sequence:

1. `AGENTS.md`
2. `docs/01_project_foundation.md`
3. `docs/02_system_scope.md`
4. `docs/03_architecture.md`
5. `docs/04_data_design.md`
6. `docs/05_evaluation_plan.md`
7. `docs/06_security_governance.md`
8. `docs/07_deployment_plan.md`
9. `README.md`
10. `.env.example` when configuration placeholders are ready
11. `data/sample/*.csv` as separate tiny deterministic track fixtures
12. `src/ecommerce_recommender/data/loading.py`
13. `src/ecommerce_recommender/data/validation.py`
14. `tests/unit/test_data_loading.py`
15. `tests/unit/test_data_validation.py`
16. `src/ecommerce_recommender/models/baseline.py` only after protocol approval
17. `tests/unit/test_baseline_recommender.py` only after the redesigned baseline contract exists

## 7. Recommended Files to Keep Unchanged

Keep these files unchanged during the next documentation restructuring step:

- `docs/reports/retailrocket_dataset_discovery.md`
- `docs/reports/abo_dataset_discovery.md`
- `docs/reports/dataset_discovery_summary.md`
- `scripts/discover_retailrocket_dataset.py`
- `scripts/discover_abo_dataset.py`
- `pyproject.toml`
- `.gitignore`
- All empty package `__init__.py` files
- Raw files under `data/raw/RetailRocket_event-based/`
- Raw files under `data/raw/amazon_berkeley_text_images-based/`

## 8. Safe Update Order

Use this migration order to avoid rebuilding code against another temporary contract:

1. **Rebuild project guidance:** Update `AGENTS.md` with the two-track strategy, no-merge rule, no-video boundary, and discovery-first gate.
2. **Rebuild foundation docs:** Replace `docs/01_project_foundation.md` through `docs/07_deployment_plan.md` using the confirmed discovery reports as source material.
3. **Define fixture contracts:** Decide the smallest deterministic fixture files for RetailRocket and ABO separately. Treat fixtures as tests and examples only.
4. **Rebuild `data/sample/`:** Replace fictional unified CSVs with track-specific fixtures.
5. **Rebuild loading and validation:** Split source adapters and validators by dataset track. Keep large raw reads chunked or bounded.
6. **Rebuild tests:** Add track-specific loader and validator tests using the new fixture contracts.
7. **Define RetailRocket evaluation protocol:** Specify the business task, temporal split, recency policy, leakage controls, metrics, and provisional weight-selection method.
8. **Implement RetailRocket baseline later:** Add the event-weighted recent popularity recommender only after protocol approval.
9. **Define ABO evaluation protocol:** Specify content-based product similarity inputs, relevance or retrieval checks, and text/image feature progression.
10. **Implement ABO baseline later:** Start with metadata/text similarity, then add image features only when evaluation proves value.
11. **Add API work after baselines:** Do not expose unstable adapters or model assumptions through an API prematurely.

## 9. Risks and Warnings

- **Cross-dataset contamination risk:** RetailRocket and ABO identifiers are unrelated. Any direct join would be fabricated and invalid.
- **Locked-weight risk:** The current baseline hardcodes synthetic event weights before RetailRocket protocol approval.
- **Schema mismatch risk:** Current loaders, validators, and tests will misrepresent real RetailRocket and ABO schemas.
- **Memory safety risk:** Raw RetailRocket item-property files and ABO archives are large. Continue using chunked CSV reads and bounded tar inspection.
- **Data-role confusion risk:** `data/sample/` must be described as fixtures only, never as the main training dataset.
- **Scope creep risk:** Video, spin, 360-degree, and 3D assets remain outside the current scope.
- **Evaluation drift risk:** Each track needs a task-appropriate protocol. Advanced methods must be compared against the corresponding baseline using the same protocol.
- **Licensing risk:** ABO documentation and future README content should preserve attribution and license notes before using dataset assets in demonstrations.

## 10. Next Recommended Codex Task

Rebuild only `AGENTS.md` first.

The updated agent rules should:

- Define RetailRocket and ABO as separate dataset tracks.
- Prohibit merging IDs across tracks.
- State that video recommendation is excluded.
- State that `data/sample/` contains tiny deterministic fixtures only.
- Require discovery-report review before schema, feature, or model decisions.
- Pause model coding, baseline weights, and API work until documentation and fixture contracts are approved.
- Require chunked reads for large RetailRocket CSVs and bounded tar inspection for ABO archives.
- Require separate evaluation protocols for the RetailRocket behavior task and ABO content/image similarity task.

After `AGENTS.md` is aligned, rebuild the seven foundation documents one at a time.
