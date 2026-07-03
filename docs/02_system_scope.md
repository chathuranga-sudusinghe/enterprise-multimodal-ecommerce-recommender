# System Scope

## 1. Purpose

This document defines the current and future boundaries of the Enterprise Multimodal E-Commerce Recommendation AI System. It aligns development with the confirmed two-track real-data strategy and prevents premature implementation claims.

## 2. Current Project Scope

The current active milestone is Data and Evaluation Evidence Hardening. It builds on completed local discovery, deterministic fixtures, safe adapters, validators, baseline implementations, and partial evaluation evidence.

The system currently targets:

- Behavior-based recommendation from RetailRocket events.
- Product text-based similarity from Amazon Berkeley Objects (ABO) listings.
- Product image-based and CLIP-based similarity from ABO catalog images in controlled local experiments.

Video recommendation is excluded from the current scope.

## 3. Track A: RetailRocket Behavior/Event Recommendation

RetailRocket data is stored under `data/raw/RetailRocket_event-based/`.

| Raw File | Role |
| --- | --- |
| `events.csv` | Visitor-item behavior events |
| `item_properties_part1.csv` | Timestamped item-property records |
| `item_properties_part2.csv` | Timestamped item-property records |
| `category_tree.csv` | Category hierarchy |

The implemented local baseline is an event-weighted global popularity recommender. Its current weights remain baseline evidence rather than optimized business policy.

## 4. Track B: Amazon ABO Text/Image Product Similarity

ABO data is stored under `data/raw/amazon_berkeley_text_images-based/`.

| Raw File | Role |
| --- | --- |
| `abo-listings.tar` | Multilingual listing metadata |
| `abo-images-small.tar` | Small catalog images and image metadata |
| `README.md` | Dataset description and license notes |

The implemented local baselines include metadata/text TF-IDF similarity and RGB histogram image similarity. CLIP text-image similarity is implemented as a bounded ABO experiment with partial proxy evaluation evidence.

## 5. In-Scope Items

- Safe inspection of raw files and archives.
- Documentation based on discovery evidence.
- Tiny deterministic fixtures for tests, examples, and CI.
- Track-specific canonical schemas.
- Safe raw-data adapters and validation.
- Separate baseline implementations and reports.
- Separate evaluation protocols and evidence hardening.
- Local-first engineering workflows.
- Basic GitHub Actions pytest quality gate for pull requests and pushes to `dev` and `main`.

## 6. Out-of-Scope Items

The current phase excludes:

- Merging RetailRocket and ABO.
- Invented shared IDs or synthetic cross-track joins.
- The old synthetic `products.csv`, `users.csv`, and `events.csv` design as the primary dataset.
- Video, spin, 360-degree, or 3D recommendation.
- API implementation.
- New model-family implementation during the evidence-hardening milestone.
- RAG implementation.
- Production agentic workflows.
- Production MCP server/client integration.
- Contextual bandits.
- Cloud deployment and Kubernetes.

## 7. Future Extension Scope

Potential future extensions may include:

- Personalized RetailRocket methods beyond popularity baselines.
- ABO image similarity and text-image retrieval.
- Track-specific vector search.
- An API service layer after baseline evidence exists.
- Monitoring, experiment tracking, and deployment automation.
- Governed RAG, agentic, or MCP layers only when a concrete business requirement justifies them.

Future extensions must preserve provenance and must not fabricate identity mappings between datasets.

## 8. Core System Modules

| Module | Current Direction |
| --- | --- |
| Discovery | Read-only schema, inventory, and bounded profiling tools |
| Fixture contracts | Tiny deterministic track-specific examples |
| Data adapters | Safe RetailRocket CSV and ABO archive readers |
| Validation | Track-specific schema and relationship checks |
| Feature preparation | Local bounded preparation exists for current baseline and CLIP-ready ABO workflows |
| Baselines | Separate RetailRocket and ABO baselines implemented locally |
| Evaluation | Separate leakage-aware protocols, local outputs, and evidence-hardening reports |
| API service | Future layer after baseline evidence |
| Monitoring and governance | Incremental controls as the system matures |

## 9. Data Scope

Raw datasets are local, ignored by Git, and accessed safely. `data/sample/` is reserved for tiny deterministic fixtures only. Fixtures must mirror discovered schemas and must not be described as the primary ML dataset.

RetailRocket identifiers belong only to RetailRocket. ABO listing and image identifiers belong only to ABO. No cross-dataset join is permitted.

## 10. Model Scope

No new model-family implementation should start during the current evidence-hardening milestone. Current local methods are:

- RetailRocket event-weighted popularity.
- ABO TF-IDF text similarity.
- ABO RGB histogram image similarity.
- ABO CLIP text-image similarity as a bounded experiment.

Advanced methods must outperform the corresponding baseline under the same task and protocol before improvement is claimed.

## 11. API Scope Later

An Application Programming Interface (API) is a later service boundary. API work must wait until stable adapters, validation, baseline evidence, and response contracts exist. No current document should claim that serving endpoints are implemented.

## 12. Evaluation Scope

Each track requires its own evaluation protocol:

- RetailRocket: temporal behavior-based top-K recommendation.
- ABO: product-to-product similarity retrieval.

Cross-track aggregate scores are not valid because the datasets and tasks are unrelated.

## 13. Security and Governance Scope

- Keep raw datasets out of Git.
- Preserve provenance, attribution, and license notes.
- Avoid sensitive logging.
- Do not commit secrets or `.env` files.
- Use bounded raw-data reads.
- Document limitations and future governance gates.

## 14. Development Boundaries

- Work in small, reviewable changes.
- Rebuild fixture contracts before adapters and tests.
- Approve evaluation protocols before baselines.
- Require baseline evidence before API implementation.
- Add deployment complexity only after local workflows are stable.

## 15. Acceptance Criteria

This scope is accepted when:

1. The two independent dataset tracks are clearly defined.
2. Cross-dataset joins and false shared-ID assumptions are prohibited.
3. `data/sample/` is described as fixture-only.
4. Video and premature advanced features are excluded from the current phase.
5. Baseline and API gates are explicit.
6. Evaluation is defined separately for RetailRocket and ABO.
7. Raw-data safety, provenance, and governance expectations are visible.
