"""Model policy controls for iterative curriculum optimization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ModelProvider(str, Enum):
    INTERNAL = "internal"


@dataclass(slots=True, frozen=True)
class ModelPolicy:
    provider: ModelProvider
    model_id: str
    temperature: float
    max_iterations: int
    max_actions_per_iteration: int
    target_score: int
    timeout_seconds: int
    retry_budget: int
    schema_version: str

    def snapshot(self) -> dict[str, str | int | float]:
        return {
            "provider": self.provider.value,
            "model": self.model_id,
            "temperature": self.temperature,
            "max_iterations": self.max_iterations,
            "max_actions_per_iteration": self.max_actions_per_iteration,
            "target_score": self.target_score,
            "timeout_seconds": self.timeout_seconds,
            "retry_budget": self.retry_budget,
            "schema_version": self.schema_version,
        }


def default_model_policy() -> ModelPolicy:
    return ModelPolicy(
        provider=ModelProvider.INTERNAL,
        model_id="internal-heuristic-v1",
        temperature=0.0,
        max_iterations=4,
        max_actions_per_iteration=4,
        target_score=82,
        timeout_seconds=30,
        retry_budget=1,
        schema_version="1.0",
    )
