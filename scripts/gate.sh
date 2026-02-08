#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "error: required Python interpreter not found: $PYTHON_BIN" >&2
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info < (3, 11):
    raise SystemExit("error: Python 3.11+ is required")
PY

echo "== syntax check =="
"$PYTHON_BIN" - <<'PY'
import ast
from pathlib import Path

for root in (Path("scripts"), Path("learning_compiler"), Path("tests")):
    if not root.exists():
        continue
    for path in sorted(root.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
print("syntax-ok")
PY

echo "== static checks =="
"$PYTHON_BIN" scripts/static_checks.py

echo "== curriculum validation =="
"$PYTHON_BIN" scripts/validator.py tests/fixtures/curriculum.json

echo "== tests =="
"$PYTHON_BIN" -m unittest discover -s tests -p 'test_*.py'

echo "== coverage check =="
"$PYTHON_BIN" scripts/coverage_check.py

echo "\n✅ gate passed"
