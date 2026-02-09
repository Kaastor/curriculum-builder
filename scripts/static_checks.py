#!/usr/bin/env python3
"""Repository static checks enforcing architecture boundaries."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DISALLOWED_IMPORT_REDIRECTS: dict[str, str] = {
    "learning_compiler.agent.llm_client": "learning_compiler.agent.llm.llm_client",
}


def _module_name(path: Path) -> str:
    return ".".join(path.with_suffix("").relative_to(ROOT).parts)


def _imported_modules(tree: ast.AST) -> list[str]:
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            modules.append(node.module)
    return modules


def _check_no_wildcard_imports(path: Path, tree: ast.AST, errors: list[str]) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" for alias in node.names):
                errors.append(f"{path}: wildcard import is not allowed")


def _check_boundaries(module: str, imports: list[str], errors: list[str]) -> None:
    if module.startswith("learning_compiler.agent"):
        if any(item.startswith("learning_compiler.orchestration") for item in imports):
            errors.append(f"{module}: agent must not depend on orchestration")

    if module.startswith("learning_compiler.validator"):
        if any(item.startswith("learning_compiler.orchestration") for item in imports):
            errors.append(f"{module}: validator must not depend on orchestration")
        if any(item.startswith("learning_compiler.agent") for item in imports):
            errors.append(f"{module}: validator must not depend on agent")

    if module.startswith("learning_compiler.orchestration"):
        forbidden = [
            item
            for item in imports
            if item.startswith("learning_compiler.agent.")
            and item not in {"learning_compiler.agent", "learning_compiler.agent.contracts"}
        ]
        if forbidden:
            errors.append(
                f"{module}: orchestration imports agent internals {sorted(set(forbidden))}"
            )


def _check_forbidden_imports(module: str, imports: list[str], errors: list[str]) -> None:
    for imported in imports:
        replacement = DISALLOWED_IMPORT_REDIRECTS.get(imported)
        if replacement is None:
            continue
        errors.append(
            f"{module}: import '{imported}' is disallowed; use '{replacement}'"
        )


def run() -> int:
    errors: list[str] = []
    for path in sorted((ROOT / "learning_compiler").rglob("*.py")):
        if "__pycache__" in path.parts:
            continue

        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        imports = _imported_modules(tree)
        module = _module_name(path)

        _check_no_wildcard_imports(path, tree, errors)
        _check_boundaries(module, imports, errors)
        _check_forbidden_imports(module, imports, errors)

    if errors:
        print("static-checks: FAIL")
        for item in errors:
            print(f"- {item}")
        return 1

    print("static-checks: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
