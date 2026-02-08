"""LLM client contracts for proposer/critic/repair stages."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from learning_compiler.agent.model_policy import ModelPolicy


@dataclass(slots=True, frozen=True)
class LLMRequest:
    stage: str
    schema_name: str
    payload: dict[str, Any]


class LLMClient(Protocol):
    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, Any]:
        """Run one structured stage request and return a JSON mapping."""


class InternalLLMClient:
    """Deterministic placeholder client for internal heuristic mode."""

    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, Any]:
        return {
            "stage": request.stage,
            "schema_name": request.schema_name,
            "model": policy.model_id,
            "status": "ok",
        }
