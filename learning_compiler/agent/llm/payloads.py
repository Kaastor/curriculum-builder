"""Shared payload-shaping helpers for LLM-backed stages."""

from __future__ import annotations

import os
from typing import Any


def compact_curriculum_for_llm(
    payload: dict[str, Any],
    *,
    include_open_questions_if_present: bool = False,
) -> dict[str, Any]:
    """Project curriculum payload to the minimal fields needed for LLM stages."""
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

    if include_open_questions_if_present:
        if "open_questions" in payload:
            compact["open_questions"] = payload.get("open_questions", [])
    else:
        open_questions = payload.get("open_questions")
        if isinstance(open_questions, list):
            compact["open_questions"] = open_questions
    return compact


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


def compact_topic_spec_for_llm(topic_spec: dict[str, Any]) -> dict[str, Any]:
    """Project topic spec payload to stable fields used by LLM stages."""
    compact: dict[str, Any] = {}
    for key in ("goal", "audience", "domain_mode", "evidence_mode", "spec_version"):
        value = topic_spec.get(key)
        if isinstance(value, str):
            compact[key] = value

    constraints = topic_spec.get("constraints")
    if isinstance(constraints, dict):
        compact["constraints"] = constraints

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


def scope_document_payload(path: str | None, text: str | None) -> dict[str, Any] | None:
    """Clip scope document content before passing it to LLM stages."""
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
