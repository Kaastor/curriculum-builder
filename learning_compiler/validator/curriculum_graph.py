"""Graph and constraint checks for curriculum DAGs."""

from __future__ import annotations

from collections import deque
from typing import Any

from learning_compiler.validator.helpers import is_number
from learning_compiler.validator.types import ValidationConfig, ValidationResult


def check_prerequisite_integrity(
    nodes: list[dict[str, Any]],
    result: ValidationResult,
    config: ValidationConfig,
) -> None:
    node_ids = {str(node.get("id")) for node in nodes if isinstance(node, dict)}
    errors = 0

    for node in nodes:
        if not isinstance(node, dict):
            continue

        node_id = str(node.get("id", "???"))
        prereqs = node.get("prerequisites")
        if not isinstance(prereqs, list):
            continue

        if (
            config.max_prerequisites_per_node is not None
            and len(prereqs) > config.max_prerequisites_per_node
        ):
            result.fail(
                f"Node {node_id}: {len(prereqs)} prerequisites exceeds max "
                f"{config.max_prerequisites_per_node}"
            )
            errors += 1

        for prereq_id in prereqs:
            prereq = str(prereq_id)
            if prereq == node_id:
                result.fail(f"Node {node_id}: self-dependency is not allowed")
                errors += 1
                continue
            if prereq not in node_ids:
                result.fail(f"Node {node_id}: prerequisite '{prereq}' does not exist")
                errors += 1

    if errors == 0:
        result.ok("All prerequisite references are valid")


def check_no_cycles(nodes: list[dict[str, Any]], result: ValidationResult) -> None:
    adjacency: dict[str, list[str]] = {
        str(node.get("id")): [str(prereq) for prereq in node.get("prerequisites", [])]
        for node in nodes
        if isinstance(node, dict)
    }

    visited: set[str] = set()
    stack: set[str] = set()

    def dfs(node_id: str) -> bool:
        if node_id in stack:
            return True
        if node_id in visited:
            return False

        visited.add(node_id)
        stack.add(node_id)
        for prereq in adjacency.get(node_id, []):
            if prereq in adjacency and dfs(prereq):
                return True
        stack.remove(node_id)
        return False

    has_cycle = any(dfs(node_id) for node_id in adjacency)
    if has_cycle:
        result.fail("Circular dependency detected")
    else:
        result.ok("No cycles detected (valid DAG)")


def check_reachability(nodes: list[dict[str, Any]], result: ValidationResult) -> None:
    node_map = {str(node.get("id")): node for node in nodes if isinstance(node, dict)}
    roots = [
        node_id
        for node_id, node in node_map.items()
        if len(node.get("prerequisites", [])) == 0
    ]

    if not roots:
        result.fail("No root nodes found (every node has prerequisites)")
        return

    dependents: dict[str, list[str]] = {node_id: [] for node_id in node_map}
    for node_id, node in node_map.items():
        for prereq in node.get("prerequisites", []):
            prereq_id = str(prereq)
            if prereq_id in dependents:
                dependents[prereq_id].append(node_id)

    visited: set[str] = set()
    queue: deque[str] = deque(roots)
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        for next_node in dependents.get(current, []):
            if next_node not in visited:
                queue.append(next_node)

    unreachable = sorted(set(node_map.keys()) - visited)
    if unreachable:
        result.fail(f"Unreachable nodes from graph roots: {unreachable}")
    else:
        result.ok("All nodes reachable from at least one root")


def check_node_count(
    nodes: list[dict[str, Any]],
    result: ValidationResult,
    config: ValidationConfig,
) -> None:
    if config.node_count_min is None and config.node_count_max is None:
        return

    count = len(nodes)
    min_count = config.node_count_min if config.node_count_min is not None else count
    max_count = config.node_count_max if config.node_count_max is not None else count

    if count < min_count or count > max_count:
        result.fail(f"Node count {count} outside [{min_count}, {max_count}]")
    else:
        result.ok(f"Node count {count} within [{min_count}, {max_count}]")


def check_total_hours(
    nodes: list[dict[str, Any]],
    result: ValidationResult,
    config: ValidationConfig,
) -> None:
    total_minutes = 0.0
    for node in nodes:
        estimate = node.get("estimate_minutes")
        if is_number(estimate):
            total_minutes += float(estimate)

    total_hours = round(total_minutes / 60.0, 2)
    if total_hours < config.total_hours_min or total_hours > config.total_hours_max:
        result.fail(
            f"derived_total_hours={total_hours} outside "
            f"[{config.total_hours_min}, {config.total_hours_max}]"
        )
    else:
        result.ok(
            f"derived_total_hours within [{config.total_hours_min}, {config.total_hours_max}]"
        )
