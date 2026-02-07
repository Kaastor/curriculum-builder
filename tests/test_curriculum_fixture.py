import json
import unittest
from pathlib import Path

from scripts.validator import validate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CURRICULUM = ROOT / "data" / "curriculum.json"
MOCK_CURRICULUM = ROOT / "data" / "reliability" / "curriculum.mock.json"


class CurriculumFixtureTests(unittest.TestCase):
    def test_default_curriculum_passes_validator(self):
        result = validate(DEFAULT_CURRICULUM)
        self.assertTrue(
            result.success,
            msg="Default curriculum failed validator:\n" + "\n".join(result.failed),
        )

    def test_mock_curriculum_matches_default(self):
        default_data = json.loads(DEFAULT_CURRICULUM.read_text())
        mock_data = json.loads(MOCK_CURRICULUM.read_text())

        self.assertEqual(default_data["nodes"], mock_data["nodes"])
        self.assertEqual(default_data["edges"], mock_data["edges"])
        self.assertEqual(default_data["coverage_map"], mock_data["coverage_map"])

    def test_app_assets_exist(self):
        app_dir = ROOT / "app"
        expected = ["index.html", "styles.css", "main.js"]
        for name in expected:
            self.assertTrue((app_dir / name).exists(), msg=f"Missing app asset: {name}")


if __name__ == "__main__":
    unittest.main()
