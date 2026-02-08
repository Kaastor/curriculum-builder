from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


class ArchitectureBoundariesTests(unittest.TestCase):
    def test_agent_does_not_import_orchestration(self) -> None:
        for path in sorted((ROOT / "learning_compiler" / "agent").glob("*.py")):
            imports = imported_modules(path)
            self.assertFalse(
                any(module.startswith("learning_compiler.orchestration") for module in imports),
                msg=f"{path} imports orchestration",
            )

    def test_validator_does_not_import_agent_or_orchestration(self) -> None:
        for path in sorted((ROOT / "learning_compiler" / "validator").glob("*.py")):
            imports = imported_modules(path)
            self.assertFalse(
                any(module.startswith("learning_compiler.agent") for module in imports),
                msg=f"{path} imports agent",
            )
            self.assertFalse(
                any(module.startswith("learning_compiler.orchestration") for module in imports),
                msg=f"{path} imports orchestration",
            )


if __name__ == "__main__":
    unittest.main()
