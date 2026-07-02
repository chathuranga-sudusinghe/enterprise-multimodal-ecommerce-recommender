# Framework v2.1 Checkpoint Audit

## Summary decision

The repository is best assessed as a Portfolio-level, local AI/ML engineering project with real-data discovery, track-specific fixtures, baseline implementations, bounded evaluation artifacts, and one advanced ABO CLIP similarity experiment. The strongest completed lifecycle checkpoint is Baseline, with partial Evaluation evidence. Delivery, Production, and Maintenance remain open because there is no implemented API, deployment stack, monitoring system, rollback process, or real operational evidence. RetailRocket and Amazon Berkeley Objects (ABO) are correctly treated as independent dataset tracks in the current README, AGENTS guidance, sample data layout, and several reports. Some core lifecycle docs are stale because they still describe baseline, image, agent, MCP, and deployment work as future-only despite later local implementation evidence.

## Last completed checkpoint

The last strongest completed checkpoint is **Baseline Complete**.

Evidence includes the RetailRocket event-weighted popularity baseline in `src/ecommerce_recommender/models/baseline.py`, the RetailRocket runner and evaluator in `scripts/run_retailrocket_baseline.py` and `scripts/evaluate_retailrocket_baseline.py`, the ABO TF-IDF text baseline in `src/ecommerce_recommender/models/abo_text_similarity.py`, and the ABO RGB histogram image baseline in `src/ecommerce_recommender/models/abo_image_similarity.py`. Local processed evidence exists for RetailRocket baseline evaluation and ABO method comparison under `data/processed/`, but these outputs are ignored local artifacts rather than committed release artifacts. Evaluation is therefore **Partial**, not the last fully completed checkpoint, because ABO evaluation is a bounded one-query metadata proxy and there is no comprehensive multi-query, human-labeled, online, or production evaluation.

## Stage-by-stage audit

| Stage | Status | Evidence found | Gaps | Recommended next action |
|---|---|---|---|---|
| Problem | Complete | `README.md`, `AGENTS.md`, `docs/01_project_foundation.md`, and `docs/02_system_scope.md` define behavior recommendation and ABO product similarity as separate tasks; video and cross-dataset joins are excluded. | Production users, service surfaces, business thresholds, and formal SLOs are not defined. | Keep the problem statement stable and link future work to separate RetailRocket and ABO tasks. |
| Data | Complete | Discovery reports in `docs/reports/retailrocket_dataset_discovery.md`, `docs/reports/abo_dataset_discovery.md`, and `docs/reports/dataset_discovery_summary.md`; fixtures under `data/sample/retailrocket/` and `data/sample/amazon_berkeley_objects/`; loaders and validators under `src/ecommerce_recommender/data/`. | Versioned processed-data contracts, checksums, lineage manifests, and automated real-data quality reports are incomplete or not formalized. | Add evidence-backed processed artifact manifests and schema/version contracts before expanding model claims. |
| Baseline | Complete | RetailRocket popularity baseline, ABO TF-IDF text baseline, ABO RGB histogram image baseline, runners, focused tests, and local processed outputs. | RetailRocket event weights are still labeled provisional; some protocol docs predate the implemented state. | Reconcile baseline docs with implemented evidence and record baseline configuration decisions explicitly. |
| Advanced AI | Partial | ABO CLIP similarity exists in `src/ecommerce_recommender/models/abo_clip_similarity.py`; runner exists in `scripts/run_abo_clip_similarity.py`; local CLIP output and proxy comparison exist under `data/processed/`; optional OpenAI explanation path is documented. | No advanced RetailRocket model; no validated broad CLIP superiority claim; CLIP depends on local dependency/model availability; no fine-tuning or production model lifecycle. | Treat CLIP as a bounded ABO experiment until evaluation is strengthened. |
| Evaluation | Partial | RetailRocket temporal evaluation script and local result `data/processed/retailrocket_baseline_evaluation.json`; ABO proxy evaluator in `src/ecommerce_recommender/evaluation/abo_proxy_similarity.py`; local `data/processed/abo_similarity_proxy_evaluation.json`. | ABO uses one bounded query and product-type proxy relevance; no human labels, confidence intervals, error analysis, latency/resource benchmark, online test, or production feedback. | Build a representative ABO multi-query proxy evaluation report with clear limitations. |
| Delivery | Open | CLI scripts exist for discovery, cleaning, baselines, CLIP, evaluation, and local orchestration; README provides commands. | `src/ecommerce_recommender/api/` is only a package placeholder; no FastAPI service, vector index, response contract, Docker image, CI/CD workflow, or delivery readiness checklist implementation. | Do not start API delivery until evaluation evidence and artifact contracts are approved. |
| Production | Open | README explicitly states the project is not deployed as a production API or service; docs describe deployment as future work. | No production deployment, monitoring, alerting, auth, rate limiting, service SLOs, incident runbooks, cloud/Kubernetes, or live operation evidence. | Keep production claims out of README and docs until real deployment evidence exists. |
| Maintenance | Open | `AI_USAGE.md`, `docs/06_security_governance.md`, and `docs/07_deployment_plan.md` discuss future governance, rollback, and maintenance direction. | No implemented monitoring, drift checks, scheduled retraining, model registry, ownership rotation, rollback automation, or recovery drills. | Convert future maintenance direction into checklists only after a delivery surface exists. |

