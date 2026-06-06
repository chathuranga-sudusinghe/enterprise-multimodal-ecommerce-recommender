# Deployment Plan

## 1. Purpose

This document defines the deployment maturity path for the Enterprise Multimodal E-Commerce Recommendation AI System. The project is currently local-first and evidence-first. Deployment complexity should be added only after stable data contracts, tests, and baseline evidence exist.

## 2. Current Phase

The current phase includes:

- Dataset discovery.
- Documentation restructuring.
- Deterministic fixture contract design.
- Safe adapter and validation planning.
- Separate evaluation protocol planning.
- Baseline planning only.

The current phase does not include model training, API implementation, Docker deployment, cloud deployment, or Kubernetes.

## 3. Local Development Workflow

The initial development environment is:

- WSL2 Ubuntu-compatible shell workflows.
- Visual Studio Code.
- Git with small focused branches and manual review.
- Python `>=3.11`.
- pytest for automated tests when code changes resume.

Development should remain reproducible without hardcoded local absolute paths.

## 4. Local Data Boundaries

Raw data remains local and ignored by Git:

```text
data/raw/RetailRocket_event-based/
data/raw/amazon_berkeley_text_images-based/
```

`data/sample/` should later contain only tiny deterministic fixtures for tests, examples, and Continuous Integration / Continuous Deployment (CI/CD). It is not the primary ML dataset.

Future processed artifacts should be lightweight, reproducible, provenance-aware, and stored outside raw folders.

## 5. Python Environment Direction

The Python project should keep a minimal, intentional dependency set. Environment management should support:

- Editable local installation when package work resumes.
- Reproducible test execution.
- Environment-variable configuration for future services.
- No committed secrets or local credentials.

Dependencies should be added only when a concrete approved task requires them.
The first CLIP-based ABO multimodal similarity dependency set is CPU-first and uses local Hugging Face Transformers model loading without token-based Inference API access.

## 6. Testing Before Deployment

Before deployment work begins, the project should have:

- Approved RetailRocket and ABO fixture contracts.
- Track-specific adapter tests.
- Track-specific validation tests.
- Memory-safety review for large-file readers.
- Bounded archive-handling tests for ABO.
- Approved baseline protocols.
- Baseline evaluation evidence.

## 7. Baseline and API Gates

```text
Discovery evidence
  -> Documentation approval
  -> Fixture contracts
  -> Safe adapters and validators
  -> Track-specific tests
  -> Evaluation protocol approval
  -> Baseline implementation and evidence
  -> API design and implementation later
```

An Application Programming Interface (API) should not expose unstable assumptions. API work starts only after baseline evidence and response contracts are approved.

## 8. Docker Direction Later

Docker is a later local deployment step. Add a Dockerfile only after adapters, tests, and baselines are stable. A future image should:

- Install only intentional dependencies.
- Run without bundled raw datasets.
- Accept safe configuration through environment variables.
- Support health checks after an API exists.
- Avoid secrets in image layers.

## 9. Docker Compose Direction Later

Docker Compose may be introduced after the single-service local workflow is stable. Add supporting services only when needed, such as a future vector index, experiment tracker, or monitoring stack. Do not add infrastructure for portfolio appearance alone.

## 10. Future API Service Direction

After evidence gates are met, a local API may expose separate track-specific capabilities:

- RetailRocket behavior-based recommendations.
- ABO text-based similar-product retrieval.
- ABO image-based similar-product retrieval later.
- Health and metrics endpoints.

Service contracts must preserve dataset provenance and must not imply cross-dataset identity mappings.

## 11. Future CI/CD Direction

Future CI/CD workflows should:

- Install the package in a reproducible environment.
- Run track-specific tests against deterministic fixtures.
- Avoid raw-data dependencies.
- Validate formatting and static checks if those tools are intentionally adopted.
- Build deployment artifacts only after tests pass.
- Keep secrets in platform-managed secret stores.

## 12. Future Cloud and Kubernetes Direction

Cloud deployment and Kubernetes are future-only options. They should be considered only after local APIs, observability, resource profiles, and operational requirements are stable. Kubernetes is not a current milestone.

## 13. Monitoring Direction

Future observability should cover:

- Adapter failures.
- Schema mismatches.
- Recommendation and retrieval latency.
- Fallback usage.
- Eligible catalog coverage.
- Model or data-quality drift where applicable.
- Resource usage for image and archive workflows.

Logs must remain privacy-aware and provenance-aware.

## 14. Rollback and Recovery Direction

Future releases should support:

- Versioned configuration.
- Versioned model or retrieval artifacts.
- Reproducible baseline fallback.
- Clear rollback instructions.
- Recovery from missing or malformed processed artifacts.
- Separate rollback decisions for RetailRocket and ABO capabilities.

## 15. Deployment Acceptance Criteria

Deployment planning is ready to advance when:

1. The current documentation and fixture contracts are approved.
2. Raw data remains excluded from Git.
3. Track-specific adapters and validators pass tests.
4. Baseline protocols are approved and baseline evidence exists.
5. API scope is explicitly approved.
6. Docker is introduced only after local stability.
7. Cloud and Kubernetes remain future-only until justified by operational needs.
