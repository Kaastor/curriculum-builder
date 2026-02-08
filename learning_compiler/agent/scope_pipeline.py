"""Scope document -> concept DAG -> topic spec synthesis pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from learning_compiler.agent.concept_dag_builder import build_concept_dag
from learning_compiler.agent.scope_contracts import ScopeDag, ScopeExtraction, ScopeIngestMode
from learning_compiler.agent.scope_extractor import extract_scope
from learning_compiler.errors import ErrorCode, LearningCompilerError
from learning_compiler.validator.topic_spec import validate_topic_spec_contract


@dataclass(slots=True, frozen=True)
class ScopeCompilationResult:
    """Artifacts synthesized from a markdown scope input."""

    topic_spec: dict[str, Any]
    scope_concepts: dict[str, Any]
    scope_dag: dict[str, Any]


def _display_path(scope_path: Path) -> str:
    try:
        return str(scope_path.relative_to(Path.cwd()))
    except ValueError:
        return str(scope_path)


def _title_from_extraction(extraction: ScopeExtraction) -> str:
    heading_items = [item.text for item in extraction.items if item.kind == "heading"]
    if heading_items:
        return heading_items[0]
    return Path(extraction.source_path).stem.replace("-", " ").replace("_", " ").title()


def _focus_terms(concepts: tuple[str, ...], max_terms: int = 8) -> tuple[str, ...]:
    seen: set[str] = set()
    terms: list[str] = []
    for title in concepts:
        for token in re.findall(r"[a-z0-9]+", title.lower()):
            if len(token) <= 3:
                continue
            if token in seen:
                continue
            seen.add(token)
            terms.append(token)
            if len(terms) >= max_terms:
                return tuple(terms)
    return tuple(terms)


def _scope_lists(dag: ScopeDag) -> tuple[list[str], list[str]]:
    by_id = {concept.id: concept.title for concept in dag.concepts}
    ordered_titles = [by_id[concept_id] for concept_id in dag.topological_order if concept_id in by_id]
    if len(ordered_titles) > 40:
        ordered_titles = ordered_titles[:40]

    prerequisite_titles: list[str] = []
    for phase_index, phase in enumerate(dag.phases):
        if phase_index >= 2:
            break
        for concept_id in phase:
            title = by_id.get(concept_id)
            if title is None:
                continue
            prerequisite_titles.append(title)
            if len(prerequisite_titles) >= 4:
                return ordered_titles, prerequisite_titles
    return ordered_titles, prerequisite_titles


def _topic_spec_from_scope(scope_path: Path, extraction: ScopeExtraction, dag: ScopeDag) -> dict[str, Any]:
    title = _title_from_extraction(extraction)
    scope_in, prerequisites = _scope_lists(dag)
    if not scope_in:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "Cannot build topic spec: no ordered concepts available.",
            {"scope_file": str(scope_path)},
        )

    node_count_min = max(6, min(12, max(6, len(scope_in) // 2)))
    node_count_max = max(node_count_min + 2, min(24, len(scope_in)))
    total_hours_min = float(max(10, round(node_count_min * 1.5)))
    total_hours_max = float(max(total_hours_min + 4.0, round(node_count_max * 2.2)))

    focus_terms = _focus_terms(tuple(scope_in))
    ambiguity_hints = list(dag.ambiguities[:3])
    misconceptions = [
        "Assuming all listed topics can be learned in arbitrary order.",
        "Treating familiarity as equivalent to demonstrated mastery.",
    ]
    misconceptions.extend(
        f"Ordering ambiguity: {hint}" for hint in ambiguity_hints if hint
    )

    return {
        "spec_version": "1.0",
        "goal": f"Build practical mastery across {title}.",
        "audience": "Self-directed learner seeking an ordered, actionable path from an unordered scope.",
        "prerequisites": prerequisites or ["Commitment to consistent technical study and practice."],
        "scope_in": scope_in,
        "scope_out": ["Topics not represented in the provided scope document."],
        "constraints": {
            "hours_per_week": 6.0,
            "total_hours_min": total_hours_min,
            "total_hours_max": total_hours_max,
            "depth": "practical",
            "node_count_min": node_count_min,
            "node_count_max": node_count_max,
            "max_prerequisites_per_node": 3,
        },
        "domain_mode": "mature",
        "evidence_mode": "standard",
        "misconceptions": misconceptions[:4],
        "context_pack": {
            "domain": title,
            "focus_terms": list(focus_terms),
            "local_paths": [_display_path(scope_path)],
            "required_outcomes": ["Implement one practical artifact per phase.", "Run explicit verification checks."],
        },
    }


def compile_scope_document(
    scope_path: Path,
    *,
    mode: ScopeIngestMode = ScopeIngestMode.FULL,
    section_filters: tuple[str, ...] = (),
) -> ScopeCompilationResult:
    """Compile a markdown scope artifact into topic spec and diagnostic DAG artifacts."""
    extraction = extract_scope(scope_path, mode=mode, section_filters=section_filters)
    dag = build_concept_dag(extraction.concepts)
    topic_spec = _topic_spec_from_scope(scope_path, extraction, dag)

    errors = validate_topic_spec_contract(topic_spec)
    if errors:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "Generated topic spec from scope document failed contract validation.",
            {"scope_file": str(scope_path), "errors": errors[:10]},
        )

    return ScopeCompilationResult(
        topic_spec=topic_spec,
        scope_concepts=extraction.to_dict(),
        scope_dag=dag.to_dict(),
    )

