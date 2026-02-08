"""Quality checks for pedagogy and graph shape beyond structural schema rules."""

from __future__ import annotations

from collections import deque
from statistics import median
import re
from typing import Any

from learning_compiler.validator.helpers import is_number
from learning_compiler.validator.types import ValidationResult

ACTION_VERBS = (
    "analyze",
    "build",
    "compare",
    "defend",
    "design",
    "document",
    "explain",
    "implement",
    "integrate",
    "measure",
    "run",
    "simulate",
    "teach",
    "test",
    "validate",
    "work",
    "write",
)

MEASURABLE_SIGNALS = (
    "must ",
    "at least",
    "include",
    "correct",
    "pass",
    "failure",
    "threshold",
    "explicit",
)


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
            elif not any(f"{verb} " in task.lower() for verb in ACTION_VERBS):
                result.fail(
                    f"Node {node_id}: mastery_check.task should contain a concrete action verb"
                )
                errors += 1
            if len(pass_criteria) < 20:
                result.fail(
                    f"Node {node_id}: mastery_check.pass_criteria too short to be measurable"
                )
                errors += 1
            elif not any(signal in pass_criteria.lower() for signal in MEASURABLE_SIGNALS):
                result.fail(
                    f"Node {node_id}: mastery_check.pass_criteria should include measurable acceptance signals"
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
    elif len(estimates) >= 8 and len(unique) <= 2:
        result.warn("Very low estimate diversity detected; effort model may be too flat")

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


def _text_prefix(text: str, words: int = 4) -> str:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return " ".join(tokens[:words])


def check_repetition(nodes: list[dict[str, Any]], result: ValidationResult) -> None:
    if len(nodes) < 6:
        return

    capabilities = [_text_prefix(str(node.get("capability", ""))) for node in nodes]
    mastery_tasks = [
        _text_prefix(
            str(node.get("mastery_check", {}).get("task", ""))
            if isinstance(node.get("mastery_check"), dict)
            else ""
        )
        for node in nodes
    ]

    cap_unique = len({item for item in capabilities if item})
    mastery_unique = len({item for item in mastery_tasks if item})

    if cap_unique <= max(2, len(nodes) // 4):
        result.warn("Capability wording is highly repetitive; consider more stage-specific phrasing")
    if mastery_unique <= max(2, len(nodes) // 4):
        result.warn("Mastery task wording is highly repetitive; vary implementation expectations")

    result.ok("Repetition checks completed")


def check_resource_relevance(
    nodes: list[dict[str, Any]],
    topic_spec: dict[str, Any] | None,
    result: ValidationResult,
) -> None:
    if not nodes or topic_spec is None:
        return

    constraints = topic_spec.get("context_pack", {}) if isinstance(topic_spec, dict) else {}
    focus_terms = constraints.get("focus_terms", []) if isinstance(constraints, dict) else []
    local_paths = constraints.get("local_paths", []) if isinstance(constraints, dict) else []

    corpus = " ".join(
        [
            str(topic_spec.get("goal", "")),
            " ".join(
                [item for item in topic_spec.get("scope_in", []) if isinstance(item, str)]
            ),
            " ".join([item for item in focus_terms if isinstance(item, str)]),
            " ".join([item for item in local_paths if isinstance(item, str)]),
        ]
    ).lower()

    keywords = {token for token in re.findall(r"[a-z0-9]{4,}", corpus)}
    if not keywords:
        return

    weak_nodes: list[str] = []
    for node in nodes:
        node_id = str(node.get("id", "???"))
        resources = node.get("resources", [])
        if not isinstance(resources, list) or not resources:
            continue

        material = " ".join(
            [
                f"{resource.get('title', '')} {resource.get('url', '')}".lower()
                for resource in resources
                if isinstance(resource, dict)
            ]
        )
        if not any(keyword in material for keyword in keywords):
            weak_nodes.append(node_id)

    if not weak_nodes:
        result.ok("Resource relevance checks passed")
        return

    for node_id in weak_nodes[:3]:
        result.warn(f"Node {node_id}: resources may be weakly relevant to topic/context keywords")
    if len(weak_nodes) > 3:
        result.warn(
            f"{len(weak_nodes) - 3} additional node(s) also have weak keyword overlap in resources"
        )


def check_learner_path_coherence(nodes: list[dict[str, Any]], result: ValidationResult) -> None:
    if len(nodes) < 2:
        return

    node_map = {str(node.get("id")): node for node in nodes if isinstance(node, dict)}
    hidden_prereq_count = 0
    workload_jump_count = 0

    for node in nodes:
        node_id = str(node.get("id", ""))
        capability = str(node.get("capability", "")).lower()
        prerequisites = [str(item) for item in node.get("prerequisites", [])]

        if not prerequisites and any(token in capability for token in ("integrate", "validate")):
            result.warn(
                f"Node {node_id}: advanced capability without prerequisites may confuse novice learners"
            )
            hidden_prereq_count += 1

        if prerequisites:
            parent_minutes = [
                int(parent.get("estimate_minutes"))
                for prereq in prerequisites
                if (parent := node_map.get(prereq)) is not None
                and is_number(parent.get("estimate_minutes"))
            ]
            current = node.get("estimate_minutes")
            if parent_minutes and is_number(current):
                baseline = max(parent_minutes)
                if float(current) > baseline * 2.2:
                    workload_jump_count += 1

    if hidden_prereq_count > 0:
        result.fail(
            f"Detected {hidden_prereq_count} possible hidden-prerequisite node(s); learning path coherence is weak"
        )
    elif workload_jump_count > 0:
        result.warn(
            f"Detected {workload_jump_count} abrupt workload jump(s) versus prerequisites"
        )
    else:
        result.ok("Learner path coherence checks passed")
