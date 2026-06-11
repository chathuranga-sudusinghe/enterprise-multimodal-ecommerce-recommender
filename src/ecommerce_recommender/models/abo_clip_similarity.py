"""CLIP-based multimodal product similarity for Amazon Berkeley Objects."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import torch
from PIL import Image


DEFAULT_CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"


@dataclass(frozen=True)
class ABOCLIPProduct:
    """Amazon Berkeley Objects product input for CLIP similarity."""

    product_id: str
    text: str
    image_path: Path


@dataclass(frozen=True)
class ABOCLIPSimilarityResult:
    """Similarity result for one Amazon Berkeley Objects product."""

    product_id: str
    score: float


class ABOCLIPSimilarityModel:
    """CLIP multimodal product-to-product similarity model for ABO products."""

    def __init__(
        self,
        model_name: str = DEFAULT_CLIP_MODEL_NAME,
        text_weight: float = 0.5,
        image_weight: float = 0.5,
        device: str | None = None,
        local_files_only: bool = False,
        model: Any | None = None,
        processor: Any | None = None,
    ) -> None:
        self.model_name = model_name
        self.text_weight = text_weight
        self.image_weight = image_weight
        self.device = device or "cpu"
        self.local_files_only = local_files_only
        self.model = model
        self.processor = processor

        self._validate_weights()

    def similar_items(
        self,
        products: Sequence[ABOCLIPProduct],
        source_product_id: str,
        top_k: int = 10,
    ) -> list[ABOCLIPSimilarityResult]:
        """Return top-K CLIP-similar ABO products for a source product."""

        if not products:
            raise ValueError("ABO CLIP product list must not be empty.")
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        product_ids = [product.product_id for product in products]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("ABO CLIP products must have unique product_id values.")
        if source_product_id not in set(product_ids):
            raise ValueError(f"Unknown Amazon Berkeley Objects product_id: {source_product_id}")

        model, processor = self._get_model_and_processor()
        text_embeddings = self._encode_texts(model, processor, [product.text for product in products])
        image_embeddings = self._encode_images(
            model,
            processor,
            [product.image_path for product in products],
        )
        fused_embeddings = self._fuse_embeddings(text_embeddings, image_embeddings)

        source_index = product_ids.index(source_product_id)
        source_embedding = fused_embeddings[source_index]
        similarities = fused_embeddings @ source_embedding

        candidates = [
            (product_id, float(score))
            for product_id, score in zip(product_ids, similarities.tolist(), strict=True)
            if product_id != source_product_id
        ]
        ranked_candidates = sorted(candidates, key=lambda item: (-item[1], item[0]))

        return [
            ABOCLIPSimilarityResult(product_id=product_id, score=score)
            for product_id, score in ranked_candidates[:top_k]
        ]

    def _validate_weights(self) -> None:
        if self.text_weight < 0 or self.image_weight < 0:
            raise ValueError("CLIP fusion weights must be non-negative.")
        if self.text_weight == 0 and self.image_weight == 0:
            raise ValueError("At least one CLIP fusion weight must be greater than zero.")

    def _get_model_and_processor(self) -> tuple[Any, Any]:
        if self.model is None or self.processor is None:
            from transformers import CLIPModel, CLIPProcessor

            try:
                self.model = CLIPModel.from_pretrained(
                    self.model_name,
                    local_files_only=self.local_files_only,
                )
                self.processor = CLIPProcessor.from_pretrained(
                    self.model_name,
                    local_files_only=self.local_files_only,
                )
            except OSError as exc:
                if self.local_files_only:
                    raise RuntimeError(
                        "CLIP model files are not available in the local Hugging Face "
                        f"cache for {self.model_name!r}. Run once without "
                        "--local-files-only to download them, then retry offline."
                    ) from exc
                raise

        if hasattr(self.model, "to"):
            self.model = self.model.to(self.device)
        if hasattr(self.model, "eval"):
            self.model.eval()

        return self.model, self.processor

    def _encode_texts(self, model: Any, processor: Any, texts: Sequence[str]) -> torch.Tensor:
        inputs = processor(
            text=list(texts),
            return_tensors="pt",
            padding=True,
            truncation=True,
        )
        inputs = _move_inputs_to_device(inputs, self.device)
        with torch.no_grad():
            embeddings = model.get_text_features(**inputs)
        return _l2_normalize(_as_tensor(embeddings, self.device))

    def _encode_images(self, model: Any, processor: Any, image_paths: Sequence[Path]) -> torch.Tensor:
        images = []
        for image_path in image_paths:
            image = Image.open(image_path).convert("RGB")
            image.filename = str(image_path)
            images.append(image)
        try:
            inputs = processor(images=images, return_tensors="pt")
            inputs = _move_inputs_to_device(inputs, self.device)
            with torch.no_grad():
                embeddings = model.get_image_features(**inputs)
        finally:
            for image in images:
                image.close()
        return _l2_normalize(_as_tensor(embeddings, self.device))

    def _fuse_embeddings(self, text_embeddings: torch.Tensor, image_embeddings: torch.Tensor) -> torch.Tensor:
        fused_embeddings = self.text_weight * text_embeddings + self.image_weight * image_embeddings
        return _l2_normalize(fused_embeddings)


def _as_tensor(values: Any, device: str) -> torch.Tensor:
    extracted_values = _extract_embedding_values(values)
    if isinstance(extracted_values, torch.Tensor):
        return extracted_values.to(device=device, dtype=torch.float32)
    return torch.as_tensor(extracted_values, dtype=torch.float32, device=device)


def _extract_embedding_values(values: Any) -> Any:
    if isinstance(values, torch.Tensor):
        return values

    if isinstance(values, Mapping):
        preferred_keys = ("text_embeds", "image_embeds", "pooler_output", "last_hidden_state")
        for key in preferred_keys:
            if key in values:
                return _pool_hidden_state_if_needed(key, values[key])
        for value in values.values():
            try:
                return _extract_embedding_values(value)
            except TypeError:
                continue
        raise TypeError("Could not extract CLIP embeddings from mapping output.")

    if hasattr(values, "pooler_output"):
        return values.pooler_output

    if hasattr(values, "last_hidden_state"):
        return _pool_hidden_state_if_needed("last_hidden_state", values.last_hidden_state)

    if isinstance(values, (tuple, list)):
        for value in values:
            try:
                return _extract_embedding_values(value)
            except TypeError:
                continue
        return values

    return values


def _pool_hidden_state_if_needed(key: str, values: Any) -> Any:
    if key != "last_hidden_state":
        return values

    hidden_state = values
    if not isinstance(hidden_state, torch.Tensor):
        hidden_state = torch.as_tensor(hidden_state, dtype=torch.float32)
    if hidden_state.ndim >= 3:
        return hidden_state[:, 0, :]
    return hidden_state


def _l2_normalize(embeddings: torch.Tensor) -> torch.Tensor:
    norms = torch.linalg.vector_norm(embeddings, ord=2, dim=1, keepdim=True)
    return embeddings / norms.clamp_min(1e-12)


def _move_inputs_to_device(inputs: Any, device: str) -> Any:
    if hasattr(inputs, "to"):
        return inputs.to(device)
    if isinstance(inputs, dict):
        return {
            key: value.to(device) if hasattr(value, "to") else value
            for key, value in inputs.items()
        }
    return inputs
