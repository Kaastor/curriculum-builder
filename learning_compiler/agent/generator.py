"""Agent-owned curriculum generation from topic spec."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from learning_compiler.agent.llm_client import build_llm_client
from learning_compiler.agent.model_policy import ModelPolicy, default_model_policy
from learning_compiler.agent.optimizer import LoopController
from learning_compiler.agent.pedagogy_critic import LLMCritic
from learning_compiler.agent.proposer import LLMProposer
from learning_compiler.agent.quality_model import DeterministicQualityJudge
from learning_compiler.agent.repair_executor import LLMRepairExecutor
from learning_compiler.agent.repair_planner import RepairPlanner
from learning_compiler.agent.research import ResourceResolver, default_resource_resolver
from learning_compiler.agent.spec import build_generation_spec
from learning_compiler.agent.trace import OptimizationTrace
from learning_compiler.errors import ErrorCode, LearningCompilerError


def _controller(policy: ModelPolicy) -> LoopController:
    client = build_llm_client(policy)
    return LoopController(
        proposer=LLMProposer(client=client),
        critic=LLMCritic(),
        judge=DeterministicQualityJudge(),
        planner=RepairPlanner(max_actions_per_iteration=policy.max_actions_per_iteration),
        repair=LLMRepairExecutor(client=client),
    )


def _optimize_curriculum(
    topic_spec: dict[str, Any],
    resolver: ResourceResolver | None = None,
) -> tuple[dict[str, Any], OptimizationTrace]:
    spec = build_generation_spec(topic_spec)
    active_resolver = resolver or default_resource_resolver(spec.topic_spec)
    policy = default_model_policy()
    result = _controller(policy).optimize(spec, active_resolver, policy)
    return result.curriculum, result.trace


def generate_curriculum(
    topic_spec: dict[str, Any],
    resolver: ResourceResolver | None = None,
) -> dict[str, Any]:
    """Generate curriculum from topic spec using the provided resource resolver."""
    curriculum, _ = _optimize_curriculum(topic_spec, resolver=resolver)
    return curriculum


def _trace_path(curriculum_path: Path) -> Path | None:
    if curriculum_path.parent.name != "curriculum":
        return None
    outputs_dir = curriculum_path.parent.parent
    if outputs_dir.name != "outputs":
        return None
    return outputs_dir / "reviews" / "optimization_trace.json"


def generate_curriculum_file(
    topic_spec_path: Path,
    curriculum_path: Path,
    resolver: ResourceResolver | None = None,
) -> dict[str, Any]:
    topic_spec = json.loads(topic_spec_path.read_text(encoding="utf-8"))
    if not isinstance(topic_spec, dict):
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"topic_spec must be an object: {topic_spec_path}",
            {"path": str(topic_spec_path)},
        )

    curriculum, trace = _optimize_curriculum(topic_spec, resolver=resolver)
    curriculum_path.parent.mkdir(parents=True, exist_ok=True)
    curriculum_path.write_text(json.dumps(curriculum, indent=2) + "\n", encoding="utf-8")

    trace_path = _trace_path(curriculum_path)
    if trace_path is not None:
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        trace_path.write_text(
            json.dumps(trace.to_dict(), indent=2) + "\n",
            encoding="utf-8",
        )
    return curriculum
