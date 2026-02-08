from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from learning_compiler.validator.core import validate


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


class ValidatorRobustnessTests(unittest.TestCase):
    def test_malformed_prerequisites_do_not_crash_validator(self) -> None:
        curriculum = """
{
  "topic": "Robustness",
  "nodes": [
    {
      "id": "N1",
      "title": "Node one",
      "capability": "Implement baseline behavior",
      "prerequisites": 1,
      "core_ideas": ["a", "b"],
      "pitfalls": ["c"],
      "mastery_check": {
        "task": "implement a realistic baseline artifact for the task",
        "pass_criteria": "must include explicit threshold and pass criteria"
      },
      "estimate_minutes": 30,
      "resources": [{"title": "Ref", "url": "https://example.com", "kind": "doc"}]
    }
  ]
}
"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = _write(Path(tmp_dir) / "curriculum.json", curriculum)
            result = validate(path)

        self.assertFalse(result.success)
        self.assertTrue(any("prerequisites must be a list" in message for message in result.failed))

    def test_non_finite_estimates_are_rejected(self) -> None:
        for token in ("NaN", "Infinity"):
            with self.subTest(token=token):
                curriculum = f"""
{{
  "topic": "Robustness",
  "nodes": [
    {{
      "id": "N1",
      "title": "Node one",
      "capability": "Implement baseline behavior",
      "prerequisites": [],
      "core_ideas": ["a", "b"],
      "pitfalls": ["c"],
      "mastery_check": {{
        "task": "implement a realistic baseline artifact for the task",
        "pass_criteria": "must include explicit threshold and pass criteria"
      }},
      "estimate_minutes": {token},
      "resources": [{{"title": "Ref", "url": "https://example.com", "kind": "doc"}}]
    }}
  ]
}}
"""
                with tempfile.TemporaryDirectory() as tmp_dir:
                    path = _write(Path(tmp_dir) / "curriculum.json", curriculum)
                    result = validate(path)

                self.assertFalse(result.success)
                self.assertTrue(
                    any("estimate_minutes must be a number" in message for message in result.failed)
                )


if __name__ == "__main__":
    unittest.main()
