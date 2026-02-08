from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
