"""Repair executor stage for deterministic DAG mutations."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from learning_compiler.agent.node_builder import (
    NodeStage,
    node_core_ideas,
    node_mastery,
    node_pitfalls,
    node_prerequisites,
)
from learning_compiler.agent.repair_actions import RepairAction, RepairActionType
from learning_compiler.agent.research import ResourceRequest, ResourceResolver
from learning_compiler.agent.spec import GenerationSpec
from learning_compiler.domain import Resource


def _id_to_index(node_id: str) -> int:
    if node_id.startswith("N") and node_id[1:].isdigit():
        return int(node_id[1:]) - 1
    return -1


def _node_id(index: int) -> str:
    return f"N{index + 1}"


def _atomic_phrase(text: str) -> str:
    lowered = text.strip()
    separators = (" and ", ";", " / ", " + ")
    for separator in separators:
        if separator in lowered.lower():
            head = lowered.split(separator, 1)[0].strip()
            if head:
                return head[0].upper() + head[1:]
    return lowered


def _collect_used_urls(nodes: list[dict[str, Any]], skip_id: str | None = None) -> tuple[str, ...]:
    urls: set[str] = set()
    for node in nodes:
        node_id = str(node.get("id", ""))
        if skip_id is not None and node_id == skip_id:
            continue
        resources = node.get("resources", [])
        if not isinstance(resources, list):
            continue
        for resource in resources:
            url = resource.get("url") if isinstance(resource, dict) else None
            if isinstance(url, str):
                urls.add(url)
    return tuple(sorted(urls))


def _replace_node(nodes: list[dict[str, Any]], node_id: str, payload: dict[str, Any]) -> None:
    for index, node in enumerate(nodes):
        if str(node.get("id", "")) == node_id:
            nodes[index] = payload
            return


def _stage_for_repair(index: int, total: int) -> NodeStage:
    if total <= 3:
        return (NodeStage.FOUNDATION, NodeStage.APPLICATION, NodeStage.VALIDATION)[
            min(index, 2)
        ]
    if index <= max(1, total // 4):
        return NodeStage.FOUNDATION
    if index <= max(2, (total * 2) // 4):
        return NodeStage.APPLICATION
    if index <= max(3, (total * 3) // 4):
        return NodeStage.INTEGRATION
    return NodeStage.VALIDATION


class LLMRepairExecutor:
    def apply(
        self,
        curriculum: dict[str, Any],
        actions: tuple[RepairAction, ...],
        spec: GenerationSpec,
        resolver: ResourceResolver,
    ) -> dict[str, Any]:
        patched = deepcopy(curriculum)
        nodes = [item for item in patched.get("nodes", []) if isinstance(item, dict)]
        for action in actions:
            if action.action_type == RepairActionType.REORDER_NODES:
                nodes.sort(key=lambda item: (len(item.get("prerequisites", [])), str(item.get("id", ""))))
                continue

            node_id = action.node_id
            if node_id is None:
                continue
            index = _id_to_index(node_id)
            if index < 0 or index >= len(nodes):
                continue
            node = deepcopy(nodes[index])

            if action.action_type == RepairActionType.REWRITE_NODE:
                self._rewrite_node(node, index, spec)
            elif action.action_type == RepairActionType.REWIRE_PREREQS:
                node["prerequisites"] = list(
                    node_prerequisites(index, len(nodes), spec.max_prerequisites_per_node)
                )
            elif action.action_type == RepairActionType.RETARGET_RESOURCES:
                node["resources"] = self._retarget_resources(node, index, nodes, spec, resolver)
            elif action.action_type == RepairActionType.RETIME_NODE:
                node["estimate_minutes"] = self._retime_node(node, index, nodes, spec)

            _replace_node(nodes, node_id, node)

        patched["nodes"] = nodes
        return patched

    def _rewrite_node(self, node: dict[str, Any], index: int, spec: GenerationSpec) -> None:
        node_id = str(node.get("id", _node_id(index)))
        title = _atomic_phrase(str(node.get("title", ""))) or spec.titles[index]
        stage = _stage_for_repair(index, len(spec.titles))
        node["title"] = title
        node["capability"] = _atomic_phrase(str(node.get("capability", ""))) or f"Implement {title.lower()}."
        node["core_ideas"] = list(node_core_ideas(title, stage))
        node["pitfalls"] = list(node_pitfalls(index, spec.misconceptions, stage))
        node["mastery_check"] = node_mastery(
            node_id=node_id,
            title=title,
            stage=stage,
            spec=spec,
        ).to_dict()

    def _retarget_resources(
        self,
        node: dict[str, Any],
        index: int,
        nodes: list[dict[str, Any]],
        spec: GenerationSpec,
        resolver: ResourceResolver,
    ) -> list[dict[str, str]]:
        node_id = str(node.get("id", _node_id(index)))
        resources = resolver.resolve(
            ResourceRequest(
                topic_spec=spec.topic_spec,
                node_id=node_id,
                node_index=index,
                node_title=str(node.get("title", spec.titles[index])),
                prerequisites=tuple(str(item) for item in node.get("prerequisites", [])),
                evidence_mode=spec.evidence_mode,
                used_resource_urls=_collect_used_urls(nodes, skip_id=node_id),
            )
        )
        return [
            Resource(
                title=item["title"],
                url=item["url"],
                kind=item["kind"],
                role=item["role"],
                citation=item.get("citation"),
            ).to_dict()
            for item in resources
        ]

    def _retime_node(
        self,
        node: dict[str, Any],
        index: int,
        nodes: list[dict[str, Any]],
        spec: GenerationSpec,
    ) -> int:
        base = spec.minutes[index] if index < len(spec.minutes) else 90
        prereq_estimates: list[int] = []
        by_id = {str(item.get("id", "")): item for item in nodes}
        for prereq in node.get("prerequisites", []):
            parent = by_id.get(str(prereq))
            if parent is None:
                continue
            value = parent.get("estimate_minutes")
            if isinstance(value, int):
                prereq_estimates.append(value)
        if not prereq_estimates:
            return base
        anchor = max(prereq_estimates)
        smoothed = max(base, anchor + 10)
        return min(220, smoothed)
