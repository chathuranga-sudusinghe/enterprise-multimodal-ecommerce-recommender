# AGENTS.md

## 1. Project Identity

- Project name: Enterprise Multimodal E-Commerce Recommendation AI System.
- This is an enterprise-style AI/ML engineering project, not a toy demo or notebook-only project.
- The current recommendation scope covers behavior-based recommendation, product text similarity, and product image similarity.
- Video recommendation is excluded from the current project scope.
- Build in small, evidence-based phases. Do not add advanced systems before the data contracts, evaluation protocols, and baseline evidence are approved.

## 2. Current Dataset Strategy

The project uses two independent real-world dataset tracks.

### Track A: RetailRocket Event-Based Recommendation

- Dataset folder: `data/raw/RetailRocket_event-based/`
- Purpose: behavior and event-based recommendation.
- Confirmed raw files:
  - `events.csv`
  - `item_properties_part1.csv`
  - `item_properties_part2.csv`
  - `category_tree.csv`
- Confirmed event values include `view`, `addtocart`, and `transaction`.

### Track B: Amazon Berkeley Objects Text/Image Similarity

- Dataset folder: `data/raw/amazon_berkeley_text_images-based/`
- Purpose: product metadata, text, and image-based product similarity recommendation.
- Confirmed raw files:
  - `abo-listings.tar`
  - `abo-images-small.tar`
  - `README.md`
- Confirmed listing metadata includes fields such as `item_id`, `item_name`, `brand`, `bullet_point`, `product_type`, `main_image_id`, and `other_image_id`.

## 3. Dataset Separation Rules

- Do not merge RetailRocket and Amazon Berkeley Objects (ABO).
- Do not create cross-dataset joins.
- Do not pretend both datasets come from the same company, catalog, users, or business system.
- Do not treat RetailRocket `visitorid` or `itemid` values as ABO `item_id` or `image_id` values.
- Do not invent mappings between RetailRocket items and ABO listings or images.
- Evaluate each track separately with a task-appropriate protocol.
- Any later system-level composition must preserve dataset provenance and explicitly avoid fabricated identity links.

## 4. Current Scope

### In Scope

- Safe dataset discovery.
- Documentation restructuring based on discovery evidence.
- Tiny deterministic fixtures for tests, examples, and CI.
- Safe raw-data adapters.
- Track-specific schema validation.
- Separate baseline definitions later.
- Separate evaluation protocols for each track.
- Behavior, text, and image recommendation only.

### Out of Scope for the Current Phase

- Video recommendation.
- Full Retrieval-Augmented Generation (RAG) implementation.
- Agentic workflows.
- Model Context Protocol (MCP) server or client implementation.
- Contextual bandit optimization.
- API implementation.
- Model training before protocol approval.
- Hardcoded baseline weights before protocol approval.
- Cloud deployment.
- Kubernetes deployment.
- Synthetic joins across dataset tracks.

## 5. Data Safety Rules

- Do not commit raw datasets.
- Keep raw dataset files under `data/raw/`, which must remain ignored by Git.
- Do not load large raw files fully into memory.
- For RetailRocket large CSV files, use only:
  - Header-only reads such as `pd.read_csv(path, nrows=0)`.
  - Streaming line counts.
  - Chunked reads such as `pd.read_csv(path, chunksize=100_000)`.
- Do not concatenate RetailRocket chunks into one full DataFrame unless explicitly approved for a proven safe subset.
- For ABO archives, use bounded `tarfile` inspection or controlled extraction only.
- Do not extract all ABO images unless explicitly approved.
- Do not process all images or generate embeddings during discovery work.
- Do not write generated files into `data/raw/`.
- Keep dataset provenance, attribution, and license requirements visible in documentation.

## 6. `data/sample/` Rules

- Treat `data/sample/` as tiny deterministic fixtures only.
- Fixtures exist for unit tests, examples, and CI. They are not the primary ML dataset.
- Fixture files must mirror discovered real schemas for their corresponding track.
- Keep RetailRocket fixtures separate from ABO fixtures.
- The old unified synthetic `products.csv`, `users.csv`, and `events.csv` design is deprecated.
- Do not invent demographic user profiles, cross-track identifiers, or unsupported fields.
- Keep fixtures small, readable, deterministic, and safe to commit.

## 7. Documentation Rules

- Rebuild `docs/01_project_foundation.md` through `docs/07_deployment_plan.md` using discovery reports as source evidence.
- Keep these discovery reports unchanged during normal restructuring:
  - `docs/reports/retailrocket_dataset_discovery.md`
  - `docs/reports/abo_dataset_discovery.md`
  - `docs/reports/dataset_discovery_summary.md`
  - `docs/reports/full_repository_alignment_audit.md`
- Avoid synthetic-data-first wording.
- Clearly distinguish raw datasets, deterministic fixtures, future processed datasets, and future model artifacts.
- Clearly separate implemented features from planned features.
- Do not claim that planned models, APIs, deployments, or governance controls already exist.
- Keep documentation professional, recruiter-readable, and engineer-readable.

## 8. Baseline Rules

- Model coding is paused until documentation and fixture contracts are approved.
- Do not hardcode event weights before task, split, metrics, recency policy, and validation protocol approval.
- RetailRocket baseline candidate: event-weighted recent popularity recommender.
- ABO baseline candidate: content-based product similarity recommender.
- Define separate business tasks and evaluation protocols for each track.
- Compare advanced RetailRocket methods against the RetailRocket baseline under the same protocol.
- Compare advanced ABO methods against the ABO baseline under the same protocol.
- Do not claim that an advanced method is better unless evaluation proves improvement.
- API implementation must not start before baseline evidence exists.

## 9. Code Rules

- Use clean, modular Python.
- Use `pathlib.Path` instead of hardcoded absolute paths.
- Use logging instead of unnecessary `print()` statements.
- Use small, focused functions.
- Add concise docstrings and helpful comments where they improve clarity.
- Use Pydantic where schema boundaries or API contracts need it.
- Keep configuration safe and environment-aware.
- Do not commit secrets, tokens, credentials, `.env` files, or private local paths.
- Do not add dependencies unless they are necessary for the requested task.
- Keep WSL2 Ubuntu and VS Code compatibility in mind.

## 10. Testing Rules

- Rebuild tests around the new track-specific fixtures.
- Maintain separate RetailRocket tests and ABO tests.
- Replace or quarantine old synthetic tests that depend on deprecated schemas.
- Add or update tests when code behavior changes.
- Use pytest for Python tests.
- Do not claim tests passed unless they were actually run.
- If tests are not run, state why.
- Add memory-safety tests or review checks where raw-data adapters could accidentally perform full-file loads.

## 11. Git and Codex Operating Rules

- Work only on the files requested by the user.
- Do not modify unrelated files.
- Do not restructure the repository unless explicitly asked.
- Do not delete existing work unless explicitly asked and confirmed.
- Keep changes small, focused, and reviewable.
- Review `git status` and `git diff --stat` after edits.
- Report tests run or explain why tests were not run.
- Do not commit or push unless explicitly asked.
- Do not run destructive commands such as `git reset --hard`, `git clean -fd`, force push, or file deletion unless explicitly requested and confirmed.
- Preserve discovery reports as evidence during normal restructuring work.
