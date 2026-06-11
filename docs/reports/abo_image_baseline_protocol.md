# Amazon Berkeley Objects Image Similarity Baseline Protocol

## Purpose

This document defines the protocol for a simple Amazon Berkeley Objects image-based product similarity baseline before implementation.

The baseline is intended to create a realistic, reproducible image-only product-to-product similarity reference for local development. It should use Amazon Berkeley Objects product images and image metadata only as the similarity signal, starting with small deterministic fixtures rather than full raw archive processing.

## Dataset Track

This protocol applies only to the `amazon_berkeley_text_images-based` dataset track.

Amazon Berkeley Objects is used for product metadata, text, and image similarity work. RetailRocket remains a separate behavior/event recommendation track and must not be joined to Amazon Berkeley Objects product, listing, or image identifiers.

The Amazon Berkeley Objects text baseline protocol, implementation, runner, and sample output artifact already exist. That text baseline is separate from this image-only protocol. Future multimodal similarity may compare or combine the text and image baselines later, but multimodal recommendation is not part of this task.

## Why This Baseline Is Needed

The completed text baseline provides a metadata/text product similarity reference. A separate image baseline is needed to establish a visual similarity reference before any multimodal work is considered.

This protocol helps ensure future image work:

- Uses Amazon Berkeley Objects image assets safely.
- Starts with small deterministic image fixtures.
- Defines evaluation before implementation.
- Avoids training a custom deep learning model for the baseline.
- Avoids overclaiming production readiness or multimodal capability.

## What This Baseline Does

The future baseline should retrieve visually similar Amazon Berkeley Objects products using image features.

It should:

- Use Amazon Berkeley Objects product images and image metadata only for similarity.
- Generate one image embedding per product image.
- Use a simple strategy for products with multiple images, such as using the main image or averaging image embeddings.
- Use cosine similarity to retrieve top-K visually similar products.
- Exclude the source product itself from returned recommendations.
- Use deterministic tie-breaking by stable Amazon Berkeley Objects product identifier.
- Include text metadata only for inspection and reporting where useful.

## What This Baseline Does Not Do

This baseline does not:

- Provide personalized recommendations.
- Use RetailRocket behavior data, users, events, visitors, items, or transactions.
- Merge RetailRocket and Amazon Berkeley Objects data.
- Use text metadata as the similarity signal.
- Implement multimodal recommendation.
- Use CLIP or multimodal embeddings in the first image-only baseline unless explicitly approved later.
- Use video, spin, 360-degree, or 3D assets.
- Train a custom deep learning model.
- Implement an Application Programming Interface (API), deployment stack, Retrieval-Augmented Generation (RAG), agents, Model Context Protocol (MCP), contextual bandits, or advanced systems.
- Claim image similarity is already implemented.
- Claim production readiness or business impact before implementation and evaluation.

## Input Assets

The baseline should use Amazon Berkeley Objects image-related assets only, such as:

- Small deterministic sample image fixtures.
- Product-to-image mapping metadata.
- Stable product identifiers.
- Stable image identifiers.
- Local sample image paths where available.
- Image metadata needed to locate and validate sample images.

Text metadata such as `item_name`, `brand`, or `product_type` may be included in outputs for inspection and evaluation context, but it must not be used as the image similarity signal.

The first implementation must not fully load, extract, or process the full raw Amazon Berkeley Objects image archives.

## Image Selection Strategy

The first implementation should use a small, deterministic image selection policy.

It should:

- Prefer existing Amazon Berkeley Objects sample fixtures.
- Use only approved local sample image paths or bounded fixture references.
- Validate that selected images exist and are readable.
- Skip or report missing, unreadable, or unsupported images safely.
- Avoid full raw archive extraction.
- Avoid processing all available raw images during initial baseline work.
- Keep product and image selection stable across repeated runs.

For products with multiple images, the implementation should define one simple policy before running similarity. Acceptable first policies include using the main image when available or averaging embeddings across a small bounded set of product images.

## Baseline Method

