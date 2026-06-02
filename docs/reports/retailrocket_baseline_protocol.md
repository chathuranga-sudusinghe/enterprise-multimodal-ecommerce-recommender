# RetailRocket Baseline Protocol

## 1. Purpose

This protocol defines the evidence and approval requirements for the first RetailRocket behavior-based recommendation baseline. It must be reviewed and approved before the final baseline implementation is coded.

The protocol applies only to the `RetailRocket_event-based` dataset track. Amazon Berkeley Objects (ABO) is an independent text/image product-similarity track and must not be merged with RetailRocket.

## 2. Dataset Track

| Attribute | Value |
| --- | --- |
| Track | `RetailRocket_event-based` |
| Raw folder | `data/raw/RetailRocket_event-based/` |
| Primary source | `events.csv` |
| Supporting sources | `item_properties_part1.csv`, `item_properties_part2.csv`, `category_tree.csv` |
| Recommendation type | Behavior and event-based item recommendation |

RetailRocket item and visitor identifiers belong only to this track. They must not be joined to ABO `item_id`, `main_image_id`, `other_image_id`, or `image_id` values.

## 3. Business Task

Given the interaction history available before a recommendation timestamp, produce a ranked top-K list of RetailRocket item identifiers that are likely to be relevant in a later evaluation window.

The first baseline should provide a simple, explainable reference point for later personalized or ranking methods. It is not intended to represent the final recommendation system.

## 4. Input Schema

The baseline input is derived from RetailRocket events with the discovered source schema:

| Column | Meaning | Notes |
| --- | --- | --- |
| `timestamp` | Interaction time | Raw Unix milliseconds |
| `visitorid` | RetailRocket visitor identifier | Track-local only |
| `event` | Interaction type | Allowed values are listed below |
| `itemid` | RetailRocket item identifier | Track-local only |
| `transactionid` | Transaction reference | Nullable for non-transaction events |

Allowed RetailRocket event values:

- `view`
- `addtocart`
- `transaction`

A later implementation may use an approved canonical interaction adapter, but it must preserve the semantics and provenance of these RetailRocket source fields.

## 5. Output Contract

The baseline should return a ranked top-K list of RetailRocket item identifiers.

The approved implementation contract should define:

- Requested `top_k` value.
- Eligible item rules.
- Ranking score representation.
- Deterministic tie-breaking behavior.
- Recency-window configuration.
- Fallback behavior when no eligible scored items exist.
- Whether diagnostic scores are returned internally for evaluation.

No ABO identifiers or product metadata are part of this output contract.

## 6. Candidate Baseline

**Event-Weighted Recent Popularity Recommender**

The candidate baseline ranks eligible RetailRocket items using interaction evidence observed before the recommendation timestamp. The baseline should remain understandable, reproducible, and computationally modest.

The final implementation should consider two signals:

1. Event importance.
2. Interaction recency.

## 7. Provisional Event-Weight Policy

Event weights are provisional until explicitly approved. The implementation must not lock final numeric values before the business task, temporal split, relevance definition, and validation procedure are approved.

The initial policy direction is:

| Event | Provisional Relative Priority | Rationale |
| --- | --- | --- |
| `view` | Lowest positive signal | Indicates product interest |
| `addtocart` | Stronger positive signal | Indicates higher purchase intent |
| `transaction` | Strongest positive signal | Indicates completed purchase behavior |

Weight selection should be documented and tested through the validation protocol. Numeric candidates may be compared during protocol review, but no value should be treated as final merely because it appears in exploratory code.

## 8. Temporal Split Requirement

Evaluation must use a temporal train, validation, and test split.

```text
Earlier events -> training window
Later events   -> validation window
Latest events  -> test window
```

Before implementation, approve:

- Exact cutoff timestamps.
- Minimum history requirements where applicable.
- Evaluation-window length.
- Eligible items and visitors.
- Recency-window behavior.
- K values for reported metrics.

## 9. Leakage Prevention Rules

- Compute popularity evidence using events available before the recommendation timestamp only.
- Do not use validation or test interactions to fit weights, recency windows, or tie-breaking rules.
- Keep the test window isolated until protocol decisions are finalized.
- Do not use future item-property snapshots for earlier recommendation decisions.
- Document any filtering applied before split construction.
- Preserve deterministic processing so results can be reproduced.

## 10. Evaluation Metrics

| Metric | Purpose |
| --- | --- |
| Recall@K | Measures how many relevant future items appear in the top-K list |
| Hit Rate@K | Measures whether at least one relevant item appears in the top-K list |
| NDCG@K | Rewards relevant items appearing higher in the ranked list |
| Coverage | Measures how much of the eligible RetailRocket catalog can be recommended |
| Latency | Measures recommendation generation time under a documented local setup |

Metrics must be reported with the approved K values, split definitions, eligibility rules, and runtime assumptions.

## 11. Cold-Start and Fallback Behavior

The implementation should define conservative fallback behavior for cases such as:

- A visitor has no prior history.
- No item meets a recency-window condition.
- A requested `top_k` exceeds the eligible catalog size.
- Input events are empty after validation and filtering.

The expected first fallback direction is deterministic RetailRocket popularity computed from the approved training evidence. Fallback behavior must remain within the RetailRocket track and must not use ABO data.

## 12. Implementation Readiness Checklist

Implementation may begin only when:

- [ ] The RetailRocket business task is approved.
- [ ] The input and output contracts are approved.
- [ ] The canonical interaction adapter decision is documented.
- [ ] Temporal train, validation, and test cutoffs are approved.
- [ ] Leakage controls are approved.
- [ ] Eligible visitor and item rules are approved.
- [ ] Relevance criteria are approved.
- [ ] K values and metrics are approved.
- [ ] Provisional event-weight selection procedure is approved.
- [ ] Recency-window behavior is approved.
- [ ] Cold-start and fallback rules are approved.
- [ ] Tiny deterministic RetailRocket fixtures are accepted for tests.

## 13. Tests Required Before Implementation Approval

The rebuilt baseline test suite should cover:

- RetailRocket input fields: `timestamp`, `visitorid`, `event`, `itemid`, and `transactionid`.
- Allowed event values: `view`, `addtocart`, and `transaction`.
- Clear rejection or handling of unsupported event values according to the approved contract.
- Event-weight application using approved provisional weights.
- Recency-window behavior.
- Deterministic ranking and tie-breaking.
- `top_k` limits.
- Empty-event fallback behavior.
- Visitor cold-start fallback behavior.
- Temporal leakage prevention.
- Separation from ABO identifiers and fixtures.
- Latency measurement hooks suitable for later evaluation.

## 14. Advanced Model Comparison Rule

Any advanced RetailRocket method must be compared against this baseline using the same business task, temporal split, eligibility rules, leakage controls, K values, and metrics. Architectural complexity alone is not evidence of improvement.

ABO methods require their own product-similarity baseline and evaluation protocol. Results from the two tracks must remain separate.
