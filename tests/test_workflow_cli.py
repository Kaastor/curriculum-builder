from __future__ import annotations

import json
import os
import shlex
import subprocess
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SCRIPT = ROOT / "scripts" / "workflow.py"
TOPIC_SPEC_TEMPLATE = ROOT / "workflows" / "templates" / "topic_spec.template.json"
AUTOMATION_TEMPLATE = ROOT / "workflows" / "templates" / "automation.template.json"
SAMPLE_CURRICULUM = ROOT / "data" / "curriculum.json"


class WorkflowCliTests(unittest.TestCase):
    def _env(self, tmp_dir: str) -> dict[str, str]:
        env = os.environ.copy()
        env["WORKFLOW_BASE_DIR"] = str(Path(tmp_dir) / "runs")
        env["WORKFLOW_TEMPLATE_FILE"] = str(TOPIC_SPEC_TEMPLATE)
        env["WORKFLOW_AUTOMATION_TEMPLATE"] = str(AUTOMATION_TEMPLATE)
        env["WORKFLOW_ARCHIVE_DIR"] = str(Path(tmp_dir) / "archives")
        return env

    def _run(self, env: dict[str, str], *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(WORKFLOW_SCRIPT), *args],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=check,
        )

    def _write_topic_spec_for_sample_curriculum(self, topic_spec_path: Path, topic_id: str) -> None:
        topic_spec = json.loads(topic_spec_path.read_text(encoding="utf-8"))
        topic_spec["topic_id"] = topic_id
        topic_spec["topic_name"] = "Tool Use Correctness"
        topic_spec["domain_ref"] = "field.md § I.1"
        topic_spec["target_role"] = "backend_developer"
        topic_spec["language"] = "python"
        topic_spec["project_type"] = "library"
        topic_spec["scenario"] = "flight_booking_agent"
        topic_spec["transfer_scenario"] = "hotel_booking_agent"
        topic_spec["prerequisites"] = ["python functions", "basic CLI"]
        topic_spec["outcome"] = "Build deterministic tool runtime reliability guardrails."
        topic_spec["failure_modes"] = [
            {
                "key": "choosing_wrong_tool",
                "label": "Choosing wrong tool",
                "description": "Wrong tool selected for a valid intent",
                "production_impact": "Incorrect business behavior despite successful execution",
                "example": "Uses payment tool instead of reservation tool",
                "must_cover_in_capstone": True,
            },
            {
                "key": "wrong_call_order",
                "label": "Wrong call order",
                "description": "Tools are called in a harmful sequence",
                "production_impact": "Invalid state transitions",
                "example": "Payment before reservation",
                "must_cover_in_capstone": True,
            },
            {
                "key": "malformed_arguments",
                "label": "Malformed arguments",
                "description": "Calls include invalid argument payloads",
                "production_impact": "Runtime faults and corrupted state",
                "example": "Missing required reservation_id",
                "must_cover_in_capstone": True,
            },
            {
                "key": "output_misinterpretation",
                "label": "Output misinterpretation",
                "description": "Caller misreads tool result semantics",
                "production_impact": "Failed operations are treated as success",
                "example": "Ignores ok=false flag",
                "must_cover_in_capstone": True,
            },
            {
                "key": "tool_hallucination",
                "label": "Tool hallucination",
                "description": "Unknown tools are invented at runtime",
                "production_impact": "Nondeterministic unsafe execution",
                "example": "Calls auto_upgrade_ticket tool that does not exist",
                "must_cover_in_capstone": True,
            },
            {
                "key": "tool_avoidance",
                "label": "Tool avoidance",
                "description": "Agent bypasses required tools with manual logic",
                "production_impact": "Audit and validation safeguards bypassed",
                "example": "Direct state mutation instead of reserve_seat tool",
                "must_cover_in_capstone": True,
            },
        ]
        topic_spec["design_patterns"] = []
        topic_spec["exercise_categories"] = [
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
                "description": "Argument correctness",
                "supports_exercise_types": ["write"],
                "is_capstone": False,
            },
            {
                "key": "output",
                "prefix": "R",
                "description": "Output handling",
                "supports_exercise_types": ["write"],
                "is_capstone": False,
            },
            {
                "key": "hallucination",
                "prefix": "H",
                "description": "Hallucination handling",
                "supports_exercise_types": ["write"],
                "is_capstone": False,
            },
            {
                "key": "avoidance",
                "prefix": "V",
                "description": "Avoidance handling",
                "supports_exercise_types": ["write"],
                "is_capstone": False,
            },
            {
                "key": "debug",
                "prefix": "D",
                "description": "Debug and read tasks",
                "supports_exercise_types": ["debug", "read"],
                "is_capstone": False,
            },
            {
                "key": "capstone",
                "prefix": "C",
                "description": "Integration capstone",
                "supports_exercise_types": ["integrate"],
                "is_capstone": True,
            },
        ]
        topic_spec["constraints"] = {
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
        }
        topic_spec["assessment"] = {
            "capstone_required_failure_modes": ["wrong_call_order"],
            "mastery_threshold": "Capstone passes all reliability checks.",
            "transfer_task_required": False,
            "max_uncaught_failure_modes": 1,
        }
        topic_spec["repo_preferences"] = {
            "repo_name": "tool-use-learning",
            "package_name": "tool_use_learning",
            "use_makefile": True,
        }
        topic_spec_path.write_text(json.dumps(topic_spec, indent=2) + "\n", encoding="utf-8")

    def test_init_creates_expected_structure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            result = self._run(env, "init", "Python Testing")
            self.assertIn("Initialized workflow run.", result.stdout)

            run_dirs = sorted((Path(tmp_dir) / "runs").iterdir())
            self.assertEqual(1, len(run_dirs), msg="Expected exactly one run folder")
            run_dir = run_dirs[0]

            self.assertTrue(run_dir.name.endswith("-python-testing"), msg="Run id should include slug")
            self.assertTrue((run_dir / "run.json").exists(), msg="Missing run metadata")
            self.assertTrue((run_dir / "inputs" / "topic_spec.json").exists(), msg="Missing topic spec")
            self.assertTrue((run_dir / "inputs" / "automation.json").exists(), msg="Missing automation config")
            self.assertTrue((run_dir / "outputs" / "curriculum").exists(), msg="Missing curriculum output dir")
            self.assertTrue((run_dir / "outputs" / "reviews").exists(), msg="Missing reviews output dir")
            self.assertTrue((run_dir / "outputs" / "repository").exists(), msg="Missing repository output dir")
            self.assertTrue((run_dir / "logs").exists(), msg="Missing logs dir")

    def test_validate_requires_ready_topic_spec(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Needs Spec")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            curriculum_path.write_text(SAMPLE_CURRICULUM.read_text(encoding="utf-8"), encoding="utf-8")

            failed = self._run(env, "validate", run_dir.name, check=False)
            self.assertNotEqual(0, failed.returncode, msg="Validation should fail when topic spec is incomplete")
            self.assertIn("Topic spec missing or incomplete", failed.stderr)

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("initialized", run_meta["stage"], msg="Stage should not advance when spec is incomplete")

    def test_status_does_not_mark_spec_ready_for_partial_spec(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Partial Spec")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            topic_spec = json.loads(topic_spec_path.read_text(encoding="utf-8"))
            topic_spec["topic_id"] = "partial_spec_topic"
            topic_spec_path.write_text(json.dumps(topic_spec, indent=2) + "\n", encoding="utf-8")

            status = self._run(env, "status", run_dir.name)
            self.assertIn("Topic spec: missing/incomplete", status.stdout)

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("initialized", run_meta["stage"])

    def test_validate_updates_stage_and_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Validation")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_topic_spec_for_sample_curriculum(topic_spec_path, "validation_topic")

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            curriculum_path.write_text(SAMPLE_CURRICULUM.read_text(encoding="utf-8"), encoding="utf-8")

            result = self._run(env, "validate", run_dir.name)
            self.assertIn("CURRICULUM VALIDATION REPORT", result.stdout)

            report_path = run_dir / "outputs" / "reviews" / "structural_validation.md"
            self.assertTrue(report_path.exists(), msg="Expected structural validation report")

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(
                "structurally_validated",
                run_meta["stage"],
                msg="Run stage should advance after successful structural validation",
            )

    def test_failed_validate_does_not_advance_stage(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Invalid Validation")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_topic_spec_for_sample_curriculum(topic_spec_path, "invalid_validation_topic")

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            curriculum_path.write_text("{}\n", encoding="utf-8")

            marker_path = run_dir / "logs" / "structural_validation.ok"
            marker_path.write_text("stale\n", encoding="utf-8")

            failed = self._run(env, "validate", run_dir.name, check=False)
            self.assertNotEqual(0, failed.returncode, msg="Validation should fail for invalid curriculum")
            self.assertFalse(
                marker_path.exists(),
                msg="Structural pass marker should be removed on failed validation",
            )

            self._run(env, "status", run_dir.name)
            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(
                "curriculum_generated",
                run_meta["stage"],
                msg="Failed validation must not advance stage to structurally_validated",
            )

    def test_run_requires_configured_commands(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Automate")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_topic_spec_for_sample_curriculum(topic_spec_path, "automate_topic")

            failed = self._run(env, "run", run_dir.name, check=False)
            self.assertNotEqual(0, failed.returncode, msg="Run should fail without configured commands")
            self.assertIn("curriculum_cmd is not configured", failed.stderr)

    def test_run_requires_repo_gate_and_only_marks_done_after_gate(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Gate Required")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_topic_spec_for_sample_curriculum(topic_spec_path, "gate_required_topic")

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            pedagogical_path = run_dir / "outputs" / "reviews" / "curriculum_review.md"
            repo_path = run_dir / "outputs" / "repository" / "gate-required-learning"

            automation_path = run_dir / "inputs" / "automation.json"
            automation = json.loads(automation_path.read_text(encoding="utf-8"))
            automation["curriculum_cmd"] = (
                f"cp {shlex.quote(str(SAMPLE_CURRICULUM))} {shlex.quote(str(curriculum_path))}"
            )
            automation["pedagogical_review_cmd"] = (
                f"printf '# pedagogical review\\n' > {shlex.quote(str(pedagogical_path))}"
            )
            automation["repo_generation_cmd"] = (
                f"mkdir -p {shlex.quote(str(repo_path))} && "
                f"printf 'repo\\n' > {shlex.quote(str(repo_path / 'README.md'))}"
            )
            automation["repo_path"] = str(repo_path.relative_to(run_dir))
            automation["repo_gate_cmd"] = ""
            automation_path.write_text(json.dumps(automation, indent=2) + "\n", encoding="utf-8")

            failed = self._run(env, "run", run_dir.name, check=False)
            self.assertNotEqual(
                0,
                failed.returncode,
                msg="Run should fail when repo gate command is not configured",
            )
            self.assertIn("repo_gate_cmd is not configured", failed.stderr)

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(
                "repo_generated",
                run_meta["stage"],
                msg="Run should stop at repo_generated when final gate is not configured",
            )
            self.assertFalse(
                (run_dir / "logs" / "final_gate.ok").exists(),
                msg="Done marker must not be created when gate is skipped",
            )

    def test_status_demotes_when_curriculum_changes_after_structural_pass(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Structural Freshness")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_topic_spec_for_sample_curriculum(topic_spec_path, "freshness_topic")

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            curriculum_path.write_text(SAMPLE_CURRICULUM.read_text(encoding="utf-8"), encoding="utf-8")

            self._run(env, "validate", run_dir.name)
            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("structurally_validated", run_meta["stage"])

            time.sleep(0.01)
            curriculum = json.loads(curriculum_path.read_text(encoding="utf-8"))
            curriculum["metadata"]["generated"] = "2099-01-01T00:00:00Z"
            curriculum_path.write_text(json.dumps(curriculum, indent=2) + "\n", encoding="utf-8")

            status = self._run(env, "status", run_dir.name)
            self.assertIn("Stage: curriculum_generated", status.stdout)

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(
                "curriculum_generated",
                run_meta["stage"],
                msg="Run stage should demote when curriculum changes after structural validation",
            )

    def test_status_demotes_done_when_repo_changes_after_gate(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env = self._env(tmp_dir)
            self._run(env, "init", "Done Freshness")
            run_dir = sorted((Path(tmp_dir) / "runs").iterdir())[0]

            topic_spec_path = run_dir / "inputs" / "topic_spec.json"
            self._write_topic_spec_for_sample_curriculum(topic_spec_path, "done_freshness_topic")

            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            pedagogical_path = run_dir / "outputs" / "reviews" / "curriculum_review.md"
            repo_path = run_dir / "outputs" / "repository" / "done-freshness-learning"
            repo_readme = repo_path / "README.md"

            automation_path = run_dir / "inputs" / "automation.json"
            automation = json.loads(automation_path.read_text(encoding="utf-8"))
            automation["curriculum_cmd"] = (
                f"cp {shlex.quote(str(SAMPLE_CURRICULUM))} {shlex.quote(str(curriculum_path))}"
            )
            automation["pedagogical_review_cmd"] = (
                f"printf '# pedagogical review\\n' > {shlex.quote(str(pedagogical_path))}"
            )
            automation["repo_generation_cmd"] = (
                f"mkdir -p {shlex.quote(str(repo_path))} && "
                f"printf 'repo\\n' > {shlex.quote(str(repo_readme))}"
            )
            automation["repo_path"] = str(repo_path.relative_to(run_dir))
            automation["repo_gate_cmd"] = "test -f README.md"
            automation_path.write_text(json.dumps(automation, indent=2) + "\n", encoding="utf-8")

            run_result = self._run(env, "run", run_dir.name)
            self.assertIn("Workflow run completed and gated", run_result.stdout)

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual("done", run_meta["stage"])

            time.sleep(0.01)
            repo_readme.write_text("repo changed\n", encoding="utf-8")

            status = self._run(env, "status", run_dir.name)
            self.assertIn("Stage: repo_generated", status.stdout)

            run_meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(
                "repo_generated",
                run_meta["stage"],
                msg="Run stage should demote when repo output changes after final gate",
            )


if __name__ == "__main__":
    unittest.main()
