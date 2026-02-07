#!/usr/bin/env python3
"""CLI entrypoint for curriculum validation."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from learning_compiler.validator.core import validate


def parse_args() -> argparse.Namespace:
    default_path = Path(__file__).resolve().parent.parent / "data" / "curriculum.json"
    parser = argparse.ArgumentParser(description="Validate curriculum JSON")
    parser.add_argument(
        "curriculum_path",
        nargs="?",
        default=str(default_path),
        help="Path to curriculum JSON (default: data/curriculum.json)",
    )
    parser.add_argument(
        "--topic-spec",
        dest="topic_spec_path",
        help="Optional topic_spec.json path for topic-specific constraints",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    curriculum_path = Path(args.curriculum_path)
    topic_spec_path = Path(args.topic_spec_path) if args.topic_spec_path else None

    result = validate(curriculum_path, topic_spec_path)
    print(result.report())
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
