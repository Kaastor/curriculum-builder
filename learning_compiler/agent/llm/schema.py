"""Strict JSON schema helpers for structured LLM stages."""

from __future__ import annotations

from typing import Any


def schema_for(schema_name: str) -> dict[str, Any]:
    if schema_name in {"proposer_curriculum_v1", "repair_curriculum_v1"}:
        resource_schema: dict[str, Any] = {
            "type": "object",
            "required": ["title", "url", "kind", "role", "citation"],
            "properties": {
                "title": {"type": "string"},
                "url": {"type": "string"},
                "kind": {"type": "string"},
                "role": {"type": "string"},
                "citation": {"type": ["string", "null"]},
            },
            "additionalProperties": False,
        }
        mastery_schema: dict[str, Any] = {
            "type": "object",
            "required": ["task", "pass_criteria"],
            "properties": {
                "task": {"type": "string"},
                "pass_criteria": {"type": "string"},
            },
            "additionalProperties": False,
        }
        node_schema: dict[str, Any] = {
            "type": "object",
            "required": [
                "id",
                "title",
                "capability",
                "core_ideas",
                "estimate_minutes",
                "prerequisites",
                "resources",
                "mastery_check",
                "pitfalls",
            ],
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "capability": {"type": "string"},
                "core_ideas": {"type": "array", "items": {"type": "string"}},
                "estimate_minutes": {"type": "number"},
                "prerequisites": {"type": "array", "items": {"type": "string"}},
                "resources": {"type": "array", "items": resource_schema},
                "mastery_check": mastery_schema,
                "pitfalls": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": False,
        }
        open_question_schema: dict[str, Any] = {
            "type": "object",
            "required": ["question", "related_nodes", "status"],
            "properties": {
                "question": {"type": "string"},
                "related_nodes": {"type": "array", "items": {"type": "string"}},
                "status": {"type": "string"},
            },
            "additionalProperties": False,
        }
        return {
            "type": "object",
            "required": ["curriculum"],
            "properties": {
                "curriculum": {
                    "type": "object",
                    "required": ["topic", "nodes", "open_questions"],
                    "properties": {
                        "topic": {"type": "string"},
                        "nodes": {"type": "array", "items": node_schema},
                        "open_questions": {
                            "type": ["array", "null"],
                            "items": open_question_schema,
                        },
                    },
                    "additionalProperties": False,
                }
            },
            "additionalProperties": False,
        }
    return {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }
