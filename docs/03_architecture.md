# 03 Architecture

## 1. Purpose of This Document

This document explains the architecture of the Enterprise Multimodal E-Commerce Recommendation AI System. It defines a clear, modular, and production-oriented architecture that can start small in Version 1 and gradually grow into a flagship enterprise AI recommendation platform.

Version 1 focuses on a simple but well-structured recommendation system using synthetic e-commerce data, baseline recommendation logic, FastAPI serving, basic evaluation, logging, and testable modules.

Future phases may extend the system with multimodal AI, vector search, Retrieval-Augmented Generation (RAG), agentic workflow orchestration, Model Context Protocol (MCP) tool access, feedback-based ranking optimization, monitoring, and deployment readiness. These future capabilities are not part of Version 1.

## 2. Architecture Principles

The system follows these architecture principles:

1. Start simple before adding advanced AI.
2. Build a real AI product, not a notebook-only demo.
3. Keep each module focused, replaceable, and testable.
4. Separate data logic, feature logic, model logic, API logic, evaluation, and monitoring.
5. Establish baseline recommenders before adding advanced models.
6. Prefer clear interfaces over tightly coupled implementation details.
7. Keep the system local-first while leaving a path to cloud-ready deployment.
8. Avoid hardcoded local paths and user-specific configuration.
9. Use configuration files and environment variables where appropriate.
10. Treat RAG, agentic AI, MCP, contextual bandits, Kubernetes, and deep learning as future extensions, not Version 1 requirements.

## 3. Version 1 Architecture Overview

Version 1 uses a lightweight modular pipeline:

```text
Synthetic E-Commerce Data
        ->
Data Validation
        ->
Feature Preparation
        ->
Baseline Recommender
        ->
FastAPI Service
        ->
Evaluation + Logging
```

Version 1 is intentionally simple. Its purpose is to create a stable foundation that can be evaluated, tested, documented, and extended without requiring premature infrastructure or advanced AI components.

## 4. Version 1 Architecture Layers

### 4.1 Data Source Layer

Version 1 uses small synthetic e-commerce datasets for local development, testing, and demonstration.

Initial datasets:

- `products.csv`
- `users.csv`
- `events.csv`

The data should be stored under the project `data/` directory using a clean structure:

