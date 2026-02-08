"""Shared deterministic DAG utilities for node dictionaries."""

from __future__ import annotations

from collections import deque
from typing import Any


def node_map(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Normalize a list of node mappings into an ID-indexed map."""
    mapping: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, dict):
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str):
            continue
        mapping[node_id] = node
    return mapping


def _graph_from_nodes(
    nodes: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, int], dict[str, list[str]]]:
    nodes_by_id = node_map(nodes)
    indegree: dict[str, int] = {node_id: 0 for node_id in nodes_by_id}
    dependents: dict[str, list[str]] = {node_id: [] for node_id in nodes_by_id}

    for node_id, node in nodes_by_id.items():
        raw_prereqs = node.get("prerequisites", [])
        if not isinstance(raw_prereqs, list):
            continue
        seen: set[str] = set()
        for prereq in raw_prereqs:
            prereq_id = str(prereq)
            if prereq_id == node_id:
                continue
            if prereq_id not in nodes_by_id:
                continue
            if prereq_id in seen:
                continue
            seen.add(prereq_id)
            indegree[node_id] += 1
            dependents[prereq_id].append(node_id)

    return nodes_by_id, indegree, dependents


def topological_order(
    nodes: list[dict[str, Any]],
    *,
    fallback_sorted_on_cycle: bool = True,
) -> list[str]:
    """Return deterministic topological order for node dictionaries."""
    nodes_by_id, indegree, dependents = _graph_from_nodes(nodes)
    queue: deque[str] = deque(sorted(node_id for node_id, degree in indegree.items() if degree == 0))
    ordered: list[str] = []

    while queue:
        current = queue.popleft()
        ordered.append(current)
        for dependent in sorted(dependents.get(current, [])):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)

    if len(ordered) == len(nodes_by_id):
        return ordered
    if not fallback_sorted_on_cycle:
        return ordered
    return sorted(nodes_by_id.keys())


def is_acyclic(nodes: list[dict[str, Any]]) -> bool:
    """Return True when graph contains no cycles."""
    nodes_by_id = node_map(nodes)
    return len(topological_order(nodes, fallback_sorted_on_cycle=False)) == len(nodes_by_id)


def max_depth(nodes: list[dict[str, Any]]) -> int:
    """Return max distance from any root using prerequisite edges."""
    nodes_by_id, indegree, dependents = _graph_from_nodes(nodes)
    queue: deque[str] = deque(node_id for node_id, degree in indegree.items() if degree == 0)
    depth: dict[str, int] = {node_id: 0 for node_id in queue}

    while queue:
        current = queue.popleft()
        current_depth = depth.get(current, 0)
        for child in dependents.get(current, []):
            child_depth = current_depth + 1
            if child_depth > depth.get(child, 0):
                depth[child] = child_depth
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    return max(depth.values()) if depth else 0


def reachable_from_roots(nodes: list[dict[str, Any]]) -> set[str]:
    """Return IDs reachable from one or more root nodes."""
    nodes_by_id, _, dependents = _graph_from_nodes(nodes)
    roots = [
        node_id
        for node_id, node in nodes_by_id.items()
        if not isinstance(node.get("prerequisites"), list) or len(node.get("prerequisites", [])) == 0
    ]
    visited: set[str] = set()
    queue: deque[str] = deque(sorted(roots))
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        for child in sorted(dependents.get(current, [])):
            if child not in visited:
                queue.append(child)
    return visited

