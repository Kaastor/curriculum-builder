#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1

echo "== syntax check =="
python3 - <<'PY'
import ast
from pathlib import Path

for root in (Path("scripts"), Path("tests")):
    if not root.exists():
        continue
    for path in sorted(root.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
print("syntax-ok")
PY

echo "== curriculum validation =="
python3 scripts/validator.py data/curriculum.json

echo "== tests =="
python3 -m unittest discover -s tests -p 'test_*.py'

echo "\n✅ gate passed"
