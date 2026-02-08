"""CLI parser and dispatch for orchestration commands."""

from __future__ import annotations

import argparse
from typing import Callable, cast

from learning_compiler.orchestration.commands_basic import (
    cmd_archive,
    cmd_init,
    cmd_list,
    cmd_next,
    cmd_status,
)
from learning_compiler.orchestration.commands_pipeline import (
    cmd_iterate,
    cmd_plan,
    cmd_run,
    cmd_validate,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Orchestration run manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize a new orchestration run")
    p_init.add_argument("name", nargs="?", help="Optional run name")
    p_init.set_defaults(func=cmd_init)

    p_status = sub.add_parser("status", help="Show run status")
    p_status.add_argument("run_id")
    p_status.set_defaults(func=cmd_status)

    p_next = sub.add_parser("next", help="Show next action for run")
    p_next.add_argument("run_id")
    p_next.set_defaults(func=cmd_next)

    p_validate = sub.add_parser("validate", help="Run validation for run")
    p_validate.add_argument("run_id")
    p_validate.set_defaults(func=cmd_validate)

    p_plan = sub.add_parser("plan", help="Generate plan for run")
    p_plan.add_argument("run_id")
    p_plan.set_defaults(func=cmd_plan)

    p_iterate = sub.add_parser("iterate", help="Generate diff report for run")
    p_iterate.add_argument("run_id")
    p_iterate.set_defaults(func=cmd_iterate)

    p_run = sub.add_parser("run", help="Execute generate -> validate -> plan -> iterate")
    p_run.add_argument("run_id")
    p_run.set_defaults(func=cmd_run)

    p_archive = sub.add_parser("archive", help="Archive run folder")
    p_archive.add_argument("run_id")
    p_archive.set_defaults(func=cmd_archive)

    p_list = sub.add_parser("list", help="List runs")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = cast(Callable[[argparse.Namespace], int], args.func)
    return handler(args)
