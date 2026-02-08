#!/usr/bin/env python3
"""CLI entrypoint for orchestration commands."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from learning_compiler.orchestration.cli import main
from learning_compiler.errors import LearningCompilerError


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LearningCompilerError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(exc.exit_code()) from exc
