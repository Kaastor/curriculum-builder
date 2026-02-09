"""Deterministic internal LLM client."""

from __future__ import annotations

from learning_compiler.agent.llm.types import LLMRequest
from learning_compiler.agent.model_policy import ModelPolicy


class InternalLLMClient:
    """Deterministic placeholder client for internal heuristic mode."""

    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, object]:
        return {
            "stage": request.stage,
            "schema_name": request.schema_name,
            "model": policy.model_id,
            "status": "ok",
        }
