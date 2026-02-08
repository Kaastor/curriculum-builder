#!/usr/bin/env python3
"""CLI entrypoint for curriculum validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from learning_compiler.orchestration.fs import latest_curriculum_path
from learning_compiler.errors import ErrorCode, LearningCompilerError
from learning_compiler.validator.core import validate


def parse_args() -> argparse.Namespace:
    default_path = latest_curriculum_path()
    parser = argparse.ArgumentParser(description="Validate curriculum JSON")
    parser.add_argument(
        "curriculum_path",
        nargs="?",
        default=str(default_path) if default_path else None,
        help=(
            "Path to curriculum JSON "
            "(default: latest runs/<run_id>/outputs/curriculum/curriculum.json)"
        ),
    )
    parser.add_argument(
        "--topic-spec",
        dest="topic_spec_path",
        help="Optional topic_spec.json path for topic-specific constraints",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.curriculum_path is None:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "No curriculum path provided and no generated run curriculum found. "
            "Run `python3.11 scripts/orchestration.py run <run_id>` first "
            "or pass an explicit curriculum path.",
        )

    curriculum_path = Path(args.curriculum_path)
    topic_spec_path = Path(args.topic_spec_path) if args.topic_spec_path else None

    result = validate(curriculum_path, topic_spec_path)
    print(result.report())
    return 0 if result.success else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LearningCompilerError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(exc.exit_code()) from exc
