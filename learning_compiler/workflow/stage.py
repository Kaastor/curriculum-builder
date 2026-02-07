"""Stage inference and synchronization logic for workflow runs."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from learning_compiler.validator.topic_spec import validate_topic_spec_contract
from learning_compiler.workflow.fs import read_json, required_paths, utc_now, write_json
from learning_compiler.workflow.types import STAGE_INDEX, RunPaths, Stage, stage_from


def append_history(meta: dict[str, Any], stage: Stage, reason: str) -> None:
    item = {"at_utc": utc_now(), "stage": stage.value, "reason": reason}
    history = meta.get("history")
    if isinstance(history, list):
        history.append(item)
    else:
        meta["history"] = [item]


def ensure_stage(meta: dict[str, Any], stage: Stage, reason: str) -> bool:
    current = stage_from(meta.get("stage", Stage.INITIALIZED.value))
    if STAGE_INDEX[stage] > STAGE_INDEX[current]:
        meta["stage"] = stage.value
        append_history(meta, stage, reason)
        return True
    return False


def topic_spec_errors(topic_spec_path: Path) -> list[str]:
    if not topic_spec_path.exists():
        return [f"missing file: {topic_spec_path}"]
    try:
        payload = read_json(topic_spec_path)
    except json.JSONDecodeError:
        return ["invalid JSON"]
    return validate_topic_spec_contract(payload)


def looks_ready_spec(topic_spec_path: Path) -> bool:
    return len(topic_spec_errors(topic_spec_path)) == 0


def latest_mtime_ns(path: Path) -> int | None:
    if not path.exists():
        return None

    latest = path.stat().st_mtime_ns
    if path.is_file():
        return latest

    for root, dirs, files in os.walk(path):
        root_path = Path(root)
        try:
            latest = max(latest, root_path.stat().st_mtime_ns)
        except OSError:
            continue

        for name in files + dirs:
            candidate = root_path / name
            try:
                latest = max(latest, candidate.stat().st_mtime_ns)
            except OSError:
                continue

    return latest


def marker_is_current(marker: Path, dependencies: list[Path]) -> bool:
    marker_mtime = latest_mtime_ns(marker)
    if marker_mtime is None:
        return False

    for dependency in dependencies:
        dep_mtime = latest_mtime_ns(dependency)
        if dep_mtime is None:
            return False
        if dep_mtime > marker_mtime:
            return False

    return True


def validation_is_current(paths: RunPaths) -> bool:
    return marker_is_current(
        paths.validation_pass_marker,
        [paths.topic_spec, paths.curriculum, paths.validation_report],
    )


def plan_is_current(paths: RunPaths) -> bool:
    return marker_is_current(paths.plan, [paths.topic_spec, paths.curriculum])


def diff_is_current(paths: RunPaths) -> bool:
    dependencies = [paths.curriculum]
    if paths.previous_curriculum.exists():
        dependencies.append(paths.previous_curriculum)
    return marker_is_current(paths.diff_report, dependencies)


def infer_stage_from_artifacts(run_dir: Path) -> Stage:
    paths = required_paths(run_dir)
    stage = Stage.INITIALIZED

    if looks_ready_spec(paths.topic_spec):
        stage = Stage.SPEC_READY
    if stage == Stage.SPEC_READY and paths.curriculum.exists():
        stage = Stage.MAP_GENERATED
    if stage == Stage.MAP_GENERATED and validation_is_current(paths):
        stage = Stage.VALIDATED
    if stage == Stage.VALIDATED and plan_is_current(paths):
        stage = Stage.PLANNED
    if stage == Stage.PLANNED and diff_is_current(paths):
        stage = Stage.ITERATED

    return stage


def persist_if_changed(run_dir: Path, meta: dict[str, Any], changed: bool) -> None:
    if not changed:
        return

    write_json(run_dir / "run.json", meta)


def sync_stage(run_dir: Path, meta: dict[str, Any]) -> tuple[Stage, bool]:
    inferred = infer_stage_from_artifacts(run_dir)
    current = stage_from(meta.get("stage", Stage.INITIALIZED.value))
    changed = current != inferred
    if changed:
        meta["stage"] = inferred.value
        append_history(meta, inferred, f"auto-sync from artifacts (was {current.value})")
    return stage_from(meta.get("stage", inferred.value)), changed
