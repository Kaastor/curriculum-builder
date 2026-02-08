"""Typed run metadata model and serialization helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from learning_compiler.orchestration.types import Stage


@dataclass(slots=True)
class RunMeta:
    run_id: str
    created_at_utc: str
    stage: Stage
    history: list[dict[str, Any]]
    extras: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "RunMeta":
        run_id = payload.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            raise ValueError("run_id must be a non-empty string")

        created_at_utc = payload.get("created_at_utc")
        if not isinstance(created_at_utc, str) or not created_at_utc.strip():
            raise ValueError("created_at_utc must be a non-empty string")

        stage_raw = payload.get("stage")
        try:
            stage = Stage(str(stage_raw))
        except ValueError as exc:
            raise ValueError(f"stage must be one of {[item.value for item in Stage]}") from exc

        history = payload.get("history")
        if not isinstance(history, list) or any(not isinstance(item, dict) for item in history):
            raise ValueError("history must be a list of objects")

        reserved = {"run_id", "created_at_utc", "stage", "history"}
        extras = {key: value for key, value in payload.items() if key not in reserved}
        return cls(
            run_id=run_id,
            created_at_utc=created_at_utc,
            stage=stage,
            history=list(history),
            extras=extras,
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "run_id": self.run_id,
            "created_at_utc": self.created_at_utc,
            "stage": self.stage.value,
            "history": self.history,
        }
        payload.update(self.extras)
        return payload
