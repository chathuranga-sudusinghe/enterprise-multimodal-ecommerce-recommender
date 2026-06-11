from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any, Sequence

import pytest
import torch
from PIL import Image

from ecommerce_recommender.models.abo_clip_similarity import (
    ABOCLIPProduct,
    ABOCLIPSimilarityModel,
)


class FakeProcessor:
    def __call__(self, **kwargs: Any) -> dict[str, Any]:
        if "text" in kwargs:
            return {"items": kwargs["text"]}
        if "images" in kwargs:
            return {"items": [Path(image.filename).stem for image in kwargs["images"]]}
        raise ValueError("FakeProcessor expected text or images.")


class FakeCLIPModel:
    def __init__(
        self,
        text_embeddings: dict[str, Sequence[float]],
        image_embeddings: dict[str, Sequence[float]],
    ) -> None:
        self.text_embeddings = text_embeddings
        self.image_embeddings = image_embeddings

    def to(self, device: str) -> "FakeCLIPModel":
        return self

    def eval(self) -> None:
        return None

    def get_text_features(self, items: Sequence[str]) -> torch.Tensor:
        return torch.tensor([self.text_embeddings[item] for item in items], dtype=torch.float32)

    def get_image_features(self, items: Sequence[str]) -> torch.Tensor:
        return torch.tensor([self.image_embeddings[item] for item in items], dtype=torch.float32)


def _write_image(path: Path) -> None:
    image = Image.new("RGB", (2, 2), color=(255, 255, 255))
    image.save(path)


def _products(tmp_path: Path, product_ids: Sequence[str]) -> list[ABOCLIPProduct]:
    products = []
    for product_id in product_ids:
        image_path = tmp_path / f"{product_id}.jpg"
        _write_image(image_path)
        products.append(
            ABOCLIPProduct(
                product_id=product_id,
                text=product_id,
                image_path=image_path,
            )
        )
    return products


def _model(
    text_embeddings: dict[str, Sequence[float]],
    image_embeddings: dict[str, Sequence[float]],
    text_weight: float = 0.5,
    image_weight: float = 0.5,
) -> ABOCLIPSimilarityModel:
    return ABOCLIPSimilarityModel(
        text_weight=text_weight,
        image_weight=image_weight,
        model=FakeCLIPModel(text_embeddings, image_embeddings),
        processor=FakeProcessor(),
    )


def test_source_product_is_excluded_from_results(tmp_path: Path) -> None:
    products = _products(tmp_path, ["source", "candidate-a", "candidate-b"])
    model = _model(
        text_embeddings={
            "source": [1.0, 0.0],
            "candidate-a": [1.0, 0.0],
            "candidate-b": [0.0, 1.0],
        },
        image_embeddings={
            "source": [1.0, 0.0],
            "candidate-a": [1.0, 0.0],
            "candidate-b": [0.0, 1.0],
        },
    )

    results = model.similar_items(products, "source", top_k=3)

    assert [result.product_id for result in results] == ["candidate-a", "candidate-b"]
    assert "source" not in [result.product_id for result in results]


def test_results_are_sorted_by_similarity_descending(tmp_path: Path) -> None:
    products = _products(tmp_path, ["source", "candidate-a", "candidate-b"])
    model = _model(
        text_embeddings={
            "source": [1.0, 0.0],
            "candidate-a": [0.9, 0.1],
            "candidate-b": [0.0, 1.0],
        },
        image_embeddings={
            "source": [1.0, 0.0],
            "candidate-a": [0.9, 0.1],
            "candidate-b": [0.0, 1.0],
        },
    )

    results = model.similar_items(products, "source", top_k=2)

    assert [result.product_id for result in results] == ["candidate-a", "candidate-b"]
    assert results[0].score > results[1].score


def test_deterministic_tie_breaking_uses_product_id_ascending(tmp_path: Path) -> None:
    products = _products(tmp_path, ["source", "candidate-b", "candidate-a"])
    model = _model(
        text_embeddings={
            "source": [1.0, 0.0],
            "candidate-b": [1.0, 0.0],
            "candidate-a": [1.0, 0.0],
        },
        image_embeddings={
            "source": [1.0, 0.0],
            "candidate-b": [1.0, 0.0],
            "candidate-a": [1.0, 0.0],
        },
    )

    results = model.similar_items(products, "source", top_k=2)

    assert [result.product_id for result in results] == ["candidate-a", "candidate-b"]