## Framework artifact audit

| Artifact | Status | Evidence path | Gap or issue | Action |
|---|---|---|---|---|
| problem definition | Complete | `README.md`; `docs/01_project_foundation.md`; `docs/02_system_scope.md` | Needs more explicit production user/persona and business threshold detail later. | Keep separate RetailRocket and ABO task definitions. |
| success metrics and risks | Partial | `docs/01_project_foundation.md`; `docs/05_evaluation_plan.md`; `docs/reports/current_project_status.md` | Metrics are defined directionally; accepted thresholds and risk owners are absent. | Add thresholds after stronger evaluation evidence. |
| dataset source manifest | Partial | `docs/reports/dataset_discovery_summary.md`; `docs/reports/retailrocket_dataset_discovery.md`; `docs/reports/abo_dataset_discovery.md`; `data/sample/README.md` | No formal manifest file with source versions, checksums, licenses, and processed artifact lineage. | Create a formal source and artifact manifest in the next milestone. |
| data readiness checklist | Partial | `AGENTS.md`; `docs/04_data_design.md`; discovery reports | Data safety rules exist, but readiness is not captured as a signed checklist with pass/fail evidence. | Add checklist fields for schemas, fixtures, bounded reads, and processed outputs. |
| baseline design | Complete | `docs/reports/retailrocket_baseline_protocol.md`; `docs/reports/abo_text_baseline_protocol.md`; `docs/reports/abo_image_baseline_protocol.md`; `docs/reports/abo_image_baseline_implementation_design.md` | Some protocol language still says future implementation where code now exists. | Reconcile docs without changing discovery reports. |
| baseline evaluation report | Partial | `data/processed/retailrocket_baseline_evaluation.json`; `data/processed/abo_similarity_proxy_evaluation.json`; `docs/reports/current_project_status.md` | Evaluation outputs are ignored local artifacts; no durable reviewed baseline evaluation report per track. | Promote reproducible, reviewed baseline results into a report with limitations. |
| advanced solution justification | Partial | `README.md`; `docs/reports/current_project_status.md`; `src/ecommerce_recommender/models/abo_clip_similarity.py` | CLIP justification exists by implementation and result, but the evidence is bounded and ABO-only. | Keep CLIP positioned as an experiment until broader evaluation exists. |
| evaluation report | Partial | `docs/reports/current_project_status.md`; `data/processed/abo_similarity_proxy_evaluation.json` | No complete framework evaluation report covering assumptions, sample selection, uncertainty, latency, and failure analysis. | Write a project-specific evaluation hardening report after data manifest work. |
| delivery readiness checklist | Open Gap | `docs/07_deployment_plan.md` | Delivery plan is directional; no implemented service or readiness checklist evidence. | Defer until evaluation and artifact contracts are stable. |
| deployment readiness checklist | Open Gap | `docs/07_deployment_plan.md` | No Docker, FastAPI, CI/CD, cloud, Kubernetes, or release checklist implementation. | Keep marked open. |
| monitoring and maintenance plan | Partial | `docs/06_security_governance.md`; `docs/07_deployment_plan.md`; `AI_USAGE.md` | Directional plan only; no monitoring implementation or maintenance runbook. | Revisit after delivery design exists. |
| rollback and recovery plan | Partial | `docs/07_deployment_plan.md` | Rollback is conceptual; no versioned artifacts, registry, or recovery test. | Keep as future operational requirement. |
| AI-assisted development disclosure | Complete | `AI_USAGE.md`; README disclosure section | Disclosure is clear and appropriately does not imply production readiness. | Keep current and update only when tool/process evidence changes. |
| `docs/framework/` evidence pack | Open Gap | Not present | `docs/framework/` does not exist, so there is no dedicated project-specific framework evidence pack. | Create only after deciding the exact artifact structure and evidence sources. |

