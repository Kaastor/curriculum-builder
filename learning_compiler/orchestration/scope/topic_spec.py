"""Topic-spec synthesis for scope-driven orchestration runs."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from learning_compiler.agent import ScopeIngestMode
from learning_compiler.errors import ErrorCode, LearningCompilerError
from learning_compiler.markdown_scope import markdown_phrase_candidates
from learning_compiler.validator.topic_spec import validate_topic_spec_contract


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _is_actionable_scope_phrase(phrase: str) -> bool:
    lowered = phrase.lower()
    if len(lowered) < 4:
        return False
    if re.fullmatch(r"[0-9.\- ]+", lowered):
        return False
    if lowered in {"scope", "overview", "introduction"}:
        return False
    return True


def scope_in_items_from_selected_scope(scope_text: str, max_items: int = 60) -> list[str]:
    candidates = markdown_phrase_candidates(
        scope_text,
        max_heading_depth=3,
        min_sentence_words=1,
    )
    actionable = [item for item in candidates if _is_actionable_scope_phrase(item)]
    return actionable[:max_items]


def topic_spec_from_scope_text(
    *,
    selected_scope_text: str,
    scope_file_for_generation: Path,
    source_scope_path: Path,
    mode: ScopeIngestMode,
    section_filters: tuple[str, ...],
) -> dict[str, Any]:
    domain = source_scope_path.stem.replace("-", " ").replace("_", " ").strip().title()
    scope_ref = display_path(source_scope_path)

    scope_in = scope_in_items_from_selected_scope(selected_scope_text)
    if not scope_in:
        scope_in = ["Scope-driven implementation and validation practice"]

    scope_size = len(scope_in)
    node_count_min = max(8, min(16, max(8, scope_size // 3)))
    node_count_max = max(node_count_min + 4, min(40, scope_size + 6))
    total_hours_min = float(max(12, round(node_count_min * 1.5)))
    total_hours_max = float(max(total_hours_min + 8.0, round(node_count_max * 2.0)))
    scope_summary = (
        f"Selected section(s): {', '.join(section_filters)}"
        if mode == ScopeIngestMode.SECTION and section_filters
        else "Full scope document"
    )
    prerequisites = scope_in[:4]
    if not prerequisites:
        prerequisites = [
            "Baseline software engineering literacy.",
            "Ability to study and implement from technical documentation.",
        ]

    topic_spec: dict[str, Any] = {
        "spec_version": "1.0",
        "goal": f"Build practical mastery from the provided scope document ({scope_ref}).",
        "audience": "Self-directed learner with unordered topics who needs an actionable DAG.",
        "prerequisites": prerequisites,
        "scope_in": scope_in,
        "scope_out": ["Topics not present in the provided scope document."],
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
        "misconceptions": [
            "Assuming unordered topics can be learned effectively without explicit dependency modeling.",
            "Treating familiarity with terms as equivalent to demonstrated implementation ability.",
        ],
        "context_pack": {
            "domain": domain or "Scope-driven learning",
            "focus_terms": [
                "scope-driven curriculum",
                "dependency ordering",
                "actionable implementation",
                "verification-first learning",
            ],
            "local_paths": [display_path(scope_file_for_generation)],
            "preferred_resource_kinds": ["doc", "spec"],
            "required_outcomes": [
                "Produce a coherent DAG curriculum grounded directly in scope.md.",
                "Include explicit implementation and validation steps per node.",
                scope_summary,
            ],
        },
    }
    errors = validate_topic_spec_contract(topic_spec)
    if errors:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "Generated topic spec from scope document failed contract validation.",
            {"scope_file": str(source_scope_path), "errors": errors[:10]},
        )
    return topic_spec
