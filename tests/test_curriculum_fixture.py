import json
import tempfile
import unittest
from pathlib import Path

from scripts.validator import validate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CURRICULUM = ROOT / "data" / "curriculum.json"
MOCK_CURRICULUM = ROOT / "data" / "reliability" / "curriculum.mock.json"


class CurriculumFixtureTests(unittest.TestCase):
    def _base_topic_spec(self) -> dict:
        return {
            "spec_version": "1.0",
            "topic_id": "tool_use_correctness",
            "topic_name": "Tool Use Correctness",
            "domain_ref": "field.md § I.1",
            "target_role": "backend_developer",
            "language": "python",
            "project_type": "library",
            "scenario": "flight_booking_agent",
            "transfer_scenario": "hotel_booking_agent",
            "prerequisites": ["python functions", "basic CLI"],
            "outcome": "Build deterministic tool runtime reliability guardrails.",
            "exercise_categories": [
                {
                    "key": "foundation",
                    "prefix": "F",
                    "description": "Foundational concepts",
                    "supports_exercise_types": ["write"],
                    "is_capstone": False,
                },
                {
                    "key": "selection",
                    "prefix": "S",
                    "description": "Selection behavior",
                    "supports_exercise_types": ["write"],
                    "is_capstone": False,
                },
                {
                    "key": "ordering",
                    "prefix": "O",
                    "description": "Ordering behavior",
                    "supports_exercise_types": ["write"],
                    "is_capstone": False,
                },
                {
                    "key": "arguments",
                    "prefix": "A",
                    "description": "Argument behavior",
                    "supports_exercise_types": ["write"],
                    "is_capstone": False,
                },
                {
                    "key": "output",
                    "prefix": "R",
                    "description": "Output behavior",
                    "supports_exercise_types": ["write"],
                    "is_capstone": False,
                },
                {
                    "key": "hallucination",
                    "prefix": "H",
                    "description": "Hallucination behavior",
                    "supports_exercise_types": ["write"],
                    "is_capstone": False,
                },
                {
                    "key": "avoidance",
                    "prefix": "V",
                    "description": "Avoidance behavior",
                    "supports_exercise_types": ["write"],
                    "is_capstone": False,
                },
                {
                    "key": "debug",
                    "prefix": "D",
                    "description": "Debug and read behavior",
                    "supports_exercise_types": ["debug", "read"],
                    "is_capstone": False,
                },
                {
                    "key": "capstone",
                    "prefix": "C",
                    "description": "Integration",
                    "supports_exercise_types": ["integrate"],
                    "is_capstone": True,
                },
            ],
            "failure_modes": [
                {
                    "key": "choosing_wrong_tool",
                    "label": "Choosing wrong tool",
                    "description": "Wrong tool selected for a valid intent",
                    "production_impact": "Incorrect behavior",
                    "example": "Uses payment tool instead of reservation tool",
                    "must_cover_in_capstone": True,
                },
                {
                    "key": "wrong_call_order",
                    "label": "Wrong call order",
                    "description": "Calls are sequenced incorrectly",
                    "production_impact": "Invalid state transitions",
                    "example": "Payment before reservation",
                    "must_cover_in_capstone": True,
                },
                {
                    "key": "malformed_arguments",
                    "label": "Malformed arguments",
                    "description": "Arguments are malformed",
                    "production_impact": "Runtime faults",
                    "example": "Missing required reservation_id",
                    "must_cover_in_capstone": True,
                },
                {
                    "key": "output_misinterpretation",
                    "label": "Output misinterpretation",
                    "description": "Output semantics are misread",
                    "production_impact": "Errors treated as success",
                    "example": "Ignores ok=false",
                    "must_cover_in_capstone": True,
                },
                {
                    "key": "tool_hallucination",
                    "label": "Tool hallucination",
                    "description": "Unknown tools are invented",
                    "production_impact": "Unsafe nondeterminism",
                    "example": "Calls non-existent tool",
                    "must_cover_in_capstone": True,
                },
                {
                    "key": "tool_avoidance",
                    "label": "Tool avoidance",
                    "description": "Manual path bypasses tools",
                    "production_impact": "Audit gaps",
                    "example": "Direct state mutation",
                    "must_cover_in_capstone": True,
                },
            ],
            "design_patterns": [],
            "assessment": {
                "mastery_threshold": "Capstone blocks required failure modes.",
                "transfer_task_required": False,
                "capstone_required_failure_modes": ["wrong_call_order"],
                "max_uncaught_failure_modes": 1,
            },
            "constraints": {
                "max_layers": 5,
                "node_count_min": 18,
                "node_count_max": 25,
                "max_prerequisites_per_node": 3,
                "exercise_time_min_minutes": 30,
                "exercise_time_max_minutes": 90,
                "debug_read_min": 2,
                "debug_read_max": 3,
                "capstone_exactly": 1,
                "capstone_layer": 4,
                "allow_external_services": False,
                "target_total_hours_min": 12,
                "target_total_hours_max": 24,
            },
            "repo_preferences": {
                "repo_name": "tool-use-learning",
                "package_name": "tool_use_learning",
                "use_makefile": True,
            },
        }

    def test_default_curriculum_passes_validator(self):
        result = validate(DEFAULT_CURRICULUM)
        self.assertTrue(
            result.success,
            msg="Default curriculum failed validator:\n" + "\n".join(result.failed),
        )

    def test_mock_curriculum_matches_default(self):
        default_data = json.loads(DEFAULT_CURRICULUM.read_text())
        mock_data = json.loads(MOCK_CURRICULUM.read_text())

        self.assertEqual(default_data["nodes"], mock_data["nodes"])
        self.assertEqual(default_data["edges"], mock_data["edges"])
        self.assertEqual(default_data["coverage_map"], mock_data["coverage_map"])
        self.assertEqual(
            default_data["pattern_coverage_map"], mock_data["pattern_coverage_map"]
        )

    def test_pattern_coverage_map_required_when_topic_spec_declares_patterns(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            topic_spec_path = Path(tmp_dir) / "topic_spec.json"
            curriculum_path = Path(tmp_dir) / "curriculum.json"
            curriculum = json.loads(DEFAULT_CURRICULUM.read_text())
            curriculum.pop("pattern_coverage_map", None)
            curriculum_path.write_text(json.dumps(curriculum), encoding="utf-8")

            topic_spec = self._base_topic_spec()
            topic_spec["design_patterns"] = [
                {
                    "key": "boundary_validation",
                    "name": "Boundary Validation",
                    "problem": "Inputs must be validated at system boundaries.",
                    "minimum_coverage": 1,
                }
            ]
            topic_spec_path.write_text(json.dumps(topic_spec), encoding="utf-8")

            result = validate(curriculum_path, topic_spec_path)
            self.assertFalse(result.success)
            self.assertIn("pattern_coverage_map missing", "\n".join(result.failed))

    def test_defaultable_topic_spec_fields_can_be_omitted(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            topic_spec_path = Path(tmp_dir) / "topic_spec.json"
            curriculum_path = Path(tmp_dir) / "curriculum.json"

            curriculum = json.loads(DEFAULT_CURRICULUM.read_text())
            if "transfer" not in curriculum["nodes"][0].get("tags", []):
                curriculum["nodes"][0]["tags"].append("transfer")
            curriculum_path.write_text(json.dumps(curriculum), encoding="utf-8")

            topic_spec = self._base_topic_spec()

            topic_spec.pop("spec_version", None)
            topic_spec.pop("constraints", None)
            topic_spec.pop("repo_preferences", None)
            topic_spec["assessment"].pop("transfer_task_required", None)
            topic_spec["assessment"].pop("max_uncaught_failure_modes", None)

            topic_spec_path.write_text(json.dumps(topic_spec), encoding="utf-8")

            result = validate(curriculum_path, topic_spec_path)
            self.assertTrue(
                result.success,
                msg="Defaultable omitted fields should still validate:\n" + "\n".join(result.failed),
            )

    def test_invalid_topic_spec_fails_fast(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            topic_spec_path = Path(tmp_dir) / "topic_spec.json"
            invalid_spec = {"spec_version": "1.0", "topic_id": "only_topic_id"}
            topic_spec_path.write_text(json.dumps(invalid_spec), encoding="utf-8")

            result = validate(DEFAULT_CURRICULUM, topic_spec_path)
            self.assertFalse(result.success)
            self.assertIn("topic_spec contract error", "\n".join(result.failed))

    def test_app_assets_exist(self):
        app_dir = ROOT / "app"
        expected = ["index.html", "styles.css", "main.js"]
        for name in expected:
            self.assertTrue((app_dir / name).exists(), msg=f"Missing app asset: {name}")


if __name__ == "__main__":
    unittest.main()
