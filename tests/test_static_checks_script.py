from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "static_checks.py"


class StaticChecksScriptTests(unittest.TestCase):
    def test_static_checks_script_passes(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode, msg=proc.stdout + "\n" + proc.stderr)

    def test_forbidden_imports_check_flags_disallowed_paths(self) -> None:
        spec = importlib.util.spec_from_file_location("static_checks_module", SCRIPT)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)

        for bad_path in ("learning_compiler.agent.llm_client", "learning_compiler.agent.llm.llm_client"):
            errors: list[str] = []
            module._check_forbidden_imports(  # type: ignore[attr-defined]
                "learning_compiler.agent.generator",
                [bad_path],
                errors,
            )

            self.assertEqual(1, len(errors))
            self.assertIn("is disallowed", errors[0])
            self.assertIn("learning_compiler.agent.llm.client", errors[0])


if __name__ == "__main__":
    unittest.main()
