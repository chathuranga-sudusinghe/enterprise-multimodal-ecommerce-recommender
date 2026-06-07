"""Text-only product similarity baseline for Amazon Berkeley Objects metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


ABO_TEXT_FIELDS: tuple[str, ...] = (
    "item_name",
    "brand",
    "bullet_point",
    "product_type",
    "color",
    "material",
    "style",
)


@dataclass(frozen=True)
class ABOSimilarityResult:
    """Inspectable result for one similar Amazon Berkeley Objects product."""

    product_id: str
    similarity_score: float
    metadata: dict[str, Any]


def normalize_metadata_text_value(value: Any) -> str:
    """Normalize scalar and list-like metadata values into safe text."""

    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    if isinstance(value, Mapping):
        return " ".join(
            normalized
            for item in value.values()
            if (normalized := normalize_metadata_text_value(item))
        )

    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return " ".join(
            normalized
            for item in value
            if (normalized := normalize_metadata_text_value(item))
        )

    return str(value).strip()


def build_combined_product_text(product: Mapping[str, Any]) -> str:
    """Build deterministic text from approved Amazon Berkeley Objects fields."""

    return " ".join(
        normalized
        for field in ABO_TEXT_FIELDS
        if (normalized := normalize_metadata_text_value(product.get(field)))
    )


class ABOTextSimilarityBaseline:
    """TF-IDF cosine-similarity baseline for ABO product-to-product retrieval."""

    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer()
        self._product_lookup: dict[str, Mapping[str, Any]] = {}
        self._text_product_ids: list[str] = []
        self._text_product_id_to_index: dict[str, int] = {}
        self._tfidf_matrix: Any | None = None
        self._is_fitted = False

    def fit(self, products: Sequence[Mapping[str, Any]]) -> "ABOTextSimilarityBaseline":
        """Prepare product metadata, combined text, and TF-IDF vectors."""

        self._product_lookup = {}
        self._text_product_ids = []
        self._text_product_id_to_index = {}
        self._tfidf_matrix = None

        product_texts: list[str] = []

        for product in products:
            product_id = self._get_product_id(product)
            if product_id in self._product_lookup:
                raise ValueError(f"Duplicate Amazon Berkeley Objects product_id: {product_id}")
            self._product_lookup[product_id] = product

            combined_text = build_combined_product_text(product)
            if not combined_text:
                continue

            self._text_product_id_to_index[product_id] = len(self._text_product_ids)
            self._text_product_ids.append(product_id)
            product_texts.append(combined_text)

        if product_texts:
            self._tfidf_matrix = self._vectorizer.fit_transform(product_texts)

        self._is_fitted = True
        return self

    def recommend_similar(
        self,
        product_id: str,
        top_k: int = 10,
    ) -> list[ABOSimilarityResult]:
        """Return top-K text-similar products for an ABO source product."""

        if not self._is_fitted:
            raise RuntimeError("ABOTextSimilarityBaseline must be fitted before recommendations.")

        source_product_id = str(product_id)
        if source_product_id not in self._product_lookup:
            raise ValueError(f"Unknown Amazon Berkeley Objects product_id: {source_product_id}")

        if top_k <= 0:
            return []

        if (
            self._tfidf_matrix is None
            or source_product_id not in self._text_product_id_to_index
            or len(self._text_product_ids) <= 1
        ):
            return []

        source_index = self._text_product_id_to_index[source_product_id]
        similarities = cosine_similarity(
            self._tfidf_matrix[source_index],
            self._tfidf_matrix,
        )[0]

        candidates: list[tuple[str, float]] = []
        for candidate_id, score in zip(self._text_product_ids, similarities, strict=True):
            if candidate_id == source_product_id:
                continue
            candidates.append((candidate_id, float(score)))

        ranked_candidates = sorted(candidates, key=lambda item: (-item[1], item[0]))

        return [
            ABOSimilarityResult(
                product_id=candidate_id,
                similarity_score=score,
                metadata=self._build_result_metadata(self._product_lookup[candidate_id]),
            )
            for candidate_id, score in ranked_candidates[:top_k]
        ]

    @staticmethod
    def _get_product_id(product: Mapping[str, Any]) -> str:
        product_id = product.get("item_id", product.get("product_id"))
        if product_id is None or str(product_id).strip() == "":
            raise ValueError("Amazon Berkeley Objects product record is missing item_id.")
        return str(product_id)

    @staticmethod
    def _build_result_metadata(product: Mapping[str, Any]) -> dict[str, Any]:
        metadata_fields = ("item_name", "brand", "product_type")
        return {field: product[field] for field in metadata_fields if field in product}
