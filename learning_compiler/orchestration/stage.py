"""Stage inference and synchronization logic for orchestration runs."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from learning_compiler.errors import LearningCompilerError
from learning_compiler.orchestration.events import stage_event
from learning_compiler.orchestration.fs import read_json, required_paths, utc_now, write_json
from learning_compiler.orchestration.meta import RunMeta
from learning_compiler.orchestration.types import STAGE_INDEX, RunPaths, Stage
from learning_compiler.validator.topic_spec import validate_topic_spec_contract


def _append_event_log(run_dir: Path, event_payload: dict[str, Any]) -> None:
    event_log = required_paths(run_dir).event_log
    event_log.parent.mkdir(parents=True, exist_ok=True)
    with event_log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event_payload) + "\n")


def append_history(
    meta: RunMeta,
    stage: Stage,
    message: str,
    *,
    run_dir: Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    event_payload = stage_event(
        at_utc=utc_now(),
        stage=stage.value,
        message=message,
        metadata=metadata,
    ).to_dict()

    meta.history.append(event_payload)
    if run_dir is not None:
        _append_event_log(run_dir, event_payload)


def ensure_stage(
    meta: RunMeta,
    stage: Stage,
    message: str,
    *,
    run_dir: Path | None = None,
    metadata: dict[str, Any] | None = None,
) -> bool:
    if STAGE_INDEX[stage] > STAGE_INDEX[meta.stage]:
        meta.stage = stage
        append_history(meta, stage, message, run_dir=run_dir, metadata=metadata)
        return True
    return False


def topic_spec_errors(topic_spec_path: Path) -> list[str]:
    if not topic_spec_path.exists():
        return [f"missing file: {topic_spec_path}"]
    try:
        payload = read_json(topic_spec_path)
    except json.JSONDecodeError:
        return ["invalid JSON"]
    except LearningCompilerError as exc:
        return [exc.message]
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
        stage = Stage.GENERATED
    if stage == Stage.GENERATED and validation_is_current(paths):
        stage = Stage.VALIDATED
    if stage == Stage.VALIDATED and plan_is_current(paths):
        stage = Stage.PLANNED
    if stage == Stage.PLANNED and diff_is_current(paths):
        stage = Stage.ITERATED

    return stage


def persist_if_changed(run_dir: Path, meta: RunMeta, changed: bool) -> None:
    if not changed:
        return

    write_json(run_dir / "run.json", meta.to_dict())


def sync_stage(run_dir: Path, meta: RunMeta) -> tuple[Stage, bool]:
    inferred = infer_stage_from_artifacts(run_dir)
    current = meta.stage
    changed = current != inferred
    if changed:
        meta.stage = inferred
        append_history(
            meta,
            inferred,
            f"auto-sync from artifacts (was {current.value})",
            run_dir=run_dir,
            metadata={"previous_stage": current.value},
        )
    return meta.stage, changed
