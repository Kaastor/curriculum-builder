"""Shared helpers for orchestration command handlers."""

from __future__ import annotations

import argparse
import re

from learning_compiler.errors import ErrorCode, LearningCompilerError


RUN_ID_PATTERN = re.compile(r"^\d{8}-\d{6}(?:-[a-z0-9-]+)?$")


def run_id_from_args(args: argparse.Namespace) -> str:
    value = getattr(args, "run_id", None)
    if not isinstance(value, str) or not value:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "run_id is required",
        )
    if not RUN_ID_PATTERN.fullmatch(value):
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "Invalid run_id format. Expected YYYYMMDD-HHMMSS[-slug].",
            {"run_id": value},
        )
    return value
