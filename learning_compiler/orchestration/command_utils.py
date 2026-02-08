"""Shared helpers for orchestration command handlers."""

from __future__ import annotations

import argparse

from learning_compiler.errors import ErrorCode, LearningCompilerError


def run_id_from_args(args: argparse.Namespace) -> str:
    value = getattr(args, "run_id", None)
    if not isinstance(value, str) or not value:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "run_id is required",
        )
    return value
