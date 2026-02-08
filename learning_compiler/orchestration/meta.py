"""Typed run metadata model and serialization helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from learning_compiler.orchestration.migrations import RUN_META_SCHEMA_VERSION
from learning_compiler.orchestration.types import Stage, stage_from


@dataclass(slots=True)
class RunMeta:
    run_id: str
    created_at_utc: str
    stage: Stage
    history: list[dict[str, Any]]
    schema_version: int = RUN_META_SCHEMA_VERSION
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunMeta":
        reserved = {"run_id", "created_at_utc", "stage", "history", "schema_version"}
        extras = {key: value for key, value in payload.items() if key not in reserved}
        history = payload.get("history")
        return cls(
            run_id=str(payload.get("run_id", "")),
            created_at_utc=str(payload.get("created_at_utc", "")),
            stage=stage_from(payload.get("stage", Stage.INITIALIZED.value)),
            history=list(history) if isinstance(history, list) else [],
            schema_version=int(payload.get("schema_version", RUN_META_SCHEMA_VERSION)),
            extras=extras,
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "created_at_utc": self.created_at_utc,
            "stage": self.stage.value,
            "history": self.history,
        }
        payload.update(self.extras)
        return payload
