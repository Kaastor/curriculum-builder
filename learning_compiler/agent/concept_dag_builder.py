"""Deterministic concept ordering and DAG relation inference."""

from __future__ import annotations

from collections import defaultdict, deque
import math
import re

from learning_compiler.agent.scope_contracts import (
    ConceptCandidate,
    ConceptEdgeCandidate,
    ScopeDag,
    ScopeRelation,
)
_FOUNDATION_TOKENS = {
    "intro",
    "introduction",
    "definition",
    "definitions",
    "fundamental",
    "fundamentals",
    "basics",
    "terminology",
    "overview",
}
_ADVANCED_TOKENS = {
    "integration",
    "optimize",
    "optimization",
    "security",
    "safety",
    "governance",
    "operations",
    "runtime",
    "evaluation",
    "testing",
    "reliability",
    "scaling",
}
def _tokens(title: str) -> tuple[str, ...]:
    return tuple(token for token in re.findall(r"[a-z0-9]+", title.lower()) if len(token) > 2)
def _complexity_score(concept: ConceptCandidate) -> float:
    tokens = _tokens(concept.title)
    score = len(tokens) / 5.0
    score += sum(0.4 for token in tokens if token in _ADVANCED_TOKENS)
    score -= sum(0.3 for token in tokens if token in _FOUNDATION_TOKENS)
    return round(score, 3)
def _relevance(
    source: ConceptCandidate,
    target: ConceptCandidate,
    source_score: float,
    target_score: float,
    distance: int,
) -> float:
    source_tokens = set(_tokens(source.title))
    target_tokens = set(_tokens(target.title))
    overlap = len(source_tokens & target_tokens)
    proximity_bonus = 1.0 / max(1, distance)
    progression_bonus = max(0.0, min(2.0, target_score - source_score)) * 0.6
    return round((overlap * 1.9) + progression_bonus + proximity_bonus, 3)
def _topological_order(
    concepts: tuple[ConceptCandidate, ...],
    hard_edges: tuple[ConceptEdgeCandidate, ...],
) -> tuple[str, ...]:
    concept_ids = [concept.id for concept in concepts]
    incoming: dict[str, int] = {concept_id: 0 for concept_id in concept_ids}
    outgoing: dict[str, list[str]] = defaultdict(list)

    for edge in hard_edges:
        incoming[edge.target_id] += 1
        outgoing[edge.source_id].append(edge.target_id)

    queue = deque(sorted((cid for cid, degree in incoming.items() if degree == 0)))
    ordered: list[str] = []
    while queue:
        current = queue.popleft()
        ordered.append(current)
        for neighbor in sorted(outgoing.get(current, [])):
            incoming[neighbor] -= 1
            if incoming[neighbor] == 0:
                queue.append(neighbor)

    if len(ordered) != len(concept_ids):
        missing = sorted(set(concept_ids) - set(ordered))
        ordered.extend(missing)
    return tuple(ordered)
def _derive_phases(
    concept_ids: tuple[str, ...],
    hard_edges: tuple[ConceptEdgeCandidate, ...],
) -> tuple[tuple[str, ...], ...]:
    prereqs: dict[str, list[str]] = defaultdict(list)
    for edge in hard_edges:
        prereqs[edge.target_id].append(edge.source_id)

    levels: dict[str, int] = {}
    for concept_id in concept_ids:
        dependencies = prereqs.get(concept_id, [])
        if not dependencies:
            levels[concept_id] = 0
            continue
        levels[concept_id] = max(levels[dep] for dep in dependencies) + 1

    grouped: dict[int, list[str]] = defaultdict(list)
    for concept_id in concept_ids:
        grouped[levels[concept_id]].append(concept_id)

    return tuple(tuple(grouped[level]) for level in sorted(grouped.keys()))
