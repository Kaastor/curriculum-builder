from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORCHESTRATION_SCRIPT = ROOT / "scripts" / "orchestration.py"
TOPIC_SPEC_TEMPLATE = ROOT / "runs" / "templates" / "topic_spec.template.json"
SAMPLE_CURRICULUM = ROOT / "tests" / "fixtures" / "curriculum.json"


class OrchestrationCliTests(unittest.TestCase):
    def _env(self, tmp_dir: str) -> dict[str, str]:
        env = os.environ.copy()
        env["ORCHESTRATION_BASE_DIR"] = str(Path(tmp_dir) / "runs")
        env["ORCHESTRATION_TEMPLATE_FILE"] = str(TOPIC_SPEC_TEMPLATE)
        env["ORCHESTRATION_ARCHIVE_DIR"] = str(Path(tmp_dir) / "archives")
        return env

    def _run(self, env: dict[str, str], *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ORCHESTRATION_SCRIPT), *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=check,
        )

    def _write_valid_topic_spec(self, topic_spec_path: Path) -> None:
        topic_spec = json.loads(topic_spec_path.read_text(encoding="utf-8"))
        topic_spec["goal"] = "Build and defend Bayesian decision recommendations."
        topic_spec["audience"] = "Data-savvy product engineers"
        topic_spec["prerequisites"] = ["basic probability", "spreadsheet literacy"]
        topic_spec["scope_in"] = ["posterior reasoning", "uncertainty communication"]
        topic_spec["scope_out"] = ["advanced measure theory"]
        topic_spec["constraints"] = {
            "hours_per_week": 6,
            "total_hours_min": 12,
            "total_hours_max": 24,
            "depth": "practical",
            "node_count_min": 6,
            "node_count_max": 20,
            "max_prerequisites_per_node": 3,
        }
        topic_spec["domain_mode"] = "mature"
        topic_spec["evidence_mode"] = "standard"
        topic_spec["misconceptions"] = ["mean alone is enough for a decision"]
        topic_spec_path.write_text(json.dumps(topic_spec, indent=2) + "\n", encoding="utf-8")

    def test_init_creates_expected_structure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            result = self._run(env, "init", "Bayesian Decisions")
            self.assertIn("Initialized orchestration run.", result.stdout)

            run_dirs = sorted((Path(tmp_dir) / "runs").iterdir())
            self.assertEqual(1, len(run_dirs))
            run_dir = run_dirs[0]

            self.assertTrue((run_dir / "run.json").exists())
            self.assertTrue((run_dir / "inputs" / "topic_spec.json").exists())
            self.assertTrue((run_dir / "outputs" / "curriculum").exists())
            self.assertTrue((run_dir / "outputs" / "reviews").exists())
            self.assertTrue((run_dir / "outputs" / "plan").exists())
            self.assertTrue((run_dir / "logs").exists())
            self.assertFalse((run_dir / "inputs" / "automation.json").exists())

    def test_validate_requires_ready_topic_spec(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Needs Spec")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            curriculum_path.write_text(SAMPLE_CURRICULUM.read_text(encoding="utf-8"), encoding="utf-8")

            failed = self._run(env, "validate", run_dir.name, check=False)
            self.assertNotEqual(0, failed.returncode)
            self.assertIn("Topic spec missing or incomplete", failed.stderr)

    def test_status_rejects_legacy_run_metadata(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            run_dir = Path(tmp_dir) / "runs" / "20260101-000000-legacy"
            run_dir.mkdir(parents=True)
            (run_dir / "run.json").write_text(
                json.dumps(
                    {
                        "run_id": run_dir.name,
                        "created_at_utc": "2026-01-01T00:00:00Z",
                        "stage": "map_generated",
                        "history": [],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            failed = self._run(env, "status", run_dir.name, check=False)
            self.assertNotEqual(0, failed.returncode)
            self.assertIn("[invalid_argument] Invalid run metadata", failed.stderr)

    def test_validate_updates_stage_and_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Validation")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_valid_topic_spec(topic_spec_path)

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            curriculum_path.write_text(SAMPLE_CURRICULUM.read_text(encoding="utf-8"), encoding="utf-8")

            result = self._run(env, "validate", run_dir.name)
            self.assertIn("CURRICULUM VALIDATION REPORT", result.stdout)

            report_path = run_dir / "outputs" / "reviews" / "validation_report.md"
            self.assertTrue(report_path.exists())

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("validated", run_meta["stage"])

    def test_plan_command_generates_plan(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Planner")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_valid_topic_spec(topic_spec_path)

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            curriculum_path.write_text(SAMPLE_CURRICULUM.read_text(encoding="utf-8"), encoding="utf-8")

            result = self._run(env, "plan", run_dir.name)
            self.assertIn("Saved plan", result.stdout)

            plan_path = run_dir / "outputs" / "plan" / "plan.json"
            self.assertTrue(plan_path.exists())
            plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertIn("weeks", plan_payload)
            self.assertGreaterEqual(plan_payload["duration_weeks"], 2)

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("planned", run_meta["stage"])

    def test_run_generates_curriculum_with_agent(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Agent Generation")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_valid_topic_spec(topic_spec_path)

            result = self._run(env, "run", run_dir.name)
            self.assertIn("Generated curriculum with agent", result.stdout)
            self.assertIn("Orchestration run completed", result.stdout)
            self.assertTrue((run_dir / "outputs" / "curriculum" / "curriculum.json").exists())

    def test_run_executes_full_pipeline_and_writes_diff(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Full Pipeline")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_valid_topic_spec(topic_spec_path)

            result = self._run(env, "run", run_dir.name)
            self.assertIn("Orchestration run completed", result.stdout)

            self.assertTrue((run_dir / "outputs" / "reviews" / "validation_report.md").exists())
            self.assertTrue((run_dir / "outputs" / "plan" / "plan.json").exists())
            self.assertTrue((run_dir / "outputs" / "reviews" / "diff_report.json").exists())

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("iterated", run_meta["stage"])

    def test_status_demotes_when_curriculum_changes_after_validation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Freshness")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_valid_topic_spec(topic_spec_path)

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            curriculum_path.write_text(SAMPLE_CURRICULUM.read_text(encoding="utf-8"), encoding="utf-8")

            self._run(env, "validate", run_dir.name)
            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("validated", run_meta["stage"])

            time.sleep(0.01)
            curriculum = json.loads(curriculum_path.read_text(encoding="utf-8"))
            curriculum["topic"] = "Changed Topic"
            curriculum_path.write_text(json.dumps(curriculum, indent=2) + "\n", encoding="utf-8")

            status = self._run(env, "status", run_dir.name)
            self.assertIn("Stage: generated", status.stdout)


if __name__ == "__main__":
    unittest.main()