## README claim check

| README claim | Status | Evidence | Notes |
|---|---|---|---|
| Two independent real-world dataset tracks are used. | Supported | `AGENTS.md`; discovery reports; `data/sample/README.md` | Strongly aligned with repository rules and fixtures. |
| Repository demonstrates data inspection, reusable preparation, baselines, multimodal similarity, offline evaluation, and local orchestration. | Partially supported | `notebooks/03_abo_data_inspection.ipynb`; `scripts/`; `src/`; `data/processed/` | Supported locally, but evaluation and orchestration are bounded and not production-grade. |
| The project is not currently deployed as a production API or service. | Supported | No API implementation beyond package placeholders; `docs/07_deployment_plan.md` future-only | This limitation is accurate and important. |
| RetailRocket data discovery and behavior baseline are implemented. | Supported | `scripts/discover_retailrocket_dataset.py`; `src/ecommerce_recommender/models/baseline.py`; `scripts/run_retailrocket_baseline.py` | Baseline weights remain provisional in code comments. |
| RetailRocket temporal offline evaluation is implemented. | Supported | `scripts/evaluate_retailrocket_baseline.py`; `data/processed/retailrocket_baseline_evaluation.json` | Evaluation exists, but production recommendation quality is not established. |
| ABO inspection and reusable cleaning are implemented. | Supported | `notebooks/03_abo_data_inspection.ipynb`; `src/ecommerce_recommender/data/clean_abo_products.py`; `scripts/clean_abo_products.py` | Bounded raw archive handling is consistent with project rules. |
| ABO TF-IDF, RGB histogram, and CLIP similarity are implemented. | Supported | `src/ecommerce_recommender/models/abo_text_similarity.py`; `abo_image_similarity.py`; `abo_clip_similarity.py`; runners in `scripts/` | CLIP requires PyTorch/Transformers and model availability. |
| ABO metadata-based proxy evaluation is implemented. | Supported | `src/ecommerce_recommender/evaluation/abo_proxy_similarity.py`; `scripts/evaluate_abo_similarity_methods.py` | Proxy relevance must not be read as real user satisfaction. |
| Lightweight agentic recommendation demo and MCP-style controlled interfaces are implemented. | Partially supported | `src/ecommerce_recommender/agents/`; `src/ecommerce_recommender/mcp_tools/`; `data/processed/abo_agentic_recommendation_demo.json` | Correct only as a local abstraction/demo; not a full MCP server/client or autonomous agent system. |
| FastAPI, vector database, monitoring, and deployment are not implemented. | Supported | No substantive API, vector DB, monitoring, Docker, or deployment implementation found | This is accurate. |
| Current full test suite contains 90 passing tests. | Partially supported | README says 90; `AI_USAGE.md` and `docs/reports/current_project_status.md` cite 99 passed in a `.venv` command | Current local default `python -m pytest -q` failed because `torch` is missing. README test count appears stale or environment-specific. |
| CLIP outperforms TF-IDF and RGB histogram in the shown ABO proxy table. | Partially supported | `data/processed/abo_similarity_proxy_evaluation.json` | Supported only for one bounded query/sample under product-type proxy relevance. |
| Missing limitation statements | Partial | README has a strong limitations section | Add explicit limitation that processed artifacts are ignored local outputs and that default Python may not have all dependencies installed. |

## Reproducibility and test check

- Commands found:
  - `python -m pip install -r requirements.txt`
  - `python -m pip install -e . --no-deps`
  - `python scripts/run_retailrocket_baseline.py`
  - `python scripts/evaluate_retailrocket_baseline.py`
  - `python scripts/clean_abo_products.py --max-records 1000`
  - `python scripts/clean_abo_products.py --max-records 5000 --output data/processed/abo_clean_products_5k.jsonl`
  - `python scripts/run_abo_text_baseline.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5`
  - `python scripts/run_abo_image_similarity.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5`
  - `python scripts/run_abo_clip_similarity.py --input data/processed/abo_clean_products_5k.jsonl --max-products 100 --top-k 5 --local-files-only`
  - `python scripts/evaluate_abo_similarity_methods.py --products data/processed/abo_clean_products_5k.jsonl --tfidf data/processed/abo_tfidf_similarity_5k_sample.json --image data/processed/abo_image_similarity_5k_sample.json --clip data/processed/abo_clip_similarity_5k_sample.json --output data/processed/abo_similarity_proxy_evaluation.json`
  - `python scripts/run_abo_agentic_recommendation_demo.py`
  - `python -m pytest -q`

