"""Filesystem and environment helpers for workflow runs."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path
from typing import Any

from learning_compiler.workflow.types import RunPaths


REPO_ROOT = Path(__file__).resolve().parents[2]


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(raw: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "workflow"


def workflow_base_dir() -> Path:
    default = REPO_ROOT / "workflows" / "runs"
    return Path(os.environ.get("WORKFLOW_BASE_DIR", str(default)))


def workflow_archive_dir() -> Path:
    default = REPO_ROOT / "workflows" / "archives"
    return Path(os.environ.get("WORKFLOW_ARCHIVE_DIR", str(default)))


def topic_spec_template() -> Path:
    default = REPO_ROOT / "workflows" / "templates" / "topic_spec.template.json"
    return Path(os.environ.get("WORKFLOW_TEMPLATE_FILE", str(default)))


def automation_template() -> Path:
    default = REPO_ROOT / "workflows" / "templates" / "automation.template.json"
    return Path(os.environ.get("WORKFLOW_AUTOMATION_TEMPLATE", str(default)))


def required_paths(run_dir: Path) -> RunPaths:
    return RunPaths(
        topic_spec=run_dir / "inputs" / "topic_spec.json",
        automation=run_dir / "inputs" / "automation.json",
        curriculum=run_dir / "outputs" / "curriculum" / "curriculum.json",
        previous_curriculum=run_dir / "outputs" / "curriculum" / "previous_curriculum.json",
        validation_report=run_dir / "outputs" / "reviews" / "validation_report.md",
        validation_pass_marker=run_dir / "logs" / "validation.ok",
        plan=run_dir / "outputs" / "plan" / "plan.json",
        diff_report=run_dir / "outputs" / "reviews" / "diff_report.json",
        run_meta=run_dir / "run.json",
    )


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_run(run_id: str) -> tuple[Path, dict[str, Any]]:
    run_dir = workflow_base_dir() / run_id
    paths = required_paths(run_dir)
    if not paths.run_meta.exists():
        raise SystemExit(f"Run not found: {run_id}")
    return run_dir, read_json(paths.run_meta)
