"""Agent entrypoints for curriculum generation."""

from learning_compiler.agent.contracts import CurriculumGenerator, DefaultCurriculumGenerator
from learning_compiler.agent.generator import generate_curriculum, generate_curriculum_file

__all__ = [
    "CurriculumGenerator",
    "DefaultCurriculumGenerator",
    "generate_curriculum",
    "generate_curriculum_file",
]
