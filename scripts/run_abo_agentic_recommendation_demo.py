"""Run the lightweight MCP-style ABO recommendation orchestration demo."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
for import_root in (PROJECT_ROOT, SRC_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from ecommerce_recommender.agents.abo_recommendation_agents import (  # noqa: E402
    ExplanationAgent,
    RecommendationOrchestrator,
)

LOGGER = logging.getLogger(__name__)
DEFAULT_PRODUCTS = PROJECT_ROOT / "data/processed/abo_clean_products_5k.jsonl"
DEFAULT_RESULTS = PROJECT_ROOT / "data/processed/abo_clip_similarity_5k_sample.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/processed/abo_agentic_recommendation_demo.json"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--products", type=Path, default=DEFAULT_PRODUCTS)
    parser.add_argument("--similarity-results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--method-name", default="clip")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--query-item-id", default=None)
    parser.add_argument("--use-openai-explanation", action="store_true")
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    _load_optional_openai_env(PROJECT_ROOT / ".env")

    orchestrator = RecommendationOrchestrator(
        explanation_agent=ExplanationAgent(use_openai=args.use_openai_explanation)
    )
    output = orchestrator.run(
        args.products,
        args.similarity_results,
        method_name=args.method_name,
        top_k=args.top_k,
        query_item_id=args.query_item_id,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    LOGGER.info(
        "ABO agentic demo selected %d recommendations; explanation mode=%s",
        len(output["selected_recommendations"]),
        output["explanation_mode"],
    )
    LOGGER.info("Wrote ABO agentic recommendation demo to %s", args.output)


def _load_optional_openai_env(path: Path) -> None:
    """Load only optional OpenAI settings from a local .env without logging values."""
    if not path.is_file():
        return
    allowed = {"OPENAI_API_KEY", "OPENAI_MODEL"}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        name = name.strip()
        if name in allowed and name not in os.environ:
            os.environ[name] = value.strip().strip("\"'")


if __name__ == "__main__":
    main()
