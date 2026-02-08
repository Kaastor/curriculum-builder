from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from learning_compiler.orchestration.fs import latest_curriculum_path, list_run_dirs, required_paths


class OrchestrationFsTests(unittest.TestCase):
    def test_latest_curriculum_path_returns_none_without_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            self.assertEqual([], list_run_dirs(base_dir))
            self.assertIsNone(latest_curriculum_path(base_dir))

    def test_latest_curriculum_path_uses_newest_run_with_curriculum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            base_dir = Path(tmp_dir)
            (base_dir / "templates").mkdir(parents=True)

            older_run = base_dir / "20260101-100000-old"
            older_run.mkdir(parents=True)
            (older_run / "run.json").write_text('{"run_id":"older"}\n', encoding="utf-8")
            older_curriculum = required_paths(older_run).curriculum
            older_curriculum.parent.mkdir(parents=True)
            older_curriculum.write_text('{"topic":"x","nodes":[{"id":"N1"}]}\n', encoding="utf-8")

            newest_run = base_dir / "20260102-100000-new"
            newest_run.mkdir(parents=True)
            (newest_run / "run.json").write_text('{"run_id":"newest"}\n', encoding="utf-8")

            run_dirs = list_run_dirs(base_dir)
            self.assertEqual([older_run, newest_run], run_dirs)
            self.assertEqual(older_curriculum, latest_curriculum_path(base_dir))


if __name__ == "__main__":
    unittest.main()
