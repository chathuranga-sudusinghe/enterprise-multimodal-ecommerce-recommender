# Evaluation Plan

## 1. Purpose

This document defines the evaluation direction for the Enterprise Multimodal E-Commerce Recommendation AI System. RetailRocket and Amazon Berkeley Objects (ABO) solve different recommendation tasks and must be evaluated separately.

No evaluation results are claimed in this document. Baseline implementation remains paused until task definitions, fixture contracts, split rules, metrics, and validation protocols are approved.

## 2. Evaluation Principles

- Use one explicit business task per dataset track.
- Prevent train-test leakage.
- Compare advanced methods with the corresponding baseline under the same protocol.
- Report quality, coverage, latency, assumptions, and limitations.
- Keep metric definitions reproducible.
- Do not create one combined score across unrelated datasets.

## 3. RetailRocket Evaluation Protocol Direction

### 3.1 Task

Evaluate top-K item recommendation from observed visitor behavior signals. The protocol should define what history is available at recommendation time and what future interaction counts as a relevant outcome.

### 3.2 Temporal Split

Use a temporal train, validation, and test split. Exact cutoff timestamps must be approved before implementation.

```text
Past interactions -> training window
Later interactions -> validation window
Latest interactions -> test window
```

### 3.3 Leakage Prevention

- Do not use future events when computing earlier popularity scores.
- Fit recency windows and event-weight choices using training and validation data only.
- Keep test data isolated until the protocol is finalized.
- Prevent item-property snapshots from leaking later information into earlier decisions.

### 3.4 Baseline Candidate

The initial candidate is an event-weighted recent popularity recommender. Event weights remain provisional until protocol approval. The protocol should document weight selection, recency windows, fallback rules, and tie-breaking behavior.

### 3.5 Candidate Metrics

| Metric | Purpose |
| --- | --- |
| Recall@K | Measures how many relevant future items appear in the top-K list |
| Hit Rate@K | Measures whether at least one relevant item appears in the top-K list |
| NDCG@K | Rewards relevant items appearing higher in the ranking |
| Coverage | Measures how much of the eligible catalog can be recommended |
| Latency | Measures recommendation response time under a defined local setup |

Optional later metrics may include diversity, novelty, and segment-level diagnostics where defensible.

## 4. Amazon ABO Evaluation Protocol Direction

### 4.1 Task

Evaluate product-to-product similarity retrieval from ABO catalog metadata, followed later by image-based similarity retrieval. The protocol should define query products, candidate products, eligibility filters, and relevance checks.

### 4.2 Baseline Candidate

The first ABO candidate is metadata/text content similarity using approved listing fields. A later image-similarity baseline or extension may use controlled image features after the text path is stable.

### 4.3 Candidate Metrics

| Metric | Purpose |
| --- | --- |
| Product-type or category consistency | Checks whether retrieved items remain meaningfully related where labels are usable |
| Retrieval quality | Measures relevance under an approved labeled or rule-based evaluation set |
| Diversity | Measures whether retrieved items are not needlessly repetitive |
| Coverage | Measures how much of the eligible ABO catalog participates in retrieval |
| Latency | Measures similar-product retrieval time under a defined local setup |

Image-text retrieval quality may be added later if multimodal experiments are approved.

## 5. No Combined Cross-Dataset Metric

RetailRocket and ABO use unrelated identifiers, different source structures, and different recommendation tasks. Their metrics must be reported in separate sections. A combined score would be misleading.

## 6. Validation Evaluation

Before model evaluation, validate:

- Required source and canonical fields.
- RetailRocket observed event values.
- RetailRocket timestamp handling and temporal boundaries.
- ABO optional-field handling.
- ABO product-to-image mappings.
- Bounded raw-data processing behavior.
- Deterministic fixture behavior in tests and CI.

## 7. Latency and System Measurement

Latency should be measured with documented local hardware assumptions and dataset sizes. Separate measurements should be recorded for:

- Adapter processing where relevant.
- RetailRocket recommendation generation.
- ABO text similarity retrieval.
- ABO image similarity retrieval later.

Memory usage should also be reviewed for raw-data adapters because the source files and archives are large.

## 8. Baseline Comparison Rule

Advanced methods must beat the corresponding baseline using the same task, data eligibility rules, splits, metrics, and measurement process.

| Track | Baseline Reference | Valid Advanced Comparison Direction |
| --- | --- | --- |
| RetailRocket | Event-weighted recent popularity | Personalized or ranking methods evaluated on the same temporal protocol |
| ABO | Metadata/text product similarity | Image or multimodal methods evaluated on the same ABO retrieval protocol |

No advanced model should be presented as better based only on architectural complexity.

## 9. Evaluation Reporting Plan

Each evaluation report should state:

1. Dataset track and source version.
2. Task definition.
3. Eligibility and filtering rules.
4. Split or retrieval-set construction.
5. Leakage controls.
6. Baseline configuration.
7. Metrics and K values where applicable.
8. Runtime environment and latency method.
9. Results, limitations, and known failure cases.

## 10. Future Evaluation Scope

Potential later evaluation areas include:

- ABO image-text retrieval quality.
- Cold-start product retrieval quality.
- Fairness and bias diagnostics where appropriate.
- Model drift and data-quality drift.
- API latency and reliability after service implementation.
- Governed Retrieval-Augmented Generation (RAG) groundedness if RAG is justified later.
- Agent task success and tool-use accuracy if agentic workflows are justified later.
- Cost tracking for hosted or cloud components if introduced later.

## 11. Evaluation Acceptance Criteria

The evaluation plan is ready for implementation when:

1. RetailRocket and ABO tasks are approved separately.
2. RetailRocket temporal split rules and leakage controls are explicit.
3. RetailRocket provisional event-weight selection is documented without premature locking.
4. ABO query, candidate, and relevance rules are explicit.
5. Track-specific metrics are approved.
6. No combined cross-dataset metric is used.
7. Baseline comparison gates are clear.
