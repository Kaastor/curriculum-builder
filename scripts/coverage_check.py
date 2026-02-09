#!/usr/bin/env python3
"""Approximate statement coverage check using stdlib trace."""

from __future__ import annotations

import ast
import io
import os
import sys
import trace
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MIN_COVERAGE = float(os.environ.get("COVERAGE_MIN", "50"))


def _statement_lines(path: Path) -> set[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    stmt_lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.stmt):
            continue
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, str):
                # Ignore docstring-style string literals.
                continue
        lineno = getattr(node, "lineno", None)
        if lineno is not None:
            stmt_lines.add(int(lineno))
    return stmt_lines


def _target_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted((ROOT / "learning_compiler").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if path.name == "__init__.py":
            continue
        files.append(path.resolve())
    return files


def run() -> int:
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")

    tracer = trace.Trace(count=True, trace=False)
    buffer = io.StringIO()
    runner = unittest.TextTestRunner(stream=buffer, verbosity=0)
    result = tracer.runfunc(runner.run, suite)
    if not result.wasSuccessful():
        print(buffer.getvalue())
        print("coverage-check: tests failed")
        return 1

    counts = tracer.results().counts

    target_files = _target_files()
    total_statements = 0
    covered_statements = 0

    for path in target_files:
        statement_lines = _statement_lines(path)
        if not statement_lines:
            continue

        total_statements += len(statement_lines)
        for line in statement_lines:
            if counts.get((str(path), line), 0) > 0:
                covered_statements += 1

    if total_statements == 0:
        print("coverage-check: no target statements discovered")
        return 1

    percent = round((covered_statements / total_statements) * 100.0, 2)
    print(
        "coverage-check: "
        f"{covered_statements}/{total_statements} statements covered ({percent}%)"
    )

    if percent < MIN_COVERAGE:
        print(
            "coverage-check: FAIL "
            f"(required >= {MIN_COVERAGE}%, got {percent}%)"
        )
        return 1

    print(f"coverage-check: ok (threshold {MIN_COVERAGE}%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
