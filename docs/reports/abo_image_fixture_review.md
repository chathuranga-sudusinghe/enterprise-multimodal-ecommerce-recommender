# Amazon Berkeley Objects Image Fixture Review

## Purpose

This report reviews the existing small Amazon Berkeley Objects image fixtures before implementing an image-only product-to-product similarity baseline.

The review checks whether the current fixtures provide enough product, image metadata, and path information for a future bounded baseline. It does not implement image similarity, image embeddings, or any new dependencies.

## Files Inspected

The following small fixture files were inspected:

- `data/sample/amazon_berkeley_objects/listings_sample.jsonl`
- `data/sample/amazon_berkeley_objects/images_sample.csv`
- `data/sample/amazon_berkeley_objects/image_paths_sample.txt`

No full raw Amazon Berkeley Objects archives were loaded, extracted, or processed.

## Fixture Structure Summary

The sample fixture directory now contains metadata fixtures and tiny synthetic JPEG image files:

| Fixture | Observed Rows | Purpose |
| --- | ---: | --- |
| `listings_sample.jsonl` | 6 listings | Product metadata and product-to-image references |
| `images_sample.csv` | 10 image metadata rows | Image identifiers, relative paths, and dimensions |
| `image_paths_sample.txt` | 10 paths | Relative image path references |
| `images/small/**/*.jpg` | 10 images | Tiny deterministic synthetic JPEG fixtures |

The listed image paths are now backed by actual sample image files in the fixture directory. These images are synthetic placeholders for validation and local baseline plumbing, not real product images.

## Product/Listings Fields Available

The listings fixture includes the following fields:

- `item_id`
- `item_name`
- `brand`
- `bullet_point`
- `product_type`
- `color`
- `material`
- `style`
- `main_image_id`
- `other_image_id`

These fields are suitable for product identity, product-to-image mapping, and inspection metadata. For an image-only baseline, text fields should be used only for reporting or manual review, not as the similarity signal.

## Image Metadata Fields Available

The image metadata fixture includes:

- `image_id`
- `path`
- `height`
- `width`

The metadata is sufficient to define a small image index and validate expected image dimensions. The fixture directory now also contains tiny synthetic JPEG files at the referenced paths.

## Image Path Format

Image paths are relative paths using the Amazon Berkeley Objects small-image layout pattern:

```text
images/small/<prefix>/<image_id>.jpg
```

Examples include:

- `images/small/a1/a1b2c3d4.jpg`
- `images/small/b2/b2c3d4e5.jpg`
- `images/small/f6/f6a7b8ca.jpg`

These paths are useful for validating expected archive-relative layout, and the referenced fixture files now exist under `data/sample/amazon_berkeley_objects/`.

## Product-to-Image Mapping Observations

The six product listings reference ten unique image identifiers through `main_image_id` and `other_image_id`.

Observed mapping coverage:

- 6 listings are present.
- 10 unique image identifiers are referenced by listings.
- 10 image metadata rows are present.
- All listing-referenced image identifiers have matching image metadata rows.
- No extra image metadata identifiers were observed outside the listing references.
- Products may have one or two image references.

This is a coherent metadata mapping fixture for future image baseline logic. The referenced paths now resolve to small synthetic JPEG files.

## Missing or Unavailable Assets

Actual sample image files are now available in the inspected fixture directory as tiny deterministic synthetic JPEG placeholders.

The following path checks were observed:

- Total image paths listed: 10
- Existing image files under `data/sample/amazon_berkeley_objects/`: 10
- Missing image files: 0

The current sample images are valid fixture files for testing path resolution, file readability, and bounded image-loading behavior. They are not real product images and should not be used to evaluate visual recommendation quality.

## Readiness for Image Baseline Implementation

The current fixtures are ready for a small image-baseline plumbing proof of concept.

Ready:

- Product metadata is available.
- Image metadata is available.
- Product-to-image mappings are internally consistent.
- Relative image path format is documented by fixture data.
- Referenced image paths now exist as tiny deterministic JPEG files.
- Small fixture size is appropriate for deterministic tests.

Still limited:

- The images are synthetic placeholders, not real product images.
- Visual spot-checking can validate pipeline behavior but not product relevance.
- Image embedding results from these placeholders should not be interpreted as meaningful product similarity.

The next implementation can use these fixtures to test image loading, embedding plumbing, cosine similarity, source-product exclusion, deterministic ordering, and small-sample latency without touching the full raw Amazon Berkeley Objects archives.

## Risks and Limitations

- Synthetic fixture images can validate pipeline mechanics but not visual similarity quality.
- Tiny placeholder images may not expose realistic image loading, decoding, format, or preprocessing issues.
- Small fixtures are useful for tests but cannot represent full Amazon Berkeley Objects image diversity.
- Text metadata must not be used as the similarity signal for the image-only baseline.
- Full raw image archives should not be extracted or processed during initial implementation.
- Any pretrained image feature extractor may require dependency or model availability review before implementation.

## Recommended Next Step

Implement a bounded image-only baseline proof of concept using the existing metadata fixtures and tiny synthetic JPEG files.

The recommended implementation decision is to treat these images as fixture preparation only. They are suitable for local image-loading and baseline mechanics, but real visual quality evaluation should wait for an approved small set of representative product images or a bounded raw-archive extraction plan.
