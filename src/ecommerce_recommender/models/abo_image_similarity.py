"""Image-only product similarity baseline for Amazon Berkeley Objects fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import numpy as np


PixelLoader = Callable[[Path], np.ndarray]


@dataclass(frozen=True)
class ABOImageSimilarityResult:
    """Inspectable result for one similar Amazon Berkeley Objects product."""

    product_id: str
    image_id: str
    similarity_score: float
    metadata: dict[str, Any]


def load_rgb_pixels(image_path: str | Path) -> np.ndarray:
    """Load RGB pixels from a small fixture image.

    Pillow is the primary path for real RGB image loading. Binary PPM is
    supported for focused unit tests. The JPEG fallback is only for repository
    placeholder JPEG fixtures when Pillow is unavailable; it is not real JPEG
    decoding and must not be treated as real visual similarity extraction.
    """

    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".ppm":
        return _load_ppm_pixels(path)

    try:
        from PIL import Image  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        if suffix in {".jpg", ".jpeg"}:
            return _load_synthetic_fixture_jpeg_pixels(path)
        raise ValueError(f"Unsupported image format without Pillow: {path.suffix}")

    with Image.open(path) as image:
        rgb_image = image.convert("RGB")
        return np.asarray(rgb_image, dtype=np.uint8)


def extract_normalized_rgb_histogram(
    image_path: str | Path,
    bins_per_channel: int = 8,
    pixel_loader: PixelLoader = load_rgb_pixels,
) -> np.ndarray:
    """Extract a deterministic normalized RGB color histogram feature."""

    if bins_per_channel <= 0:
        raise ValueError("bins_per_channel must be greater than 0.")

    pixels = pixel_loader(Path(image_path))
    if pixels.ndim != 3 or pixels.shape[2] != 3:
        raise ValueError("RGB image pixels must have shape (height, width, 3).")

    channel_histograms = [
        np.histogram(pixels[:, :, channel], bins=bins_per_channel, range=(0, 256))[0]
        for channel in range(3)
    ]
    feature = np.concatenate(channel_histograms).astype(float)
    norm = np.linalg.norm(feature)
    if norm == 0:
        raise ValueError(f"Image contains no pixels: {image_path}")
    return feature / norm


def compute_cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    """Compute cosine similarity for two numeric vectors."""

    denominator = float(np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
    if denominator == 0:
        return 0.0
    return float(np.dot(vector_a, vector_b) / denominator)


class ABOImageSimilarityBaseline:
    """Color-histogram cosine-similarity baseline for ABO product retrieval."""

    def __init__(
        self,
        bins_per_channel: int = 8,
        pixel_loader: PixelLoader = load_rgb_pixels,
    ) -> None:
        self._bins_per_channel = bins_per_channel
        self._pixel_loader = pixel_loader
        self._product_lookup: dict[str, Mapping[str, Any]] = {}
        self._product_image_ids: dict[str, str] = {}
        self._feature_product_ids: list[str] = []
        self._feature_product_id_to_index: dict[str, int] = {}
        self._feature_matrix: np.ndarray | None = None
        self._is_fitted = False

    def fit(
        self,
        products: Sequence[Mapping[str, Any]],
        images: Any,
        image_root: str | Path,
    ) -> "ABOImageSimilarityBaseline":
        """Prepare product metadata, selected images, and color features."""

        self._product_lookup = {}
        self._product_image_ids = {}
        self._feature_product_ids = []
        self._feature_product_id_to_index = {}
        self._feature_matrix = None

        image_root_path = Path(image_root)
        image_paths_by_id = self._build_image_path_lookup(images)
        features: list[np.ndarray] = []

        for product in products:
            product_id = self._get_product_id(product)
            self._product_lookup[product_id] = product

            image_id = self._selected_image_id(product)
            if not image_id or image_id not in image_paths_by_id:
                continue

            image_path = image_root_path / image_paths_by_id[image_id]
            feature = extract_normalized_rgb_histogram(
                image_path,
                bins_per_channel=self._bins_per_channel,
                pixel_loader=self._pixel_loader,
            )

            self._product_image_ids[product_id] = image_id
            self._feature_product_id_to_index[product_id] = len(self._feature_product_ids)
            self._feature_product_ids.append(product_id)
            features.append(feature)

        if features:
            self._feature_matrix = np.vstack(features)

        self._is_fitted = True
        return self

    def recommend_similar(
        self,
        product_id: str,
        top_k: int = 10,
    ) -> list[ABOImageSimilarityResult]:
        """Return top-K image-similar products for an ABO source product."""

        if not self._is_fitted:
            raise RuntimeError("ABOImageSimilarityBaseline must be fitted before recommendations.")

        source_product_id = str(product_id)
        if source_product_id not in self._product_lookup:
            raise ValueError(f"Unknown Amazon Berkeley Objects product_id: {source_product_id}")

        if top_k <= 0:
            return []

        if (
            self._feature_matrix is None
            or source_product_id not in self._feature_product_id_to_index
            or len(self._feature_product_ids) <= 1
        ):
            return []

        source_index = self._feature_product_id_to_index[source_product_id]
        source_vector = self._feature_matrix[source_index]

        candidates: list[tuple[str, float]] = []
        for candidate_id, candidate_vector in zip(
            self._feature_product_ids,
            self._feature_matrix,
            strict=True,
        ):
            score = compute_cosine_similarity(source_vector, candidate_vector)
            if candidate_id == source_product_id:
                continue
            candidates.append((candidate_id, float(score)))

        ranked_candidates = sorted(candidates, key=lambda item: (-item[1], item[0]))

        return [
            ABOImageSimilarityResult(
                product_id=candidate_id,
                image_id=self._product_image_ids[candidate_id],
                similarity_score=score,
                metadata=self._build_result_metadata(self._product_lookup[candidate_id]),
            )
            for candidate_id, score in ranked_candidates[:top_k]
        ]

    @staticmethod
    def _build_image_path_lookup(images: Any) -> dict[str, str]:
        if hasattr(images, "to_dict"):
            records = images.to_dict("records")
        else:
            records = images

        image_paths: dict[str, str] = {}
        for image in records:
            image_id = str(image.get("image_id", "")).strip()
            image_path = str(image.get("path", "")).strip()
            if image_id and image_path:
                image_paths[image_id] = image_path
        return image_paths

    @staticmethod
    def _get_product_id(product: Mapping[str, Any]) -> str:
        product_id = product.get("item_id", product.get("product_id"))
        if product_id is None or str(product_id).strip() == "":
            raise ValueError("Amazon Berkeley Objects product record is missing item_id.")
        return str(product_id)

    @staticmethod
    def _selected_image_id(product: Mapping[str, Any]) -> str | None:
        image_id = product.get("main_image_id")
        if image_id is None or str(image_id).strip() == "":
            return None
        return str(image_id)

    @staticmethod
    def _build_result_metadata(product: Mapping[str, Any]) -> dict[str, Any]:
        metadata_fields = ("item_name", "brand", "product_type")
        return {field: product[field] for field in metadata_fields if field in product}


def _load_ppm_pixels(path: Path) -> np.ndarray:
    data = path.read_bytes()
    tokens, offset = _read_ppm_header(data)
    if len(tokens) != 4 or tokens[0] != b"P6":
        raise ValueError(f"Unsupported PPM fixture format: {path}")

    width = int(tokens[1])
    height = int(tokens[2])
    max_value = int(tokens[3])
    if width <= 0 or height <= 0 or max_value != 255:
        raise ValueError(f"Unsupported PPM dimensions or max value: {path}")

    pixel_bytes = data[offset:]
    expected_bytes = width * height * 3
    if len(pixel_bytes) != expected_bytes:
        raise ValueError(f"PPM pixel data length mismatch: {path}")

    return np.frombuffer(pixel_bytes, dtype=np.uint8).reshape((height, width, 3))

# The following PPM header parsing logic is adapted from the Pillow library's PPM image plugin,
def _read_ppm_header(data: bytes) -> tuple[list[bytes], int]:
    tokens: list[bytes] = []
    index = 0
    while len(tokens) < 4 and index < len(data):
        while index < len(data) and data[index:index + 1].isspace():
            index += 1
        if index < len(data) and data[index:index + 1] == b"#":
            while index < len(data) and data[index:index + 1] not in {b"\n", b"\r"}:
                index += 1
            continue

        start = index
        while index < len(data) and not data[index:index + 1].isspace():
            index += 1
        if start != index:
            tokens.append(data[start:index])

    while index < len(data) and data[index:index + 1].isspace():
        index += 1
    return tokens, index


def _load_synthetic_fixture_jpeg_pixels(path: Path) -> np.ndarray:
    data = path.read_bytes()
    if not (data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9")):
        raise ValueError(f"JPEG fixture has invalid start/end markers: {path}")

    width, height = _read_jpeg_dimensions(data, path)
    # This fallback is only for repository placeholder JPEG fixtures when
    # Pillow is unavailable. It validates the fixture wrapper and returns a
    # neutral placeholder pixel array; it is not real JPEG decoding and should
    # not be interpreted as real visual similarity extraction.
    return np.full((height, width, 3), 128, dtype=np.uint8)


def _read_jpeg_dimensions(data: bytes, path: Path) -> tuple[int, int]:
    index = 2
    while index < len(data) - 1:
        if data[index] != 0xFF:
            index += 1
            continue

        marker = data[index + 1]
        index += 2
        if marker in {0xD8, 0xD9}:
            continue
        if index + 2 > len(data):
            break

        segment_length = int.from_bytes(data[index:index + 2], byteorder="big")
        segment_start = index + 2
        segment_end = index + segment_length
        if segment_end > len(data):
            break

        if marker in {0xC0, 0xC1, 0xC2}:
            if segment_start + 5 >= segment_end:
                break
            height = int.from_bytes(data[segment_start + 1:segment_start + 3], "big")
            width = int.from_bytes(data[segment_start + 3:segment_start + 5], "big")
            if width <= 0 or height <= 0:
                break
            return width, height

        index = segment_end

    raise ValueError(f"Could not read JPEG dimensions: {path}")
