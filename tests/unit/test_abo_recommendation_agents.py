import json
from pathlib import Path
from types import SimpleNamespace

from ecommerce_recommender.agents.abo_recommendation_agents import (
    ExplanationAgent,
    PolicyCheckAgent,
    RecommendationOrchestrator,
    RetrievalAgent,
)


def _write_fixtures(tmp_path: Path) -> tuple[Path, Path]:
    products_path = tmp_path / "products.jsonl"
    products = [
        {"item_id": "query", "item_name": "White Plate", "brand": "Home", "product_type": "PLATE"},
        {"item_id": "good", "item_name": "Dinner Plate", "brand": "Home", "product_type": "PLATE"},
        {"item_id": "other", "item_name": "Coffee Mug", "brand": "Home", "product_type": "MUG"},
    ]
    products_path.write_text(
        "\n".join(json.dumps(product) for product in products) + "\n",
        encoding="utf-8",
    )
    results_path = tmp_path / "results.json"
    results_path.write_text(
        json.dumps(
            {
                "method_name": "clip_multimodal_similarity",
                "query_item_id": "query",
                "recommendations": [
                    {"item_id": "good", "score": 0.9},
                    {"item_id": "query", "score": 1.0},
                    {"item_id": "other", "score": 0.7},
                ],
            }
        ),
        encoding="utf-8",
    )
    return products_path, results_path


def test_retrieval_agent_returns_query_and_candidates(tmp_path: Path) -> None:
    products_path, results_path = _write_fixtures(tmp_path)

    result = RetrievalAgent().run(products_path, results_path, top_k=2)

    assert result["query_item_id"] == "query"
    assert result["query_product"]["item_name"] == "White Plate"
    assert [candidate["item_id"] for candidate in result["candidates"]] == ["good", "query"]
    assert result["candidates"][0]["item_name"] == "Dinner Plate"


def test_policy_agent_separates_approved_and_rejected() -> None:
    query = {"item_id": "query", "product_type": "PLATE"}
    candidates = [
        {"item_id": "good", "item_name": "Plate", "product_type": "PLATE", "score": 0.9},
        {"item_id": "query", "item_name": "Plate", "product_type": "PLATE", "score": 1.0},
    ]

    result = PolicyCheckAgent().run(query, candidates)

    assert [item["item_id"] for item in result["approved_recommendations"]] == ["good"]
    assert [item["item_id"] for item in result["rejected_recommendations"]] == ["query"]
    assert result["policy_checks_summary"] == {
        "candidates_checked": 2,
        "approved_count": 1,
        "rejected_count": 1,
        "warning_count": 0,
    }


def test_explanation_agent_deterministic_fallback_without_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    agent = ExplanationAgent(use_openai=True)

    result = agent.run(
        {"item_id": "query", "item_name": "White Plate"},
        [{"item_id": "good", "item_name": "Dinner Plate", "product_type_matches_query": True}],
    )

    assert result["explanation_mode"] == "deterministic"
    assert "Dinner Plate" in result["explanation"]


def test_openai_explanation_path_uses_mock_client(monkeypatch) -> None:
    calls = []

    class Responses:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(output_text="Mocked concise explanation.")

    fake_client = SimpleNamespace(responses=Responses())
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-key")
    agent = ExplanationAgent(
        use_openai=True,
        model="test-model",
        client_factory=lambda api_key: fake_client,
    )

    result = agent.run(
        {"item_id": "query", "item_name": "White Plate"},
        [{"item_id": "good", "item_name": "Dinner Plate", "score": 0.9}],
    )

    assert result == {
        "explanation": "Mocked concise explanation.",
        "explanation_mode": "openai_llm",
    }
    assert calls[0]["model"] == "test-model"
    assert "Dinner Plate" in calls[0]["input"]


def test_orchestrator_returns_structured_response(tmp_path: Path) -> None:
    products_path, results_path = _write_fixtures(tmp_path)
    orchestrator = RecommendationOrchestrator(
        explanation_agent=ExplanationAgent(use_openai=False)
    )

    result = orchestrator.run(products_path, results_path, method_name="clip", top_k=3)

    assert result["orchestrator_name"] == "abo_recommendation_orchestrator"
    assert result["dataset_track"] == "amazon_berkeley_text_images-based"
    assert result["method_name"] == "clip"
    assert result["query_item_id"] == "query"
    assert [item["item_id"] for item in result["selected_recommendations"]] == ["good", "other"]
    assert [item["item_id"] for item in result["rejected_recommendations"]] == ["query"]
    assert result["explanation_mode"] == "deterministic"
    assert result["assumptions"]
    assert result["limitations"]


def test_empty_and_invalid_recommendations_are_handled(tmp_path: Path) -> None:
    products_path, results_path = _write_fixtures(tmp_path)
    results_path.write_text(
        json.dumps(
            {
                "query_item_id": "query",
                "recommendations": [
                    {},
                    {"item_id": "missing", "score": 0.5},
                ],
            }
        ),
        encoding="utf-8",
    )

    result = RecommendationOrchestrator().run(products_path, results_path, top_k=5)

    assert result["selected_recommendations"] == []
    assert len(result["rejected_recommendations"]) == 2
    assert result["policy_checks_summary"]["rejected_count"] == 2
    assert result["explanation_mode"] == "deterministic"
