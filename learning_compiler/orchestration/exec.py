"""Execution helpers for orchestration commands."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from learning_compiler.orchestration.fs import REPO_ROOT


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