```text
data/
|-- raw/
|-- interim/
|-- processed/
`-- sample/
```

The synthetic data should avoid sensitive personal information and should be realistic enough to support baseline recommendation behavior.

### 4.2 Data Validation Layer

The data validation layer checks whether input data is usable before feature preparation and recommendation logic.

Validation responsibilities include:

- Required column checks.
- Missing value checks.
- Duplicate record checks.
- Invalid category checks.
- Invalid event type checks.
- Basic price and rating checks.
- Simple schema validation.

Version 1 can start with lightweight validation using Python functions and Pydantic where schema objects are useful. Future versions may add validation frameworks such as Pandera or Great Expectations if the project scale requires them.

### 4.3 Feature Preparation Layer

The feature preparation layer transforms raw e-commerce data into simple features that baseline recommenders can use.

Version 1 feature preparation may include:

- Product popularity scores.
- User preferred category mappings.
- Product category mappings.
- Event-based interaction scores.
- Basic product metadata features.

Example event weights:

| Event Type | Score |
| --- | ---: |
| `view` | 1 |
| `click` | 2 |
| `add_to_cart` | 4 |
| `purchase` | 6 |
| `not_interested` | -3 |

These weights are baseline assumptions and can be adjusted later during evaluation.

### 4.4 Baseline Recommendation Layer

Version 1 should include baseline recommendation logic before any advanced model is added.

Initial baseline recommenders may include:

1. Popularity-based recommender.
2. Category-based recommender.
3. Simple content-based recommender using product metadata.

The purpose of this layer is to create a measurable starting point. Future models should demonstrate improvement against these baselines before becoming part of the main system.

### 4.5 API Service Layer

FastAPI is used as the Version 1 service layer.

Initial API endpoints:

```text
GET  /health
POST /api/v1/recommend
```

Future endpoints may include:

```text
POST /api/v1/feedback
POST /api/v1/recommend/explain
POST /api/v1/rag/policy-check
POST /api/v1/agent/recommend
GET  /metrics
```

The API layer should use:

- FastAPI routes.
- Pydantic request and response schemas.
- Service functions or service classes.
- Structured error handling.
- Configuration-driven behavior.
- Logging for operational visibility.

### 4.6 Evaluation Layer

The evaluation layer measures recommendation quality and helps prove whether future improvements are meaningful.

Version 1 can start with simple offline metrics:

- Precision@K.
- Recall@K.
- Hit Rate.
- Coverage.
- Latency.

Future versions may add:

- MAP@K.
- NDCG@K.
- MRR.
- Diversity.
- Novelty.
- Fairness checks.
- Offline A/B-style comparisons.

Evaluation is required because the project should show measurable recommendation quality, not only working API behavior.

### 4.7 Logging and Monitoring Preparation Layer

Version 1 should include basic structured logging.

Logging should capture:

- API request flow.
- Recommendation request received.
- Recommender type used.
- Number of recommended products.
- Errors and fallback behavior.

Version 1 does not require Prometheus, Grafana, or full observability infrastructure. The code should still be organized so operational metrics can be added later.

Future monitoring may include:

- API latency.
- Request count.
- Recommendation latency.
- Model or recommender error rate.
- Fallback trigger count.
- Feedback event volume.
- Recommendation quality drift.

## 5. Suggested Version 1 Module Structure

The source code should follow a clean package structure:

```text
src/
`-- ecommerce_recommender/
    |-- __init__.py
    |-- api/
    |   |-- routes.py
    |   `-- schemas.py
    |-- core/
    |   `-- config.py
    |-- data/
    |   |-- loading.py
    |   `-- validation.py
    |-- features/
    |   `-- build_features.py
    |-- models/
    |   |-- base.py
    |   |-- popularity.py
    |   |-- category.py
    |   `-- content_based.py
    |-- evaluation/
    |   `-- metrics.py
    |-- monitoring/
    |   `-- logging_config.py
    `-- utils/
        `-- paths.py
```

This structure keeps the system modular and easy to extend. It also separates the concerns that should evolve independently: data access, validation, feature preparation, model behavior, API serving, evaluation, monitoring, and utility functions.

## 6. Future Flagship Architecture

The future flagship architecture expands Version 1 into a broader enterprise AI personalization platform.

```text
Data Sources
        ->
Data Validation and Governance
        ->
Feature Engineering
        ->
Baseline + ML Recommendation Models
        ->
Multimodal Embedding Layer
        ->
Vector Search Layer
        ->
RAG Business Rule Grounding
        ->
Agentic Workflow Orchestration
        ->
Ranking and Feedback Optimization
        ->
FastAPI Service Layer
        ->