def test_top_k_limits_returned_products(tmp_path: Path) -> None:
    products = _products(tmp_path, ["source", "candidate-a", "candidate-b"])
    model = _model(
        text_embeddings={
            "source": [1.0, 0.0],
            "candidate-a": [1.0, 0.0],
            "candidate-b": [0.0, 1.0],
        },
        image_embeddings={
            "source": [1.0, 0.0],
            "candidate-a": [1.0, 0.0],
            "candidate-b": [0.0, 1.0],
        },
    )

    results = model.similar_items(products, "source", top_k=1)

    assert [result.product_id for result in results] == ["candidate-a"]


def test_duplicate_product_ids_raise_value_error(tmp_path: Path) -> None:
    image_path_a = tmp_path / "duplicate-a.jpg"
    image_path_b = tmp_path / "duplicate-b.jpg"
    _write_image(image_path_a)
    _write_image(image_path_b)
    products = [
        ABOCLIPProduct(product_id="duplicate", text="source", image_path=image_path_a),
        ABOCLIPProduct(product_id="duplicate", text="candidate", image_path=image_path_b),
    ]
    model = _model({"source": [1.0, 0.0], "candidate": [0.0, 1.0]}, {})

    with pytest.raises(ValueError, match="unique product_id"):
        model.similar_items(products, "duplicate")


def test_missing_source_product_raises_value_error(tmp_path: Path) -> None:
    products = _products(tmp_path, ["known"])
    model = _model({"known": [1.0, 0.0]}, {"known": [1.0, 0.0]})

    with pytest.raises(ValueError, match="Unknown Amazon Berkeley Objects product_id"):
        model.similar_items(products, "missing")


def test_invalid_weights_raise_value_error() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        ABOCLIPSimilarityModel(text_weight=-0.1, image_weight=0.5, model=object(), processor=object())

    with pytest.raises(ValueError, match="greater than zero"):
        ABOCLIPSimilarityModel(text_weight=0.0, image_weight=0.0, model=object(), processor=object())


def test_invalid_top_k_raises_value_error(tmp_path: Path) -> None:
    products = _products(tmp_path, ["source"])
    model = _model({"source": [1.0, 0.0]}, {"source": [1.0, 0.0]})

    with pytest.raises(ValueError, match="top_k"):
        model.similar_items(products, "source", top_k=0)


def test_fusion_weights_affect_ranking_deterministically(tmp_path: Path) -> None:
    products = _products(tmp_path, ["source", "text-match", "image-match"])
    text_embeddings = {
        "source": [1.0, 0.0],
        "text-match": [1.0, 0.0],
        "image-match": [0.0, 1.0],
    }
    image_embeddings = {
        "source": [0.0, 1.0],
        "text-match": [1.0, 0.0],
        "image-match": [0.0, 1.0],
    }

    text_weighted_results = _model(
        text_embeddings,
        image_embeddings,
        text_weight=0.9,
        image_weight=0.1,
    ).similar_items(products, "source", top_k=2)
    image_weighted_results = _model(
        text_embeddings,
        image_embeddings,
        text_weight=0.1,
        image_weight=0.9,
    ).similar_items(products, "source", top_k=2)

    assert text_weighted_results[0].product_id == "text-match"
    assert image_weighted_results[0].product_id == "image-match"


def test_hugging_face_loaders_receive_local_files_only(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, bool]] = []

    class Loader:
        @classmethod
        def from_pretrained(cls, model_name: str, local_files_only: bool = False) -> object:
            calls.append((model_name, local_files_only))
            return object()

    monkeypatch.setitem(
        sys.modules,
        "transformers",
        SimpleNamespace(CLIPModel=Loader, CLIPProcessor=Loader),
    )

    model = ABOCLIPSimilarityModel(local_files_only=True)
    model._get_model_and_processor()

    assert calls == [
        ("openai/clip-vit-base-patch32", True),
        ("openai/clip-vit-base-patch32", True),
    ]


def test_local_cache_miss_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class MissingLoader:
        @classmethod
        def from_pretrained(cls, model_name: str, local_files_only: bool = False) -> object:
            raise OSError("cache miss")

    monkeypatch.setitem(
        sys.modules,
        "transformers",
        SimpleNamespace(CLIPModel=MissingLoader, CLIPProcessor=MissingLoader),
    )

    model = ABOCLIPSimilarityModel(local_files_only=True)

    with pytest.raises(RuntimeError, match="not available in the local Hugging Face cache"):
        model._get_model_and_processor()
