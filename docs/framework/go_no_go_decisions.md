# GO/NO-GO Decisions

## Purpose

This document records current framework decisions for the repository. It exists to prevent accidental movement into advanced implementation work before the data and evaluation gates support it.

## Current Active Milestone

Data and Evaluation Evidence Hardening.

## GO Decisions

### GO: Keep Two-Track Architecture

Decision:

- Continue with separate RetailRocket behavior recommendation and ABO product text/image similarity tracks.

Rationale:

- The datasets serve different tasks and do not share users, products, catalogs, or business identity.

### GO: Keep Existing Baseline Evidence as Local Baseline Checkpoint

Decision:

- Preserve existing baseline reports and outputs as local evidence checkpoints.

Rationale:

- Baseline evidence is useful for portfolio-level progress and later comparison, provided it remains separate by track and is not overclaimed as production proof.

### GO: Continue Data/Evaluation Evidence Hardening

Decision:

- Continue work on schema contracts, validation plans, lineage, reproducibility, evaluation protocols, and gate evidence.

Rationale:

- These controls are required before retrieval, API, MCP, deployment, or monitoring can safely become implementation priorities.

## NO-GO Decisions

### NO-GO: FAISS/Vector DB Implementation Now

Decision:

- Do not implement FAISS, vector databases, or vector retrieval as the main work now.

Rationale:

- Data readiness and evaluation evidence are still partial. Vector retrieval requires stable artifact contracts, validation evidence, and approved evaluation criteria.

### NO-GO: API Implementation Now

Decision:

- Do not implement production or portfolio API/service work now.

Rationale:

- API contracts should depend on approved data contracts, baseline/evaluation evidence, and stable model or retrieval behavior.

### NO-GO: MCP Production Implementation Now

Decision:

- Do not implement production MCP server/client or agentic workflow integration now.

Rationale:

- MCP integration should sit above stable service, governance, and data contracts. Those gates are not yet ready.

### NO-GO: Deployment/Monitoring Now

Decision:

- Do not implement deployment, Kubernetes, cloud infrastructure, or production monitoring now.

Rationale:

- Deployment and monitoring require a validated system boundary, service layer, operational metrics, and production-readiness evidence.

### NO-GO: Production-Readiness Claims

Decision:

- Do not claim the repository is production-ready.

Rationale:

- The current repository is a local, portfolio-level enterprise AI/ML engineering project in evidence-hardening stages. Production claims would overstate the current implementation.

## Next Allowed Step

The next allowed step is documentation and data/evaluation hardening:

- Approve the final architecture target.
- Harden schema contracts.
- Implement or manually evidence validation checks.
- Improve lineage and reproducibility records.
- Strengthen track-specific evaluation protocols.
