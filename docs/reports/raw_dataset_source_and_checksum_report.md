# Raw Dataset Source and Checksum Report

## Purpose

This report records local raw dataset file presence, file sizes, SHA256 checksums, and Git ignore evidence for the Data Gate Hardening milestone.

The report is evidence only. It does not modify raw data, commit raw data, implement FAISS, vector databases, APIs, MCP, deployment, monitoring, or production features.

Raw files are not committed and must not be committed.

## Run Context

- Generated at UTC: `2026-07-05T05:08:30Z`
- Reporter: `scripts/report_raw_dataset_sources.py`
- Hashing method: SHA256 with bounded chunked file reads

## Raw Dataset Tracks

| Track | Purpose | Local folder |
|---|---|---|
| RetailRocket event-based recommendation | Behavior/event recommendation | `data/raw/RetailRocket_event-based/` |
| Amazon Berkeley Objects text/image similarity | Product metadata, text, and image similarity | `data/raw/amazon_berkeley_text_images-based/` |

## Expected Raw Files for RetailRocket

| Path | Purpose |
|---|---|
| `data/raw/RetailRocket_event-based/events.csv` | Behavior/event recommendation raw events |
| `data/raw/RetailRocket_event-based/item_properties_part1.csv` | RetailRocket item properties part 1 |
| `data/raw/RetailRocket_event-based/item_properties_part2.csv` | RetailRocket item properties part 2 |
| `data/raw/RetailRocket_event-based/category_tree.csv` | RetailRocket category hierarchy |

## Expected Raw Files for ABO

| Path | Purpose |
|---|---|
| `data/raw/amazon_berkeley_text_images-based/abo-listings.tar` | ABO listing metadata archive |
| `data/raw/amazon_berkeley_text_images-based/abo-images-small.tar` | ABO small image archive |
| `data/raw/amazon_berkeley_text_images-based/README.md` | ABO local README/source notes |

## Local File Presence, Sizes, and Checksums

| Track | Path | Present | Size bytes | Size MiB | SHA256 |
|---|---|---:|---:|---:|---|
| RetailRocket event-based recommendation | `data/raw/RetailRocket_event-based/events.csv` | yes | 94237913 | 89.87 | `3745aa83238b1e6d44d8fda209807899f420084398f94ddf745f3cbcfecbf9e7` |
| RetailRocket event-based recommendation | `data/raw/RetailRocket_event-based/item_properties_part1.csv` | yes | 484315749 | 461.88 | `30aad5aeca58b2dc27dcc73e1708565f5818e45adb3eb57401f91e87355b0b81` |
| RetailRocket event-based recommendation | `data/raw/RetailRocket_event-based/item_properties_part2.csv` | yes | 408929907 | 389.99 | `d5e7d1a91dc40f522aeb596b267e6c87d8aed689a7192d12369cfb165eb987e5` |
| RetailRocket event-based recommendation | `data/raw/RetailRocket_event-based/category_tree.csv` | yes | 14454 | 0.01 | `94e865eb0a3d48cbbfe3b79079018dd92509315c88f5fd8d00d0b4b5af434f5b` |
| Amazon Berkeley Objects text/image similarity | `data/raw/amazon_berkeley_text_images-based/abo-listings.tar` | yes | 87480320 | 83.43 | `b7f7ceacb328fa5ab6e143b88e1f948443a877cfc95b67ff09c8ebabd50644e3` |
| Amazon Berkeley Objects text/image similarity | `data/raw/amazon_berkeley_text_images-based/abo-images-small.tar` | yes | 3253381120 | 3102.67 | `b766c6585c0f882bc64b2315171a0f81c020fc2f46204b2781075198367a01a8` |
| Amazon Berkeley Objects text/image similarity | `data/raw/amazon_berkeley_text_images-based/README.md` | yes | 4132 | 0.00 | `3f42e33f6636704b5670b6a198b0403b2f885cebe459d9620f84e7323a61bc71` |

## Raw Data Git Ignore Status

Repository `.gitignore` includes `data/raw/*` and preserves `data/raw/.gitkeep`.

| Path | Git ignored | Git tracked |
|---|---:|---:|
| `data/raw/RetailRocket_event-based/events.csv` | yes | no |
| `data/raw/RetailRocket_event-based/item_properties_part1.csv` | yes | no |
| `data/raw/RetailRocket_event-based/item_properties_part2.csv` | yes | no |
| `data/raw/RetailRocket_event-based/category_tree.csv` | yes | no |
| `data/raw/amazon_berkeley_text_images-based/abo-listings.tar` | yes | no |
| `data/raw/amazon_berkeley_text_images-based/abo-images-small.tar` | yes | no |
| `data/raw/amazon_berkeley_text_images-based/README.md` | yes | no |

## Source and Provenance Notes

- RetailRocket raw files are local copies for the event-based recommendation track.
- ABO raw files are local copies for the product metadata, text similarity, and image similarity track.
- The two dataset tracks are independent and must not be joined or treated as one catalog, user system, or business source.
- Upstream source URLs, exact download timestamps, and upstream-provided checksums are not fully captured in this report.
- Local SHA256 checksums in this report identify the files currently present in this workspace.

## Data Gate Impact

- Data Gate impact: local raw file presence, checksum evidence, and Git ignore evidence are available for expected raw files.
- This strengthens Data Gate evidence but does not by itself make the full Data Gate GO.
- Raw data must remain local under `data/raw/` and must not be committed.
- This report supports documentation and evidence hardening only.

## Limitations

- Checksums are local workspace checksums, not upstream authenticity guarantees.
- The report does not validate schemas, row counts, missing values, or model quality.
- The report does not prove source licensing compliance by itself.
- The report does not authorize FAISS, vector DB, API, MCP, deployment, monitoring, or production-readiness work.
