"""Optimization trace model for explainable curriculum generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from learning_compiler.agent.quality.actions import RepairAction


@dataclass(slots=True, frozen=True)
class IterationTrace:
    iteration: int
    model_policy: dict[str, str | int | float]
    pedagogy_summary: dict[str, Any]
    score_summary: dict[str, Any]
    learner_path_diagnostics: tuple[dict[str, Any], ...]
    selected_actions: tuple[RepairAction, ...]
    post_score_summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "iteration": self.iteration,
            "model_policy": self.model_policy,
            "pedagogy_summary": self.pedagogy_summary,
            "score_summary": self.score_summary,
            "learner_path_diagnostics": list(self.learner_path_diagnostics),
            "selected_actions": [action.to_dict() for action in self.selected_actions],
            "post_score_summary": self.post_score_summary,
        }


@dataclass(slots=True, frozen=True)
class OptimizationTrace:
    schema_version: str
    stop_reason: str
    iterations: tuple[IterationTrace, ...]
    best_score: int
    accepted: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "stop_reason": self.stop_reason,
            "best_score": self.best_score,
            "accepted": self.accepted,
            "iterations": [item.to_dict() for item in self.iterations],
        }