def build_concept_dag(
    concepts: tuple[ConceptCandidate, ...],
    *,
    max_hard_prerequisites: int = 2,
) -> ScopeDag:
    """Infer deterministic hard and soft relations between concept candidates."""
    if not concepts:
        return ScopeDag(
            concepts=(),
            hard_edges=(),
            soft_edges=(),
            topological_order=(),
            phases=(),
            ambiguities=("No concepts available for DAG construction.",),
        )

    if len(concepts) == 1:
        single = concepts[0].id
        return ScopeDag(
            concepts=concepts,
            hard_edges=(),
            soft_edges=(),
            topological_order=(single,),
            phases=((single,),),
            ambiguities=(),
        )

    scores = {concept.id: _complexity_score(concept) for concept in concepts}
    sorted_concepts = tuple(
        sorted(
            concepts,
            key=lambda concept: (scores[concept.id], concept.title.lower(), concept.id),
        )
    )

    hard_edges: list[ConceptEdgeCandidate] = []
    soft_edges: list[ConceptEdgeCandidate] = []
    ambiguities: list[str] = []

    for index in range(1, len(sorted_concepts)):
        target = sorted_concepts[index]
        ranked_sources: list[tuple[float, ConceptCandidate]] = []
        for source_index in range(index):
            source = sorted_concepts[source_index]
            rel = _relevance(
                source,
                target,
                scores[source.id],
                scores[target.id],
                distance=index - source_index,
            )
            ranked_sources.append((rel, source))

        ranked_sources.sort(key=lambda item: (-item[0], item[1].title.lower(), item[1].id))
        chosen = [
            source
            for rel, source in ranked_sources
            if rel >= 1.9 and scores[source.id] <= (scores[target.id] + 0.35)
        ][: max_hard_prerequisites]

        if chosen:
            for source in chosen:
                rel = next(rel for rel, candidate in ranked_sources if candidate.id == source.id)
                confidence = round(min(0.95, 0.55 + (rel / 10.0)), 2)
                hard_edges.append(
                    ConceptEdgeCandidate(
                        source_id=source.id,
                        target_id=target.id,
                        relation=ScopeRelation.PREREQUISITE,
                        confidence=confidence,
                        reason="lexical overlap and complexity progression",
                    )
                )
            continue

        fallback = sorted_concepts[index - 1]
        soft_edges.append(
            ConceptEdgeCandidate(
                source_id=fallback.id,
                target_id=target.id,
                relation=ScopeRelation.RECOMMENDED_BEFORE,
                confidence=0.5,
                reason="no strong deterministic prerequisite signal",
            )
        )
        ambiguities.append(
            f"Uncertain prerequisite for '{target.title}'; kept as recommended order only."
        )

    hard_edge_keys: set[tuple[str, str, ScopeRelation]] = {
        (edge.source_id, edge.target_id, edge.relation) for edge in hard_edges
    }
    for index in range(1, len(sorted_concepts)):
        left = sorted_concepts[index - 1]
        right = sorted_concepts[index]
        if (left.id, right.id, ScopeRelation.PREREQUISITE) in hard_edge_keys:
            continue
        left_tokens = set(_tokens(left.title))
        right_tokens = set(_tokens(right.title))
        if not left_tokens.intersection(right_tokens):
            continue
        soft_edges.append(
            ConceptEdgeCandidate(
                source_id=left.id,
                target_id=right.id,
                relation=ScopeRelation.RELATED,
                confidence=0.45,
                reason="shared terminology",
            )
        )

    deduped_soft: list[ConceptEdgeCandidate] = []
    seen_soft: set[tuple[str, str, ScopeRelation]] = set()
    for edge in soft_edges:
        key = (edge.source_id, edge.target_id, edge.relation)
        if key in seen_soft:
            continue
        if key in hard_edge_keys:
            continue
        seen_soft.add(key)
        deduped_soft.append(edge)

    topo = _topological_order(sorted_concepts, tuple(hard_edges))
    phases = _derive_phases(topo, tuple(hard_edges))

    max_phase_size = max((len(phase) for phase in phases), default=1)
    if max_phase_size > int(math.sqrt(len(sorted_concepts)) + 4):
        ambiguities.append("Large phase groups detected; ordering confidence is lower within phases.")

    return ScopeDag(
        concepts=sorted_concepts,
        hard_edges=tuple(hard_edges),
        soft_edges=tuple(deduped_soft),
        topological_order=topo,
        phases=phases,
        ambiguities=tuple(ambiguities),
    )
