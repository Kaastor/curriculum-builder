"""Versioned scope artifact envelope helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from learning_compiler.agent.scope_contracts import (
    ScopeArtifactEnvelope,
    ScopeArtifactType,
    ScopeIngestMode,
)
from learning_compiler.agent.scope_policy import ScopeSynthesisPolicy
from learning_compiler.errors import ErrorCode, LearningCompilerError


def build_scope_artifact(
    *,
    artifact_type: ScopeArtifactType,
    source_path: Path,
    mode: ScopeIngestMode,
    section_filters: tuple[str, ...],
    policy: ScopeSynthesisPolicy,
    payload: dict[str, Any],
) -> ScopeArtifactEnvelope:
    return ScopeArtifactEnvelope(
        schema_version=policy.artifact_schema_version,
        artifact_type=artifact_type,
        source_path=str(source_path),
        mode=mode,
        section_filters=section_filters,
        policy_snapshot=policy.snapshot(),
        payload=payload,
    )


def parse_scope_artifact(payload: dict[str, Any], expected_type: ScopeArtifactType) -> ScopeArtifactEnvelope:
    """Validate and parse persisted scope artifact envelopes."""
    try:
        envelope = ScopeArtifactEnvelope.from_mapping(payload)
    except ValueError as exc:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            "Invalid scope artifact payload.",
            {"error": str(exc)},
        ) from exc
    if envelope.artifact_type != expected_type:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Unexpected scope artifact type: expected {expected_type.value}",
            {"actual": envelope.artifact_type.value},
        )
    return envelope


def load_scope_artifact(path: Path, expected_type: ScopeArtifactType) -> ScopeArtifactEnvelope:
    """Load and validate a persisted scope artifact envelope from disk."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise LearningCompilerError(
            ErrorCode.NOT_FOUND,
            f"Scope artifact file not found: {path}",
            {"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Invalid JSON in scope artifact: {path}",
            {"path": str(path)},
        ) from exc
    if not isinstance(payload, dict):
        raise LearningCompilerError(
            ErrorCode.INVALID_ARGUMENT,
            f"Scope artifact root must be an object: {path}",
            {"path": str(path)},
        )
    return parse_scope_artifact(payload, expected_type)

