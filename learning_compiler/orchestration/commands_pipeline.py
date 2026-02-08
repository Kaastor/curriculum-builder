"""Thin CLI adapters for pipeline lifecycle commands."""

from __future__ import annotations

import argparse

from learning_compiler.orchestration.command_utils import run_id_from_args
from learning_compiler.orchestration.pipeline import RunPipeline, ScopeRunOptions
from learning_compiler.orchestration.scope import (
    scope_file_from_args,
    scope_mode_from_args,
    scope_policy_from_args,
    scope_sections_from_args,
)


def _pipeline() -> RunPipeline:
    return RunPipeline()


def cmd_validate(args: argparse.Namespace) -> int:
    return _pipeline().run_validate(run_id_from_args(args))


def cmd_plan(args: argparse.Namespace) -> int:
    return _pipeline().run_plan(run_id_from_args(args))


def cmd_iterate(args: argparse.Namespace) -> int:
    return _pipeline().run_iterate(run_id_from_args(args))


def _scope_options_from_args(args: argparse.Namespace) -> ScopeRunOptions | None:
    scope_file = scope_file_from_args(args)
    if scope_file is None:
        return None
    return ScopeRunOptions(
        scope_file=scope_file,
        mode=scope_mode_from_args(args),
        sections=scope_sections_from_args(args),
        policy=scope_policy_from_args(args),
    )


def cmd_run(args: argparse.Namespace) -> int:
    return _pipeline().run_full(run_id_from_args(args), _scope_options_from_args(args))

