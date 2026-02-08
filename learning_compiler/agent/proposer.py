"""Draft curriculum proposer stage."""

from __future__ import annotations

from typing import Any

from learning_compiler.agent.llm_client import LLMClient, LLMRequest
from learning_compiler.agent.model_policy import ModelPolicy, ModelProvider
from learning_compiler.agent.node_builder import build_node
from learning_compiler.agent.research import ResourceResolver
from learning_compiler.agent.spec import GenerationSpec
from learning_compiler.domain import OpenQuestion
from learning_compiler.errors import ErrorCode, LearningCompilerError


def node_id(index: int) -> str:
    return f"N{index + 1}"


class LLMProposer:
    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def propose(
        self,
        spec: GenerationSpec,
        resolver: ResourceResolver,
        policy: ModelPolicy,
    ) -> dict[str, Any]:
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

        if policy.provider != ModelProvider.CODING_AGENT:
            return payload

        scope_document_payload: dict[str, str] | None = None
        if spec.scope_document_text is not None:
            scope_document_payload = {
                "path": spec.scope_document_path or "",
                "text": spec.scope_document_text,
            }

        response = self._client.run_json(
            LLMRequest(
                stage="proposer",
                schema_name="proposer_curriculum_v1",
                payload={
                    "topic_spec": spec.topic_spec.to_dict(),
                    "draft_curriculum": payload,
                    "scope_document": scope_document_payload,
                    "requirements": {
                        "strict_atomic_nodes": True,
                        "must_remain_dag": True,
                        "ground_in_scope_document": scope_document_payload is not None,
                    },
                },
            ),
            policy,
        )
        candidate = response.get("curriculum")
        if not isinstance(candidate, dict):
            raise LearningCompilerError(
                ErrorCode.INTERNAL_ERROR,
                "coding_agent proposer returned invalid curriculum payload.",
            )
        return candidate
