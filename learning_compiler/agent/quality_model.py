"""Deterministic quality judge used as optimizer acceptance authority."""

from __future__ import annotations

from typing import Any

from learning_compiler.agent.quality_content_rules import (
    score_effort_coherence,
    score_learner_coherence,
    score_mastery_actionability,
    score_redundancy,
    score_resource_relevance,
)
from learning_compiler.agent.pedagogy_critic import PedagogyCritique
from learning_compiler.agent.quality_rules import (
    score_atomicity,
    score_progression,
    score_structural,
    weighted_total,
)
from learning_compiler.agent.quality_types import QualityDiagnostic, QualityReport
from learning_compiler.domain import TopicSpec


class DeterministicQualityJudge:
    """Deterministic quality acceptance gate for optimization loop."""

    def evaluate(
        self,
        curriculum: dict[str, Any],
        topic_spec: TopicSpec,
        pedagogy: PedagogyCritique,
    ) -> QualityReport:
        nodes_raw = curriculum.get("nodes", [])
        nodes = [item for item in nodes_raw if isinstance(item, dict)]
        diagnostics: list[QualityDiagnostic] = []

        dimensions = {
            "structural_validity": score_structural(nodes, diagnostics),
            "atomicity": score_atomicity(nodes, diagnostics),
            "pedagogical_progression": score_progression(nodes, diagnostics),
            "resource_relevance": score_resource_relevance(nodes, topic_spec, diagnostics),
            "mastery_actionability": score_mastery_actionability(nodes, diagnostics),
            "effort_coherence": score_effort_coherence(nodes, diagnostics),
            "redundancy": score_redundancy(nodes, diagnostics),
            "learner_path_coherence": score_learner_coherence(pedagogy, diagnostics),
        }

        hard_fail_count = len([item for item in diagnostics if item.hard_fail])
        return QualityReport(
            dimensions=dimensions,
            total_score=weighted_total(dimensions),
            hard_fail_count=hard_fail_count,
            diagnostics=tuple(diagnostics),
        )
