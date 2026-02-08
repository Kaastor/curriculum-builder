"""Backward-compatible migration helpers for run metadata."""

from __future__ import annotations

from typing import Any

from learning_compiler.orchestration.events import stage_event
from learning_compiler.orchestration.types import Stage, stage_from


RUN_META_SCHEMA_VERSION = 2


def _migrate_history(history: Any, created_at_utc: str, current_stage: str) -> tuple[list[dict[str, Any]], bool]:
    if not isinstance(history, list):
        initial = stage_event(
            at_utc=created_at_utc,
            stage=current_stage,
            message="history initialized from migration",
        ).to_dict()
        return [initial], True

    changed = False
    migrated: list[dict[str, Any]] = []
    for item in history:
        if not isinstance(item, dict):
            changed = True
            continue

        at_utc = str(item.get("at_utc", created_at_utc))
        stage = stage_from(item.get("stage", current_stage)).value
        reason = item.get("reason")
        message = str(item.get("message", "")).strip()
        if not message and isinstance(reason, str):
            message = reason
        if not message:
            message = "stage metadata migrated"

        metadata = item.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
            changed = True

        if "reason" in item:
            changed = True

        event_type = item.get("event_type")
        if event_type != "stage_transition":
            changed = True

        migrated.append(
            stage_event(
                at_utc=at_utc,
                stage=stage,
                message=message,
                metadata=metadata,
            ).to_dict()
        )

    if not migrated:
        migrated.append(
            stage_event(
                at_utc=created_at_utc,
                stage=current_stage,
                message="history restored during migration",
            ).to_dict()
        )
        changed = True

    return migrated, changed


def migrate_run_meta(meta: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    changed = False
    migrated = dict(meta)

    stage = stage_from(migrated.get("stage", Stage.INITIALIZED.value)).value
    if migrated.get("stage") != stage:
        migrated["stage"] = stage
        changed = True

    created_at_utc = str(migrated.get("created_at_utc", "")).strip()
    if not created_at_utc:
        created_at_utc = "1970-01-01T00:00:00Z"
        migrated["created_at_utc"] = created_at_utc
        changed = True

    history, history_changed = _migrate_history(
        migrated.get("history"),
        created_at_utc,
        stage,
    )
    if history_changed:
        changed = True
    migrated["history"] = history

    if migrated.get("schema_version") != RUN_META_SCHEMA_VERSION:
        migrated["schema_version"] = RUN_META_SCHEMA_VERSION
        changed = True

    return migrated, changed
