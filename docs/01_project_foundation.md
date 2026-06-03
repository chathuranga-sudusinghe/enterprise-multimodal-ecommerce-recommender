# Project Foundation

## 1. Project Overview

The Enterprise Multimodal E-Commerce Recommendation AI System is a production-oriented Artificial Intelligence (AI) and Machine Learning (ML) engineering project. It is designed to develop recommendation capabilities through evidence-based phases rather than a notebook-only demonstration.

The current project focuses on three recommendation signals:

- Customer behavior events.
- Product text metadata.
- Product images.

The repository uses two independent real-world dataset tracks. RetailRocket supports behavior-based recommendation research. Amazon Berkeley Objects (ABO) supports product metadata, text, and image similarity research. These datasets are not merged and must not be represented as a shared commerce platform.

## 2. Business Problem

E-commerce recommendation systems must help users discover relevant products while remaining measurable, explainable, and operationally safe. Different recommendation tasks require different evidence:

- Behavior-based recommendation uses observed interactions to identify items that may be useful to visitors.
- Product similarity recommendation uses catalog content to retrieve related products, including for items without interaction history.

This project develops those capabilities separately before considering any future service-level composition.

## 3. AI/ML Objectives

The project objectives are to:

1. Build safe adapters for discovered real-data schemas.
2. Establish deterministic fixtures for tests and Continuous Integration / Continuous Deployment (CI/CD) workflows.
3. Define leakage-aware evaluation protocols for each dataset track.
4. Implement simple, measurable baselines only after protocol approval.
5. Compare later advanced methods against the corresponding baseline under the same protocol.
6. Add service, monitoring, and governance layers only when supporting evidence exists.

## 4. Confirmed Two-Track Dataset Strategy

| Track | Dataset | Purpose | Initial Baseline Candidate |
| --- | --- | --- | --- |
| A | `RetailRocket_event-based` | Behavior and event-based recommendation | Event-weighted recent popularity recommender |
| B | `amazon_berkeley_text_images-based` | Product metadata, text, and image similarity recommendation | Content-based product similarity recommender |

### 4.1 Track A: RetailRocket Event-Based Recommendation

RetailRocket raw data is stored under `data/raw/RetailRocket_event-based/`. Discovery confirmed event records with `timestamp`, `visitorid`, `event`, `itemid`, and `transactionid`, including observed event values `view`, `addtocart`, and `transaction`.

### 4.2 Track B: Amazon ABO Text/Image Similarity

ABO raw data is stored under `data/raw/amazon_berkeley_text_images-based/`. Discovery confirmed listing metadata, image identifiers, and small catalog images suitable for controlled product-similarity research.

### 4.3 Dataset Separation Rule

RetailRocket and ABO are independent datasets. Their visitor, item, listing, and image identifiers are unrelated. The project must not invent cross-dataset joins or claim that both datasets represent one company, one catalog, or one user population.

## 5. Current Scope

The current phase includes:

- Safe dataset discovery.
- Documentation restructuring from discovery evidence.
- Tiny deterministic fixture contracts.
- Safe raw-data adapter planning.
- Track-specific validation planning.
- Separate baseline and evaluation protocol design.

Video recommendation is excluded from the current scope.

## 6. Out-of-Scope Boundaries

The current phase does not include:

- Cross-dataset identity mapping.
- Video, spin, 360-degree, or 3D recommendation.
- Model training before protocol approval.
- Hardcoded baseline event weights before protocol approval.
- Application Programming Interface (API) implementation.
- Retrieval-Augmented Generation (RAG).
- Agentic workflows.
- Model Context Protocol (MCP) integration.
- Contextual bandit optimization.
- Cloud deployment or Kubernetes.

## 7. Stakeholders

| Stakeholder | Primary Interest |
| --- | --- |
| Product and business teams | Clear recommendation tasks, useful outcomes, and measurable trade-offs |
| ML engineers | Reproducible data contracts, baselines, evaluation, and extensibility |
| Software engineers | Modular adapters, validation, tests, and later service boundaries |
| Data and governance reviewers | Provenance, attribution, privacy, and safe data handling |
| Portfolio reviewers and recruiters | Evidence of disciplined, production-oriented AI/ML engineering |

## 8. Success Metrics

Success metrics will be defined and reported separately for each track.

### 8.1 RetailRocket Direction

- Recall@K.
- Hit Rate@K.
- Normalized Discounted Cumulative Gain (NDCG)@K.
- Catalog coverage.
- Recommendation latency.

### 8.2 ABO Direction

- Product-type or category consistency where usable.
- Retrieval quality from approved relevance checks.
- Diversity.
- Catalog coverage.
- Similarity retrieval latency.

No combined score should be produced across unrelated datasets.

## 9. Architecture Principles

- Use discovery evidence before schema, feature, or model decisions.
- Keep dataset tracks independent and provenance-aware.
- Start with measurable baselines before advanced models.
- Prevent evaluation leakage through explicit split protocols.
- Keep raw-data access bounded and memory-safe.
- Separate fixtures, raw data, processed artifacts, models, and services.
- Build locally first and add deployment complexity only when justified.

## 10. Expected Delivery Phases

1. Complete safe dataset discovery and alignment reporting.
2. Rebuild project documentation around the two-track strategy.
3. Approve deterministic fixture contracts for each track.
4. Build safe adapters, validators, and track-specific tests.
5. Approve separate evaluation protocols.
6. Implement and evaluate the RetailRocket baseline.
7. Implement and evaluate the ABO metadata/text baseline.
8. Add controlled image-similarity experiments.
9. Consider API, monitoring, and deployment layers after baseline evidence exists.
10. Evaluate future enterprise extensions only when they add demonstrated value.

## 11. Key Risks

| Risk | Mitigation Direction |
| --- | --- |
| Fabricated cross-dataset joins | Enforce independent schemas, identifiers, and evaluations |
| Full-memory loading of large raw files | Require header-only, streaming, chunked, or bounded archive reads |
| Premature model claims | Require approved protocols and baseline comparisons |
| Data-role confusion | Treat `data/sample/` as fixture-only and keep raw data ignored |
| Scope creep | Keep video and advanced orchestration out of the current phase |
| License or attribution gaps | Preserve ABO attribution and license notes in public-facing documentation |

## 12. Governance Expectations

The project must preserve dataset provenance, avoid sensitive logging, exclude raw data from Git, and document limitations. Future RAG, agent, MCP, or external-tool layers require explicit governance controls before implementation.

## 13. Expected Outcome

The expected outcome is a credible enterprise-style recommendation engineering project with two independently evaluated tracks: a RetailRocket behavior recommender and an ABO text/image similarity recommender. The project should demonstrate disciplined data handling, honest evaluation, and a clear path from local evidence to later production-oriented capabilities.
