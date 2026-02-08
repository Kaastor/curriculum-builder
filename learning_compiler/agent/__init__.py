"""Agent entrypoints for curriculum generation."""

from learning_compiler.agent.contracts import CurriculumGenerator, DefaultCurriculumGenerator
from learning_compiler.agent.generator import generate_curriculum, generate_curriculum_file
from learning_compiler.agent.scope_contracts import ScopeArtifactType, ScopeIngestMode
from learning_compiler.agent.scope_policy import (
    ScopeProfile,
    ScopeSynthesisPolicy,
    scope_policy_for_profile,
)
from learning_compiler.agent.scope_artifacts import load_scope_artifact, parse_scope_artifact
from learning_compiler.agent.scope_pipeline import (
    ScopeCompilationResult,
    compile_scope_document,
)

__all__ = [
    "CurriculumGenerator",
    "DefaultCurriculumGenerator",
    "generate_curriculum",
    "generate_curriculum_file",
    "ScopeCompilationResult",
    "ScopeArtifactType",
    "ScopeIngestMode",
    "ScopeProfile",
    "ScopeSynthesisPolicy",
    "compile_scope_document",
    "load_scope_artifact",
    "parse_scope_artifact",
    "scope_policy_for_profile",
]
