"""Lightweight deterministic agents for the ABO recommendation demo."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from ecommerce_recommender.mcp_tools.abo_recommendation_tools import (
    get_query_item_id,
    get_recommendations,
    load_product_catalog,
    load_similarity_results,
    lookup_product,
    policy_check_recommendation,
)

LOGGER = logging.getLogger(__name__)
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
OpenAIClientFactory = Callable[[str], Any]


class RetrievalAgent:
    """Retrieve one query product and candidates through MCP-style tools."""

    def run(
        self,
        products_path: str | Path,
        similarity_results_path: str | Path,
        top_k: int = 5,
        query_item_id: str | None = None,
    ) -> dict[str, Any]:
        catalog = load_product_catalog(products_path)
        results = load_similarity_results(similarity_results_path)
        selected_query_id = query_item_id or get_query_item_id(results)
        query_product = lookup_product(catalog, selected_query_id)
        if query_product is None:
            raise ValueError(f"Query item_id is not present in ABO catalog: {selected_query_id}")

        candidates: list[dict[str, Any]] = []
        for recommendation in get_recommendations(results, top_k):
            item_id = str(recommendation.get("item_id", "")).strip()
            product = lookup_product(catalog, item_id) if item_id else None
            enriched = dict(product or {})
            enriched.update(recommendation)
            enriched["catalog_found"] = product is not None
            candidates.append(enriched)

        return {
            "method_name": str(results.get("method_name", "unknown")),
            "query_item_id": selected_query_id,
            "query_product": query_product,
            "candidates": candidates,
        }


class PolicyCheckAgent:
    """Approve or reject retrieved candidates with deterministic policy checks."""

    def run(
        self,
        query_product: Mapping[str, Any],
        candidates: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        approved: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        checks: list[dict[str, Any]] = []
        for candidate in candidates:
            check = policy_check_recommendation(query_product, candidate)
            checks.append(check)
            target = approved if check["approved"] else rejected
            target.append(
                {
                    **check["recommendation"],
                    "policy_reasons": check["rejection_reasons"],
                    "policy_warnings": check["warnings"],
                }
            )

        return {
            "approved_recommendations": approved,
            "rejected_recommendations": rejected,
            "policy_checks_summary": {
                "candidates_checked": len(candidates),
                "approved_count": len(approved),
                "rejected_count": len(rejected),
                "warning_count": sum(len(check["warnings"]) for check in checks),
            },
        }


class ExplanationAgent:
    """Explain fixed recommendations deterministically or through optional OpenAI."""

    def __init__(
        self,
        use_openai: bool = False,
        model: str | None = None,
        client_factory: OpenAIClientFactory | None = None,
    ) -> None:
        self.use_openai = use_openai
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        self.client_factory = client_factory

    def run(
        self,
        query_product: Mapping[str, Any],
        recommendations: Sequence[Mapping[str, Any]],
    ) -> dict[str, str]:
        deterministic = self._deterministic_explanation(query_product, recommendations)
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not self.use_openai or not api_key:
            return {"explanation": deterministic, "explanation_mode": "deterministic"}

        try:
            client = (
                self.client_factory(api_key)
                if self.client_factory is not None
                else self._create_openai_client(api_key)
            )
            response = client.responses.create(
                model=self.model,
                input=self._build_prompt(query_product, recommendations),
            )
            explanation = str(getattr(response, "output_text", "")).strip()
            if not explanation:
                raise ValueError("OpenAI response did not contain output_text")
            return {"explanation": explanation, "explanation_mode": "openai_llm"}
        except Exception as exc:  # Optional explanation must never break recommendations.
            LOGGER.warning("OpenAI explanation unavailable; using deterministic fallback: %s", exc)
            return {"explanation": deterministic, "explanation_mode": "deterministic"}

    @staticmethod
    def _create_openai_client(api_key: str) -> Any:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("OpenAI SDK is not installed") from exc
        return OpenAI(api_key=api_key)

    @staticmethod
    def _deterministic_explanation(
        query_product: Mapping[str, Any],
        recommendations: Sequence[Mapping[str, Any]],
    ) -> str:
        query_name = str(query_product.get("item_name") or query_product.get("item_id"))
        if not recommendations:
            return f"No recommendations passed policy checks for {query_name}."
        details = []
        for recommendation in recommendations:
            name = str(recommendation.get("item_name") or recommendation.get("item_id"))
            reason = (
                "same product type"
                if recommendation.get("product_type_matches_query")
                else "model similarity"
            )
            details.append(f"{name} ({reason})")
        return f"For {query_name}, the approved recommendations are: " + "; ".join(details) + "."

    def _build_prompt(
        self,
        query_product: Mapping[str, Any],
        recommendations: Sequence[Mapping[str, Any]],
    ) -> str:
        payload = {
            "query_product": _compact_product(query_product),
            "fixed_recommendations": [_compact_product(item) for item in recommendations],
        }
        return (
            "Explain the fixed recommendations concisely. Do not add, remove, reorder, "
            "or choose recommendations. Use only this structured data:\n"
            + json.dumps(payload, ensure_ascii=False)
        )


class RecommendationOrchestrator:
    """Coordinate retrieval, policy checks, and explanation generation."""

    def __init__(
        self,
        retrieval_agent: RetrievalAgent | None = None,
        policy_agent: PolicyCheckAgent | None = None,
        explanation_agent: ExplanationAgent | None = None,
    ) -> None:
        self.retrieval_agent = retrieval_agent or RetrievalAgent()
        self.policy_agent = policy_agent or PolicyCheckAgent()
        self.explanation_agent = explanation_agent or ExplanationAgent()

    def run(
        self,
        products_path: str | Path,
        similarity_results_path: str | Path,
        method_name: str | None = None,
        top_k: int = 5,
        query_item_id: str | None = None,
    ) -> dict[str, Any]:
        retrieval = self.retrieval_agent.run(
            products_path,
            similarity_results_path,
            top_k=top_k,
            query_item_id=query_item_id,
        )
        policy = self.policy_agent.run(
            retrieval["query_product"], retrieval["candidates"]
        )
        explanation = self.explanation_agent.run(
            retrieval["query_product"], policy["approved_recommendations"]
        )
        return {
            "orchestrator_name": "abo_recommendation_orchestrator",
            "dataset_track": "amazon_berkeley_text_images-based",
            "method_name": method_name or retrieval["method_name"],
            "query_item_id": retrieval["query_item_id"],
            "query_product": retrieval["query_product"],
            "selected_recommendations": policy["approved_recommendations"],
            "rejected_recommendations": policy["rejected_recommendations"],
            "policy_checks_summary": policy["policy_checks_summary"],
            **explanation,
            "assumptions": [
                "Similarity recommendations are precomputed and fixed before explanation.",
                "MCP-style tools provide controlled local data access; this is not a production MCP server.",
                "ABO and RetailRocket identifiers remain separate.",
            ],
            "limitations": [
                "This is a lightweight local orchestration demo, not a production agent system.",
                "The explanation does not validate recommendation quality or user satisfaction.",
                "OpenAI explanation is optional and never selects recommendations.",
            ],
        }


def _compact_product(product: Mapping[str, Any]) -> dict[str, Any]:
    fields = (
        "item_id",
        "item_name",
        "brand",
        "product_type",
        "score",
        "product_type_matches_query",
    )
    return {field: product[field] for field in fields if product.get(field) is not None}