Monitoring, Evaluation, Security, and Deployment
```

These layers should be introduced only after the baseline system is stable, tested, and documented.

## 7. Future Architecture Layers

### 7.1 Multimodal AI Layer

The multimodal layer will use product text and product images to improve recommendation quality.

Possible future components:

- Product title embeddings.
- Product description embeddings.
- Review embeddings.
- Product image embeddings.
- Visual similarity search.
- Text similarity search.
- Multimodal product ranking.

This layer is especially useful for cold-start products and visually driven e-commerce categories.

### 7.2 Vector Search Layer

The vector search layer will support semantic product retrieval and similarity search.

Possible tools:

- FAISS for local vector search.
- Pinecone for cloud-ready vector search later.

Use cases:

- Similar product search.
- Product-to-product recommendation.
- Search query understanding.
- Retrieval for RAG policy grounding.

### 7.3 RAG Business Grounding Layer

Retrieval-Augmented Generation may be used later to ground recommendations in business rules and policy documents.

Possible RAG documents:

- Stock rules.
- Pricing rules.
- Campaign rules.
- Return and refund policies.
- Blocked product rules.
- Customer segment rules.
- Recommendation governance rules.

The RAG layer should help prevent unsafe, unavailable, or business-invalid recommendations. It is not required for Version 1.

### 7.4 Agentic Workflow Layer

The agentic workflow layer may coordinate controlled recommendation decision steps in future versions.

Possible agents:

- Recommendation Agent.
- Candidate Retrieval Agent.
- Inventory Check Agent.
- Policy/RAG Agent.
- Ranking Agent.
- Explanation Agent.
- Fallback Agent.
- Evaluation Agent.

The agentic layer should not behave like an uncontrolled chatbot. It should follow a structured workflow with clear tool access, retry limits, fallback behavior, and audit logging.

### 7.5 MCP Tool Access Layer

The Model Context Protocol layer may provide controlled access to enterprise-style tools and data.

Possible MCP tools:

- Catalog lookup.
- Inventory lookup.
- Pricing lookup.
- Campaign lookup.
- Policy lookup.
- Customer segment lookup.
- Recommendation audit log.

This layer would allow the system to act like an enterprise AI application connected to governed tools, not just a standalone model script.

### 7.6 Feedback Optimization Layer

Future versions may use contextual bandit-style optimization to improve ranking based on user feedback.

Example reward design:

| User Action | Reward |
| --- | ---: |
| `impression_only` | 0.0 |
| `click` | 0.2 |
| `add_to_cart` | 0.6 |
| `purchase` | 1.0 |
| `not_interested` | -0.7 |
| `return_refund` | -0.5 |

This should be framed as feedback-based ranking optimization, not full large-scale reinforcement learning in the early stages.

## 8. Deployment Architecture Direction

Version 1 should be local-first and simple to run in a developer environment.

Initial local stack:

- Python.
- FastAPI.
- pytest.
- Docker later.
- GitHub Actions later.

Future local enterprise stack may include:

- FastAPI.
- PostgreSQL.
- Kafka.
- Airflow.
- MinIO.
- FAISS.
- MLflow.
- Prometheus.
- Grafana.
- Docker Compose.

Future cloud-ready direction may include:

- AWS or Azure.
- Managed PostgreSQL.
- Object storage.
- Container deployment.
- Pinecone.
- CI/CD pipeline.
- Monitoring dashboards.

Kubernetes should only be considered after the Docker Compose version is stable and there is a real deployment need.

## 9. Security and Governance Architecture

The architecture should support security and governance from the beginning.

Version 1 security and governance practices:

- No secrets in code.
- `.env` ignored by Git.
- `.env.example` used for safe configuration examples.
- Input validation through Pydantic where appropriate.
- No sensitive personal data in synthetic datasets.
- Clear documentation of assumptions and limitations.

Future security and governance practices may include:

- Protected admin endpoints.
- Audit logs.
- Restricted MCP tool access.
- Recommendation policy checks.
- Fairness and bias analysis.
- Human review for risky outputs.
- Fallback behavior for uncertain recommendations.
- No sensitive data in logs.

## 10. Architecture Acceptance Criteria

This architecture document is complete when it clearly explains:

1. The Version 1 architecture.
2. The future flagship architecture.
3. The main system layers.
4. The data flow from input data to recommendation output.
5. The role of FastAPI in the system.
6. The role of baseline recommenders.
7. The future role of multimodal AI, RAG, agents, MCP, and feedback optimization.
8. The local-first and cloud-ready deployment direction.
9. The security and governance direction.
10. The reason advanced tools are future extensions, not Version 1 requirements.

## 11. Summary

The project architecture starts with a simple, testable, and production-style recommendation system.

Version 1 focuses on:

- Synthetic e-commerce data.
- Data validation.
- Feature preparation.
- Baseline recommendation logic.
- FastAPI serving.
- Evaluation.
- Logging.

Future phases may expand the system into a flagship enterprise AI platform with multimodal recommendation, vector search, RAG business grounding, agentic workflow orchestration, MCP tool access, feedback-based ranking optimization, observability, security, and deployment readiness.
