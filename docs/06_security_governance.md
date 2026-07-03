# Security and Governance

## 1. Purpose

This document defines security and governance expectations for the Enterprise Multimodal E-Commerce Recommendation AI System. The current priority is safe local development with two independent real-data tracks and honest, evidence-based claims.

## 2. Governance Principles

- Preserve dataset provenance.
- Keep raw data out of Git.
- Avoid fabricated relationships between unrelated datasets.
- Use least-privilege access patterns.
- Avoid sensitive logging.
- Require evaluation evidence before model-quality claims.
- Add advanced AI governance only when advanced capabilities are justified.

## 3. Safe Local Development

Current work is local-first. Development should use WSL2, Visual Studio Code, Git, Python, and test tooling with reviewable configuration. Local paths, credentials, and environment-specific values must not be hardcoded into source files or documentation examples.

## 4. Raw Data Handling

Raw datasets must remain under ignored local folders:

```text
data/raw/RetailRocket_event-based/
data/raw/amazon_berkeley_text_images-based/
```

Rules:

- Do not commit raw data.
- Do not upload raw archives or CSVs unless explicitly approved and permitted by the source license.
- Do not write generated artifacts into `data/raw/`.
- Do not fully load large RetailRocket CSVs into memory.
- Use header-only reads, streaming line counts, or chunked reads for RetailRocket discovery and adapters.
- Use bounded tar inspection or controlled extraction for ABO archives.
- Do not extract or process all ABO images unless explicitly approved.

## 5. Dataset Attribution and License Notes

Dataset provenance must remain visible in reports and future public-facing documentation. Amazon Berkeley Objects (ABO) license and attribution information must be preserved before using ABO assets, metadata, or derived demonstrations publicly.

RetailRocket and ABO must not be presented as datasets from one company, one catalog, or one customer system.

## 6. Secrets and Configuration

- Never commit API keys, access tokens, passwords, private keys, or `.env` files.
- Use environment variables and safe `.env.example` placeholders when configuration is introduced.
- Keep Git ignore rules aligned with local secrets, raw data, and model artifacts.
- Do not print credentials in logs, notebooks, reports, or command output.

## 7. Logging Rules

Logs should record operational context without exposing unnecessary identifiers or raw records.

Avoid logging:

- Raw visitor histories.
- Full product listing records.
- Local absolute paths containing personal information.
- Secrets or environment values.
- Large archive member dumps.

Prefer aggregate counts, bounded samples where justified, and explicit error categories.

## 8. Dataset Separation Governance

The following joins are prohibited:

```text
RetailRocket visitorid/itemid  -X-  ABO item_id/image_id
```

- Do not invent shared IDs.
- Do not create synthetic cross-track customer profiles.
- Do not imply that ABO products correspond to RetailRocket interactions.
- Evaluate outputs separately.
- Preserve source-dataset labels in future processed artifacts.

## 9. Evaluation Gates Before Claims

Before claiming model improvement:

1. Approve the track-specific business task.
2. Approve fixture and validation contracts.
3. Approve split or retrieval-set construction.
4. Define leakage controls.
5. Implement a simple baseline.
6. Compare advanced methods under the same protocol.
7. Report limitations and known failure modes.

Architectural complexity is not evidence of recommendation quality.

## 10. Fallback and Failure Handling Direction

Future adapters and services should fail clearly and conservatively when:

- Required source files are missing.
- Raw schemas differ from expected contracts.
- Archive members are unsafe or malformed.
- Product-to-image mappings are missing.
- Recommendation candidates are unavailable.
- A future model or service dependency is unavailable.

Fallback behavior must be track-specific, observable, and documented before API exposure.

## 11. Future RAG, Agent, and MCP Governance

Retrieval-Augmented Generation (RAG), production agentic workflows, and production Model Context Protocol (MCP) integrations are out of scope for the current milestone. The repository includes a lightweight local orchestration demo and MCP-style helper boundaries, but these are not a production agent system or full MCP server/client. If production-grade versions are introduced later, they require:

- Explicit business justification.
- Restricted tool access.
- Input and output validation.
- Audit logging.
- Retry and timeout limits.
- Fallback behavior.
- Policy checks.
- Human review paths for risky actions.
- Separate evaluation protocols.

## 12. Limitations

- RetailRocket identifiers are dataset-specific and do not provide a unified customer profile.
- ABO metadata fields vary by listing and locale.
- ABO image mappings require controlled validation.
- The current project does not include video recommendation.
- Current documentation and local tests define direction and local evidence; they do not claim deployed security controls or implemented recommendation services.

## 13. Security and Governance Acceptance Criteria

This document is accepted when:

1. Raw-data exclusion and bounded-read requirements are explicit.
2. ABO attribution and license preservation are visible.
3. Secrets and logging rules are defined.
4. False cross-dataset claims and joins are prohibited.
5. Evaluation gates precede model-quality claims.
6. Future advanced-system governance requirements are documented without claiming implementation.
