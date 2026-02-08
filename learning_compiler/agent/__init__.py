"""Agent entrypoints for curriculum generation."""

from learning_compiler.agent.contracts import CurriculumGenerator, DefaultCurriculumGenerator
from learning_compiler.agent.generator import generate_curriculum, generate_curriculum_file
from learning_compiler.agent.scope_contracts import ScopeIngestMode
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
    "ScopeIngestMode",
    "compile_scope_document",
]
