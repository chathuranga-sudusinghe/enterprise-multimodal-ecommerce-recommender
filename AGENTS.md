# AGENTS.md

## 1. Project Overview

- Project name: Enterprise Multimodal E-Commerce Recommendation AI System.
- Purpose: Build a production-oriented e-commerce recommendation platform that starts with baseline recommenders and grows into a future multimodal, RAG-grounded, agentic, MCP-enabled, feedback-optimized personalization system.
- This is an enterprise AI/ML engineering project, not a toy demo or notebook-only project.

## 2. Current Project Stage

- The project is currently in the foundation stage.
- Documentation foundation is complete.
- Next development should move toward repository structure, sample synthetic data, data validation, baseline recommenders, FastAPI skeleton, tests, and evaluation.
- Advanced AI features must not be implemented before the baseline system is stable.

## 3. Development Philosophy

- Start simple, then improve step by step.
- Build modular, testable, production-style components.
- Prefer clear interfaces and readable implementation over premature complexity.
- Every serious feature must have a clear purpose.
- Keep work small, focused, and reviewable.
- Use advanced AI only when it adds clear value.

## 4. Version 1 Scope

Version 1 includes:

- Synthetic sample data.
- Data validation.
- Feature preparation.
- Baseline recommenders.
- Simple evaluation metrics.
- FastAPI local service.
- API schemas.
- Basic tests.
- Safe configuration.
- Clear documentation.

## 5. Out of Scope for Version 1

Do not implement these in Version 1:

- Real customer data.
- Real payment data.
- Production deployment.
- Cloud deployment.
- Kubernetes.
- Full Retrieval-Augmented Generation (RAG) implementation.
- Large Language Model (LLM) fine-tuning.
- LangGraph agent workflows.
- Model Context Protocol (MCP) server/client implementation.
- Contextual bandit optimization.
- Large-scale real-time data pipelines.

## 6. Repository Rules

- Work only on the files requested by the user.
- Do not modify unrelated files.
- Do not restructure the repository unless explicitly asked.
- Do not delete existing work unless explicitly asked.
- Do not add dependencies unless they are necessary for the requested task.
- Do not add secrets, tokens, API keys, or private credentials.
- Keep changes small, focused, and reviewable.

## 7. Coding Standards

- Use clean, modular Python.
- Use readable names.
- Use small focused functions.
- Use `pathlib.Path` instead of hardcoded absolute paths.
- Use logging instead of unnecessary `print()` statements.
- Use Pydantic schemas where API or data validation schemas are needed.
- Use environment variables for configuration and secrets.
- Add helpful comments and docstrings where they improve clarity.
- Avoid overengineering.

## 8. Documentation Standards

- Keep documentation professional, recruiter-readable, and engineer-readable.
- Clearly separate implemented features from future roadmap features.
- Do not claim that planned systems are already implemented.
- Use Markdown headings, tables, and concise explanations.
- Write the full term before abbreviations when useful.

## 9. Data and Privacy Rules

- Use synthetic data only in Version 1.
- Do not include names, emails, phone numbers, addresses, payment details, or real customer identifiers.
- Do not log sensitive data.
- Keep `.env` ignored by Git.
- Use `.env.example` only for safe placeholder values.

## 10. AI/ML Engineering Rules

- Start with baseline recommenders before advanced models.
- Do not add deep learning, RAG, agents, MCP, or contextual bandits too early.
- Future advanced models must be evaluated against baselines.
- Recommendation logic should be explainable.
- Evaluation is required before claiming improvement.
- Use advanced AI only when it adds clear value.

## 11. Testing and Evaluation Rules

- Add or update tests when code behavior changes.
- Use pytest for Python tests when tests are introduced.
- Evaluation should include Precision@K, Recall@K, Hit Rate@K, Coverage, Diversity, and Latency when implemented.
- Do not claim tests passed unless they were actually run.
- If tests are not run, state why.

## 12. Git Workflow Rules

- `main` is stable and portfolio-ready.
- `dev` is the development integration branch.
- `feature/*` branches are used for focused tasks.
- Do not work directly on `main` unless explicitly asked.
- Review `git status` and `git diff` before commit.
- Keep commits small and focused.
- Do not commit or push unless explicitly asked.

## 13. Safety Rules for Codex

- Prefer safe edits over risky edits.
- Ask before making broad or ambiguous changes.
- Do not run destructive commands.
- Do not use `git reset --hard`, `git clean -fd`, force push, or file deletion unless explicitly requested and confirmed.
- Do not expose private keys, tokens, or secrets.
- Keep WSL2 Ubuntu and VS Code compatibility in mind.

## 14. Expected Response After Changes

After editing files, show:

1. Short summary of changes.
2. Files changed.
3. Commands run.
4. Tests run or not run.
5. `git status`.
6. Relevant `git diff`.

## 15. Immediate Next Development Direction

After `AGENTS.md`, the next likely steps are:

1. Create or verify project folder structure.
2. Create sample synthetic CSV data.
3. Add data loading and validation modules.
4. Add baseline recommender logic.
5. Add FastAPI skeleton.
6. Add tests and evaluation scripts.
