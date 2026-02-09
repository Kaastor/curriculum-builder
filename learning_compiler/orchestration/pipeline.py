"""Service object for orchestration run execution workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

from learning_compiler.agent import (
    DefaultCurriculumGenerator,
    ScopeIngestMode,
)
from learning_compiler.agent.contracts import CurriculumGenerator
from learning_compiler.domain import parse_curriculum, parse_topic_spec
from learning_compiler.errors import ErrorCode, LearningCompilerError, StageConflictError
from learning_compiler.orchestration.exec import run_validator, write_validation_report
from learning_compiler.orchestration.fs import load_run, read_json, required_paths, write_json
from learning_compiler.orchestration.meta import RunMeta
from learning_compiler.orchestration.planning import build_plan, compute_diff
from learning_compiler.orchestration.scope_args import validate_scope_selection
from learning_compiler.orchestration.scope_pipeline import (
    synthesize_topic_spec_from_scope,
)
from learning_compiler.orchestration.scope_selection import resolve_scope_path
from learning_compiler.orchestration.stage import (
    ensure_stage,
    plan_is_current,
    persist_if_changed,
    sync_stage,
    topic_spec_errors,
    validation_is_current,
)
from learning_compiler.orchestration.types import RunPaths, Stage


@dataclass(slots=True, frozen=True)
class ScopeRunOptions:
    scope_file: str
    mode: ScopeIngestMode
    sections: tuple[str, ...]


@dataclass(slots=True)
class RunContext:
    run_id: str
    run_dir: Path
    meta: RunMeta
    paths: RunPaths


class RunPipeline:
    """Coordinated orchestration pipeline for run lifecycle commands."""

    def __init__(self, generator: CurriculumGenerator | None = None) -> None:
        self._generator = generator or DefaultCurriculumGenerator()

    def _load_context(self, run_id: str) -> RunContext:
        run_dir, meta = load_run(run_id)
        _, changed = sync_stage(run_dir, meta)
        persist_if_changed(run_dir, meta, changed)
        return RunContext(run_id=run_id, run_dir=run_dir, meta=meta, paths=required_paths(run_dir))

    def _save_meta_if_advanced(self, context: RunContext, stage: Stage, message: str, metadata: dict | None = None) -> None:
        if ensure_stage(context.meta, stage, message, run_dir=context.run_dir, metadata=metadata):
            write_json(context.run_dir / "run.json", context.meta.to_dict())

    def _validate(self, context: RunContext) -> int:
        spec_errors = topic_spec_errors(context.paths.topic_spec)
        if spec_errors:
            print(f"Topic spec missing or incomplete: {context.paths.topic_spec}", file=sys.stderr)
            for error in spec_errors[:10]:
                print(f"- {error}", file=sys.stderr)
            return 1

        if not context.paths.curriculum.exists():
            print(f"Missing curriculum file: {context.paths.curriculum}", file=sys.stderr)
            return 1

        result = run_validator(context.paths.curriculum, context.paths.topic_spec)
        report_path = write_validation_report(context.run_dir, result)

        print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        print(f"Saved validation report: {report_path}")

        if result.returncode == 0:
            context.paths.validation_pass_marker.write_text("ok\n", encoding="utf-8")
            self._save_meta_if_advanced(context, Stage.VALIDATED, "validator passed")
        else:
            context.paths.validation_pass_marker.unlink(missing_ok=True)
            _, sync_changed = sync_stage(context.run_dir, context.meta)
            persist_if_changed(context.run_dir, context.meta, sync_changed)

        return result.returncode

    def _save_plan(self, context: RunContext) -> None:
        try:
            topic_spec = parse_topic_spec(read_json(context.paths.topic_spec))
            curriculum = parse_curriculum(read_json(context.paths.curriculum))
            plan = build_plan(topic_spec, curriculum)
        except (KeyError, TypeError, ValueError) as exc:
            raise LearningCompilerError(
                ErrorCode.INVALID_ARGUMENT,
                "Unable to build plan from current artifacts. Validate and regenerate inputs.",
                {"run_dir": str(context.run_dir)},
            ) from exc

        write_json(context.paths.plan, plan)
        self._save_meta_if_advanced(context, Stage.PLANNED, "plan generated")
        print(f"Saved plan: {context.paths.plan}")

    def _save_diff(self, context: RunContext) -> None:
        try:
            current = parse_curriculum(read_json(context.paths.curriculum))
            previous = (
                parse_curriculum(read_json(context.paths.previous_curriculum))
                if context.paths.previous_curriculum.exists()
                else parse_curriculum({"topic": current.topic, "nodes": []})
            )
            diff = compute_diff(previous, current)
        except (KeyError, TypeError, ValueError) as exc:
            raise LearningCompilerError(
                ErrorCode.INVALID_ARGUMENT,
                "Unable to compute diff from current artifacts. Validate and regenerate inputs.",
                {"run_dir": str(context.run_dir)},
            ) from exc

        write_json(context.paths.diff_report, diff)
        self._save_meta_if_advanced(context, Stage.ITERATED, "diff generated")
        print(f"Saved diff report: {context.paths.diff_report}")

    def _generate_curriculum(self, context: RunContext) -> None:
        if context.paths.curriculum.exists():
            context.paths.previous_curriculum.write_text(
                context.paths.curriculum.read_text(encoding="utf-8"),
                encoding="utf-8",
            )
        self._generator.generate_file(context.paths.topic_spec, context.paths.curriculum)
        self._save_meta_if_advanced(context, Stage.GENERATED, "agent generated curriculum")
        print(f"Generated curriculum with agent: {context.paths.curriculum}")

    def _apply_scope_options(self, context: RunContext, options: ScopeRunOptions) -> None:
        scope_path = resolve_scope_path(context.run_dir, options.scope_file)
        validate_scope_selection(options.mode, options.sections)
        synthesize_topic_spec_from_scope(
            context.paths,
            scope_path=scope_path,
            mode=options.mode,
            section_filters=options.sections,
        )
        self._save_meta_if_advanced(
            context,
            Stage.SPEC_READY,
            "topic spec synthesized from scope document",
            metadata={
                "scope_file": str(scope_path),
                "scope_mode": options.mode.value,
                "scope_sections": list(options.sections),
            },
        )
        print(f"Synthesized topic spec from scope file: {scope_path}")

    def run_validate(self, run_id: str) -> int:
        context = self._load_context(run_id)
        return self._validate(context)

    def run_plan(self, run_id: str) -> int:
        context = self._load_context(run_id)
        if self._validate(context) != 0:
            return 1
        self._save_plan(context)
        return 0

    def run_iterate(self, run_id: str) -> int:
        context = self._load_context(run_id)
        if not context.paths.curriculum.exists():
            print(f"Missing curriculum file: {context.paths.curriculum}", file=sys.stderr)
            return 1
        if self._validate(context) != 0:
            return 1
        if not plan_is_current(context.paths) or not validation_is_current(context.paths):
            self._save_plan(context)
        self._save_diff(context)
        return 0

    def run_full(self, run_id: str, options: ScopeRunOptions | None = None) -> int:
        context = self._load_context(run_id)
        if options is not None:
            self._apply_scope_options(context, options)
        elif context.meta.stage == Stage.INITIALIZED:
            raise StageConflictError(
                f"Topic spec not ready: {context.paths.topic_spec}",
                {"run_id": run_id, "stage": context.meta.stage.value},
            )

        self._generate_curriculum(context)
        if not context.paths.curriculum.exists():
            raise StageConflictError(
                f"Curriculum was not produced at expected path: {context.paths.curriculum}",
                {"run_id": run_id},
            )
        if self._validate(context) != 0:
            return 1
        self._save_plan(context)
        self._save_diff(context)
        print(f"Orchestration run completed: {run_id}")
        return 0
