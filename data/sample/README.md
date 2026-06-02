# Sample Fixtures

`data/sample/` contains tiny deterministic fixtures for tests, examples, and
Continuous Integration / Continuous Deployment (CI/CD) workflows. These files
are safe to commit, but they are not the primary Machine Learning (ML)
datasets.

The real datasets are stored under `data/raw/` and are ignored by Git:

- `data/raw/RetailRocket_event-based/`
- `data/raw/amazon_berkeley_text_images-based/`

## Fixture Tracks

- `retailrocket/` mirrors the discovered RetailRocket event, item-property,
  and category-tree schemas for behavior-pipeline tests.
- `amazon_berkeley_objects/` mirrors selected Amazon Berkeley Objects (ABO)
  listing and image-metadata fields for product metadata and image-mapping
  tests.

RetailRocket and ABO are independent datasets. Their visitor, item, listing,
and image identifiers must not be joined or treated as shared identifiers.

The previous unified synthetic `products.csv`, `users.csv`, and `events.csv`
fixture design is deprecated.
