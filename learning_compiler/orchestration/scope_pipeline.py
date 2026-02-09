"""Scope-driven topic-spec synthesis and artifact emission."""

from __future__ import annotations

from pathlib import Path

from learning_compiler.agent import ScopeArtifactType, ScopeIngestMode, build_scope_artifact
from learning_compiler.orchestration.fs import write_json
from learning_compiler.orchestration.scope_selection import selected_scope_text
from learning_compiler.orchestration.scope_topic_spec import display_path, topic_spec_from_scope_text
from learning_compiler.orchestration.types import RunPaths


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
    selected_text = selected_scope_text(
        scope_path,
        mode=mode,
        section_filters=section_filters,
    )
    paths.scope_document.parent.mkdir(parents=True, exist_ok=True)
    paths.scope_document.write_text(selected_text, encoding="utf-8")

    topic_spec = topic_spec_from_scope_text(
        selected_scope_text=selected_text,
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
            "scope_file_for_generation": display_path(paths.scope_document),
            "selection_mode": mode.value,
            "section_filters": list(section_filters),
            "scope_preview": _artifact_payload_preview(selected_text),
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
            "scope_file_for_generation": display_path(paths.scope_document),
            "selection_mode": mode.value,
            "section_filters": list(section_filters),
        },
    )
    write_json(paths.scope_concepts, concepts_envelope.to_dict())
    write_json(paths.scope_dag, dag_envelope.to_dict())
