"""Filesystem and environment helpers for orchestration runs."""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

from learning_compiler.config import load_config
from learning_compiler.errors import ErrorCode, LearningCompilerError, NotFoundError
from learning_compiler.orchestration.meta import RunMeta
from learning_compiler.orchestration.types import RunPaths


REPO_ROOT = load_config().repo_root


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(raw: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    return slug or "orchestration"


def orchestration_base_dir() -> Path:
    return load_config().runs_dir


def orchestration_archive_dir() -> Path:
    return load_config().runs_archive_dir


def topic_spec_template() -> Path:
    return load_config().topic_spec_template


def required_paths(run_dir: Path) -> RunPaths:
    return RunPaths(
        topic_spec=run_dir / "inputs" / "topic_spec.json",
        curriculum=run_dir / "outputs" / "curriculum" / "curriculum.json",
        previous_curriculum=run_dir / "outputs" / "curriculum" / "previous_curriculum.json",
        event_log=run_dir / "logs" / "events.jsonl",
        validation_report=run_dir / "outputs" / "reviews" / "validation_report.md",
        optimization_trace=run_dir / "outputs" / "reviews" / "optimization_trace.json",
        validation_pass_marker=run_dir / "logs" / "validation.ok",
        plan=run_dir / "outputs" / "plan" / "plan.json",
        diff_report=run_dir / "outputs" / "reviews" / "diff_report.json",
        run_meta=run_dir / "run.json",
    )


def list_run_dirs(base_dir: Path | None = None) -> list[Path]:
    root = base_dir or orchestration_base_dir()
    if not root.exists():
        return []
    return sorted(
        candidate
        for candidate in root.iterdir()
        if candidate.is_dir() and (candidate / "run.json").exists()
    )


def latest_curriculum_path(base_dir: Path | None = None) -> Path | None:
    for run_dir in reversed(list_run_dirs(base_dir)):
        curriculum_path = required_paths(run_dir).curriculum
        if curriculum_path.exists():
            return curriculum_path
    return None


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Expected JSON object in {path}",
            {"path": str(path)},
        )
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def resolve_within(base_dir: Path, candidate: Path) -> Path:
    base_resolved = base_dir.resolve()
    candidate_resolved = candidate.resolve()
    if candidate_resolved != base_resolved and base_resolved not in candidate_resolved.parents:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Path escapes configured base directory: {candidate}",
            {"base_dir": str(base_resolved), "candidate": str(candidate_resolved)},
        )
    return candidate_resolved


def load_run(run_id: str) -> tuple[Path, RunMeta]:
    base_dir = orchestration_base_dir()
    run_dir = resolve_within(base_dir, base_dir / run_id)
    paths = required_paths(run_dir)
    if not paths.run_meta.exists():
        raise NotFoundError(f"Run not found: {run_id}", {"run_id": run_id})

    payload = read_json(paths.run_meta)
    try:
        meta = RunMeta.from_dict(payload)
    except ValueError as exc:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Invalid run metadata in {paths.run_meta}; delete and re-initialize this run.",
            {"run_id": run_id, "path": str(paths.run_meta)},
        ) from exc
    return run_dir, meta
