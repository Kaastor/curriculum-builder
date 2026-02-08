"""Typed contracts for scope ingestion artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ScopeIngestMode(str, Enum):
    """How markdown content should be selected from source scope."""

    FULL = "full"
    SECTION = "section"
    SEED_LIST = "seed-list"


class ScopeArtifactType(str, Enum):
    """Versioned artifact envelope types."""

    CONCEPTS = "scope_concepts"
    DAG = "scope_dag"


@dataclass(slots=True, frozen=True)
class ScopeArtifactEnvelope:
    """Versioned envelope used for persisted scope artifacts."""

    schema_version: str
    artifact_type: ScopeArtifactType
    source_path: str
    mode: ScopeIngestMode
    section_filters: tuple[str, ...]
    policy_snapshot: dict[str, Any]
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_type": self.artifact_type.value,
            "source_path": self.source_path,
            "mode": self.mode.value,
            "section_filters": list(self.section_filters),
            "policy_snapshot": dict(self.policy_snapshot),
            "payload": self.payload,
        }

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "ScopeArtifactEnvelope":
        schema_version = str(payload.get("schema_version", "")).strip()
        artifact_raw = str(payload.get("artifact_type", "")).strip().lower()
        mode_raw = str(payload.get("mode", "")).strip().lower()
        source_path = str(payload.get("source_path", "")).strip()
        section_filters_raw = payload.get("section_filters", [])
        policy_snapshot = payload.get("policy_snapshot", {})
        nested_payload = payload.get("payload")

        if schema_version != "1.0":
            raise ValueError("scope artifact schema_version must be '1.0'")
        try:
            artifact_type = ScopeArtifactType(artifact_raw)
        except ValueError as exc:
            raise ValueError(f"invalid scope artifact_type: {artifact_raw}") from exc
        try:
            mode = ScopeIngestMode(mode_raw)
        except ValueError as exc:
            raise ValueError(f"invalid scope artifact mode: {mode_raw}") from exc
        if not source_path:
            raise ValueError("scope artifact source_path is required")
        if not isinstance(section_filters_raw, list) or not all(
            isinstance(item, str) and item.strip() for item in section_filters_raw
        ):
            raise ValueError("scope artifact section_filters must be a list of non-empty strings")
        if not isinstance(policy_snapshot, dict):
            raise ValueError("scope artifact policy_snapshot must be an object")
        if not isinstance(nested_payload, dict):
            raise ValueError("scope artifact payload must be an object")

        return cls(
            schema_version=schema_version,
            artifact_type=artifact_type,
            source_path=source_path,
            mode=mode,
            section_filters=tuple(item.strip() for item in section_filters_raw),
            policy_snapshot=policy_snapshot,
            payload=nested_payload,
        )
