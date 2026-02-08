"""Helpers for scope-document ingestion in orchestration commands."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Any

from learning_compiler.agent import (
    ScopeArtifactType,
    ScopeIngestMode,
    build_scope_artifact,
)
from learning_compiler.config import load_config
from learning_compiler.errors import ErrorCode, LearningCompilerError
from learning_compiler.orchestration.fs import resolve_within, write_json
from learning_compiler.orchestration.types import RunPaths
from learning_compiler.validator.topic_spec import validate_topic_spec_contract


def scope_file_from_args(args: argparse.Namespace) -> str | None:
    value = getattr(args, "scope_file", None)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-file must be a non-empty path when provided.",
        )
    return value.strip()


def scope_sections_from_args(args: argparse.Namespace) -> tuple[str, ...]:
    raw = getattr(args, "scope_section", [])
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-section must be provided as repeatable strings.",
        )
    sections = [str(value).strip() for value in raw if str(value).strip()]
    return tuple(sections)


def scope_mode_from_args(args: argparse.Namespace) -> ScopeIngestMode:
    raw = getattr(args, "scope_mode", ScopeIngestMode.FULL.value)
    if not isinstance(raw, str):
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-mode must be a string.",
        )
    normalized = raw.strip().lower()
    try:
        return ScopeIngestMode(normalized)
    except ValueError as exc:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-mode must be one of: full, section, seed-list.",
            {"scope_mode": raw},
        ) from exc


def validate_scope_selection(mode: ScopeIngestMode, sections: tuple[str, ...]) -> None:
    if mode == ScopeIngestMode.SECTION and not sections:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "--scope-mode section requires at least one --scope-section value.",
        )


def resolve_scope_path(run_dir: Path, scope_file: str) -> Path:
    candidate = Path(scope_file).expanduser()
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    else:
        candidate = candidate.resolve()

    if not candidate.exists() or not candidate.is_file():
        raise LearningCompilerError(
            ErrorCode.NOT_FOUND,
            f"Scope file not found: {scope_file}",
            {"scope_file": str(candidate)},
        )

    config = load_config()
    allowed_roots = (config.repo_root.resolve(), config.runs_dir.resolve(), run_dir.resolve())
    for root in allowed_roots:
        try:
            resolve_within(root, candidate)
            return candidate
        except LearningCompilerError:
            continue

    raise LearningCompilerError(
        ErrorCode.INVALID_ARGUMENT,
        "Scope file must be inside the repository, runs directory, or current run directory.",
        {"scope_file": str(candidate)},
    )


def _canonical_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _section_match(heading_path: tuple[str, ...], section_filters: tuple[str, ...]) -> bool:
    if not section_filters:
        return True
    normalized_path = " / ".join(_canonical_key(heading) for heading in heading_path if heading.strip())
    return any(filter_text in normalized_path for filter_text in section_filters)


def _selected_scope_text(
    scope_path: Path,
    *,
    mode: ScopeIngestMode,
    section_filters: tuple[str, ...],
) -> str:
    lines = scope_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Scope document is empty: {scope_path}",
            {"scope_file": str(scope_path)},
        )

    heading_re = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
    bullet_re = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")

    selected: list[str] = []
    heading_stack: list[str] = []
    in_code_block = False
    in_front_matter = bool(lines and lines[0].strip() == "---")

    normalized_filters = tuple(
        filter_text
        for filter_text in (_canonical_key(item) for item in section_filters)
        if filter_text
    )

    for index, raw_line in enumerate(lines):
        line_no = index + 1
        stripped = raw_line.strip()

        if in_front_matter:
            if line_no == 1:
                continue
            if stripped == "---":
                in_front_matter = False
            continue

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        heading_match = heading_re.match(raw_line)
        if heading_match:
            depth = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            while len(heading_stack) >= depth:
                heading_stack.pop()
            heading_stack.append(heading)
            if mode == ScopeIngestMode.SEED_LIST:
                continue
            if mode == ScopeIngestMode.SECTION and not _section_match(tuple(heading_stack), normalized_filters):
                continue
            selected.append(raw_line)
            continue

        if mode == ScopeIngestMode.SECTION and not _section_match(tuple(heading_stack), normalized_filters):
            continue
        if mode == ScopeIngestMode.SEED_LIST and not bullet_re.match(raw_line):
            continue
        if stripped:
            selected.append(raw_line)

    normalized = "\n".join(selected).strip()
    if not normalized:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "Selected scope content is empty after applying mode/section filters.",
            {"scope_file": str(scope_path), "mode": mode.value, "section_filters": list(section_filters)},
        )
    return normalized + "\n"


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _normalize_scope_phrase(raw: str) -> str:
    value = raw.strip()
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("`", "")
    value = re.sub(r"\s+", " ", value).strip(" -:;,.")
    return value


def _is_actionable_scope_phrase(phrase: str) -> bool:
    lowered = phrase.lower()
    if len(lowered) < 4:
        return False
    if re.fullmatch(r"[0-9.\- ]+", lowered):
        return False
    if lowered in {"scope", "overview", "introduction"}:
        return False
    return True


def _scope_in_items_from_selected_scope(scope_text: str, max_items: int = 60) -> list[str]:
    heading_re = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
    bullet_re = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*?)\s*$")

    candidates: list[str] = []
    for raw_line in scope_text.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        heading_match = heading_re.match(raw_line)
        if heading_match:
            depth = len(heading_match.group(1))
            if depth <= 3:
                heading = _normalize_scope_phrase(heading_match.group(2))
                if _is_actionable_scope_phrase(heading):
                    candidates.append(heading)
            continue

        bullet_match = bullet_re.match(raw_line)
        if bullet_match:
            bullet = _normalize_scope_phrase(bullet_match.group(1))
            if _is_actionable_scope_phrase(bullet):
                candidates.append(bullet)
            continue

        for fragment in re.split(r"[.!?;]+", stripped):
            phrase = _normalize_scope_phrase(fragment)
            if _is_actionable_scope_phrase(phrase):
                candidates.append(phrase)

    deduped: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= max_items:
            break
    return deduped


def _topic_spec_from_scope_text(
    *,
    selected_scope_text: str,
    scope_file_for_generation: Path,
    source_scope_path: Path,
    mode: ScopeIngestMode,
    section_filters: tuple[str, ...],
) -> dict[str, Any]:
    domain = source_scope_path.stem.replace("-", " ").replace("_", " ").strip().title()
    scope_ref = _display_path(source_scope_path)

    scope_in = _scope_in_items_from_selected_scope(selected_scope_text)
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
            "local_paths": [_display_path(scope_file_for_generation)],
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


def _artifact_payload_preview(scope_text: str, max_chars: int = 6000) -> str:
    if len(scope_text) <= max_chars:
        return scope_text
    return scope_text[:max_chars] + "\n...[truncated]..."


def synthesize_topic_spec_from_scope(
    paths: RunPaths,
    *,
    scope_path: Path,
    mode: ScopeIngestMode,
    section_filters: tuple[str, ...],
) -> None:
    selected_scope_text = _selected_scope_text(
        scope_path,
        mode=mode,
        section_filters=section_filters,
    )
    paths.scope_document.parent.mkdir(parents=True, exist_ok=True)
    paths.scope_document.write_text(selected_scope_text, encoding="utf-8")

    topic_spec = _topic_spec_from_scope_text(
        selected_scope_text=selected_scope_text,
        scope_file_for_generation=paths.scope_document,
        source_scope_path=scope_path,
        mode=mode,
        section_filters=section_filters,
    )
    write_json(paths.topic_spec, topic_spec)

    concepts_envelope = build_scope_artifact(
        artifact_type=ScopeArtifactType.CONCEPTS,
        source_path=scope_path,
        mode=mode,
        section_filters=section_filters,
        policy_snapshot={},
        payload={
            "selection_strategy": "direct_scope_passthrough",
            "scope_file_for_generation": _display_path(paths.scope_document),
            "selection_mode": mode.value,
            "section_filters": list(section_filters),
            "scope_preview": _artifact_payload_preview(selected_scope_text),
        },
    )
    dag_envelope = build_scope_artifact(
        artifact_type=ScopeArtifactType.DAG,
        source_path=scope_path,
        mode=mode,
        section_filters=section_filters,
        policy_snapshot={},
        payload={
            "selection_strategy": "direct_scope_passthrough",
            "notes": [
                "Generation consumes selected scope markdown directly.",
                "No heuristic concept-to-dag inference is used in this orchestration path.",
            ],
            "scope_file_for_generation": _display_path(paths.scope_document),
            "selection_mode": mode.value,
            "section_filters": list(section_filters),
        },
    )
    write_json(paths.scope_concepts, concepts_envelope.to_dict())
    write_json(paths.scope_dag, dag_envelope.to_dict())
