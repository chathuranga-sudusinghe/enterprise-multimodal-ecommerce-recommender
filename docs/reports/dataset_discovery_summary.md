# Dataset Discovery Summary

## Confirmed Two-Track Dataset Strategy

The project uses two independent real-world dataset tracks. They must not be merged, and their customer or product identifiers must not be treated as shared identifiers.

| Track | Dataset | Purpose | Initial Baseline Candidate |
| --- | --- | --- | --- |
| A | `RetailRocket_event-based` | Behavior and event-based recommendation | Event-weighted recent popularity recommender |
| B | `amazon_berkeley_text_images-based` | Product metadata, text, and image-based similarity recommendation | Content-based product similarity recommender |

## Dataset Separation Rule

- RetailRocket visitor and item identifiers belong only to the RetailRocket track.
- Amazon Berkeley Objects listing and image identifiers belong only to the ABO track.
- Do not create synthetic joins between tracks.
- Evaluate each track against a task-appropriate protocol before considering later system-level composition.

## Scope Boundary

Video recommendation is excluded from the current project scope. Current work focuses on behavior, text, and image-based recommendation only. ABO spin, turntable, 360-degree, and 3D assets are not part of the current implementation plan.

## Safe Baseline Direction

- RetailRocket: inspect event values, timestamp ranges, and item-property structure before selecting provisional event weights. The first candidate is an event-weighted recent popularity recommender.
- ABO: inspect multilingual listing fields and image identifier mappings before selecting metadata features. The first candidate is content-based product similarity.
- Advanced methods must be evaluated against their corresponding baseline using the same business task and evaluation protocol.

## Recommended Documentation Restructuring

1. Update system scope to describe the two-track dataset strategy.
2. Update architecture to separate behavior-based and content/image-based pipelines.
3. Update data design with discovered raw schemas and canonical mapping decisions.
4. Update evaluation planning with one protocol per dataset track and leakage controls.
5. Update security and governance notes with dataset provenance, attribution, and raw-data handling boundaries.
6. Keep model implementation paused until the discovery reports are reviewed.

## Generated Discovery Reports

- [`retailrocket_dataset_discovery.md`](retailrocket_dataset_discovery.md)
- [`abo_dataset_discovery.md`](abo_dataset_discovery.md)
