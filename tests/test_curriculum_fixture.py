import json
import tempfile
import unittest
from pathlib import Path

from learning_compiler.validator.core import validate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CURRICULUM = ROOT / "data" / "curriculum.json"


class CurriculumFixtureTests(unittest.TestCase):
    def _base_topic_spec(self) -> dict:
        return {
            "spec_version": "1.0",
            "goal": "Use Bayesian reasoning to make product decisions under uncertainty.",
            "audience": "Data-savvy product engineers",
            "prerequisites": ["basic probability", "spreadsheet literacy"],
            "scope_in": ["posterior reasoning", "decision framing", "uncertainty communication"],
            "scope_out": ["advanced measure theory", "MCMC internals"],
            "constraints": {
                "hours_per_week": 6,
                "total_hours_min": 12,
                "total_hours_max": 24,
                "depth": "practical",
                "node_count_min": 6,
                "node_count_max": 20,
                "max_prerequisites_per_node": 3,
            },
            "domain_mode": "mature",
            "evidence_mode": "standard",
            "misconceptions": [
                "A high average is enough without uncertainty context.",
                "Bayes rule is only for academics.",
            ],
        }

    def test_default_curriculum_passes_validator_without_topic_spec(self):
        result = validate(DEFAULT_CURRICULUM)
        self.assertTrue(result.success, msg="\n".join(result.failed))

    def test_default_curriculum_passes_with_standard_topic_spec(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            topic_spec_path = Path(tmp_dir) / "topic_spec.json"
            topic_spec_path.write_text(json.dumps(self._base_topic_spec()), encoding="utf-8")

            result = validate(DEFAULT_CURRICULUM, topic_spec_path)
            self.assertTrue(result.success, msg="\n".join(result.failed))

    def test_strict_mode_requires_citations_confidence_and_open_questions(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            topic_spec_path = Path(tmp_dir) / "topic_spec.json"
            strict_spec = self._base_topic_spec()
            strict_spec["evidence_mode"] = "strict"
            topic_spec_path.write_text(json.dumps(strict_spec), encoding="utf-8")

            result = validate(DEFAULT_CURRICULUM, topic_spec_path)
            self.assertFalse(result.success)
            failures = "\n".join(result.failed)
            self.assertIn("missing citation in strict mode", failures)
            self.assertIn("strict evidence requires estimate_confidence", failures)
            self.assertIn("strict mode requires top-level open_questions list", failures)

    def test_strict_mode_can_pass_with_required_fields(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            topic_spec_path = Path(tmp_dir) / "topic_spec.json"
            curriculum_path = Path(tmp_dir) / "curriculum.json"

            strict_spec = self._base_topic_spec()
            strict_spec["domain_mode"] = "frontier"
            strict_spec["evidence_mode"] = "strict"
            topic_spec_path.write_text(json.dumps(strict_spec), encoding="utf-8")

            curriculum = json.loads(DEFAULT_CURRICULUM.read_text(encoding="utf-8"))
            for node in curriculum["nodes"]:
                node["estimate_confidence"] = 0.75
                for resource in node["resources"]:
                    resource["citation"] = "Source section 1.2"
            curriculum["open_questions"] = [
                {
                    "question": "How stable is posterior choice under sparse event data?",
                    "related_nodes": ["N4", "N8"],
                    "status": "open",
                }
            ]
            curriculum_path.write_text(json.dumps(curriculum), encoding="utf-8")

            result = validate(curriculum_path, topic_spec_path)
            self.assertTrue(result.success, msg="\n".join(result.failed))

    def test_invalid_topic_spec_fails_fast(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            topic_spec_path = Path(tmp_dir) / "topic_spec.json"
            topic_spec_path.write_text(json.dumps({"goal": "only goal"}), encoding="utf-8")

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
