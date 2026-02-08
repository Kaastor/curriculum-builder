"""Model policy controls for iterative curriculum optimization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os

from learning_compiler.config import load_config


class ModelProvider(str, Enum):
    INTERNAL = "internal"
    REMOTE_LLM = "remote_llm"
    CODEX_EXEC = "codex_exec"


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


def _env_int(raw: str, default: int) -> int:
    try:
        parsed = int(raw)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _parse_provider(raw: str) -> ModelProvider:
    value = raw.strip().lower()
    if value == ModelProvider.REMOTE_LLM.value:
        return ModelProvider.REMOTE_LLM
    if value in {ModelProvider.CODEX_EXEC.value, "coding_agent"}:
        return ModelProvider.CODEX_EXEC
    return ModelProvider.INTERNAL


def default_model_policy() -> ModelPolicy:
    config = load_config()
    provider = _parse_provider(config.agent_provider)
    configured_model = config.agent_model.strip()
    if configured_model:
        model_id = configured_model
    elif provider == ModelProvider.REMOTE_LLM:
        model_id = "gpt-4.1-mini"
    elif provider == ModelProvider.CODEX_EXEC:
        model_id = "codex"
    else:
        model_id = "internal-heuristic-v1"

    return ModelPolicy(
        provider=provider,
        model_id=model_id,
        temperature=0.0,
        max_iterations=_env_int(os.environ.get("AGENT_MAX_ITERATIONS", "4"), 4),
        max_actions_per_iteration=_env_int(
            os.environ.get("AGENT_MAX_ACTIONS_PER_ITERATION", "4"), 4
        ),
        target_score=_env_int(os.environ.get("AGENT_TARGET_SCORE", "82"), 82),
        timeout_seconds=_env_int(os.environ.get("AGENT_TIMEOUT_SECONDS", "30"), 30),
        retry_budget=_env_int(os.environ.get("AGENT_RETRY_BUDGET", "1"), 1),
        schema_version="1.0",
    )
