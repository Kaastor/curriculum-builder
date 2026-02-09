"""Typed repair actions for iterative DAG optimization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RepairActionType(str, Enum):
    SPLIT_NODE = "split_node"
    MERGE_NODES = "merge_nodes"
    REWRITE_NODE = "rewrite_node"
    REWIRE_PREREQS = "rewire_prereqs"
    RETARGET_RESOURCES = "retarget_resources"
    RETIME_NODE = "retime_node"
    REORDER_NODES = "reorder_nodes"


class ActionSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True, frozen=True)
class RepairAction:
    action_type: RepairActionType
    reason: str
    severity: ActionSeverity
    node_id: str | None = None
    node_a: str | None = None
    node_b: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload: dict[str, str] = {
            "action_type": self.action_type.value,
            "reason": self.reason,
            "severity": self.severity.value,
        }
        if self.node_id is not None:
            payload["node_id"] = self.node_id
        if self.node_a is not None:
            payload["node_a"] = self.node_a
        if self.node_b is not None:
            payload["node_b"] = self.node_b
        return payload


SEVERITY_RANK = {
    ActionSeverity.CRITICAL: 4,
    ActionSeverity.HIGH: 3,
    ActionSeverity.MEDIUM: 2,
    ActionSeverity.LOW: 1,
}
