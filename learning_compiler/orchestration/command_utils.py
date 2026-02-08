"""Shared helpers for orchestration command handlers."""

from __future__ import annotations

import argparse


def run_id_from_args(args: argparse.Namespace) -> str:
    value = getattr(args, "run_id", None)
    if not isinstance(value, str) or not value:
        raise SystemExit("run_id is required")
    return value
