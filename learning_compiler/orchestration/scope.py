"""Helpers for scope-document ingestion in orchestration commands."""

from __future__ import annotations

import argparse
from pathlib import Path

from learning_compiler.agent import ScopeIngestMode, compile_scope_document
from learning_compiler.config import load_config
from learning_compiler.errors import ErrorCode, LearningCompilerError
from learning_compiler.orchestration.fs import resolve_within, write_json
from learning_compiler.orchestration.types import RunPaths


def scope_file_from_args(args: argparse.Namespace) -> str | None:
    value = getattr(args, "scope_file", None)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-file must be a non-empty path when provided.",
        )
    return value.strip()


def scope_sections_from_args(args: argparse.Namespace) -> tuple[str, ...]:
    raw = getattr(args, "scope_section", [])
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-section must be provided as repeatable strings.",
        )
    sections = [str(value).strip() for value in raw if str(value).strip()]
    return tuple(sections)


def scope_mode_from_args(args: argparse.Namespace) -> ScopeIngestMode:
    raw = getattr(args, "scope_mode", ScopeIngestMode.FULL.value)
    if not isinstance(raw, str):
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-mode must be a string.",
        )
    normalized = raw.strip().lower()
    try:
        return ScopeIngestMode(normalized)
    except ValueError as exc:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-mode must be one of: full, section, seed-list.",
            {"scope_mode": raw},
        ) from exc


def validate_scope_selection(mode: ScopeIngestMode, sections: tuple[str, ...]) -> None:
    if mode == ScopeIngestMode.SECTION and not sections:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-mode section requires at least one --scope-section value.",
        )


def resolve_scope_path(run_dir: Path, scope_file: str) -> Path:
    candidate = Path(scope_file).expanduser()
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not candidate.exists() or not candidate.is_file():
        raise LearningCompilerError(
            ErrorCode.NOT_FOUND,
            f"Scope file not found: {scope_file}",
            {"scope_file": str(candidate)},
        )

    config = load_config()
    allowed_roots = (config.repo_root.resolve(), config.runs_dir.resolve(), run_dir.resolve())
    for root in allowed_roots:
        try:
            resolve_within(root, candidate)
            return candidate
        except LearningCompilerError:
            continue

    raise LearningCompilerError(
        ErrorCode.INVALID_ARGUMENT,
        "Scope file must be inside the repository, runs directory, or current run directory.",
        {"scope_file": str(candidate)},
    )


def synthesize_topic_spec_from_scope(
    paths: RunPaths,
    *,
    scope_path: Path,
    mode: ScopeIngestMode,
    section_filters: tuple[str, ...],
) -> None:
    compiled = compile_scope_document(
        scope_path,
        mode=mode,
        section_filters=section_filters,
    )
    write_json(paths.topic_spec, compiled.topic_spec)
    write_json(paths.scope_concepts, compiled.scope_concepts)
    write_json(paths.scope_dag, compiled.scope_dag)
