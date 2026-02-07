#!/usr/bin/env python3
"""Workflow run manager for prompt-driven curriculum generation."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any

try:
    from validator import validate_topic_spec_contract
except ImportError:  # pragma: no cover - fallback for module execution mode
    from scripts.validator import validate_topic_spec_contract


STAGES = [
    "initialized",
    "spec_ready",
    "curriculum_generated",
    "structurally_validated",
    "pedagogically_validated",
    "repo_generated",
    "done",
]
STAGE_INDEX = {name: idx for idx, name in enumerate(STAGES)}

REPO_ROOT = Path(__file__).resolve().parents[1]


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


def required_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "topic_spec": run_dir / "inputs" / "topic_spec.json",
        "automation": run_dir / "inputs" / "automation.json",
        "curriculum": run_dir / "outputs" / "curriculum" / "curriculum.json",
        "structural_review": run_dir / "outputs" / "reviews" / "structural_validation.md",
        "structural_pass_marker": run_dir / "logs" / "structural_validation.ok",
        "pedagogical_review": run_dir / "outputs" / "reviews" / "curriculum_review.md",
        "repository_output": run_dir / "outputs" / "repository",
        "done_marker": run_dir / "logs" / "final_gate.ok",
        "run_meta": run_dir / "run.json",
    }


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def append_history(meta: dict[str, Any], stage: str, reason: str) -> None:
    history = meta.setdefault("history", [])
    history.append({"at_utc": utc_now(), "stage": stage, "reason": reason})


def ensure_stage(meta: dict[str, Any], stage: str, reason: str) -> bool:
    current = meta.get("stage", "initialized")
    if STAGE_INDEX[stage] > STAGE_INDEX.get(current, -1):
        meta["stage"] = stage
        append_history(meta, stage, reason)
        return True
    return False


def looks_ready_spec(topic_spec_path: Path) -> bool:
    return len(topic_spec_errors(topic_spec_path)) == 0


def topic_spec_errors(topic_spec_path: Path) -> list[str]:
    if not topic_spec_path.exists():
        return [f"missing file: {topic_spec_path}"]
    try:
        payload = read_json(topic_spec_path)
    except json.JSONDecodeError:
        return ["invalid JSON"]
    return validate_topic_spec_contract(payload)


def has_repo_output(repo_out: Path) -> bool:
    if not repo_out.exists():
        return False
    return any(repo_out.iterdir())


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

        for name in files:
            candidate = root_path / name
            try:
                latest = max(latest, candidate.stat().st_mtime_ns)
            except OSError:
                continue

        for name in dirs:
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

    for dep in dependencies:
        dep_mtime = latest_mtime_ns(dep)
        if dep_mtime is None:
            return False
        if dep_mtime > marker_mtime:
            return False

    return True


def structural_validation_is_current(paths: dict[str, Path]) -> bool:
    return marker_is_current(
        paths["structural_pass_marker"],
        [paths["topic_spec"], paths["curriculum"], paths["structural_review"]],
    )


def final_gate_is_current(paths: dict[str, Path]) -> bool:
    return marker_is_current(
        paths["done_marker"],
        [paths["repository_output"]],
    )


def infer_stage_from_artifacts(run_dir: Path) -> str:
    paths = required_paths(run_dir)
    stage = "initialized"

    if looks_ready_spec(paths["topic_spec"]):
        stage = "spec_ready"
    if stage == "spec_ready" and paths["curriculum"].exists():
        stage = "curriculum_generated"
    if stage == "curriculum_generated" and structural_validation_is_current(paths):
        stage = "structurally_validated"
    if stage == "structurally_validated" and paths["pedagogical_review"].exists():
        stage = "pedagogically_validated"
    if stage == "pedagogically_validated" and has_repo_output(paths["repository_output"]):
        stage = "repo_generated"
    if stage == "repo_generated" and final_gate_is_current(paths):
        stage = "done"

    return stage


def load_run(run_id: str) -> tuple[Path, dict[str, Any]]:
    run_dir = workflow_base_dir() / run_id
    run_meta_path = run_dir / "run.json"
    if not run_meta_path.exists():
        raise SystemExit(f"Run not found: {run_id}")
    return run_dir, read_json(run_meta_path)


def persist_if_changed(run_dir: Path, meta: dict[str, Any], changed: bool) -> None:
    if changed:
        write_json(run_dir / "run.json", meta)


def cmd_init(args: argparse.Namespace) -> int:
    base_dir = workflow_base_dir()
    base_dir.mkdir(parents=True, exist_ok=True)

    spec_template = topic_spec_template()
    auto_template = automation_template()
    if not spec_template.exists():
        raise SystemExit(f"Topic spec template not found: {spec_template}")

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    if args.name:
        run_id = f"{timestamp}-{slugify(args.name)}"
    else:
        run_id = timestamp

    run_dir = base_dir / run_id
    if run_dir.exists():
        raise SystemExit(f"Run directory already exists: {run_dir}")

    (run_dir / "inputs").mkdir(parents=True)
    (run_dir / "references").mkdir(parents=True)
    (run_dir / "outputs" / "curriculum").mkdir(parents=True)
    (run_dir / "outputs" / "reviews").mkdir(parents=True)
    (run_dir / "outputs" / "repository").mkdir(parents=True)
    (run_dir / "logs").mkdir(parents=True)

    shutil.copy2(spec_template, run_dir / "inputs" / "topic_spec.json")
    if auto_template.exists():
        shutil.copy2(auto_template, run_dir / "inputs" / "automation.json")

    meta = {
        "run_id": run_id,
        "created_at_utc": utc_now(),
        "stage": "initialized",
        "history": [
            {"at_utc": utc_now(), "stage": "initialized", "reason": "run initialized"}
        ],
    }
    write_json(run_dir / "run.json", meta)

    print("Initialized workflow run.")
    print(f"Run directory: {run_dir}")
    print(f"Topic spec: {run_dir / 'inputs' / 'topic_spec.json'}")
    if auto_template.exists():
        print(f"Automation config: {run_dir / 'inputs' / 'automation.json'}")
    return 0


def sync_stage(run_dir: Path, meta: dict[str, Any]) -> tuple[str, bool]:
    inferred = infer_stage_from_artifacts(run_dir)
    current = meta.get("stage", "initialized")
    changed = current != inferred
    if changed:
        meta["stage"] = inferred
        append_history(meta, inferred, f"auto-sync from artifacts (was {current})")
    return meta.get("stage", inferred), changed


def cmd_status(args: argparse.Namespace) -> int:
    run_dir, meta = load_run(args.run_id)
    stage, changed = sync_stage(run_dir, meta)
    persist_if_changed(run_dir, meta, changed)

    paths = required_paths(run_dir)
    print(f"Run: {args.run_id}")
    print(f"Stage: {stage}")
    print(f"Topic spec: {'ok' if looks_ready_spec(paths['topic_spec']) else 'missing/incomplete'}")
    print(f"Curriculum: {'ok' if paths['curriculum'].exists() else 'missing'}")
    print(f"Structural review: {'ok' if paths['structural_review'].exists() else 'missing'}")
    print(f"Structural pass marker: {'ok' if paths['structural_pass_marker'].exists() else 'missing'}")
    print(f"Pedagogical review: {'ok' if paths['pedagogical_review'].exists() else 'missing'}")
    print(f"Repository output: {'ok' if has_repo_output(paths['repository_output']) else 'missing'}")
    print(f"Done marker: {'ok' if paths['done_marker'].exists() else 'missing'}")
    return 0


def cmd_next(args: argparse.Namespace) -> int:
    run_dir, meta = load_run(args.run_id)
    stage, changed = sync_stage(run_dir, meta)
    persist_if_changed(run_dir, meta, changed)
    p = required_paths(run_dir)

    print(f"Current stage: {stage}")
    if stage == "initialized":
        print(f"Next: fill {p['topic_spec']}")
    elif stage == "spec_ready":
        print(f"Next: generate curriculum to {p['curriculum']}")
    elif stage == "curriculum_generated":
        print(f"Next: run structural validation -> python scripts/workflow.py validate {args.run_id}")
    elif stage == "structurally_validated":
        print(f"Next: create pedagogical review at {p['pedagogical_review']}")
    elif stage == "pedagogically_validated":
        print(f"Next: generate repository into {p['repository_output']}")
    elif stage == "repo_generated":
        print("Next: run repository gate, then mark done by creating logs/final_gate.ok")
    else:
        print("Run is complete.")
    return 0


def run_validator(
    curriculum_path: Path, topic_spec_path: Path | None = None
) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "validator.py"), str(curriculum_path)]
    if topic_spec_path is not None:
        cmd.extend(["--topic-spec", str(topic_spec_path)])
    return subprocess.run(cmd, text=True, capture_output=True)


def write_structural_report(run_dir: Path, result: subprocess.CompletedProcess[str]) -> Path:
    out_path = run_dir / "outputs" / "reviews" / "structural_validation.md"
    verdict = "PASS" if result.returncode == 0 else "FAIL"
    report = [
        "## Structural Validation Report\n",
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


def cmd_validate(args: argparse.Namespace) -> int:
    run_dir, meta = load_run(args.run_id)
    stage, changed = sync_stage(run_dir, meta)
    persist_if_changed(run_dir, meta, changed)
    paths = required_paths(run_dir)

    spec_errors = topic_spec_errors(paths["topic_spec"])
    if spec_errors:
        print(f"Topic spec missing or incomplete: {paths['topic_spec']}", file=sys.stderr)
        for error in spec_errors[:5]:
            print(f"- {error}", file=sys.stderr)
        return 1

    curriculum_path = paths["curriculum"]
    if not curriculum_path.exists():
        print(f"Missing curriculum file: {curriculum_path}", file=sys.stderr)
        return 1

    result = run_validator(curriculum_path, paths["topic_spec"])
    report_path = write_structural_report(run_dir, result)
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    print(f"Saved structural report: {report_path}")

    if result.returncode == 0:
        paths["structural_pass_marker"].write_text("ok\n", encoding="utf-8")
        if ensure_stage(meta, "structurally_validated", "validator passed"):
            write_json(run_dir / "run.json", meta)
    else:
        paths["structural_pass_marker"].unlink(missing_ok=True)
        _, changed = sync_stage(run_dir, meta)
        persist_if_changed(run_dir, meta, changed)
    return result.returncode


def cmd_archive(args: argparse.Namespace) -> int:
    run_dir, _ = load_run(args.run_id)
    archive_dir = workflow_archive_dir()
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{args.run_id}.tar.gz"

    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(run_dir, arcname=args.run_id)

    print(f"Archive created: {archive_path}")
    return 0


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
        )
    if proc.returncode != 0:
        raise SystemExit(f"Command failed ({proc.returncode}): {command}\nSee: {log_path}")


def cmd_run(args: argparse.Namespace) -> int:
    run_dir, meta = load_run(args.run_id)
    stage, changed = sync_stage(run_dir, meta)
    persist_if_changed(run_dir, meta, changed)
    paths = required_paths(run_dir)

    if stage == "initialized":
        raise SystemExit(f"Topic spec not ready: {paths['topic_spec']}")

    automation = load_automation(run_dir)
    logs_dir = run_dir / "logs"

    curriculum_cmd = str(automation.get("curriculum_cmd", ""))
    pedagogical_cmd = str(automation.get("pedagogical_review_cmd", ""))
    repo_cmd = str(automation.get("repo_generation_cmd", ""))
    repo_gate_cmd = str(automation.get("repo_gate_cmd", ""))
    repo_path_value = str(automation.get("repo_path", "")).strip()

    if not paths["curriculum"].exists():
        if not is_command_set(curriculum_cmd):
            raise SystemExit("curriculum_cmd is not configured in inputs/automation.json")
        run_shell(curriculum_cmd, REPO_ROOT, logs_dir / "01_curriculum_generation.log")

    if not paths["curriculum"].exists():
        raise SystemExit(f"Curriculum was not produced at expected path: {paths['curriculum']}")

    validate_code = cmd_validate(argparse.Namespace(run_id=args.run_id))
    if validate_code != 0:
        return validate_code

    if not paths["pedagogical_review"].exists():
        if not is_command_set(pedagogical_cmd):
            raise SystemExit("pedagogical_review_cmd is not configured in inputs/automation.json")
        run_shell(pedagogical_cmd, REPO_ROOT, logs_dir / "02_pedagogical_review.log")

    if not paths["pedagogical_review"].exists():
        raise SystemExit(f"Pedagogical review missing: {paths['pedagogical_review']}")

    if not has_repo_output(paths["repository_output"]):
        if not is_command_set(repo_cmd):
            raise SystemExit("repo_generation_cmd is not configured in inputs/automation.json")
        run_shell(repo_cmd, REPO_ROOT, logs_dir / "03_repo_generation.log")

    if not has_repo_output(paths["repository_output"]):
        raise SystemExit(f"Repository output missing under: {paths['repository_output']}")

    if ensure_stage(meta, "repo_generated", "repository output generated"):
        write_json(run_dir / "run.json", meta)

    if repo_path_value:
        repo_path = Path(repo_path_value)
        if not repo_path.is_absolute():
            repo_path = run_dir / repo_path
    else:
        raise SystemExit("repo_path is not configured in inputs/automation.json")

    if not repo_path.exists():
        raise SystemExit(f"Configured repo_path does not exist: {repo_path}")
    if not is_command_set(repo_gate_cmd):
        raise SystemExit("repo_gate_cmd is not configured in inputs/automation.json")

    run_shell(repo_gate_cmd, repo_path, logs_dir / "04_repo_gate.log")
    paths["done_marker"].write_text("ok\n", encoding="utf-8")

    if ensure_stage(meta, "done", "workflow run completed and final gate passed"):
        write_json(run_dir / "run.json", meta)

    print(f"Workflow run completed and gated: {args.run_id}")
    return 0


def cmd_list(_: argparse.Namespace) -> int:
    base = workflow_base_dir()
    if not base.exists():
        return 0
    for path in sorted([p for p in base.iterdir() if p.is_dir()]):
        print(path.name)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Workflow run manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize a new workflow run")
    p_init.add_argument("name", nargs="?", help="Optional run name")
    p_init.set_defaults(func=cmd_init)

    p_status = sub.add_parser("status", help="Show run status")
    p_status.add_argument("run_id")
    p_status.set_defaults(func=cmd_status)

    p_next = sub.add_parser("next", help="Show next action for run")
    p_next.add_argument("run_id")
    p_next.set_defaults(func=cmd_next)

    p_validate = sub.add_parser("validate", help="Run structural validation for run")
    p_validate.add_argument("run_id")
    p_validate.set_defaults(func=cmd_validate)

    p_archive = sub.add_parser("archive", help="Archive run folder")
    p_archive.add_argument("run_id")
    p_archive.set_defaults(func=cmd_archive)

    p_run = sub.add_parser("run", help="Execute configured automation pipeline for run")
    p_run.add_argument("run_id")
    p_run.set_defaults(func=cmd_run)

    p_list = sub.add_parser("list", help="List runs")
    p_list.set_defaults(func=cmd_list)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
