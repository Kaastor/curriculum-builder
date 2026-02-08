from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from learning_compiler.agent.spec import build_generation_spec


def _topic_spec_with_scope(scope_path: Path) -> dict[str, object]:
    return {
        "spec_version": "1.0",
        "goal": "Build robust agentic workflows from source scope document.",
        "audience": "Engineers",
        "prerequisites": ["python"],
        "scope_in": ["placeholder scope item"],
        "scope_out": [],
        "constraints": {
            "hours_per_week": 6.0,
            "total_hours_min": 10.0,
            "total_hours_max": 24.0,
            "depth": "practical",
            "node_count_min": 6,
            "node_count_max": 12,
            "max_prerequisites_per_node": 3,
        },
        "domain_mode": "mature",
        "evidence_mode": "standard",
        "context_pack": {
            "domain": "agentic systems",
            "local_paths": [str(scope_path)],
            "required_outcomes": ["run explicit verification checks"],
        },
    }


class ScopeDirectGenerationTests(unittest.TestCase):
    def test_build_generation_spec_reads_scope_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            scope_path = Path(tmp_dir) / "scope.md"
            scope_path.write_text(
                (
                    "# Agentic Engineering\n"
                    "## Control Plane\n"
                    "- Tool execution policy\n"
                    "- Retry and timeout strategy\n"
                    "## Validation\n"
                    "- Regression evaluation harness\n"
                ),
                encoding="utf-8",
            )

            spec = build_generation_spec(_topic_spec_with_scope(scope_path))
            self.assertIsNotNone(spec.scope_document_text)
            self.assertIn("Tool execution policy", spec.scope_document_text or "")
            self.assertIn("Control Plane", spec.titles)
            self.assertIn("Tool execution policy", spec.titles)

    def test_build_generation_spec_uses_prose_only_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            scope_path = Path(tmp_dir) / "scope.md"
            scope_path.write_text(
                (
                    "This roadmap focuses on deterministic orchestration and reliable tool execution. "
                    "It emphasizes failure isolation boundaries and explicit recovery workflows. "
                    "It also requires repeatable validation and regression harness design."
                ),
                encoding="utf-8",
            )

            spec = build_generation_spec(_topic_spec_with_scope(scope_path))
            self.assertIsNotNone(spec.scope_document_text)
            self.assertGreaterEqual(len(spec.titles), 6)
            self.assertTrue(any("deterministic orchestration" in title.lower() for title in spec.titles))


if __name__ == "__main__":
    unittest.main()
