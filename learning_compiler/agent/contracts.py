"""Generation contracts and default generator implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from learning_compiler.agent.generator import generate_curriculum_file


class CurriculumGenerator(Protocol):
    """Interface for curriculum generation engines."""

    def generate_file(self, topic_spec_path: Path, curriculum_path: Path) -> dict[str, Any]:
        """Generate curriculum artifact from topic spec and return parsed payload."""


class DefaultCurriculumGenerator:
    """Default generator used by orchestration."""

    def generate_file(self, topic_spec_path: Path, curriculum_path: Path) -> dict[str, Any]:
        return generate_curriculum_file(topic_spec_path, curriculum_path)
