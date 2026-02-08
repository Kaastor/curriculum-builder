"""Stable public interfaces for generation, validation, and orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from learning_compiler.agent import (
    ScopeCompilationResult,
    ScopeIngestMode,
    compile_scope_document,
    generate_curriculum,
    generate_curriculum_file,
)
from learning_compiler.domain import TopicSpec
from learning_compiler.orchestration.cli import main as orchestration_main
from learning_compiler.validator.core import validate
from learning_compiler.validator.types import ValidationResult


@dataclass(slots=True)
class AgentAPI:
    """Public agent-facing API."""

    def generate(self, topic_spec: TopicSpec) -> dict[str, Any]:
        return generate_curriculum(topic_spec.to_dict())

    def generate_from_mapping(self, topic_spec: dict[str, Any]) -> dict[str, Any]:
        return generate_curriculum(topic_spec)

    def generate_to_file(self, topic_spec_path: Path, curriculum_path: Path) -> dict[str, Any]:
        return generate_curriculum_file(topic_spec_path, curriculum_path)

    def compile_scope(
        self,
        scope_path: Path,
        *,
        mode: ScopeIngestMode = ScopeIngestMode.FULL,
        section_filters: tuple[str, ...] = (),
    ) -> ScopeCompilationResult:
        return compile_scope_document(
            scope_path,
            mode=mode,
            section_filters=section_filters,
        )


@dataclass(slots=True)
class ValidatorAPI:
    """Public validator API."""

    def validate(
        self,
        curriculum_path: Path,
        topic_spec_path: Path | None = None,
    ) -> ValidationResult:
        return validate(curriculum_path, topic_spec_path)


@dataclass(slots=True)
class OrchestrationAPI:
    """Public orchestration API."""

    def run_cli(self, argv: list[str]) -> int:
        return orchestration_main(argv)
