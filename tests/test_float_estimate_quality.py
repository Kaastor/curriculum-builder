from __future__ import annotations

import unittest

from learning_compiler.agent.model_policy import default_model_policy
from learning_compiler.agent.quality.pedagogy_critic import LLMCritic
from learning_compiler.agent.quality.quality_content_rules import score_effort_coherence
from learning_compiler.agent.quality.quality_types import QualityDiagnostic
from learning_compiler.domain import parse_topic_spec


def _topic_spec() -> dict[str, object]:
    return {
        "spec_version": "1.0",
        "goal": "Evaluate estimate handling",
        "audience": "Engineers",
        "prerequisites": ["python"],
        "scope_in": ["validation", "planning"],
        "scope_out": [],
        "constraints": {
            "hours_per_week": 6.0,
            "total_hours_min": 8.0,
            "total_hours_max": 40.0,
            "depth": "practical",
            "node_count_min": 2,
            "node_count_max": 8,
            "max_prerequisites_per_node": 3,
        },
        "domain_mode": "mature",
        "evidence_mode": "minimal",
    }


class FloatEstimateQualityTests(unittest.TestCase):
    def test_effort_coherence_accepts_float_estimates(self) -> None:
        diagnostics: list[QualityDiagnostic] = []
        nodes = [
            {"id": "N1", "estimate_minutes": 20.5},
            {"id": "N2", "estimate_minutes": 21.0},
            {"id": "N3", "estimate_minutes": 24.25},
        ]

        score = score_effort_coherence(nodes, diagnostics)
        self.assertEqual(100, score)
        self.assertEqual([], diagnostics)

    def test_pedagogy_workload_jump_detects_with_float_estimates(self) -> None:
        critic = LLMCritic()
        topic_spec = parse_topic_spec(_topic_spec())
        curriculum = {
            "topic": "Float estimates",
            "nodes": [
                {
                    "id": "N1",
                    "title": "Foundations",
                    "capability": "Build core understanding",
                    "prerequisites": [],
                    "estimate_minutes": 10.5,
                },
                {
                    "id": "N2",
                    "title": "Integration",
                    "capability": "Integrate systems in one project",
                    "prerequisites": ["N1"],
                    "estimate_minutes": 30.0,
                },
            ],
        }

        critique = critic.critique(curriculum, topic_spec, default_model_policy())
        self.assertTrue(any(item.rule_id == "learner.workload_jump" for item in critique.diagnostics))


if __name__ == "__main__":
    unittest.main()
