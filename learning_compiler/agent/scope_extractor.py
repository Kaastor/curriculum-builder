"""Deterministic extraction of concept candidates from scope markdown."""

from __future__ import annotations

import re
from pathlib import Path

from learning_compiler.agent.scope_contracts import (
    ConceptCandidate,
    ScopeExtraction,
    ScopeIngestMode,
    ScopeItem,
)
from learning_compiler.agent.scope_markdown import (
    build_id,
    canonical_key,
    collect_scope_items,
    normalize_text,
)
from learning_compiler.errors import ErrorCode, LearningCompilerError


def _split_fragments(text: str) -> tuple[str, ...]:
    cleaned = normalize_text(text)
    if not cleaned:
        return ()

    split_input = cleaned
    if ":" in split_input:
        left, right = split_input.split(":", 1)
        if len(left.split()) <= 4 and right.strip():
            split_input = right.strip()

    parts = re.split(
        r"\s*(?:,|;|\||/|\band\b|\bthen\b)\s*",
        split_input,
        flags=re.IGNORECASE,
    )
    filtered = [normalize_text(part) for part in parts if normalize_text(part)]
    if len(filtered) <= 1:
        return (split_input,)

    compact = tuple(part for part in filtered if len(part.split()) <= 14)
    return compact or (split_input,)


def _concept_confidence(item_kind: str, token_count: int) -> float:
    score = 0.5
    if item_kind == "bullet":
        score += 0.25
    elif item_kind == "heading":
        score += 0.15
    elif item_kind == "table_cell":
        score += 0.2
    else:
        score += 0.05

    if 2 <= token_count <= 8:
        score += 0.15
    elif token_count > 12:
        score -= 0.1

    return round(max(0.35, min(0.95, score)), 2)


def _extract_concepts(items: tuple[ScopeItem, ...], max_concepts: int = 120) -> tuple[ConceptCandidate, ...]:
    ordered: dict[str, ConceptCandidate] = {}
    concept_sources: dict[str, list[str]] = {}

    for item in items:
        for fragment in _split_fragments(item.text):
            key = canonical_key(fragment)
            if not key or len(key) < 3:
                continue
            if key in {"l0", "l1", "l2", "l3", "l4"}:
                continue

            concept_id = build_id("C", key)
            if concept_id not in ordered:
                title = fragment[0].upper() + fragment[1:] if len(fragment) > 1 else fragment.upper()
                ordered[concept_id] = ConceptCandidate(
                    id=concept_id,
                    title=title,
                    source_item_ids=(item.id,),
                    confidence=_concept_confidence(item.kind, len(fragment.split())),
                )
                concept_sources[concept_id] = [item.id]
            else:
                concept_sources[concept_id].append(item.id)

            if len(ordered) >= max_concepts:
                break
        if len(ordered) >= max_concepts:
            break

    concepts: list[ConceptCandidate] = []
    for concept_id, concept in ordered.items():
        source_ids = tuple(dict.fromkeys(concept_sources[concept_id]))
        confidence_bonus = 0.05 if len(source_ids) > 1 else 0.0
        concepts.append(
            ConceptCandidate(
                id=concept.id,
                title=concept.title,
                source_item_ids=source_ids,
                confidence=round(min(0.98, concept.confidence + confidence_bonus), 2),
            )
        )
    return tuple(concepts)


def extract_scope(
    scope_path: Path,
    *,
    mode: ScopeIngestMode = ScopeIngestMode.FULL,
    section_filters: tuple[str, ...] = (),
    max_concepts: int = 120,
) -> ScopeExtraction:
    """Extract deterministic concept candidates from a markdown scope document."""
    if not scope_path.exists():
        raise LearningCompilerError(
            ErrorCode.NOT_FOUND,
            f"Scope file not found: {scope_path}",
            {"scope_file": str(scope_path)},
        )

    if mode == ScopeIngestMode.SECTION and not section_filters:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "Section mode requires at least one section filter.",
            {"scope_file": str(scope_path), "mode": mode.value},
        )

    normalized_filters = tuple(filter(None, (canonical_key(item) for item in section_filters)))
    items = collect_scope_items(scope_path, mode, normalized_filters)
    concepts = _extract_concepts(items, max_concepts=max_concepts)
    if not concepts:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "No usable concepts were extracted from scope document.",
            {
                "scope_file": str(scope_path),
                "mode": mode.value,
                "section_filters": list(section_filters),
            },
        )

    return ScopeExtraction(
        source_path=str(scope_path),
        mode=mode,
        section_filters=normalized_filters,
        items=items,
        concepts=concepts,
    )
