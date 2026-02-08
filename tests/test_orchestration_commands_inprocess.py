from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from learning_compiler import OrchestrationAPI
from learning_compiler.config import reset_config_cache
from learning_compiler.errors import LearningCompilerError


ROOT = Path(__file__).resolve().parents[1]
TOPIC_SPEC_TEMPLATE = ROOT / "runs" / "templates" / "topic_spec.template.json"


class OrchestrationInProcessTests(unittest.TestCase):
    def _set_env(self, tmp_dir: str) -> tuple[dict[str, str | None], Path]:
        previous = {
            "ORCHESTRATION_BASE_DIR": os.environ.get("ORCHESTRATION_BASE_DIR"),
            "ORCHESTRATION_TEMPLATE_FILE": os.environ.get("ORCHESTRATION_TEMPLATE_FILE"),
            "ORCHESTRATION_ARCHIVE_DIR": os.environ.get("ORCHESTRATION_ARCHIVE_DIR"),
            "AGENT_PROVIDER": os.environ.get("AGENT_PROVIDER"),
        }
        runs_dir = Path(tmp_dir) / "runs"
        os.environ["ORCHESTRATION_BASE_DIR"] = str(runs_dir)
        os.environ["ORCHESTRATION_TEMPLATE_FILE"] = str(TOPIC_SPEC_TEMPLATE)
        os.environ["ORCHESTRATION_ARCHIVE_DIR"] = str(Path(tmp_dir) / "archives")
        os.environ["AGENT_PROVIDER"] = "internal"
        reset_config_cache()
        return previous, runs_dir

    def _restore_env(self, previous: dict[str, str | None]) -> None:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        reset_config_cache()

    def test_init_and_status_in_process(self) -> None:
        api = OrchestrationAPI()
        with tempfile.TemporaryDirectory() as tmp_dir:
            previous, runs_dir = self._set_env(tmp_dir)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    code = api.run_cli(["init", "in-process"])
                self.assertEqual(0, code)
                run_id = sorted(runs_dir.iterdir())[0].name
                with contextlib.redirect_stdout(io.StringIO()):
                    status_code = api.run_cli(["status", run_id])
                self.assertEqual(0, status_code)
            finally:
                self._restore_env(previous)

    def test_run_requires_ready_spec_when_no_scope_file(self) -> None:
        api = OrchestrationAPI()
        with tempfile.TemporaryDirectory() as tmp_dir:
            previous, _ = self._set_env(tmp_dir)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    api.run_cli(["init", "spec-required"])
                run_id = sorted(Path(tmp_dir, "runs").iterdir())[0].name
                with self.assertRaises(LearningCompilerError):
                    with contextlib.redirect_stdout(io.StringIO()):
                        api.run_cli(["run", run_id])
            finally:
                self._restore_env(previous)

    def test_scope_section_mode_requires_sections_in_process(self) -> None:
        api = OrchestrationAPI()
        with tempfile.TemporaryDirectory() as tmp_dir:
            previous, runs_dir = self._set_env(tmp_dir)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    api.run_cli(["init", "scope-section"])
                run_dir = sorted(runs_dir.iterdir())[0]
                scope_path = run_dir / "inputs" / "scope.md"
                scope_path.write_text("# Scope\n- Topic\n", encoding="utf-8")
                with self.assertRaises(LearningCompilerError):
                    with contextlib.redirect_stdout(io.StringIO()):
                        api.run_cli(
                            [
                                "run",
                                run_dir.name,
                                "--scope-file",
                                str(scope_path),
                                "--scope-mode",
                                "section",
                            ]
                        )
            finally:
                self._restore_env(previous)

    def test_scope_run_generates_artifacts(self) -> None:
        api = OrchestrationAPI()
        with tempfile.TemporaryDirectory() as tmp_dir:
            previous, runs_dir = self._set_env(tmp_dir)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    api.run_cli(["init", "scope-input"])
                run_dir = sorted(runs_dir.iterdir())[0]
                scope_path = run_dir / "inputs" / "scope.md"
                scope_path.write_text(
                    "# Scope\n- deterministic planning\n- validation gates\n- reliability checks\n",
                    encoding="utf-8",
                )

                with contextlib.redirect_stdout(io.StringIO()):
                    code = api.run_cli(
                        [
                            "run",
                            run_dir.name,
                            "--scope-file",
                            str(scope_path),
                            "--scope-mode",
                            "seed-list",
                        ]
                    )
                self.assertEqual(0, code)
                concepts = json.loads((run_dir / "scope_concepts.json").read_text(encoding="utf-8"))
                self.assertEqual("1.0", concepts.get("schema_version"))
                self.assertEqual("scope_concepts", concepts.get("artifact_type"))
                self.assertEqual({}, concepts.get("policy_snapshot"))
                effective_scope = (run_dir / "inputs" / "scope.md").read_text(encoding="utf-8")
                self.assertIn("deterministic planning", effective_scope)
            finally:
                self._restore_env(previous)

    def test_scope_section_mode_writes_selected_scope_input(self) -> None:
        api = OrchestrationAPI()
        with tempfile.TemporaryDirectory() as tmp_dir:
            previous, runs_dir = self._set_env(tmp_dir)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    api.run_cli(["init", "scope-section-selection"])
                run_dir = sorted(runs_dir.iterdir())[0]
                source_scope = run_dir / "inputs" / "source.md"
                source_scope.write_text(
                    (
                        "# Scope\n"
                        "## Runtime\n"
                        "- retry policies\n"
                        "## Evaluation\n"
                        "- benchmark harness\n"
                    ),
                    encoding="utf-8",
                )
                with contextlib.redirect_stdout(io.StringIO()):
                    code = api.run_cli(
                        [
                            "run",
                            run_dir.name,
                            "--scope-file",
                            str(source_scope),
                            "--scope-mode",
                            "section",
                            "--scope-section",
                            "runtime",
                        ]
                    )
                self.assertEqual(0, code)
                effective_scope = (run_dir / "inputs" / "scope.md").read_text(encoding="utf-8")
                self.assertIn("## Runtime", effective_scope)
                self.assertIn("retry policies", effective_scope)
                self.assertNotIn("## Evaluation", effective_scope)
                self.assertNotIn("benchmark harness", effective_scope)
            finally:
                self._restore_env(previous)

    def test_scope_breadth_scales_scope_in_and_curriculum_size(self) -> None:
        api = OrchestrationAPI()
        with tempfile.TemporaryDirectory() as tmp_dir:
            previous, runs_dir = self._set_env(tmp_dir)
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    api.run_cli(["init", "scope-breadth"])
                run_dir = sorted(runs_dir.iterdir())[0]
                scope_path = run_dir / "inputs" / "scope.md"
                scope_path.write_text(
                    "\n".join(
                        ["# Scope"]
                        + [f"- topic area {index}: implementation and validation pattern {index}" for index in range(1, 31)]
                    )
                    + "\n",
                    encoding="utf-8",
                )
                with contextlib.redirect_stdout(io.StringIO()):
                    code = api.run_cli(
                        [
                            "run",
                            run_dir.name,
                            "--scope-file",
                            str(scope_path),
                            "--scope-mode",
                            "seed-list",
                        ]
                    )
                self.assertEqual(0, code)

                topic_spec = json.loads((run_dir / "inputs" / "topic_spec.json").read_text(encoding="utf-8"))
                curriculum = json.loads(
                    (run_dir / "outputs" / "curriculum" / "curriculum.json").read_text(encoding="utf-8")
                )
                self.assertGreaterEqual(len(topic_spec.get("scope_in", [])), 20)
                self.assertGreater(len(curriculum.get("nodes", [])), 8)
            finally:
                self._restore_env(previous)


if __name__ == "__main__":
    unittest.main()
