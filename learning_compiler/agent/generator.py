"""Agent-owned curriculum generation from topic spec."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from learning_compiler.agent.node_builder import build_node
from learning_compiler.agent.research import DeterministicResourceResolver, ResourceResolver
from learning_compiler.agent.spec import GenerationSpec, build_generation_spec
from learning_compiler.domain import Curriculum, OpenQuestion
from learning_compiler.errors import ErrorCode, LearningCompilerError


def _build_curriculum(spec: GenerationSpec, resolver: ResourceResolver) -> Curriculum:
    nodes = tuple(build_node(index, spec, resolver) for index in range(spec.target_nodes))

    open_questions: tuple[OpenQuestion, ...] = ()
    if spec.strict_mode:
        tail = (f"N{max(1, spec.target_nodes - 1)}", f"N{spec.target_nodes}")
        open_questions = (
            OpenQuestion(
                question=(
                    "Which claims remain weakly evidenced or contradictory for "
                    "this topic under current references?"
                ),
                related_nodes=tail,
                status="open",
            ),
        )

    return Curriculum(topic=spec.topic_label, nodes=nodes, open_questions=open_questions)


def generate_curriculum(
    topic_spec: dict[str, Any],
    resolver: ResourceResolver | None = None,
) -> dict[str, Any]:
    """Generate curriculum from topic spec using the provided resource resolver."""
    spec = build_generation_spec(topic_spec)
    active_resolver = resolver or DeterministicResourceResolver()
    curriculum = _build_curriculum(spec, active_resolver)
    return curriculum.to_dict()


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

    curriculum = generate_curriculum(topic_spec, resolver=resolver)
    curriculum_path.parent.mkdir(parents=True, exist_ok=True)
    curriculum_path.write_text(json.dumps(curriculum, indent=2) + "\n", encoding="utf-8")
    return curriculum
