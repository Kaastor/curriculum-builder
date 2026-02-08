"""Deterministic planning and diff utilities for orchestration runs."""

from __future__ import annotations

import math
from typing import Any

from learning_compiler.dag import topological_order as dag_topological_order
from learning_compiler.domain import Curriculum, CurriculumNode, TopicSpec, parse_curriculum, parse_topic_spec

def _as_topic_spec(topic_spec: TopicSpec | dict[str, Any]) -> TopicSpec:
    if isinstance(topic_spec, TopicSpec):
        return topic_spec
    return parse_topic_spec(topic_spec)


def _as_curriculum(curriculum: Curriculum | dict[str, Any]) -> Curriculum:
    if isinstance(curriculum, Curriculum):
        return curriculum
    return parse_curriculum(curriculum)


def _nodes_to_mappings(nodes: tuple[CurriculumNode, ...]) -> list[dict[str, Any]]:
    return [node.to_dict() for node in nodes]


def topological_order(nodes: list[dict[str, Any]]) -> list[str]:
    """Return deterministic topological order for node dictionaries."""
    return dag_topological_order(nodes)


def compute_critical_path(nodes: tuple[CurriculumNode, ...]) -> list[str]:
    """Return node IDs on the longest estimated-time prerequisite chain."""
    node_map = {node.id: node for node in nodes}
    ordered = topological_order(_nodes_to_mappings(nodes))

    duration = {
        node_id: float(node_map[node_id].estimate_minutes)
        for node_id in ordered if node_id in node_map
    }
    best: dict[str, float] = {}
    previous: dict[str, str | None] = {}

    for node_id in ordered:
        node = node_map.get(node_id)
        if not node:
            continue

        prereqs = [prereq for prereq in node.prerequisites if prereq in duration]
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


def build_plan(
    topic_spec: TopicSpec | dict[str, Any],
    curriculum: Curriculum | dict[str, Any],
) -> dict[str, Any]:
    """Build a 2-4 week deterministic plan from topic spec and curriculum DAG."""
    topic = _as_topic_spec(topic_spec)
    curriculum_doc = _as_curriculum(curriculum)
    nodes = curriculum_doc.nodes
    node_map = {node.id: node for node in nodes}
    ordered = topological_order(_nodes_to_mappings(nodes))

    total_minutes = sum(float(node.estimate_minutes) for node in nodes)
    weekly_budget_minutes = float(topic.constraints.hours_per_week) * 60.0

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

        estimate = float(node.estimate_minutes)
        if (
            week_index < weeks - 1
            and week_minutes + estimate > week_capacity
            and buckets[week_index]["nodes"]
        ):
            week_index += 1
            week_minutes = 0.0

        buckets[week_index]["nodes"].append(node_id)
        buckets[week_index]["deliverables"].append(
            {
                "node_id": node_id,
                "task": node.mastery_check.task,
                "pass_criteria": node.mastery_check.pass_criteria,
            }
        )
        week_minutes += estimate

    for index in range(1, weeks):
        prior_nodes = buckets[index - 1]["nodes"]
        if prior_nodes:
            buckets[index]["review"] = prior_nodes[-2:]

    return {
        "topic": curriculum_doc.topic,
        "duration_weeks": weeks,
        "weekly_budget_minutes": round(weekly_budget_minutes, 2),
        "total_estimated_minutes": round(total_minutes, 2),
        "weeks": buckets,
    }


def compute_diff(
    previous: Curriculum | dict[str, Any],
    current: Curriculum | dict[str, Any],
) -> dict[str, Any]:
    """Compute structural and effort deltas between previous/current curricula."""
    previous_doc = _as_curriculum(previous)
    current_doc = _as_curriculum(current)
    previous_nodes = {
        node.id: node.to_dict()
        for node in previous_doc.nodes
    }
    current_nodes = {
        node.id: node.to_dict()
        for node in current_doc.nodes
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

    previous_critical = compute_critical_path(previous_doc.nodes)
    current_critical = compute_critical_path(current_doc.nodes)

    return {
        "added_nodes": added,
        "removed_nodes": removed,
        "changed_nodes": changed,
        "time_delta_minutes": round(current_minutes - previous_minutes, 2),
        "critical_path_changed": previous_critical != current_critical,
        "previous_critical_path": previous_critical,
        "current_critical_path": current_critical,
    }
