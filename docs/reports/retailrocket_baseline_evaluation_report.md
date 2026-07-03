# RetailRocket Baseline Evaluation Report

## Decision Supported

The RetailRocket event-weighted global popularity baseline provides a measurable local reference point for the behavior recommendation track. This supports the Framework v2.1 **Baseline Complete** checkpoint for RetailRocket and contributes partial Evaluation evidence.

This report does not support production readiness, personalization quality, online performance, or business impact claims.

## Dataset Track

| Item | Value |
| --- | --- |
| Dataset track | RetailRocket event-based recommendation |
| Expected raw folder | `data/raw/RetailRocket_event-based/` |
| Primary raw file | `events.csv` |
| Supporting raw files | `item_properties_part1.csv`, `item_properties_part2.csv`, `category_tree.csv` |
| Output artifact | `data/processed/retailrocket_baseline_evaluation.json` |
| Artifact status | Local generated output; ignored by Git |

RetailRocket identifiers are track-local. They must not be joined to Amazon Berkeley Objects (ABO) identifiers.

## Baseline Method

The implemented baseline is an event-weighted global popularity recommender. It ranks RetailRocket `itemid` values by weighted event counts observed in the training portion of the event stream.

The implementation is intentionally simple, non-personalized, and explainable. It is a floor for later RetailRocket methods, not a final recommendation system.

## Event Weights

The current code documents these provisional baseline weights:

| Event | Weight |
| --- | ---: |
| `view` | 1.0 |
| `addtocart` | 3.0 |
| `transaction` | 5.0 |

These weights are useful for local baseline evidence. They should not be treated as optimized business weights without a separate validation and sensitivity analysis.

## Split and Evaluation Protocol

The local evaluator uses a temporal split derived from the observed timestamp range in `events.csv`.

| Protocol item | Current implementation |
| --- | --- |
| Split method | Timestamp-based train/test split |
| Train ratio | 0.8 |
| Evaluation target | Later visitor-item interactions after the split timestamp |
| Recommendation list | One global top-K list from training events |
| K | 10 in the current evaluation artifact |
| Metrics in artifact | HitRate@10 and Recall@10 |
| Large-file handling | Chunked CSV processing with default chunk size 100,000 |

The evaluator does not use ABO data and does not create cross-dataset metrics.

## Current Local Results

Source: `data/processed/retailrocket_baseline_evaluation.json`.

| Metric | Result |
| --- | ---: |
| Train events | 2,266,414 |
| Test events | 489,687 |
| Evaluated visitors | 275,826 |
| Split timestamp | 1,440,160,551,107 |
| Top K | 10 |
| HitRate@10 | 0.0081645675 |
| Recall@10 | 0.0073435373 |

The artifact records the recommended global item IDs as:

```text
461686, 5411, 187946, 257040, 309778, 370653, 7943, 369447, 298009, 48030
```

## Run Commands

Generate ranked top items:

```bash
python scripts/run_retailrocket_baseline.py
```

Generate evaluation metrics:

```bash
python scripts/evaluate_retailrocket_baseline.py
```

Run fixture/unit tests:

```bash
python -m pytest -q
```

## Interpretation

The low HitRate@10 and Recall@10 values are expected for a global non-personalized popularity baseline across a large event stream. The result is still useful because it establishes a reproducible baseline floor under the current temporal evaluation logic.

Future RetailRocket methods should be compared against this baseline under the same task, split policy, eligible-event rules, K value, and metric definitions.

## Limitations

- Results are local generated evidence, not a committed benchmark artifact.
- The baseline is global and does not use visitor history, sessions, item properties, recency decay, or personalization.
- Event weights are provisional and not tuned through a documented validation process.
- The evaluation currently reports HitRate@10 and Recall@10; it does not report NDCG, coverage, latency, confidence intervals, or segment-level diagnostics.
- The timestamp split is simple and should be reviewed before comparing advanced behavior models.
- No online A/B test, click-through test, conversion test, or production serving evidence exists.

## Open Gaps

- Add a reviewed split-policy note with exact rationale for the train ratio and timestamp cutoff.
- Add NDCG@K, catalog coverage, and latency measurements if they are required for the next RetailRocket evaluation stage.
- Add sensitivity analysis for event weights before treating them as approved business weights.
- Preserve item-property leakage controls if future methods use `item_properties_part1.csv`, `item_properties_part2.csv`, or `category_tree.csv`.
- Keep Delivery, Production, and Maintenance open until a separately approved service milestone exists.

## Production Readiness Statement

This report documents a local baseline and offline evaluation. It does not claim that the RetailRocket recommender is production-ready, deployed, monitored, personalized, or suitable for business operation without further validation.
