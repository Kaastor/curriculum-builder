"""Shared types for deterministic quality evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class QualityDiagnostic:
    rule_id: str
    severity: str
    message: str
    node_id: str | None = None
    hard_fail: bool = False

    def to_dict(self) -> dict[str, str | bool]:
        payload: dict[str, str | bool] = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "hard_fail": self.hard_fail,
        }
        if self.node_id is not None:
            payload["node_id"] = self.node_id
        return payload


@dataclass(slots=True, frozen=True)
class QualityReport:
    dimensions: dict[str, int]
    total_score: int
    hard_fail_count: int
    diagnostics: tuple[QualityDiagnostic, ...]

    @property
    def passed(self) -> bool:
        return self.hard_fail_count == 0

    def score_summary(self) -> dict[str, Any]:
        return {
            "dimensions": self.dimensions,
            "total_score": self.total_score,
            "hard_fail_count": self.hard_fail_count,
            "diagnostic_count": len(self.diagnostics),
        }
