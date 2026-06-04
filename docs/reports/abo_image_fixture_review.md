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

The sample fixture directory currently contains metadata fixtures only:

| Fixture | Observed Rows | Purpose |
| --- | ---: | --- |
| `listings_sample.jsonl` | 6 listings | Product metadata and product-to-image references |
| `images_sample.csv` | 10 image metadata rows | Image identifiers, relative paths, and dimensions |
| `image_paths_sample.txt` | 10 paths | Relative image path references |

The listed image paths are not backed by actual image files in the sample fixture directory.

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

The metadata is sufficient to define a small image index and validate expected image dimensions. It does not provide actual pixel data.

## Image Path Format

Image paths are relative paths using the Amazon Berkeley Objects small-image layout pattern:

```text
images/small/<prefix>/<image_id>.jpg
```

Examples include:

- `images/small/a1/a1b2c3d4.jpg`
- `images/small/b2/b2c3d4e5.jpg`
- `images/small/f6/f6a7b8ca.jpg`

These paths are useful for validating expected archive-relative layout, but the referenced files are not present under `data/sample/amazon_berkeley_objects/`.

## Product-to-Image Mapping Observations

The six product listings reference ten unique image identifiers through `main_image_id` and `other_image_id`.

Observed mapping coverage:

- 6 listings are present.
- 10 unique image identifiers are referenced by listings.
- 10 image metadata rows are present.
- All listing-referenced image identifiers have matching image metadata rows.
- No extra image metadata identifiers were observed outside the listing references.
- Products may have one or two image references.

This is a coherent metadata mapping fixture for future image baseline logic, but not yet a complete image fixture because image files are missing.

## Missing or Unavailable Assets

Actual sample image files are not available in the inspected fixture directory.

The following path checks were observed:

- Total image paths listed: 10
- Existing image files under `data/sample/amazon_berkeley_objects/`: 0
- Missing image files: 10

Because no actual images are present, the current fixtures are not sufficient for running real image embedding extraction or image similarity scoring.

## Readiness for Image Baseline Implementation

The current fixtures are partially ready.

Ready:

- Product metadata is available.
- Image metadata is available.
- Product-to-image mappings are internally consistent.
- Relative image path format is documented by fixture data.
- Small fixture size is appropriate for deterministic tests.

Not ready:

- Actual image files are missing.
- Image embedding extraction cannot be tested against real pixels yet.
- Visual spot-checking cannot be performed from the current sample directory.

The next implementation should either add a tiny set of safe sample image files matching the existing paths or explicitly mock image loading only for non-embedding tests. A real image-only baseline proof of concept needs actual sample images.

## Risks and Limitations

- Metadata-only fixtures can validate mapping logic but not visual similarity quality.
- Missing sample images may hide image loading, decoding, format, and preprocessing issues.
- Small fixtures are useful for tests but cannot represent full Amazon Berkeley Objects image diversity.
- Text metadata must not be used as the similarity signal for the image-only baseline.
- Full raw image archives should not be extracted or processed during initial implementation.
- Any pretrained image feature extractor may require dependency or model availability review before implementation.

## Recommended Next Step

Add or verify a tiny deterministic set of actual sample image files that match the existing `image_paths_sample.txt` paths, then implement a bounded image-only baseline proof of concept.

The recommended implementation decision is to keep the current metadata fixtures and add minimal real image fixtures before embedding work. This will allow the future baseline to test image loading, feature extraction, cosine similarity, source-product exclusion, deterministic ordering, and small-sample latency without touching the full raw Amazon Berkeley Objects archives.
