# 04 Data Design

## 1. Purpose of This Document

This document defines the Version 1 data design for the Enterprise Multimodal E-Commerce Recommendation AI System. It describes the initial synthetic datasets, schema expectations, relationships, validation rules, privacy boundaries, and future data extensions.

The goal is to keep Version 1 simple, realistic, and suitable for local development while creating a clean foundation for future enterprise-scale recommendation, multimodal AI, RAG, agentic workflows, MCP tool access, and feedback optimization.

## 2. Version 1 Data Design Overview

Version 1 uses a small synthetic e-commerce dataset. The dataset is designed to support baseline recommendation logic, API testing, evaluation metrics, and documentation without using real customer data or production systems.

The Version 1 data design focuses on three core entities:

- Products: Items that can be recommended.
- Users: Synthetic users who interact with products.
- Events: Behavioral signals connecting users and products.

The data should be easy to inspect, validate, and replace as the project evolves.

## 3. Version 1 Dataset Files

Version 1 uses the following dataset files:

```text
data/sample/products.csv
data/sample/users.csv
data/sample/events.csv
```

These files should remain small enough for local testing and portfolio review. They should be treated as sample development data, not production data.

## 4. `products.csv` Schema

The `products.csv` file defines the product catalog used by the baseline recommender.

| Column | Type | Required | Description |
| --- | --- | ---: | --- |
| `product_id` | string | Yes | Unique product identifier |
| `product_name` | string | Yes | Product display name |
| `category` | string | Yes | Main product category |
| `brand` | string | Yes | Product brand |
| `price` | float | Yes | Product price |
| `description` | string | Yes | Short product description |
| `image_path` | string | No | Local or future image path |
| `stock_status` | string | Yes | Stock state such as `in_stock` or `out_of_stock` |
| `rating` | float | No | Average product rating |
| `created_at` | datetime/string | Yes | Product creation timestamp |

Version 1 should use product fields that support baseline popularity, category-based, and simple content-based recommendation logic.

## 5. `users.csv` Schema

The `users.csv` file defines synthetic user records for local development and evaluation.

| Column | Type | Required | Description |
| --- | --- | ---: | --- |
| `user_id` | string | Yes | Unique synthetic user identifier |
| `age_group` | string | No | Broad synthetic age group |
| `country` | string | No | Synthetic country or market |
| `preferred_category` | string | No | User preferred product category |
| `created_at` | datetime/string | Yes | User creation timestamp |

The user dataset must avoid names, email addresses, phone numbers, physical addresses, payment information, or any other sensitive personal data.

## 6. `events.csv` Schema

The `events.csv` file defines behavioral events that connect users to products.

| Column | Type | Required | Description |
| --- | --- | ---: | --- |
| `event_id` | string | Yes | Unique event identifier |
| `user_id` | string | Yes | User who performed the event |
| `product_id` | string | Yes | Product connected to the event |
| `event_type` | string | Yes | Type of behavior event |
| `timestamp` | datetime/string | Yes | Event timestamp |

Events provide the main interaction signal for baseline recommendation features and evaluation.

## 7. Allowed Event Types

Version 1 supports a controlled set of event types.

| Event Type | Meaning |
| --- | --- |
| `view` | User viewed a product |
| `click` | User clicked or opened a product |
| `add_to_cart` | User added product to cart |
| `purchase` | User purchased product |
| `not_interested` | User rejected or ignored product intentionally |

Using controlled event values keeps validation simple and prevents inconsistent behavior labels.

## 8. Interaction Scoring Logic

Version 1 can convert event types into simple interaction scores for baseline recommendation logic.

| Event Type | Score |
| --- | ---: |
| `view` | 1 |
| `click` | 2 |
| `add_to_cart` | 4 |
| `purchase` | 6 |
| `not_interested` | -3 |

These scores are baseline assumptions. They should be documented, tested, and adjusted only after evaluation shows a clear reason to change them.

## 9. Data Relationships

The Version 1 data model follows simple relational rules:

- `events.user_id` must match `users.user_id`.
- `events.product_id` must match `products.product_id`.
- One user can have many events.
- One product can appear in many events.
- Products can exist even if they have no events.
- Users can exist even if they have no events.

Text-based relationship diagram:

