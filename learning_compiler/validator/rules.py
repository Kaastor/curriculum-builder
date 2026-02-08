"""Rule registry for deterministic curriculum validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from typing import Any

from learning_compiler.validator.curriculum_evidence import check_evidence, check_open_questions
from learning_compiler.validator.curriculum_graph import (
    check_no_cycles,
    check_node_count,
    check_prerequisite_integrity,
    check_reachability,
    check_total_hours,
)
from learning_compiler.validator.curriculum_quality import (
    check_graph_progression,
    check_learner_path_coherence,
    check_node_quality,
    check_repetition,
    check_resource_relevance,
    check_time_granularity,
)
from learning_compiler.validator.curriculum_schema import (
    check_node_schema,
    check_top_level_structure,
    check_unique_ids_and_titles,
)
from learning_compiler.validator.types import ValidationConfig, ValidationResult


@dataclass(slots=True, frozen=True)
class ValidationContext:
    data: dict[str, Any]
    nodes: list[Any]
    config: ValidationConfig
    topic_spec: dict[str, Any] | None


@dataclass(slots=True, frozen=True)
class ValidationRule:
    rule_id: str
    run: Callable[[ValidationContext, ValidationResult], None]
    enabled: bool = True


RULES: tuple[ValidationRule, ...] = (
    ValidationRule("schema.top_level", lambda ctx, res: check_top_level_structure(ctx.data, res)),
    ValidationRule("schema.node_shape", lambda ctx, res: check_node_schema(ctx.nodes, res)),
    ValidationRule("schema.unique_ids_titles", lambda ctx, res: check_unique_ids_and_titles(ctx.nodes, res)),
    ValidationRule(
        "graph.prerequisite_integrity",
        lambda ctx, res: check_prerequisite_integrity(ctx.nodes, res, ctx.config),
    ),
    ValidationRule("graph.no_cycles", lambda ctx, res: check_no_cycles(ctx.nodes, res)),
    ValidationRule("graph.reachability", lambda ctx, res: check_reachability(ctx.nodes, res)),
    ValidationRule("graph.progression", lambda ctx, res: check_graph_progression(ctx.nodes, res)),
    ValidationRule("graph.node_count", lambda ctx, res: check_node_count(ctx.nodes, res, ctx.config)),
    ValidationRule("graph.total_hours", lambda ctx, res: check_total_hours(ctx.nodes, res, ctx.config)),
    ValidationRule("quality.node_quality", lambda ctx, res: check_node_quality(ctx.nodes, res)),
    ValidationRule("quality.repetition", lambda ctx, res: check_repetition(ctx.nodes, res)),
    ValidationRule("quality.time_granularity", lambda ctx, res: check_time_granularity(ctx.nodes, res)),
    ValidationRule(
        "quality.learner_path_coherence",
        lambda ctx, res: check_learner_path_coherence(ctx.nodes, res),
    ),
    ValidationRule("evidence.mode_rules", lambda ctx, res: check_evidence(ctx.nodes, res, ctx.config)),
    ValidationRule(
        "quality.resource_relevance",
        lambda ctx, res: check_resource_relevance(ctx.nodes, ctx.topic_spec, res),
    ),
    ValidationRule(
        "evidence.open_questions",
        lambda ctx, res: check_open_questions(ctx.data, ctx.nodes, res, ctx.config),
    ),
)
