from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from learning_compiler import AgentAPI, OrchestrationAPI, ValidatorAPI
from learning_compiler.config import reset_config_cache


class PublicApiTests(unittest.TestCase):
    def test_public_api_objects_construct(self) -> None:
        self.assertIsNotNone(AgentAPI())
        self.assertIsNotNone(OrchestrationAPI())
        self.assertIsNotNone(ValidatorAPI())

    def test_orchestration_api_cli_list(self) -> None:
        api = OrchestrationAPI()
        with tempfile.TemporaryDirectory() as tmp_dir:
            previous = os.environ.get("ORCHESTRATION_BASE_DIR")
            os.environ["ORCHESTRATION_BASE_DIR"] = tmp_dir
            reset_config_cache()
            try:
                code = api.run_cli(["list"])
            finally:
                if previous is None:
                    os.environ.pop("ORCHESTRATION_BASE_DIR", None)
                else:
                    os.environ["ORCHESTRATION_BASE_DIR"] = previous
                reset_config_cache()
            self.assertEqual(0, code)

    def test_validator_api_returns_result(self) -> None:
        validator = ValidatorAPI()
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "curriculum.json"
            path.write_text('{"topic":"x","nodes":[]}', encoding="utf-8")
            result = validator.validate(path)
            self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main()
