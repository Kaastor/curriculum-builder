from __future__ import annotations

import unittest

from learning_compiler.orchestration.planning import build_plan, compute_diff


def _topic_spec() -> dict[str, object]:
    return {
        "spec_version": "1.0",
        "goal": "Planning precision regression check",
        "audience": "Engineers",
        "prerequisites": ["python"],
        "scope_in": ["planning"],
        "scope_out": [],
        "constraints": {
            "hours_per_week": 6.0,
            "total_hours_min": 1.0,
            "total_hours_max": 20.0,
            "depth": "practical",
            "node_count_min": 2,
            "node_count_max": 10,
            "max_prerequisites_per_node": 3,
        },
        "domain_mode": "mature",
        "evidence_mode": "minimal",
    }


class PlanningPrecisionTests(unittest.TestCase):
    def test_build_plan_preserves_fractional_estimates(self) -> None:
        curriculum = {
            "topic": "Precision",
            "nodes": [
                {
                    "id": "N1",
                    "title": "A",
                    "capability": "Do A",
                    "prerequisites": [],
                    "core_ideas": ["a", "b"],
                    "pitfalls": ["c"],
                    "mastery_check": {"task": "Do A", "pass_criteria": "Pass A"},
                    "estimate_minutes": 22.5,
                    "resources": [],
                },
                {
                    "id": "N2",
                    "title": "B",
                    "capability": "Do B",
                    "prerequisites": ["N1"],
                    "core_ideas": ["a", "b"],
                    "pitfalls": ["c"],
                    "mastery_check": {"task": "Do B", "pass_criteria": "Pass B"},
                    "estimate_minutes": 47.5,
                    "resources": [],
                },
            ],
        }

        plan = build_plan(_topic_spec(), curriculum)
        self.assertEqual(70.0, plan["total_estimated_minutes"])

    def test_compute_diff_preserves_fractional_time_delta(self) -> None:
        previous = {
            "topic": "Precision",
            "nodes": [
                {
                    "id": "N1",
                    "title": "A",
                    "capability": "Do A",
                    "prerequisites": [],
                    "core_ideas": ["a", "b"],
                    "pitfalls": ["c"],
                    "mastery_check": {"task": "Do A", "pass_criteria": "Pass A"},
                    "estimate_minutes": 20.25,
                    "resources": [],
                }
            ],
        }
        current = {
            "topic": "Precision",
            "nodes": [
                {
                    "id": "N1",
                    "title": "A",
                    "capability": "Do A",
                    "prerequisites": [],
                    "core_ideas": ["a", "b"],
                    "pitfalls": ["c"],
                    "mastery_check": {"task": "Do A", "pass_criteria": "Pass A"},
                    "estimate_minutes": 21.75,
                    "resources": [],
                }
            ],
        }

        diff = compute_diff(previous, current)
        self.assertEqual(1.5, diff["time_delta_minutes"])


if __name__ == "__main__":
    unittest.main()

