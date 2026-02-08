"""Run event schema for orchestration history and traces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True, frozen=True)
class RunEvent:
    at_utc: str
    event_type: str
    stage: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "at_utc": self.at_utc,
            "event_type": self.event_type,
            "stage": self.stage,
            "message": self.message,
            "metadata": self.metadata,
        }


def stage_event(
    at_utc: str,
    stage: str,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> RunEvent:
    return RunEvent(
        at_utc=at_utc,
        event_type="stage_transition",
        stage=stage,
        message=message,
        metadata=metadata or {},
    )
