"""Graph-oriented quality rules and weighted score aggregation."""

from __future__ import annotations

from typing import Any

from learning_compiler.dag import is_acyclic, max_depth as dag_max_depth
from learning_compiler.agent.quality.types import QualityDiagnostic


def max_depth(nodes: list[dict[str, Any]]) -> int:
    return dag_max_depth(nodes)


def contains_cycle(nodes: list[dict[str, Any]]) -> bool:
    return not is_acyclic(nodes)


def weighted_total(dimensions: dict[str, int]) -> int:
    weights = {
        "structural_validity": 0.22,
        "atomicity": 0.14,
        "pedagogical_progression": 0.14,
        "resource_relevance": 0.12,
        "mastery_actionability": 0.14,
        "effort_coherence": 0.08,
        "redundancy": 0.08,
        "learner_path_coherence": 0.08,
    }
    score = 0.0
    for key, weight in weights.items():
        score += float(dimensions.get(key, 0)) * weight
    return int(round(score))


def score_structural(nodes: list[dict[str, Any]], diagnostics: list[QualityDiagnostic]) -> int:
    score = 100
    ids = [str(node.get("id", "")) for node in nodes]
    if len(ids) != len(set(ids)):
        diagnostics.append(
            QualityDiagnostic(
                rule_id="structure.duplicate_node_ids",
                severity="critical",
                message="Duplicate node IDs detected.",
                hard_fail=True,
            )
        )
        score -= 60
    known = set(ids)
    for node in nodes:
        node_id = str(node.get("id", ""))
        for prereq in node.get("prerequisites", []):
            prereq_id = str(prereq)
            if prereq_id not in known:
                diagnostics.append(
                    QualityDiagnostic(
                        rule_id="structure.missing_prerequisite",
                        severity="critical",
                        node_id=node_id,
                        message=f"Prerequisite {prereq_id} does not exist.",
                        hard_fail=True,
                    )
                )
                score -= 15
    if nodes and contains_cycle(nodes):
        diagnostics.append(
            QualityDiagnostic(
                rule_id="structure.cycle",
                severity="critical",
                message="Cycle detected in prerequisite graph.",
                hard_fail=True,
            )
        )
        score -= 50
    return max(0, score)


def score_atomicity(nodes: list[dict[str, Any]], diagnostics: list[QualityDiagnostic]) -> int:
    score = 100
    offenders = 0
    for node in nodes:
        node_id = str(node.get("id", ""))
        capability = str(node.get("capability", "")).lower()
        if " and " in capability or ";" in capability:
            offenders += 1
            score -= 12
            diagnostics.append(
                QualityDiagnostic(
                    rule_id="atomicity.compound_capability",
                    severity="high",
                    node_id=node_id,
                    message="Capability appears compound; should target one primary skill.",
                )
            )
    if nodes and offenders > max(1, len(nodes) // 4):
        diagnostics.append(
            QualityDiagnostic(
                rule_id="atomicity.threshold",
                severity="critical",
                message="Too many non-atomic nodes.",
                hard_fail=True,
            )
        )
    return max(0, score)


def score_progression(nodes: list[dict[str, Any]], diagnostics: list[QualityDiagnostic]) -> int:
    score = 100
    roots = [node for node in nodes if len(node.get("prerequisites", [])) == 0]
    if len(nodes) >= 4 and len(roots) == len(nodes):
        score -= 45
        diagnostics.append(
            QualityDiagnostic(
                rule_id="progression.all_roots",
                severity="high",
                message="All nodes are roots; progression is weak.",
            )
        )
    depth = max_depth(nodes)
    if len(nodes) >= 6 and depth < 2:
        score -= 40
        diagnostics.append(
            QualityDiagnostic(
                rule_id="progression.depth_too_shallow",
                severity="high",
                message="Graph depth is too shallow for curriculum size.",
            )
        )
    return max(0, score)
