# Architecture

## 1. Purpose

This document defines the architecture direction for the Enterprise Multimodal E-Commerce Recommendation AI System. The current architecture is local-first, discovery-first, and deliberately split into two independent dataset tracks.

No model or Application Programming Interface (API) implementation is claimed as complete in this document. Baseline implementation remains gated by approved data contracts and evaluation protocols.

## 2. Architecture Principles

- Preserve dataset provenance and separation.
- Use bounded raw-data access patterns.
- Design canonical schemas before model code.
- Evaluate each track independently.
- Start with simple baselines before advanced models.
- Keep fixtures, raw data, processed data, model artifacts, and services separate.
- Add API and deployment layers only after baseline evidence exists.

## 3. Two-Track Architecture Overview

```text
Track A: RetailRocket Behavior Recommendation
Raw RetailRocket CSVs
  -> Safe ingestion
  -> Canonical interaction schema
  -> Temporal split
  -> Event-weighted recent popularity baseline
  -> RetailRocket evaluation

Track B: Amazon ABO Text/Image Similarity
ABO listings and image archives
  -> Safe archive inspection and controlled extraction planning
  -> Canonical product schema
  -> Product-to-image mapping
  -> Text metadata similarity baseline
  -> Later image similarity baseline
  -> ABO evaluation
```

The tracks remain independent. Their outputs may be presented as separate capabilities later, but their identifiers must not be joined or treated as shared.

## 4. Track A: RetailRocket Pipeline

### 4.1 Raw Inputs

RetailRocket raw CSV files are stored under `data/raw/RetailRocket_event-based/`:

- `events.csv`
- `item_properties_part1.csv`
- `item_properties_part2.csv`
- `category_tree.csv`

### 4.2 Safe Ingestion

Large CSV files must use header-only reads, streaming line counts, or chunked processing. Full-file DataFrame loads are not appropriate for raw RetailRocket files.

### 4.3 Canonical Interaction Schema

A future adapter should map discovered event rows into a documented interaction contract while preserving source fields and provenance. Core discovered source fields are:

```text
timestamp, visitorid, event, itemid, transactionid
```

Observed events are `view`, `addtocart`, and `transaction`.

### 4.4 Temporal Split

Behavior evaluation requires temporal train, validation, and test boundaries. Split logic must prevent future interactions from leaking into earlier recommendation decisions.

### 4.5 Baseline Direction

The first candidate is an event-weighted recent popularity recommender. Exact weights, recency windows, and fallback behavior remain provisional until the RetailRocket evaluation protocol is approved.

## 5. Track B: Amazon ABO Pipeline

### 5.1 Raw Inputs

ABO raw files are stored under `data/raw/amazon_berkeley_text_images-based/`:

- `abo-listings.tar`
- `abo-images-small.tar`
- `README.md`

### 5.2 Safe Archive Inspection and Extraction Planning

Archive processing must use bounded `tarfile` inspection or explicitly approved controlled extraction. The project must not extract all images or process all image content during discovery work.

### 5.3 Canonical Product Schema

A future ABO adapter should normalize approved listing fields such as:

```text
item_id, item_name, brand, bullet_point, product_type,
color, material, style, main_image_id, other_image_id
```

Field availability can vary by listing and locale, so canonicalization must define optional fields deliberately.

### 5.4 Product-to-Image Mapping

ABO listing image IDs may map to image metadata fields:

```text
image_id, path, height, width
```

This mapping belongs only to ABO. It must never be used as a bridge to RetailRocket items.

### 5.5 Baseline Direction

The initial candidate is text metadata similarity. Image similarity is a later controlled baseline or extension after the metadata path is evaluated.

## 6. No Dataset Merge Rule

```text
RetailRocket visitorid/itemid  -X-  ABO item_id/image_id
```

The datasets represent separate sources with unrelated identifiers. The architecture prohibits fabricated joins, shared customer assumptions, and claims that both datasets originate from one company or catalog.

## 7. Fixture and Validation Architecture

```text
Discovered raw schema
  -> Approved canonical contract
  -> Tiny deterministic fixture
  -> Track-specific validator
  -> Adapter tests and CI checks
```

`data/sample/` should eventually contain separate RetailRocket and ABO fixture folders. Fixtures are test assets, not training datasets.

## 8. Future API and Service Layer Concept

After adapters, validation, baselines, and evaluation evidence are stable, an API layer may expose separate capabilities such as:

- Behavior-based top-K recommendation.
- Text-based similar-product retrieval.
- Image-based similar-product retrieval.
- Health and observability endpoints.

The API must keep dataset provenance explicit and must not imply unsupported cross-track personalization.

## 9. Future Multimodal Extension Path

The ABO track may progress from metadata similarity to image similarity and then to evaluated text-image retrieval or multimodal ranking. Any added method must be compared with the corresponding ABO baseline under the same protocol.

## 10. Future Enterprise Architecture Path

```text
Track-specific raw sources
  -> Safe ingestion and validation
  -> Provenance-aware processed artifacts
  -> Approved baselines and advanced models
  -> Track-specific retrieval or ranking services
  -> API gateway and observability
  -> Governed business extensions when justified
```

Possible later extensions include vector search, monitoring, experiment tracking, governed Retrieval-Augmented Generation (RAG), controlled agent workflows, and Model Context Protocol (MCP) tools. These are not current-phase requirements.

## 11. Local-First Direction

Current work should run locally with WSL2, Visual Studio Code, Git, Python, and pytest. Docker, cloud deployment, and Kubernetes remain later maturity steps after adapters, tests, and baseline evidence are stable.

## 12. Architecture Acceptance Criteria

The architecture is accepted when it:

1. Defines separate RetailRocket and ABO pipelines.
2. Makes bounded raw-data access explicit.
3. Prohibits cross-dataset joins.
4. Separates fixture contracts from raw datasets.
5. Gates model and API work behind approved protocols and evidence.
6. Defines a realistic local-first path to later enterprise capabilities.
