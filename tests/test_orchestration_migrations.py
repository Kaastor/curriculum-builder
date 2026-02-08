from __future__ import annotations

import unittest

from learning_compiler.orchestration.migrations import RUN_META_SCHEMA_VERSION, migrate_run_meta


class OrchestrationMigrationTests(unittest.TestCase):
    def test_legacy_stage_and_history_are_migrated(self) -> None:
        legacy = {
            "run_id": "20260101-000000-legacy",
            "created_at_utc": "2026-01-01T00:00:00Z",
            "stage": "map_generated",
            "history": [
                {
                    "at_utc": "2026-01-01T00:00:00Z",
                    "stage": "initialized",
                    "reason": "run initialized",
                }
            ],
        }

        migrated, changed = migrate_run_meta(legacy)

        self.assertTrue(changed)
        self.assertEqual("generated", migrated["stage"])
        self.assertEqual(RUN_META_SCHEMA_VERSION, migrated["schema_version"])
        self.assertEqual("stage_transition", migrated["history"][0]["event_type"])
        self.assertEqual("run initialized", migrated["history"][0]["message"])

    def test_missing_history_is_reconstructed(self) -> None:
        payload = {
            "run_id": "20260101-000001",
            "created_at_utc": "2026-01-01T00:00:01Z",
            "stage": "validated",
        }

        migrated, changed = migrate_run_meta(payload)

        self.assertTrue(changed)
        self.assertEqual(1, len(migrated["history"]))
        self.assertEqual("validated", migrated["history"][0]["stage"])


if __name__ == "__main__":
    unittest.main()
