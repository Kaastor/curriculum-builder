"""Typed domain models for topic spec and curriculum artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class Constraints:
    hours_per_week: float
    total_hours_min: float
    total_hours_max: float
    depth: str
    node_count_min: int | None
    node_count_max: int | None
    max_prerequisites_per_node: int | None

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "Constraints":
        return cls(
            hours_per_week=float(payload.get("hours_per_week", 6.0)),
            total_hours_min=float(payload.get("total_hours_min", 8.0)),
            total_hours_max=float(payload.get("total_hours_max", 40.0)),
            depth=str(payload.get("depth", "practical")),
            node_count_min=_to_int_or_none(payload.get("node_count_min")),
            node_count_max=_to_int_or_none(payload.get("node_count_max")),
            max_prerequisites_per_node=_to_int_or_none(payload.get("max_prerequisites_per_node")),
        )


@dataclass(slots=True, frozen=True)
class ContextPack:
    domain: str | None
    focus_terms: tuple[str, ...]
    local_paths: tuple[str, ...]
    preferred_resource_kinds: tuple[str, ...]
    required_outcomes: tuple[str, ...]

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "ContextPack":
        domain_raw = payload.get("domain")
        domain = str(domain_raw).strip() if isinstance(domain_raw, str) and domain_raw.strip() else None
        return cls(
            domain=domain,
            focus_terms=_string_tuple(payload.get("focus_terms")),
            local_paths=_string_tuple(payload.get("local_paths")),
            preferred_resource_kinds=_string_tuple(payload.get("preferred_resource_kinds")),
            required_outcomes=_string_tuple(payload.get("required_outcomes")),
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.domain is not None:
            payload["domain"] = self.domain
        if self.focus_terms:
            payload["focus_terms"] = list(self.focus_terms)
        if self.local_paths:
            payload["local_paths"] = list(self.local_paths)
        if self.preferred_resource_kinds:
            payload["preferred_resource_kinds"] = list(self.preferred_resource_kinds)
        if self.required_outcomes:
            payload["required_outcomes"] = list(self.required_outcomes)
        return payload


@dataclass(slots=True, frozen=True)
class TopicSpec:
    spec_version: str
    goal: str
    audience: str
    prerequisites: tuple[str, ...]
    scope_in: tuple[str, ...]
    scope_out: tuple[str, ...]
    constraints: Constraints
    domain_mode: str
    evidence_mode: str
    misconceptions: tuple[str, ...]
    context_pack: ContextPack | None

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "TopicSpec":
        constraints_raw = payload.get("constraints", {})
        constraints = Constraints.from_mapping(
            constraints_raw if isinstance(constraints_raw, dict) else {}
        )
        context_raw = payload.get("context_pack")
        context_pack = ContextPack.from_mapping(context_raw) if isinstance(context_raw, dict) else None

        return cls(
            spec_version=str(payload.get("spec_version", "1.0")),
            goal=str(payload.get("goal", "")).strip(),
            audience=str(payload.get("audience", "")).strip(),
            prerequisites=_string_tuple(payload.get("prerequisites")),
            scope_in=_string_tuple(payload.get("scope_in")),
            scope_out=_string_tuple(payload.get("scope_out")),
            constraints=constraints,
            domain_mode=str(payload.get("domain_mode", "mature")),
            evidence_mode=str(payload.get("evidence_mode", "minimal")),
            misconceptions=_string_tuple(payload.get("misconceptions")),
            context_pack=context_pack,
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "spec_version": self.spec_version,
            "goal": self.goal,
            "audience": self.audience,
            "prerequisites": list(self.prerequisites),
            "scope_in": list(self.scope_in),
            "scope_out": list(self.scope_out),
            "constraints": {
                "hours_per_week": self.constraints.hours_per_week,
                "total_hours_min": self.constraints.total_hours_min,
                "total_hours_max": self.constraints.total_hours_max,
                "depth": self.constraints.depth,
                "node_count_min": self.constraints.node_count_min,
                "node_count_max": self.constraints.node_count_max,
                "max_prerequisites_per_node": self.constraints.max_prerequisites_per_node,
            },
            "domain_mode": self.domain_mode,
            "evidence_mode": self.evidence_mode,
            "misconceptions": list(self.misconceptions),
        }
        if self.context_pack is not None:
            context_payload = self.context_pack.to_dict()
            if context_payload:
                payload["context_pack"] = context_payload
        return payload


@dataclass(slots=True, frozen=True)
class Resource:
    title: str
    url: str
    kind: str
    role: str
    citation: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {
            "title": self.title,
            "url": self.url,
            "kind": self.kind,
            "role": self.role,
        }
        if self.citation is not None:
            payload["citation"] = self.citation
        return payload


@dataclass(slots=True, frozen=True)
class MasteryCheck:
    task: str
    pass_criteria: str

    def to_dict(self) -> dict[str, str]:
        return {"task": self.task, "pass_criteria": self.pass_criteria}


@dataclass(slots=True, frozen=True)
class CurriculumNode:
    id: str
    title: str
    capability: str
    prerequisites: tuple[str, ...]
    core_ideas: tuple[str, ...]
    pitfalls: tuple[str, ...]
    mastery_check: MasteryCheck
    estimate_minutes: float
    resources: tuple[Resource, ...]
    estimate_confidence: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "title": self.title,
            "capability": self.capability,
            "prerequisites": list(self.prerequisites),
            "core_ideas": list(self.core_ideas),
            "pitfalls": list(self.pitfalls),
            "mastery_check": self.mastery_check.to_dict(),
            "estimate_minutes": self.estimate_minutes,
            "resources": [item.to_dict() for item in self.resources],
        }
        if self.estimate_confidence is not None:
            payload["estimate_confidence"] = self.estimate_confidence
        return payload


@dataclass(slots=True, frozen=True)
class OpenQuestion:
    question: str
    related_nodes: tuple[str, ...]
    status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "question": self.question,
            "related_nodes": list(self.related_nodes),
            "status": self.status,
        }


@dataclass(slots=True, frozen=True)
class Curriculum:
    topic: str
    nodes: tuple[CurriculumNode, ...]
    open_questions: tuple[OpenQuestion, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "topic": self.topic,
            "nodes": [node.to_dict() for node in self.nodes],
        }
        if self.open_questions:
            payload["open_questions"] = [q.to_dict() for q in self.open_questions]
        return payload


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    cleaned = [str(item).strip() for item in value if isinstance(item, str) and item.strip()]
    return tuple(cleaned)


def _to_int_or_none(value: Any) -> int | None:
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None
