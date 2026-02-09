"""Argument parsing helpers for scope-driven orchestration options."""

from __future__ import annotations

import argparse

from learning_compiler.agent import ScopeIngestMode
from learning_compiler.errors import ErrorCode, LearningCompilerError


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
