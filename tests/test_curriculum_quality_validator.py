from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from learning_compiler.validator.core import validate


ROOT = Path(__file__).resolve().parents[1]
CURRICULUM_FIXTURE = ROOT / "tests" / "fixtures" / "curriculum.json"


def _load_fixture() -> dict[str, object]:
    return json.loads(CURRICULUM_FIXTURE.read_text(encoding="utf-8"))


class CurriculumQualityValidatorTests(unittest.TestCase):
    def test_all_root_nodes_fail_progression_check(self) -> None:
        curriculum = _load_fixture()
        for node in curriculum["nodes"]:
            node["prerequisites"] = []

        with tempfile.TemporaryDirectory() as tmp_dir:
            curriculum_path = Path(tmp_dir) / "curriculum.json"
            curriculum_path.write_text(json.dumps(curriculum), encoding="utf-8")

            result = validate(curriculum_path)
            self.assertFalse(result.success)
            self.assertIn(
                "No learning progression: all nodes are roots",
                "\n".join(result.failed),
            )

    def test_too_few_core_ideas_fails_node_quality(self) -> None:
        curriculum = _load_fixture()
        curriculum["nodes"][0]["core_ideas"] = ["Only one"]

        with tempfile.TemporaryDirectory() as tmp_dir:
            curriculum_path = Path(tmp_dir) / "curriculum.json"
            curriculum_path.write_text(json.dumps(curriculum), encoding="utf-8")

            result = validate(curriculum_path)
            self.assertFalse(result.success)
            self.assertIn(
                "core_ideas should contain at least 2 items",
                "\n".join(result.failed),
            )

    def test_identical_estimates_emit_warning_not_failure(self) -> None:
        curriculum = _load_fixture()
        for node in curriculum["nodes"]:
            node["estimate_minutes"] = 90

        with tempfile.TemporaryDirectory() as tmp_dir:
            curriculum_path = Path(tmp_dir) / "curriculum.json"
            curriculum_path.write_text(json.dumps(curriculum), encoding="utf-8")

            result = validate(curriculum_path)
            self.assertTrue(result.success, msg="\n".join(result.failed))
            self.assertIn(
                "All nodes use the same estimate_minutes value",
                "\n".join(result.warnings),
            )

    def test_mastery_task_without_action_verb_fails(self) -> None:
        curriculum = _load_fixture()
        curriculum["nodes"][0]["mastery_check"]["task"] = "Understanding of concepts and quality."

        with tempfile.TemporaryDirectory() as tmp_dir:
            curriculum_path = Path(tmp_dir) / "curriculum.json"
            curriculum_path.write_text(json.dumps(curriculum), encoding="utf-8")

            result = validate(curriculum_path)
            self.assertFalse(result.success)
            self.assertIn(
                "mastery_check.task should contain a concrete action verb",
                "\n".join(result.failed),
            )


if __name__ == "__main__":
    unittest.main()
