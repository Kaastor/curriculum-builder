"""Pipeline orchestration commands: generate/validate/plan/iterate/run."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from learning_compiler.agent import generate_curriculum_file
from learning_compiler.orchestration.command_utils import run_id_from_args
from learning_compiler.orchestration.exec import (
    run_validator,
    write_validation_report,
)
from learning_compiler.orchestration.fs import load_run, read_json, required_paths, write_json
from learning_compiler.orchestration.planning import build_plan, compute_diff
from learning_compiler.orchestration.stage import (
    ensure_stage,
    persist_if_changed,
    sync_stage,
    topic_spec_errors,
)
from learning_compiler.orchestration.types import RunPaths, Stage, stage_from


def _load_synced_run(run_id: str) -> tuple[Path, dict[str, Any], RunPaths]:
    run_dir, meta = load_run(run_id)
    _, changed = sync_stage(run_dir, meta)
    persist_if_changed(run_dir, meta, changed)
    return run_dir, meta, required_paths(run_dir)


def _validate_run(run_dir: Path, meta: dict[str, Any], paths: RunPaths) -> int:
    spec_errors = topic_spec_errors(paths.topic_spec)
    if spec_errors:
        print(f"Topic spec missing or incomplete: {paths.topic_spec}", file=sys.stderr)
        for error in spec_errors[:10]:
            print(f"- {error}", file=sys.stderr)
        return 1

    if not paths.curriculum.exists():
        print(f"Missing curriculum file: {paths.curriculum}", file=sys.stderr)
        return 1

    result = run_validator(paths.curriculum, paths.topic_spec)
    report_path = write_validation_report(run_dir, result)

    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    print(f"Saved validation report: {report_path}")

    if result.returncode == 0:
        paths.validation_pass_marker.write_text("ok\n", encoding="utf-8")
        if ensure_stage(meta, Stage.VALIDATED, "validator passed"):
            write_json(run_dir / "run.json", meta)
    else:
        paths.validation_pass_marker.unlink(missing_ok=True)
        _, sync_changed = sync_stage(run_dir, meta)
        persist_if_changed(run_dir, meta, sync_changed)

    return result.returncode


def _save_plan(run_dir: Path, meta: dict[str, Any], paths: RunPaths) -> None:
    topic_spec = read_json(paths.topic_spec)
    curriculum = read_json(paths.curriculum)
    plan = build_plan(topic_spec, curriculum)
    write_json(paths.plan, plan)

    if ensure_stage(meta, Stage.PLANNED, "plan generated"):
        write_json(run_dir / "run.json", meta)

    print(f"Saved plan: {paths.plan}")


def _save_diff(run_dir: Path, meta: dict[str, Any], paths: RunPaths) -> None:
    current = read_json(paths.curriculum)
    previous = (
        read_json(paths.previous_curriculum)
        if paths.previous_curriculum.exists()
        else {"nodes": []}
    )

    diff = compute_diff(previous, current)
    write_json(paths.diff_report, diff)

    if ensure_stage(meta, Stage.ITERATED, "diff generated"):
        write_json(run_dir / "run.json", meta)

    print(f"Saved diff report: {paths.diff_report}")


def cmd_validate(args: argparse.Namespace) -> int:
    run_id = run_id_from_args(args)
    run_dir, meta, paths = _load_synced_run(run_id)
    return _validate_run(run_dir, meta, paths)


def cmd_plan(args: argparse.Namespace) -> int:
    run_id = run_id_from_args(args)
    run_dir, meta, paths = _load_synced_run(run_id)

    if _validate_run(run_dir, meta, paths) != 0:
        return 1

    _save_plan(run_dir, meta, paths)
    return 0


def cmd_iterate(args: argparse.Namespace) -> int:
    run_id = run_id_from_args(args)
    run_dir, meta, paths = _load_synced_run(run_id)

    if not paths.curriculum.exists():
        print(f"Missing curriculum file: {paths.curriculum}", file=sys.stderr)
        return 1

    _save_diff(run_dir, meta, paths)
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    run_id = run_id_from_args(args)
    run_dir, meta, paths = _load_synced_run(run_id)
    stage = stage_from(meta.get("stage", Stage.INITIALIZED.value))

    if stage == Stage.INITIALIZED:
        raise SystemExit(f"Topic spec not ready: {paths.topic_spec}")

    if paths.curriculum.exists():
        paths.previous_curriculum.write_text(
            paths.curriculum.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    generate_curriculum_file(paths.topic_spec, paths.curriculum)
    if ensure_stage(meta, Stage.GENERATED, "agent generated curriculum"):
        write_json(run_dir / "run.json", meta)
    print(f"Generated curriculum with agent: {paths.curriculum}")

    if not paths.curriculum.exists():
        raise SystemExit(f"Curriculum was not produced at expected path: {paths.curriculum}")

    if _validate_run(run_dir, meta, paths) != 0:
        return 1

    _save_plan(run_dir, meta, paths)
    _save_diff(run_dir, meta, paths)

    print(f"Orchestration run completed: {run_id}")
    return 0
