"""Typed contracts for scope document extraction and inferred concept DAGs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ScopeIngestMode(str, Enum):
    """How markdown content should be interpreted as learning scope."""

    FULL = "full"
    SECTION = "section"
    SEED_LIST = "seed-list"


class ScopeRelation(str, Enum):
    """Semantic relation between inferred concepts."""

    PREREQUISITE = "prerequisite"
    RECOMMENDED_BEFORE = "recommended_before"
    RELATED = "related"


@dataclass(slots=True, frozen=True)
class ScopeItem:
    """Normalized unit extracted from source markdown."""

    id: str
    text: str
    kind: str
    source_path: str
    heading_path: tuple[str, ...]
    line_span: tuple[int, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "kind": self.kind,
            "source_path": self.source_path,
            "heading_path": list(self.heading_path),
            "line_span": [self.line_span[0], self.line_span[1]],
        }


@dataclass(slots=True, frozen=True)
class ConceptCandidate:
    """Atomic concept candidate derived from one or more scope items."""

    id: str
    title: str
    source_item_ids: tuple[str, ...]
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "source_item_ids": list(self.source_item_ids),
            "confidence": self.confidence,
        }


@dataclass(slots=True, frozen=True)
class ConceptEdgeCandidate:
    """Potential graph relation between two concept candidates."""

    source_id: str
    target_id: str
    relation: ScopeRelation
    confidence: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation": self.relation.value,
            "confidence": self.confidence,
            "reason": self.reason,
        }


@dataclass(slots=True, frozen=True)
class ScopeExtraction:
    """Extraction result from source markdown."""

    source_path: str
    mode: ScopeIngestMode
    section_filters: tuple[str, ...]
    items: tuple[ScopeItem, ...]
    concepts: tuple[ConceptCandidate, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_path": self.source_path,
            "mode": self.mode.value,
            "section_filters": list(self.section_filters),
            "items": [item.to_dict() for item in self.items],
            "concepts": [concept.to_dict() for concept in self.concepts],
        }


@dataclass(slots=True, frozen=True)
class ScopeDag:
    """Deterministic DAG-style ordering inferred from extracted concepts."""

    concepts: tuple[ConceptCandidate, ...]
    hard_edges: tuple[ConceptEdgeCandidate, ...]
    soft_edges: tuple[ConceptEdgeCandidate, ...]
    topological_order: tuple[str, ...]
    phases: tuple[tuple[str, ...], ...]
    ambiguities: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [concept.to_dict() for concept in self.concepts],
            "hard_edges": [edge.to_dict() for edge in self.hard_edges],
            "soft_edges": [edge.to_dict() for edge in self.soft_edges],
            "topological_order": list(self.topological_order),
            "phases": [list(phase) for phase in self.phases],
            "ambiguities": list(self.ambiguities),
        }

