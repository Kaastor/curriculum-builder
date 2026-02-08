"""Basic orchestration commands: init/status/next/list/archive."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import tarfile

from learning_compiler.errors import ConfigError
from learning_compiler.orchestration.command_utils import run_id_from_args
from learning_compiler.orchestration.events import stage_event
from learning_compiler.orchestration.fs import (
    list_run_dirs,
    load_run,
    orchestration_archive_dir,
    orchestration_base_dir,
    required_paths,
    slugify,
    topic_spec_template,
    utc_now,
    write_json,
)
from learning_compiler.orchestration.meta import RunMeta
from learning_compiler.orchestration.migrations import RUN_META_SCHEMA_VERSION
from learning_compiler.orchestration.stage import (
    looks_ready_spec,
    persist_if_changed,
    sync_stage,
)
from learning_compiler.orchestration.types import Stage


def cmd_init(args: argparse.Namespace) -> int:
    base_dir = orchestration_base_dir()
    base_dir.mkdir(parents=True, exist_ok=True)

    spec_template = topic_spec_template()
    if not spec_template.exists():
        raise ConfigError(
            f"Topic spec template not found: {spec_template}",
            {"template_path": str(spec_template)},
        )

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run_name = getattr(args, "name", None)
    run_id = f"{timestamp}-{slugify(run_name)}" if run_name else timestamp

    run_dir = base_dir / run_id
    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")

    (run_dir / "inputs").mkdir(parents=True)
    (run_dir / "outputs" / "curriculum").mkdir(parents=True)
    (run_dir / "outputs" / "reviews").mkdir(parents=True)
    (run_dir / "outputs" / "plan").mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True)

    shutil.copy2(spec_template, run_dir / "inputs" / "topic_spec.json")

    now = utc_now()
    meta = RunMeta(
        schema_version=RUN_META_SCHEMA_VERSION,
        run_id=run_id,
        created_at_utc=now,
        stage=Stage.INITIALIZED,
        history=[
            stage_event(
                at_utc=now,
                stage=Stage.INITIALIZED.value,
                message="run initialized",
            ).to_dict()
        ],
    )
    write_json(run_dir / "run.json", meta.to_dict())
    required_paths(run_dir).event_log.write_text(
        json.dumps(meta.history[0]) + "\n",
        encoding="utf-8",
    )

    print("Initialized orchestration run.")
    print(f"Run directory: {run_dir}")
    print(f"Topic spec: {run_dir / 'inputs' / 'topic_spec.json'}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    run_id = run_id_from_args(args)
    run_dir, meta = load_run(run_id)
    stage, changed = sync_stage(run_dir, meta)
    persist_if_changed(run_dir, meta, changed)

    paths = required_paths(run_dir)
    print(f"Run: {run_id}")
    print(f"Stage: {stage.value}")
    print(f"Topic spec: {'ok' if looks_ready_spec(paths.topic_spec) else 'missing/incomplete'}")
    print(f"Curriculum: {'ok' if paths.curriculum.exists() else 'missing'}")
    print(f"Validation report: {'ok' if paths.validation_report.exists() else 'missing'}")
    print(f"Plan: {'ok' if paths.plan.exists() else 'missing'}")
    print(f"Diff report: {'ok' if paths.diff_report.exists() else 'missing'}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    run_id = run_id_from_args(args)
    run_dir, meta = load_run(run_id)
    stage, changed = sync_stage(run_dir, meta)
    persist_if_changed(run_dir, meta, changed)
    paths = required_paths(run_dir)

    print(f"Current stage: {stage.value}")
    if stage == Stage.INITIALIZED:
        print(f"Next: fill {paths.topic_spec}")
    elif stage == Stage.SPEC_READY:
        print(f"Next: run generation -> python scripts/orchestration.py run {run_id}")
    elif stage == Stage.GENERATED:
        print(f"Next: run validation -> python scripts/orchestration.py validate {run_id}")
    elif stage == Stage.VALIDATED:
        print(f"Next: generate plan -> python scripts/orchestration.py plan {run_id}")
    elif stage == Stage.PLANNED:
        print(f"Next: generate diff -> python scripts/orchestration.py iterate {run_id}")
    else:
        print("Run completed through iterate stage.")
    return 0


def cmd_archive(args: argparse.Namespace) -> int:
    run_id = run_id_from_args(args)
    run_dir, _ = load_run(run_id)
    archive_dir = orchestration_archive_dir()
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{run_id}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(run_dir, arcname=run_id)

    print(f"Archive created: {archive_path}")
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    for path in list_run_dirs(orchestration_base_dir()):
        print(path.name)
    return 0
