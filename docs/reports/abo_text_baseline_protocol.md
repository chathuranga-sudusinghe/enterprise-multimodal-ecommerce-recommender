# Amazon Berkeley Objects Text Baseline Protocol

## Purpose

This document defines the protocol for a simple Amazon Berkeley Objects text-based product similarity baseline before implementation.

The baseline provides a clear, deterministic reference method for recommending similar products using only product metadata and text fields from the Amazon Berkeley Objects dataset track. It is intended to support future implementation, testing, and evaluation without introducing advanced models or unsupported system claims.

## Dataset Track

This protocol applies only to the `amazon_berkeley_text_images-based` dataset track.

Amazon Berkeley Objects is used in this project for product metadata, text, and image-based similarity work. This baseline uses only product metadata and text fields. RetailRocket remains a separate behavior/event recommendation track and must not be merged with Amazon Berkeley Objects data or identifiers.

## Why This Baseline Is Needed

A simple text baseline is needed before implementing more advanced product similarity methods. It establishes:

- A reproducible product-to-product similarity reference.
- A clear data contract for usable Amazon Berkeley Objects text fields.
- A practical evaluation approach for non-personalized product similarity.
- A baseline that future Machine Learning (ML), image similarity, or multimodal methods can be compared against when those methods are in scope.

## What This Baseline Does

This baseline creates product-to-product recommendations from Amazon Berkeley Objects metadata text.

It will:

- Build a combined text representation for each product from available metadata fields.
- Normalize missing, empty, or unavailable fields safely.
- Use TF-IDF (Term Frequency-Inverse Document Frequency) vectorization.
- Use cosine similarity to compare products.
- Return the top-K most similar products for a given source product.
- Exclude the source product itself from recommendation results.
- Use deterministic sorting so repeated runs produce stable outputs.

## What This Baseline Does Not Do

This baseline does not:

- Provide personalized recommendations.
- Use user behavior, sessions, transactions, or event labels.
- Use RetailRocket visitor, item, or event identifiers.
- Merge Amazon Berkeley Objects with RetailRocket.
- Use product images, video, 360-degree, spin, or 3D assets.
- Implement image similarity, multimodal similarity, advanced models, Retrieval-Augmented Generation (RAG), agents, Model Context Protocol (MCP), contextual bandits, an API (Application Programming Interface), or deployment infrastructure.
- Claim production readiness or business impact before implementation and evaluation.

## Input Fields

The baseline should use available Amazon Berkeley Objects product metadata fields, including:

- `item_name`
- `brand`
- `bullet_point`
- `product_type`
- `color`
- `material`
- `style`

Fields may be missing, empty, or represented inconsistently across products. The implementation should treat unavailable fields as empty text rather than failing or inventing values.

## Text Construction Strategy

Each product should receive one combined text representation built from the available metadata fields.

The construction strategy should:

- Convert missing values to empty text.
- Normalize lists, repeated values, and scalar values into readable text.
- Preserve useful product terms from names, brands, bullets, product types, colors, materials, and styles.
- Avoid adding synthetic attributes not present in the Amazon Berkeley Objects metadata.
- Avoid using RetailRocket fields or identifiers.
- Produce deterministic text for the same input record.

The combined text should be suitable for TF-IDF vectorization and small fixture-based tests.

## Baseline Method

The baseline method is a content-based product similarity approach.

The expected method is:

1. Load a bounded Amazon Berkeley Objects metadata sample or approved processed metadata table.
2. Build a combined text field per product from the approved input fields.
3. Fit a TF-IDF (Term Frequency-Inverse Document Frequency) vectorizer on the combined product text.
4. Compute cosine similarity between product text vectors.
5. For each source product, rank candidate products by similarity score.
6. Return the top-K most similar products after excluding the source product itself.

The baseline should remain simple, interpretable, and deterministic.

## Similarity Search Logic

For a given source product, the similarity search should:

- Identify the source product by its Amazon Berkeley Objects product identifier.
- Compute similarity between the source product vector and candidate product vectors.
- Exclude the source product from the candidate list.
- Sort results by descending cosine similarity.
- Apply deterministic tie-breaking, such as sorting by stable product identifier after similarity score.
- Return top-K product identifiers with similarity scores and relevant metadata needed for inspection.

The result format should support manual review and automated validity checks.

## Evaluation Strategy

Because Amazon Berkeley Objects does not provide user event labels in the current project scope, this baseline should be evaluated as a product similarity baseline, not as a user-personalized recommendation model.

Evaluation should include:

- Manual spot-checking of similar items for obvious relevance.
- Category or `product_type` consistency between source and recommended products.
- Brand consistency where brand similarity is relevant to the product type.
- Text similarity sanity checks using item names, bullet points, and product attributes.
- Top-K output validity, including no duplicate recommendations and no self-recommendations.
- Coverage over products with usable text.
- Latency checks for small deterministic fixtures.
- Deterministic repeatability across repeated runs with the same inputs.

These checks should be treated as baseline validation, not as proof of final production performance.

## Expected Outputs

The implemented baseline should produce:

- A top-K list of similar Amazon Berkeley Objects products for each requested source product.
- Similarity scores for returned recommendations.
- Source product metadata and recommended product metadata needed for inspection.
- Coverage metrics over products with usable text.
- Evaluation artifacts or test outputs that show deterministic behavior on small fixtures.

## Risks and Limitations

Key risks and limitations include:

- Text-only similarity may miss visual similarity, functional similarity, or complementary product relationships.
- Sparse or missing metadata can reduce recommendation quality.
- Brand, color, material, or style terms may dominate similarity in ways that are not always useful.
- TF-IDF may not capture semantic similarity when products use different wording.
- Manual spot-checking is useful but subjective.
- Without user behavior labels, this protocol cannot evaluate personalized recommendation quality.
- This baseline is not a production-ready recommender by itself.

## Acceptance Criteria

This protocol is accepted when:

- The baseline is clearly defined as Amazon Berkeley Objects text-only product-to-product similarity.
- RetailRocket is described only as a separate dataset track.
- The input metadata fields are listed clearly.
- TF-IDF (Term Frequency-Inverse Document Frequency) and cosine similarity are specified as the baseline method.
- Source-product exclusion and deterministic tie-breaking are required.
- Evaluation is framed as product similarity validation, not user-personalized recommendation evaluation.
- Out-of-scope systems are not claimed as implemented.
- The document is concise, professional, and implementation-ready.

## Next Step After This Protocol

The recommended next step is to implement a small, deterministic Amazon Berkeley Objects text baseline module and focused tests using approved sample fixtures. The implementation should follow this protocol, avoid raw dataset overloading, and produce inspectable top-K product similarity outputs.
