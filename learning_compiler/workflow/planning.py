"""Deterministic planning and diff utilities for workflow runs."""

from __future__ import annotations

import math
from collections import deque
from typing import Any


def topological_order(nodes: list[dict[str, Any]]) -> list[str]:
    """Return deterministic topological order for node dictionaries."""
    indegree: dict[str, int] = {}
    dependents: dict[str, list[str]] = {}
    node_ids: list[str] = []

    for node in nodes:
        node_id = str(node.get("id"))
        node_ids.append(node_id)
        indegree[node_id] = 0
        dependents[node_id] = []

    for node in nodes:
        node_id = str(node.get("id"))
        for prereq in node.get("prerequisites", []):
            prereq_id = str(prereq)
            if prereq_id not in indegree:
                continue
            indegree[node_id] += 1
            dependents[prereq_id].append(node_id)

    queue = deque(sorted([node_id for node_id, value in indegree.items() if value == 0]))
    ordered: list[str] = []

    while queue:
        current = queue.popleft()
        ordered.append(current)
        for dependent in sorted(dependents.get(current, [])):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)

    if len(ordered) != len(nodes):
        return sorted(node_ids)

    return ordered


def compute_critical_path(nodes: list[dict[str, Any]]) -> list[str]:
    """Return node IDs on the longest estimated-time prerequisite chain."""
    node_map = {str(node.get("id")): node for node in nodes}
    ordered = topological_order(nodes)

    duration = {
        node_id: float(node_map[node_id].get("estimate_minutes", 0.0))
        for node_id in ordered
        if node_id in node_map
    }
    best: dict[str, float] = {}
    previous: dict[str, str | None] = {}

    for node_id in ordered:
        node = node_map.get(node_id)
        if not node:
            continue

        prereqs = [str(item) for item in node.get("prerequisites", []) if str(item) in duration]
        if not prereqs:
            best[node_id] = duration.get(node_id, 0.0)
            previous[node_id] = None
            continue

        best_prereq = prereqs[0]
        best_value = best.get(best_prereq, duration.get(best_prereq, 0.0))
        for candidate in prereqs[1:]:
            candidate_value = best.get(candidate, duration.get(candidate, 0.0))
            if candidate_value > best_value:
                best_value = candidate_value
                best_prereq = candidate

        best[node_id] = best_value + duration.get(node_id, 0.0)
        previous[node_id] = best_prereq

    if not best:
        return []

    end = max(best, key=best.get)
    path: list[str] = []
    cursor: str | None = end
    while cursor is not None:
        path.insert(0, cursor)
        cursor = previous.get(cursor)
    return path


def build_plan(topic_spec: dict[str, Any], curriculum: dict[str, Any]) -> dict[str, Any]:
    """Build a 2-4 week deterministic plan from topic spec and curriculum DAG."""
    constraints = topic_spec["constraints"]
    nodes = curriculum.get("nodes", [])
    if not isinstance(nodes, list):
        nodes = []

    node_map = {str(node.get("id")): node for node in nodes if isinstance(node, dict)}
    ordered = topological_order([node for node in nodes if isinstance(node, dict)])

    total_minutes = sum(
        float(node.get("estimate_minutes", 0.0))
        for node in nodes
        if isinstance(node, dict)
    )
    weekly_budget_minutes = float(constraints["hours_per_week"]) * 60.0

    if weekly_budget_minutes <= 0:
        weeks = 4
    else:
        weeks_required = math.ceil(total_minutes / weekly_budget_minutes) if total_minutes else 2
        weeks = max(2, min(4, weeks_required))

    fallback_capacity = total_minutes / weeks if weeks else 0.0
    week_capacity = weekly_budget_minutes if weekly_budget_minutes > 0 else fallback_capacity
    week_capacity = max(1.0, week_capacity)

    buckets: list[dict[str, Any]] = [
        {"week": index + 1, "nodes": [], "deliverables": [], "review": []}
        for index in range(weeks)
    ]

    week_index = 0
    week_minutes = 0.0
    for node_id in ordered:
        node = node_map.get(node_id)
        if node is None:
            continue

        estimate = float(node.get("estimate_minutes", 0.0))
        if (
            week_index < weeks - 1
            and week_minutes + estimate > week_capacity
            and buckets[week_index]["nodes"]
        ):
            week_index += 1
            week_minutes = 0.0

        buckets[week_index]["nodes"].append(node_id)
        mastery = node.get("mastery_check", {})
        task = mastery.get("task", "") if isinstance(mastery, dict) else ""
        pass_criteria = mastery.get("pass_criteria", "") if isinstance(mastery, dict) else ""
        buckets[week_index]["deliverables"].append(
            {
                "node_id": node_id,
                "task": task,
                "pass_criteria": pass_criteria,
            }
        )
        week_minutes += estimate

    for index in range(1, weeks):
        prior_nodes = buckets[index - 1]["nodes"]
        if prior_nodes:
            buckets[index]["review"] = prior_nodes[-2:]

    return {
        "topic": curriculum.get("topic"),
        "duration_weeks": weeks,
        "weekly_budget_minutes": round(weekly_budget_minutes, 2),
        "total_estimated_minutes": round(total_minutes, 2),
        "weeks": buckets,
    }


def compute_diff(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Compute structural and effort deltas between previous/current curricula."""
    previous_nodes = {
        str(node.get("id")): node
        for node in previous.get("nodes", [])
        if isinstance(node, dict)
    }
    current_nodes = {
        str(node.get("id")): node
        for node in current.get("nodes", [])
        if isinstance(node, dict)
    }

    previous_ids = set(previous_nodes.keys())
    current_ids = set(current_nodes.keys())

    added = sorted(current_ids - previous_ids)
    removed = sorted(previous_ids - current_ids)

    changed: list[dict[str, Any]] = []
    for node_id in sorted(previous_ids & current_ids):
        old_node = previous_nodes[node_id]
        new_node = current_nodes[node_id]
        changed_fields = sorted(
            [
                key
                for key in sorted(set(old_node.keys()) | set(new_node.keys()))
                if old_node.get(key) != new_node.get(key)
            ]
        )
        if changed_fields:
            changed.append({"id": node_id, "changed_fields": changed_fields})

    previous_minutes = sum(
        float(node.get("estimate_minutes", 0.0)) for node in previous_nodes.values()
    )
    current_minutes = sum(
        float(node.get("estimate_minutes", 0.0)) for node in current_nodes.values()
    )

    previous_critical = compute_critical_path(list(previous_nodes.values()))
    current_critical = compute_critical_path(list(current_nodes.values()))

    return {
        "added_nodes": added,
        "removed_nodes": removed,
        "changed_nodes": changed,
        "time_delta_minutes": round(current_minutes - previous_minutes, 2),
        "critical_path_changed": previous_critical != current_critical,
        "previous_critical_path": previous_critical,
        "current_critical_path": current_critical,
    }
