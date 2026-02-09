"""Draft curriculum proposer stage."""

from __future__ import annotations

import os
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


def _compact_curriculum_for_llm(payload: dict[str, Any]) -> dict[str, Any]:
    compact_nodes: list[dict[str, Any]] = []
    for node in payload.get("nodes", []):
        if not isinstance(node, dict):
            continue
        compact_nodes.append(
            {
                "id": node.get("id", ""),
                "title": node.get("title", ""),
                "prerequisites": node.get("prerequisites", []),
                "estimate_minutes": node.get("estimate_minutes", 0),
            }
        )
    compact: dict[str, Any] = {
        "topic": payload.get("topic", ""),
        "nodes": compact_nodes,
    }
    if "open_questions" in payload:
        compact["open_questions"] = payload.get("open_questions", [])
    return compact


def _compact_topic_spec_for_llm(topic_spec: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for key in ("goal", "audience", "domain_mode", "evidence_mode", "spec_version"):
        value = topic_spec.get(key)
        if isinstance(value, str):
            compact[key] = value

    constraints = topic_spec.get("constraints")
    if isinstance(constraints, dict):
        compact["constraints"] = constraints

    def _limited_str_list(value: Any, limit: int) -> list[str]:
        if not isinstance(value, list):
            return []
        result: list[str] = []
        for item in value:
            if isinstance(item, str):
                result.append(item)
            if len(result) >= limit:
                break
        return result

    compact["misconceptions"] = _limited_str_list(topic_spec.get("misconceptions"), 16)
    compact["prerequisites"] = _limited_str_list(topic_spec.get("prerequisites"), 24)
    compact["scope_in"] = _limited_str_list(topic_spec.get("scope_in"), 60)
    compact["scope_out"] = _limited_str_list(topic_spec.get("scope_out"), 24)

    context_pack = topic_spec.get("context_pack")
    if isinstance(context_pack, dict):
        compact_context: dict[str, Any] = {}
        domain = context_pack.get("domain")
        if isinstance(domain, str):
            compact_context["domain"] = domain
        compact_context["focus_terms"] = _limited_str_list(context_pack.get("focus_terms"), 24)
        compact_context["required_outcomes"] = _limited_str_list(
            context_pack.get("required_outcomes"),
            24,
        )
        compact_context["local_paths"] = _limited_str_list(context_pack.get("local_paths"), 16)
        compact["context_pack"] = compact_context
    return compact


def _scope_document_payload(path: str | None, text: str | None) -> dict[str, Any] | None:
    if text is None:
        return None
    max_chars_raw = os.environ.get("AGENT_SCOPE_TEXT_MAX_CHARS", "12000")
    try:
        max_chars = max(2000, int(max_chars_raw))
    except ValueError:
        max_chars = 12000
    was_truncated = len(text) > max_chars
    clipped = text[:max_chars]
    if was_truncated:
        clipped += "\n\n[scope truncated for LLM payload]"
    return {
        "path": path or "",
        "text": clipped,
        "truncated": was_truncated,
        "source_chars": len(text),
    }


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

        if policy.provider == ModelProvider.INTERNAL:
            return payload

        scope_document_payload = _scope_document_payload(
            spec.scope_document_path,
            spec.scope_document_text,
        )

        response = self._client.run_json(
            LLMRequest(
                stage="proposer",
                schema_name="proposer_curriculum_v1",
                payload={
                    "topic_spec": _compact_topic_spec_for_llm(spec.topic_spec.to_dict()),
                    "draft_curriculum": _compact_curriculum_for_llm(payload),
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
                "llm proposer returned invalid curriculum payload.",
            )
        return candidate