- Commands recommended:
  - `python -m pip install -r requirements.txt`
  - `python -m pip install -e . --no-deps`
  - `python -m pytest -q`
  - For raw-data workflows, run each track independently and keep generated outputs under `data/processed/`.

- Expected blockers:
  - The default Windows `python -m pytest -q` run during this audit failed at collection because `torch` was not installed.
  - The workspace `.venv` appears to be WSL-style (`.venv/bin/python`) and did not provide reliable stdout when invoked from PowerShell.
  - CLIP workflows may require PyTorch, Transformers, Pillow, and either a populated local Hugging Face cache or an approved first-time model download.
  - Raw RetailRocket and ABO data are intentionally not committed.

- Whether raw data is required:
  - Unit tests and deterministic fixture workflows should not require raw data.
  - Discovery, full cleaning, RetailRocket real evaluation, and 5,000-record ABO processed artifact regeneration require local raw datasets at the documented `data/raw/` paths.

- Whether tests should run without raw data:
  - Yes, the tests are expected to run against committed fixtures without raw datasets.
  - In this audit environment, tests did not pass with default `python` because dependencies were incomplete, not because raw data was missing.

## Open risks and gaps

### Data and evaluation

- Processed artifacts exist locally under ignored `data/processed/`, but there is no formal manifest with source versions, checksums, generation commands, and schema versions.
- ABO evaluation is based on one bounded query and product-type proxy relevance, not human judgment, click labels, purchases, or satisfaction outcomes.
- RetailRocket has a global popularity baseline result, but no advanced behavior method comparison under the same protocol.
- Some protocol and lifecycle docs are stale relative to implemented baselines, CLIP, local agents, and MCP-style helpers.
- Baseline weights remain provisional in code comments and should be reconciled with protocol approval evidence.

### System and delivery

- CLI workflows exist, but there is no FastAPI service, vector database, response contract, Docker image, deployment pipeline, or end-to-end service test.
- `configs/` is present but does not provide substantive tracked configuration evidence.
- `pyproject.toml` has no project dependency list; dependencies are pinned in `requirements.txt`.
- Local orchestration is a demo, not a product delivery surface.

### Security and governance

- Governance rules are documented, but there is no implemented security review checklist, dependency scan, secrets scan evidence, or access-control surface.
- `.env` is ignored by `.gitignore`, but configuration handling is not formalized beyond local environment-variable guidance.
- ABO attribution and license preservation are visible as requirements, but a formal release/publication checklist is still missing.
- Optional OpenAI explanation mode is bounded by design, but production governance for external API usage is not implemented.

### Production and maintenance

- No production deployment, monitoring, alerting, model registry, drift detection, incident runbook, rollback automation, or recovery drill evidence exists.
- `src/ecommerce_recommender/api/` and `src/ecommerce_recommender/monitoring/` are placeholders, not production capability.
- README correctly says there are no production service-level guarantees.
- Maintenance remains a future plan rather than an operational practice.

## Recommended next milestone

The recommended next milestone is **Data and Evaluation Evidence Hardening for the existing Portfolio-level local system**.

This milestone should not add new model families, APIs, vector databases, deployment infrastructure, autonomous agents, or production monitoring. It should make the current Data, Baseline, and partial Evaluation checkpoint reproducible and reviewable by creating project-specific evidence around processed artifact lineage, baseline configuration, and ABO multi-query proxy evaluation.

## Ordered next actions

1. Create a project-specific data and processed-artifact manifest covering raw source expectations, generated local artifacts, commands, schema fields, and ignored-file status.
2. Reconcile README, `AI_USAGE.md`, `docs/reports/current_project_status.md`, and lifecycle docs so test counts, implemented components, limitations, and future-only claims agree.
3. Promote RetailRocket baseline evaluation results into a reviewed report that states split policy, provisional weights, metrics, limitations, and reproducibility commands.
4. Define and document a representative ABO multi-query proxy evaluation set before making any stronger CLIP, TF-IDF, or image-similarity comparison claims.
5. Regenerate ABO TF-IDF, RGB histogram, and CLIP outputs under that approved multi-query protocol using bounded data only.
6. Write an ABO evaluation report with aggregate proxy metrics, query coverage, failure cases, latency/resource notes, and explicit non-production limitations.
7. Update reproducibility instructions to distinguish fixture-only tests from raw-data workflows and document the required Python environment for PyTorch/CLIP tests.
8. Keep Delivery, Production, and Maintenance marked open until a separately approved API/delivery milestone begins.
