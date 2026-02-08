"""Draft curriculum proposer stage."""

from __future__ import annotations

from typing import Any

from learning_compiler.agent.node_builder import build_node
from learning_compiler.agent.research import ResourceResolver
from learning_compiler.agent.spec import GenerationSpec
from learning_compiler.domain import OpenQuestion


def node_id(index: int) -> str:
    return f"N{index + 1}"


class LLMProposer:
    def propose(self, spec: GenerationSpec, resolver: ResourceResolver) -> dict[str, Any]:
        nodes = []
        used_urls: set[str] = set()
        for index in range(spec.target_nodes):
            node = build_node(
                index=index,
                spec=spec,
                resolver=resolver,
                used_resource_urls=tuple(sorted(used_urls)),
            ).to_dict()
            for resource in node.get("resources", []):
                url = resource.get("url") if isinstance(resource, dict) else None
                if isinstance(url, str):
                    used_urls.add(url)
            nodes.append(node)

        payload: dict[str, Any] = {"topic": spec.topic_label, "nodes": nodes}
        if spec.strict_mode:
            tail = (node_id(max(0, spec.target_nodes - 2)), node_id(spec.target_nodes - 1))
            payload["open_questions"] = [
                OpenQuestion(
                    question=(
                        "Which claims remain weakly evidenced or contradictory for "
                        "this topic under current references?"
                    ),
                    related_nodes=tail,
                    status="open",
                ).to_dict()
            ]
        return payload
