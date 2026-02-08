from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from learning_compiler.agent.generator import generate_curriculum, generate_curriculum_file


def topic_spec() -> dict[str, object]:
    return {
        "spec_version": "1.0",
        "goal": "Develop a robust incident response checklist for ML systems.",
        "audience": "ML platform engineers",
        "prerequisites": ["python", "service operations"],
        "scope_in": ["monitoring", "rollback", "postmortems"],
        "scope_out": ["hardware-level debugging"],
        "constraints": {
            "hours_per_week": 5,
            "total_hours_min": 10,
            "total_hours_max": 18,
            "depth": "practical",
            "node_count_min": 6,
            "node_count_max": 8,
            "max_prerequisites_per_node": 3,
        },
        "domain_mode": "mature",
        "evidence_mode": "standard",
        "misconceptions": ["Postmortems are optional documentation"],
    }


class AgentDeterminismTests(unittest.TestCase):
    _previous_provider: str | None

    def setUp(self) -> None:
        self._previous_provider = os.environ.get("AGENT_PROVIDER")
        os.environ["AGENT_PROVIDER"] = "internal"

    def tearDown(self) -> None:
        if self._previous_provider is None:
            os.environ.pop("AGENT_PROVIDER", None)
            return
        os.environ["AGENT_PROVIDER"] = self._previous_provider

    def test_generate_curriculum_is_deterministic_for_same_spec(self) -> None:
        spec = topic_spec()
        first = generate_curriculum(spec)
        second = generate_curriculum(spec)
        self.assertEqual(first, second)

    def test_generate_curriculum_file_is_byte_stable(self) -> None:
        spec = topic_spec()

        with tempfile.TemporaryDirectory() as tmp_dir:
            spec_path = Path(tmp_dir) / "topic_spec.json"
            out_path = Path(tmp_dir) / "curriculum.json"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")

            generate_curriculum_file(spec_path, out_path)
            first = out_path.read_text(encoding="utf-8")
            generate_curriculum_file(spec_path, out_path)
            second = out_path.read_text(encoding="utf-8")
            self.assertEqual(first, second)

    def test_context_pack_generation_is_deterministic(self) -> None:
        spec = topic_spec()
        spec["context_pack"] = {
            "domain": "repo-engineering",
            "focus_terms": ["orchestration", "validation"],
            "local_paths": ["README.md", "learning_compiler/agent/spec.py"],
            "required_outcomes": ["integration plan"],
        }
        first = generate_curriculum(spec)
        second = generate_curriculum(spec)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
