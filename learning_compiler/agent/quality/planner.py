"""Compile diagnostics into stable ordered repair actions."""

from __future__ import annotations

from dataclasses import dataclass

from learning_compiler.agent.quality.pedagogy_critic import CriticDiagnostic, PedagogyCritique
from learning_compiler.agent.quality.types import QualityDiagnostic, QualityReport
from learning_compiler.agent.quality.actions import (
    ActionSeverity,
    RepairAction,
    RepairActionType,
    SEVERITY_RANK,
)


_RULE_ACTIONS = {
    "atomicity.compound_capability": RepairActionType.REWRITE_NODE,
    "atomicity.threshold": RepairActionType.REWRITE_NODE,
    "progression.all_roots": RepairActionType.REWIRE_PREREQS,
    "progression.depth_too_shallow": RepairActionType.REWIRE_PREREQS,
    "resource.weak_relevance": RepairActionType.RETARGET_RESOURCES,
    "resource.repetitive_anchor": RepairActionType.RETARGET_RESOURCES,
    "mastery.non_actionable_task": RepairActionType.REWRITE_NODE,
    "mastery.non_measurable_criteria": RepairActionType.REWRITE_NODE,
    "effort.flat_distribution": RepairActionType.RETIME_NODE,
    "effort.outlier": RepairActionType.RETIME_NODE,
    "redundancy.title_repetition": RepairActionType.REWRITE_NODE,
    "learner.hidden_prerequisite": RepairActionType.REWIRE_PREREQS,
    "learner.concept_jump": RepairActionType.REWRITE_NODE,
    "learner.workload_jump": RepairActionType.RETIME_NODE,
    "learner.prerequisite_overload": RepairActionType.REWIRE_PREREQS,
}


def _to_action_severity(value: str) -> ActionSeverity:
    if value == "critical":
        return ActionSeverity.CRITICAL
    if value == "high":
        return ActionSeverity.HIGH
    if value == "medium":
        return ActionSeverity.MEDIUM
    return ActionSeverity.LOW


@dataclass(slots=True, frozen=True)
class RepairPlanner:
    max_actions_per_iteration: int

    def plan(self, report: QualityReport, pedagogy: PedagogyCritique) -> tuple[RepairAction, ...]:
        candidates: list[RepairAction] = []
        for item in report.diagnostics:
            action = self._action_from_quality(item)
            if action is not None:
                candidates.append(action)
        for item in pedagogy.diagnostics:
            action = self._action_from_critic(item)
            if action is not None:
                candidates.append(action)

        deduped: dict[tuple[RepairActionType, str | None], RepairAction] = {}
        for action in candidates:
            key = (action.action_type, action.node_id)
            current = deduped.get(key)
            if current is None or SEVERITY_RANK[action.severity] > SEVERITY_RANK[current.severity]:
                deduped[key] = action

        ordered = sorted(
            deduped.values(),
            key=lambda item: (
                -SEVERITY_RANK[item.severity],
                item.node_id or "",
                item.action_type.value,
            ),
        )
        selected = ordered[: self.max_actions_per_iteration]

        if not selected and report.total_score < 85:
            selected = [
                RepairAction(
                    action_type=RepairActionType.REORDER_NODES,
                    reason="No targeted actions available; normalize progression order.",
                    severity=ActionSeverity.LOW,
                )
            ]
        return tuple(selected)

    def _action_from_quality(self, diagnostic: QualityDiagnostic) -> RepairAction | None:
        action_type = _RULE_ACTIONS.get(diagnostic.rule_id)
        if action_type is None:
            return None
        return RepairAction(
            action_type=action_type,
            reason=diagnostic.message,
            severity=_to_action_severity(diagnostic.severity),
            node_id=diagnostic.node_id,
        )

    def _action_from_critic(self, diagnostic: CriticDiagnostic) -> RepairAction | None:
        action_type = _RULE_ACTIONS.get(diagnostic.rule_id)
        if action_type is None:
            return None
        return RepairAction(
            action_type=action_type,
            reason=diagnostic.message,
            severity=_to_action_severity(diagnostic.severity),
            node_id=diagnostic.node_id,
        )
