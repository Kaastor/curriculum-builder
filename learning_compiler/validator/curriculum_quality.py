"""Quality checks for pedagogy and graph shape beyond structural schema rules."""

from __future__ import annotations

from collections import deque
from statistics import median
from typing import Any

from learning_compiler.validator.helpers import is_number
from learning_compiler.validator.types import ValidationResult


def _max_depth(nodes: list[dict[str, Any]]) -> int:
    node_map = {str(node.get("id")): node for node in nodes if isinstance(node, dict)}
    indegree = {node_id: 0 for node_id in node_map}
    dependents: dict[str, list[str]] = {node_id: [] for node_id in node_map}

    for node_id, node in node_map.items():
        for prereq in node.get("prerequisites", []):
            prereq_id = str(prereq)
            if prereq_id not in node_map:
                continue
            indegree[node_id] += 1
            dependents[prereq_id].append(node_id)

    queue = deque([node_id for node_id, degree in indegree.items() if degree == 0])
    depth = {node_id: 0 for node_id in queue}

    while queue:
        current = queue.popleft()
        for child in dependents.get(current, []):
            depth[child] = max(depth.get(child, 0), depth[current] + 1)
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    return max(depth.values()) if depth else 0


def check_graph_progression(nodes: list[dict[str, Any]], result: ValidationResult) -> None:
    if not nodes:
        return

    roots = [node for node in nodes if len(node.get("prerequisites", [])) == 0]
    node_count = len(nodes)
    root_count = len(roots)

    if node_count >= 4 and root_count == node_count:
        result.fail("No learning progression: all nodes are roots (no prerequisite structure)")
        return

    if node_count >= 6 and root_count > max(3, round(node_count * 0.5)):
        result.warn(
            "High root-node ratio suggests weak progression structure; consider stronger prerequisite links"
        )

    depth = _max_depth(nodes)
    if node_count >= 6 and depth < 2:
        result.fail(
            f"Graph depth too shallow for {node_count} nodes (max depth {depth}); likely missing intermediate progression"
        )
    else:
        result.ok(f"Graph progression depth is {depth}")


def check_node_quality(nodes: list[dict[str, Any]], result: ValidationResult) -> None:
    errors = 0

    for node in nodes:
        node_id = str(node.get("id", "???"))
        core_ideas = node.get("core_ideas", [])
        pitfalls = node.get("pitfalls", [])
        mastery = node.get("mastery_check", {})

        if isinstance(core_ideas, list) and len(core_ideas) < 2:
            result.fail(f"Node {node_id}: core_ideas should contain at least 2 items")
            errors += 1

        if isinstance(pitfalls, list) and len(pitfalls) < 1:
            result.fail(f"Node {node_id}: pitfalls should contain at least 1 item")
            errors += 1

        if isinstance(mastery, dict):
            task = str(mastery.get("task", "")).strip()
            pass_criteria = str(mastery.get("pass_criteria", "")).strip()
            if len(task) < 20:
                result.fail(f"Node {node_id}: mastery_check.task too short to be actionable")
                errors += 1
            if len(pass_criteria) < 20:
                result.fail(
                    f"Node {node_id}: mastery_check.pass_criteria too short to be measurable"
                )
                errors += 1

    if errors == 0:
        result.ok("Node quality checks passed")


def check_time_granularity(nodes: list[dict[str, Any]], result: ValidationResult) -> None:
    estimates = [float(node.get("estimate_minutes")) for node in nodes if is_number(node.get("estimate_minutes"))]
    if not estimates:
        return

    unique = sorted(set(estimates))
    if len(estimates) >= 6 and len(unique) == 1:
        result.warn("All nodes use the same estimate_minutes value; granularity may be too coarse")

    smallest = min(estimates)
    largest = max(estimates)
    if smallest > 0 and largest / smallest > 6.0:
        result.warn(
            "Large estimate range detected (>6x between smallest and largest node); check granularity consistency"
        )

    med = median(estimates)
    if med > 0:
        outliers = [value for value in estimates if value > med * 3.0]
        if outliers:
            result.warn(
                f"Detected {len(outliers)} high-duration outlier nodes (>3x median estimate); consider splitting"
            )

    result.ok("Time granularity checks completed")
