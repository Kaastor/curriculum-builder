"""Graph-oriented quality rules and weighted score aggregation."""

from __future__ import annotations

from collections import deque
from typing import Any

from learning_compiler.agent.quality_types import QualityDiagnostic


def max_depth(nodes: list[dict[str, Any]]) -> int:
    node_ids = {str(node.get("id")) for node in nodes if isinstance(node.get("id"), str)}
    indegree = {node_id: 0 for node_id in node_ids}
    edges: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for node in nodes:
        current = str(node.get("id", ""))
        for prereq in node.get("prerequisites", []):
            prereq_id = str(prereq)
            if prereq_id not in node_ids or current not in node_ids:
                continue
            indegree[current] += 1
            edges[prereq_id].append(current)
    queue = deque([node_id for node_id, degree in indegree.items() if degree == 0])
    depth = {node_id: 0 for node_id in queue}
    while queue:
        current = queue.popleft()
        for child in edges.get(current, []):
            depth[child] = max(depth.get(child, 0), depth[current] + 1)
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)
    return max(depth.values()) if depth else 0


def contains_cycle(nodes: list[dict[str, Any]]) -> bool:
    node_map = {str(node.get("id")): node for node in nodes if isinstance(node.get("id"), str)}
    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(node_id: str) -> bool:
        if node_id in visited:
            return False
        if node_id in visiting:
            return True
        visiting.add(node_id)
        for prereq in node_map[node_id].get("prerequisites", []):
            prereq_id = str(prereq)
            if prereq_id in node_map and dfs(prereq_id):
                return True
        visiting.remove(node_id)
        visited.add(node_id)
        return False

    return any(dfs(node_id) for node_id in sorted(node_map))


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
