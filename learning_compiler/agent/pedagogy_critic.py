"""Pedagogical critic for iterative curriculum optimization."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from learning_compiler.agent.llm_client import InternalLLMClient, LLMClient, LLMRequest
from learning_compiler.agent.model_policy import ModelPolicy
from learning_compiler.domain import TopicSpec


@dataclass(slots=True, frozen=True)
class CriticDiagnostic:
    rule_id: str
    severity: str
    message: str
    node_id: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload: dict[str, str] = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
        }
        if self.node_id is not None:
            payload["node_id"] = self.node_id
        return payload


@dataclass(slots=True, frozen=True)
class PedagogyCritique:
    score: int
    min_quality_met: bool
    summary: str
    diagnostics: tuple[CriticDiagnostic, ...]

    def summary_dict(self) -> dict[str, Any]:
        high_count = len([item for item in self.diagnostics if item.severity in {"high", "critical"}])
        return {
            "score": self.score,
            "min_quality_met": self.min_quality_met,
            "summary": self.summary,
            "diagnostic_count": len(self.diagnostics),
            "high_severity_count": high_count,
        }


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{4,}", text.lower()))


def _node_map(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        str(node.get("id")): node
        for node in nodes
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }


def _max_prereq_estimate(node: dict[str, Any], node_index: dict[str, dict[str, Any]]) -> int:
    values: list[int] = []
    for prereq in node.get("prerequisites", []):
        entry = node_index.get(str(prereq))
        if not isinstance(entry, dict):
            continue
        estimate = entry.get("estimate_minutes")
        if isinstance(estimate, int):
            values.append(estimate)
    return max(values) if values else 0


class LLMCritic:
    """Deterministic critic with LLM-like stage interface."""

    def __init__(self, client: LLMClient | None = None) -> None:
        self._client = client or InternalLLMClient()

    def critique(
        self,
        curriculum: dict[str, Any],
        topic_spec: TopicSpec,
        policy: ModelPolicy,
    ) -> PedagogyCritique:
        nodes_raw = curriculum.get("nodes", [])
        nodes = [item for item in nodes_raw if isinstance(item, dict)]
        index = _node_map(nodes)
        diagnostics: list[CriticDiagnostic] = []

        for node in nodes:
            node_id = str(node.get("id", ""))
            title_tokens = _tokens(str(node.get("title", "")))
            cap_tokens = _tokens(str(node.get("capability", "")))
            prereqs = tuple(str(item) for item in node.get("prerequisites", []))

            if not prereqs and (
                "integrate" in cap_tokens or "validate" in cap_tokens or "integration" in title_tokens
            ):
                diagnostics.append(
                    CriticDiagnostic(
                        rule_id="learner.hidden_prerequisite",
                        severity="high",
                        node_id=node_id,
                        message="Node appears advanced but has no prerequisites.",
                    )
                )

            if len(prereqs) >= 3:
                diagnostics.append(
                    CriticDiagnostic(
                        rule_id="learner.prerequisite_overload",
                        severity="medium",
                        node_id=node_id,
                        message="Too many prerequisites may increase novice confusion.",
                    )
                )

            if prereqs:
                overlap = 0
                for prereq in prereqs:
                    prereq_node = index.get(prereq)
                    if prereq_node is None:
                        continue
                    prereq_tokens = _tokens(str(prereq_node.get("title", ""))) | _tokens(
                        str(prereq_node.get("capability", ""))
                    )
                    if title_tokens.intersection(prereq_tokens):
                        overlap += 1
                if overlap == 0:
                    diagnostics.append(
                        CriticDiagnostic(
                            rule_id="learner.concept_jump",
                            severity="medium",
                            node_id=node_id,
                            message="Weak lexical bridge with prerequisites suggests a concept jump.",
                        )
                    )

            estimate = node.get("estimate_minutes")
            if isinstance(estimate, int):
                prereq_peak = _max_prereq_estimate(node, index)
                if prereq_peak > 0 and estimate > int(prereq_peak * 2.2):
                    diagnostics.append(
                        CriticDiagnostic(
                            rule_id="learner.workload_jump",
                            severity="medium",
                            node_id=node_id,
                            message="Workload jump versus prerequisites may be too abrupt.",
                        )
                    )

        # Track a synthetic client call for policy + trace completeness.
        self._client.run_json(
            LLMRequest(
                stage="pedagogy_critic",
                schema_name="pedagogy_critique_v1",
                payload={
                    "goal": topic_spec.goal,
                    "node_count": len(nodes),
                    "diagnostic_count": len(diagnostics),
                },
            ),
            policy,
        )

        high = len([item for item in diagnostics if item.severity in {"high", "critical"}])
        medium = len([item for item in diagnostics if item.severity == "medium"])
        low = len([item for item in diagnostics if item.severity == "low"])
        score = max(0, 100 - (high * 18) - (medium * 9) - (low * 4))
        met = high == 0 and score >= 72
        summary = (
            "Pedagogy critique indicates acceptable novice progression."
            if met
            else "Pedagogy critique found progression/coherence issues."
        )
        return PedagogyCritique(
            score=score,
            min_quality_met=met,
            summary=summary,
            diagnostics=tuple(diagnostics),
        )
