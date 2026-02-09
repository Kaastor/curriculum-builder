"""Agent entrypoints for curriculum generation."""

from learning_compiler.agent.contracts import CurriculumGenerator, DefaultCurriculumGenerator
from learning_compiler.agent.generator import generate_curriculum, generate_curriculum_file
from learning_compiler.agent.scope.scope_contracts import ScopeArtifactType, ScopeIngestMode
from learning_compiler.agent.scope.scope_artifacts import (
    build_scope_artifact,
    load_scope_artifact,
    parse_scope_artifact,
)

__all__ = [
    "CurriculumGenerator",
    "DefaultCurriculumGenerator",
    "generate_curriculum",
    "generate_curriculum_file",
    "ScopeArtifactType",
    "ScopeIngestMode",
    "build_scope_artifact",
    "load_scope_artifact",
    "parse_scope_artifact",
]
