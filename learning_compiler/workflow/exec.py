"""Execution helpers for workflow commands."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

from learning_compiler.workflow.fs import REPO_ROOT, read_json


def run_validator(
    curriculum_path: Path,
    topic_spec_path: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "validator.py"), str(curriculum_path)]
    if topic_spec_path is not None:
        cmd.extend(["--topic-spec", str(topic_spec_path)])
    return subprocess.run(cmd, text=True, capture_output=True, check=False)


def write_validation_report(run_dir: Path, result: subprocess.CompletedProcess[str]) -> Path:
    out_path = run_dir / "outputs" / "reviews" / "validation_report.md"
    verdict = "PASS" if result.returncode == 0 else "FAIL"
    report = [
        "## Validation Report\n",
        f"- Verdict: **{verdict}**\n",
        "### Validator Output\n",
        "```text",
        result.stdout.rstrip(),
    ]
    if result.stderr.strip():
        report.extend(["", "---", "stderr:", result.stderr.rstrip()])
    report.append("```")
    out_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    return out_path


def load_automation(run_dir: Path) -> dict[str, Any]:
    path = run_dir / "inputs" / "automation.json"
    if not path.exists():
        raise SystemExit(f"Missing automation config: {path}")
    return read_json(path)


def is_command_set(command: str) -> bool:
    cleaned = command.strip()
    return bool(cleaned) and "<" not in cleaned and "replace" not in cleaned.lower()


def run_shell(command: str, cwd: Path, log_path: Path) -> None:
    with log_path.open("w", encoding="utf-8") as log_file:
        proc = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            text=True,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            executable="/bin/bash",
            check=False,
        )
    if proc.returncode != 0:
        raise SystemExit(f"Command failed ({proc.returncode}): {command}\nSee: {log_path}")
