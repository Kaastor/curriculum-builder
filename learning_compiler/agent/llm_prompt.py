"""Prompt construction and response parsing helpers for LLM stages."""

from __future__ import annotations

import json
from typing import Any

from learning_compiler.agent.llm_types import LLMRequest
from learning_compiler.errors import ErrorCode, LearningCompilerError


def build_prompt(request: LLMRequest) -> str:
    payload = json.dumps(
        request.payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    scope_hint = ""
    if isinstance(request.payload.get("scope_document"), dict):
        scope_hint = (
            "If scope_document.text is provided, ground node titles, ordering, and mastery checks "
            "in that source document; treat draft_curriculum as scaffolding only.\n"
        )
    return (
        "You are generating structured curriculum-engineering output.\n"
        "Return ONLY JSON that conforms to the provided schema.\n"
        f"{scope_hint}"
        f"Stage: {request.stage}\n"
        f"Schema: {request.schema_name}\n"
        "Input payload:\n"
        f"{payload}\n"
    )


def parse_json_mapping(raw: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LearningCompilerError(
            ErrorCode.INTERNAL_ERROR,
            "model output is not valid JSON.",
            {"error": str(exc)},
        ) from exc
    if not isinstance(payload, dict):
        raise LearningCompilerError(
            ErrorCode.INTERNAL_ERROR,
            "model output root must be object.",
        )
    return payload


def extract_remote_payload(response_payload: dict[str, Any]) -> dict[str, Any]:
    output_text = response_payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return parse_json_mapping(output_text)

    output = response_payload.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                block_json = block.get("json")
                if isinstance(block_json, dict):
                    return block_json
                block_text = block.get("text")
                if isinstance(block_text, str) and block_text.strip():
                    return parse_json_mapping(block_text)

    raise LearningCompilerError(
        ErrorCode.INTERNAL_ERROR,
        "remote_llm did not return structured JSON content.",
        {"response_keys": sorted(str(key) for key in response_payload.keys())},
    )