The baseline should be image-only, simple, and reproducible.

The expected method is:

1. Load a small Amazon Berkeley Objects image fixture and product-image mapping.
2. Select source and candidate images using the documented image selection policy.
3. Generate one embedding per selected product image using a simple pretrained image embedding model.
4. Prefer a lightweight pretrained computer vision model if already available later, such as ResNet-style embeddings or a similar standard feature extractor.
5. Do not train a custom model for this baseline.
6. Do not add new dependencies or model downloads without review.
7. Compare image vectors using cosine similarity.
8. Return top-K visually similar products.

CLIP-style or other multimodal embeddings should not be used for this first image-only baseline unless explicitly approved later.

## Similarity Search Logic

For a given source product, the similarity search should:

- Resolve the source product image or images from Amazon Berkeley Objects image mapping metadata.
- Build or load image vectors for source and candidate products.
- Exclude the source product itself from returned recommendations.
- Sort candidates by descending cosine similarity.
- Apply deterministic tie-breaking by stable Amazon Berkeley Objects product identifier.
- Return top-K visually similar products with similarity scores and useful inspection metadata.

If a source product has no usable image, the implementation should return a clear error or an empty result according to the documented runner behavior.

## Evaluation Strategy

Because this is image-only product similarity and not personalized recommendation, evaluation should focus on visual relevance and output validity.

Evaluation should include:

- Manual visual spot-checking of retrieved products.
- `product_type` or category consistency where metadata is available.
- No self-recommendations.
- No duplicate recommendations.
- Image coverage over products with usable images.
- Deterministic output for repeated runs with the same input.
- Small fixture-based tests.
- Latency checks on small samples.
- Failure handling for missing, unreadable, or unsupported images.

These checks should validate baseline behavior without claiming production-level performance.

## Expected Outputs

The implemented baseline should produce:

- A top-K list of visually similar Amazon Berkeley Objects products for a source product.
- Similarity scores for returned products.
- Source product identifier and source image identifier or identifiers.
- Candidate product identifiers and image identifiers.
- Inspection metadata where available, such as `item_name`, `brand`, or `product_type`.
- Coverage counts for usable and skipped images.
- A small, human-readable sample output artifact.

## Risks and Limitations

Key risks and limitations include:

- Small fixtures may not represent the full Amazon Berkeley Objects image distribution.
- Visual similarity may not match product usefulness, compatibility, or customer intent.
- Missing or unreadable sample images can reduce coverage.
- Pretrained image features may require dependency or model availability review.
- Image-only similarity may miss important text-only attributes such as brand, size, material, or style.
- Manual visual checks are useful but subjective.
- This baseline is not personalized, not behavior-based, not multimodal, and not production-ready.

## Acceptance Criteria

This protocol is accepted when:

- The baseline is clearly defined as Amazon Berkeley Objects image-only product-to-product similarity.
- RetailRocket is kept separate and is not used in ABO image logic.
- Text metadata is limited to inspection and reporting, not similarity scoring.
- The first implementation is constrained to small deterministic fixtures.
- Full raw Amazon Berkeley Objects image archives are not fully extracted or processed.
- A simple pretrained image embedding approach is specified without requiring dependency changes in this document.
- CLIP-style or multimodal embeddings are excluded from the first implementation unless explicitly approved later.
- Cosine similarity, top-K retrieval, source-product exclusion, and deterministic product identifier tie-breaking are specified.
- Evaluation includes manual visual checks, output validity, coverage, determinism, small fixture testing, and latency checks.
- The document does not claim image similarity, multimodal recommendation, API, deployment, or advanced systems are implemented.

## Next Step After This Protocol

The recommended next implementation step is to inspect the existing Amazon Berkeley Objects sample image fixtures and mapping metadata, then build a small bounded image-only baseline proof of concept.

Before implementation, confirm the fixture image paths, choose the lightweight pretrained image feature approach, and review any dependency or model download requirements. The implementation should remain local, deterministic, image-only, and independent from RetailRocket.
