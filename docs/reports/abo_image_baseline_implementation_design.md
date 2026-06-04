# Amazon Berkeley Objects Image Baseline Implementation Design

## Purpose

This document defines the implementation design for the first Amazon Berkeley Objects image-only product-to-product similarity baseline.

The design is local-first, small, deterministic, and intended for fixture-based implementation. It does not implement image similarity yet, add dependencies, or claim production readiness.

## Current Inputs Available

The current Amazon Berkeley Objects sample fixtures include:

- `data/sample/amazon_berkeley_objects/listings_sample.jsonl`
- `data/sample/amazon_berkeley_objects/images_sample.csv`
- `data/sample/amazon_berkeley_objects/image_paths_sample.txt`
- `data/sample/amazon_berkeley_objects/images/small/`

The fixtures provide:

- Product metadata and stable `item_id` values.
- Product-to-image references through `main_image_id` and `other_image_id`.
- Image metadata with `image_id`, `path`, `height`, and `width`.
- Tiny deterministic synthetic JPEG files matching the sample image paths.

RetailRocket data must not be used in this baseline.

## Recommended First Baseline Method

The recommended first method is an image-only color histogram baseline.

The baseline should:

- Load only the tiny Amazon Berkeley Objects sample JPEG fixtures.
- Extract deterministic normalized Red, Green, Blue (RGB) color histogram features from each image.
- Build product-level image representations from one or more image features.
- Use cosine similarity over image feature vectors.
- Return top-K visually similar products.
- Exclude the source product itself.
- Use deterministic tie-breaking by stable Amazon Berkeley Objects product identifier.
- Include product metadata only for inspection and reporting.

This is a baseline, not the final advanced visual model.

## Why Color Histogram Baseline First

A color histogram baseline is the best first implementation because it:

- Avoids heavy model downloads.
- Avoids Graphics Processing Unit (GPU) requirements.
- Avoids adding deep learning dependencies.
- Works with tiny deterministic image fixtures.
- Is easy to test with small synthetic images.
- Provides a simple visual similarity reference before advanced image embeddings.
- Keeps the implementation local, explainable, and reviewable.

The goal is to validate image fixture plumbing, feature extraction, ranking, and output contracts before introducing heavier models.

## Why Not ResNet/CLIP Yet

ResNet-style embeddings and CLIP-style embeddings can be useful later, but they are not recommended for the first image-only baseline.

They are deferred because they may require:

- Additional dependencies.
- Model downloads.
- Larger runtime and memory requirements.
- More complex preprocessing.
- More careful evaluation and governance notes.

CLIP is also a multimodal-style embedding approach and should not be used in the first image-only baseline unless explicitly approved later. ResNet-style computer vision embeddings can be considered as a separate improvement after the color histogram baseline is implemented and reviewed.

## Image Loading Strategy

The future implementation should:

- Read image paths from `image_paths_sample.txt` and/or `images_sample.csv`.
- Resolve paths relative to `data/sample/amazon_berkeley_objects/`.
- Load only tiny sample JPEG fixtures.
- Validate that each selected image exists.
- Handle missing, unreadable, or unsupported files with clear errors or skip reporting.
- Avoid loading, extracting, or processing the full raw Amazon Berkeley Objects image archives.

If a lightweight image library is already available later, it may be used. If not, the implementation should use the smallest safe image-loading approach and document the tradeoff.

## Feature Extraction Strategy

The first feature should be a normalized RGB color histogram.

Suggested design:

- Convert each image to RGB.
- Use a small fixed number of bins per channel.
- Concatenate channel histograms into one vector.
- Normalize the vector so images of different dimensions remain comparable.
- Keep the feature extraction deterministic for the same image bytes.

The feature should use image pixels only. Product text metadata must not be part of the similarity vector.

## Product-Level Image Representation

Products may have one or more image references.

The first implementation should use a simple documented policy, such as:

- Prefer `main_image_id` when available; or
- Average normalized image vectors across the product's bounded image set.

The recommended first policy is to use `main_image_id` for product-level representation because it is simple, deterministic, and easy to inspect. Averaging multiple image embeddings can be added later if needed.

## Similarity Search Logic

