# Amazon Berkeley Objects Image Baseline Protocol

## Purpose

This document defines the protocol for a simple Amazon Berkeley Objects image-only product-to-product similarity baseline before implementation.

The baseline is intended to establish a reproducible reference for comparing product images using Amazon Berkeley Objects image assets and image mapping metadata. It should start with small deterministic fixtures and avoid full raw archive processing during the first implementation.

## Dataset Track

This protocol applies only to the `amazon_berkeley_text_images-based` dataset track.

Amazon Berkeley Objects is used in this project for product metadata, text, and image similarity work. RetailRocket remains a separate behavior/event recommendation track and must not be joined to Amazon Berkeley Objects product, listing, or image identifiers.

## Why This Baseline Is Needed

The completed Amazon Berkeley Objects text baseline provides a text-only product-to-product similarity reference. An image-only baseline is needed next to define a separate visual similarity reference before any multimodal work is considered.

This protocol helps ensure that future image work:

- Uses Amazon Berkeley Objects image data safely.
- Starts from small deterministic sample fixtures.
- Defines evaluation before implementation.
- Avoids overclaiming production readiness or multimodal recommendation.
- Provides a baseline that later image or multimodal methods can be compared against.

## What This Baseline Does

The future baseline should compare product images and return visually similar product images or products.

It should:

- Use Amazon Berkeley Objects image assets and image mapping metadata.
- Select usable images from small deterministic fixtures first.
- Produce image feature vectors using a simple reproducible image embedding approach.
- Compare image vectors with cosine similarity.
- Return top-K similar product images or products for a given source image or source product.
- Exclude the source image from returned recommendations.
- Use deterministic sorting and tie-breaking for repeatable output.

## What This Baseline Does Not Do

This baseline does not:

- Provide personalized recommendations.
- Use RetailRocket user behavior, events, visitors, items, or transactions.
- Merge RetailRocket and Amazon Berkeley Objects data.
- Use text fields as the primary similarity signal.
- Implement multimodal recommendation.
- Use video, 360-degree, spin, or 3D assets.
- Train a vision model from scratch.
- Implement an Application Programming Interface (API), deployment stack, Retrieval-Augmented Generation (RAG), agents, Model Context Protocol (MCP), contextual bandits, or advanced production systems.
- Claim production readiness or business impact before implementation and evaluation.
- Claim that image similarity is already implemented.

## Input Data

The baseline should use Amazon Berkeley Objects image-related data only, such as:

- Small deterministic image fixtures.
- Product-to-image mapping metadata.
- Image identifiers.
- Local sample image paths where available.
- Product metadata only when needed for inspection or evaluation context, such as `item_id`, `product_type`, or category-like fields.

The first implementation must not fully extract or process the full raw Amazon Berkeley Objects image archives. Any raw archive inspection should remain bounded and controlled.

## Image Selection Strategy

The first implementation should use a small, deterministic image selection strategy.

It should:

- Prefer existing sample fixtures under the Amazon Berkeley Objects sample track.
- Select only images with valid local paths or approved fixture references.
- Handle missing, unreadable, or unsupported image files safely.
- Avoid extracting the full raw image archive.
- Avoid processing every available image during initial baseline work.
- Keep source image and candidate image identifiers stable across repeated runs.

When products have multiple images, the implementation should define a clear policy, such as using the main image first or evaluating each mapped image separately. The chosen policy should be documented in the implementation output.

## Baseline Method

The baseline should remain simple, reproducible, and image-only.

Possible future implementation options include:

- Simple pretrained Convolutional Neural Network (CNN) embeddings.
- Optional CLIP-style image embeddings later, if justified and dependency impact is reviewed.
- Cosine similarity over image feature vectors.

The initial implementation should prefer pretrained image features rather than training a new vision model from scratch. Any dependency or model download requirement should be reviewed before implementation.

## Similarity Search Logic

For a given source image or source product, the similarity search should:

- Resolve the source image from Amazon Berkeley Objects image mapping metadata.
- Build or load image vectors for the source and candidate images.
- Exclude the source image from returned results.
- Sort candidates by descending cosine similarity.
- Apply deterministic tie-breaking, such as sorting by stable product identifier and image identifier.
- Return top-K similar product images or products with similarity scores and useful inspection metadata.

The search should return an empty result or a clear error when the source image is missing, unreadable, or not included in the fitted candidate set.

## Evaluation Strategy

Because this is an image-only product similarity baseline and not a personalized recommender, evaluation should focus on visual similarity quality and output validity.

Evaluation should include:

- Manual visual spot-checking of similar images.
- Product type or category consistency where metadata exists.
- Duplicate and self-match prevention.
- Top-K output validity, including stable product and image identifiers.
- Coverage over products with usable images.
- Deterministic repeatability across repeated runs.
- Latency checks on small deterministic fixtures.
- Failure handling for missing, unreadable, or unsupported images.

These checks should validate the baseline behavior without claiming production-level performance.

## Expected Outputs

The implemented baseline should produce:

- A top-K list of similar Amazon Berkeley Objects product images or products for each source image or product.
- Similarity scores for returned candidates.
- Source product and source image identifiers.
- Candidate product and image identifiers.
- Useful metadata for inspection, such as product name or product type where available.
- Coverage and failure counts for usable, missing, and unreadable images.
- A small, human-readable sample output artifact for review.

## Risks and Limitations

Key risks and limitations include:

- Small image fixtures may not represent the full Amazon Berkeley Objects image distribution.
- Visual similarity may not align with product usefulness, category relevance, or customer intent.
- Missing or unreadable images can reduce coverage.
- Pretrained image embeddings may introduce dependency, runtime, or model availability concerns.
- Image-only similarity may miss important textual details such as brand, material, size, or compatibility.
- Manual spot-checking is useful but subjective.
- This baseline is not personalized, not multimodal, and not production-ready by itself.

## Acceptance Criteria

This protocol is accepted when:

- The baseline is clearly defined as Amazon Berkeley Objects image-only product-to-product similarity.
- RetailRocket is described only as a separate dataset track.
- The first implementation is constrained to small deterministic fixtures.
- Full raw Amazon Berkeley Objects image archives are not fully extracted or processed.
- Possible future embedding approaches are described without requiring implementation yet.
- Cosine similarity, top-K retrieval, source-image exclusion, and deterministic tie-breaking are specified.
- Evaluation focuses on visual similarity validation and output quality, not personalized recommendation metrics.
- The document does not claim image similarity, multimodal recommendation, API, deployment, or advanced systems are implemented.

## Next Step After This Protocol

The recommended next step is to implement a small Amazon Berkeley Objects image baseline proof of concept using existing deterministic image fixtures and mapping metadata.

Before implementation, confirm the available fixture image paths, choose the initial pretrained embedding approach, and review any dependency or model download requirements. The implementation should remain image-only, bounded, and independent from RetailRocket.