```text
users.csv
  user_id
     |
     | 1-to-many
     v
events.csv
  user_id, product_id
     ^
     | many-to-1
     |
products.csv
  product_id
```

These relationships allow the system to support popularity-based recommendations, user-category matching, and basic product interaction analysis.

## 10. Data Validation Rules

Version 1 validation should ensure that sample data is structurally correct before it is used by feature preparation, recommendation, evaluation, or API workflows.

Validation rules:

- Required columns must exist in each dataset file.
- Required values must not be empty.
- `product_id` values should be unique in `products.csv`.
- `user_id` values should be unique in `users.csv`.
- `event_id` values should be unique in `events.csv`.
- `events.user_id` should exist in `users.csv`.
- `events.product_id` should exist in `products.csv`.
- `event_type` must be one of the allowed values.
- `price` must be greater than or equal to 0.
- `rating` should be between 0 and 5 when available.
- `stock_status` should use controlled values such as `in_stock`, `low_stock`, or `out_of_stock`.
- Timestamps should be valid datetime values.

Validation should fail clearly and early when data is invalid. Error messages should help developers identify the dataset, column, and rule that failed.

## 11. Data Privacy and Safety Rules

Version 1 data must remain synthetic and safe for a public or portfolio-style repository.

Privacy and safety rules:

- Do not include real customer personal data.
- Do not include payment data, addresses, phone numbers, emails, or account credentials.
- Do not include secrets, API keys, access tokens, or local machine paths.
- Do not use externally sourced product data unless usage rights are documented.
- Do not log sensitive data if future datasets become more realistic.
- Keep synthetic identifiers generic and non-identifying.
- Prefer broad segments such as age groups and countries instead of personal attributes.

These rules keep the project safe, reviewable, and aligned with enterprise data governance expectations.

## 12. Out of Scope for Version 1

The following data capabilities are not part of Version 1:

- Real customer personal data.
- Real payment data.
- Real addresses.
- Large-scale production datasets.
- Real product image processing.
- Reviews dataset.
- Search query dataset.
- Inventory database.
- Pricing database.
- Campaign rules.
- Policy documents.
- RAG document ingestion.
- Multimodal embedding storage.

These items should be treated as future extensions after the baseline recommender, validation, evaluation, and API foundation are stable.

## 13. Future Flagship Data Extensions

Future versions may expand the data design to support a full enterprise AI recommendation platform.

Possible future datasets and stores:

- `reviews.csv` for review text and sentiment signals.
- `search_queries.csv` for search intent and query-to-product behavior.
- `feedback.csv` for explicit recommendation feedback.
- `inventory.csv` for stock availability and fulfillment constraints.
- `pricing.csv` for pricing, discounts, and margin-aware ranking.
- `campaigns.csv` for promotion and merchandising rules.
- Product image folders for visual recommendation features.
- Policy documents for RAG-based business grounding.
- Multilingual product text for international recommendation support.
- Real-time event streams through Kafka.
- PostgreSQL database tables for structured enterprise data.
- Vector database indexes for text and image embeddings.

Future data extensions should be added only when they have a clear purpose, validation strategy, governance boundary, and measurable impact on recommendation quality or business usefulness.

## 14. Data Design Acceptance Criteria

The Version 1 data design is acceptable when:

- The three sample dataset files are clearly defined.
- Product, user, and event schemas are documented.
- Allowed event types are controlled and documented.
- Interaction scoring logic is explicit and easy to test.
- Data relationships between users, products, and events are clear.
- Validation rules cover required fields, uniqueness, references, controlled values, numeric ranges, and timestamps.
- Privacy and safety rules prevent sensitive or unsafe data from entering the project.
- Version 1 data scope is clearly separated from future flagship data extensions.
- The design supports baseline recommendation, evaluation, and API development without requiring advanced infrastructure.

## 15. Summary

Version 1 data design uses three small synthetic CSV files: products, users, and events. This design is intentionally simple so the project can build a reliable recommendation foundation before adding advanced data systems.

The future flagship data architecture may include reviews, search queries, feedback, inventory, pricing, campaigns, product images, policy documents, real-time streams, relational databases, and vector indexes. Those extensions should come later, after the baseline system is stable and measurable.