For a source product, the baseline should:

1. Resolve the source product's selected image.
2. Build or reuse product-level image vectors for candidate products.
3. Compute cosine similarity between the source product vector and candidate vectors.
4. Exclude the source product itself.
5. Sort by descending similarity score.
6. Break ties deterministically by stable Amazon Berkeley Objects product identifier.
7. Return top-K visually similar products.

The baseline should raise a clear error for unknown source products and handle products without usable images according to the documented behavior.

## Expected Output Artifact

The future runner should write a small JSON report, such as:

- `docs/reports/abo_image_similarity_sample_output.json`

The artifact should include:

- `baseline_name`
- `dataset_track`
- `method`
- `input_sample_paths`
- `top_k`
- `generated_at_utc`
- `source_product_id`
- `source_image_id`
- `source_product_metadata`
- `recommendations`
- `assumptions`
- `limitations`

Recommendation records should include:

- `product_id`
- `image_id`
- `similarity_score`
- Useful metadata for inspection, such as `item_name`, `brand`, and `product_type`

The artifact should clearly state that this is image-only similarity and not multimodal recommendation.

## Testing Plan

Focused tests should cover:

- Loading sample image paths from fixture metadata.
- Resolving image files relative to the Amazon Berkeley Objects sample directory.
- Extracting deterministic normalized color histogram features.
- Building product-level image representations.
- Excluding the source product from recommendations.
- Ranking similar products with deterministic tie-breaking.
- Handling unknown source products.
- Handling missing or unreadable image files.
- Creating a valid small JSON runner artifact.

Tests should use only small sample fixtures or temporary files.

## Evaluation Plan

Evaluation should focus on baseline validity rather than production visual quality.

Evaluation should include:

- Manual inspection of top-K outputs.
- No self-recommendations.
- No duplicate recommendations.
- Image coverage over products with usable fixture images.
- Deterministic repeatability.
- Small fixture latency checks.
- Product type or category consistency where metadata is available.

Because current images are tiny synthetic fixtures, visual quality conclusions should be limited. Real visual relevance evaluation should wait for an approved representative image sample.

## Risks and Limitations

- Color histograms capture coarse color distribution, not object shape, texture, brand, or product function.
- Tiny synthetic fixtures are useful for plumbing but not meaningful visual relevance evaluation.
- Product images with similar colors may rank highly even when product types differ.
- Product images with different colors may rank poorly even when products are visually or functionally similar.
- This baseline is not personalized, not behavior-based, not multimodal, and not production-ready.
- Full raw Amazon Berkeley Objects image archives must not be processed in this implementation step.

## Files to Create in the Next Implementation Step

Expected future implementation files may include:

- `src/ecommerce_recommender/models/abo_image_similarity.py`
- `scripts/run_abo_image_baseline.py`
- `tests/unit/test_abo_image_similarity.py`
- `tests/unit/test_run_abo_image_baseline.py`
- `docs/reports/abo_image_similarity_sample_output.json`

No dependency file should be edited unless a required image-loading dependency is reviewed and approved.

## Acceptance Criteria

The future implementation is acceptable when:

- It is image-only product-to-product similarity.
- It uses Amazon Berkeley Objects sample fixtures only.
- It does not use RetailRocket data or identifiers.
- It does not use text metadata as the similarity signal.
- It extracts deterministic normalized RGB color histogram features.
- It returns top-K products using cosine similarity.
- It excludes the source product.
- It uses deterministic product identifier tie-breaking.
- It includes focused unit tests and a small JSON sample output.
- It does not claim production readiness, multimodal recommendation, Application Programming Interface (API), deployment, Retrieval-Augmented Generation (RAG), agents, Model Context Protocol (MCP), contextual bandits, or advanced image modeling.

## Next Step After This Design

Implement the small color-histogram image-only baseline using the existing Amazon Berkeley Objects sample fixtures.

The implementation should start with `src/ecommerce_recommender/models/abo_image_similarity.py`, then add a small runner, focused unit tests, and a sample JSON output artifact. ResNet-style embeddings, CLIP-style embeddings, and multimodal similarity should remain future improvements after this first baseline is reviewed.
