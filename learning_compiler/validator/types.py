"""Shared types and schema constants for curriculum validation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum


class Depth(str, Enum):
    SURVEY = "survey"
    PRACTICAL = "practical"
    MASTERY = "mastery"


class DomainMode(str, Enum):
    MATURE = "mature"
    FRONTIER = "frontier"


class EvidenceMode(str, Enum):
    MINIMAL = "minimal"
    STANDARD = "standard"
    STRICT = "strict"


class ResourceKind(str, Enum):
    DOC = "doc"
    PAPER = "paper"
    VIDEO = "video"
    BOOK = "book"
    SPEC = "spec"
    OTHER = "other"


class ResourceRole(str, Enum):
    DEFINITION = "definition"
    EXAMPLE = "example"
    REFERENCE = "reference"
    OTHER = "other"


VALID_DEPTHS = {item.value for item in Depth}
VALID_DOMAIN_MODES = {item.value for item in DomainMode}
VALID_EVIDENCE_MODES = {item.value for item in EvidenceMode}
VALID_RESOURCE_KINDS = {item.value for item in ResourceKind}
VALID_RESOURCE_ROLES = {item.value for item in ResourceRole}

REQUIRED_TOPIC_SPEC_FIELDS = {
    "goal",
    "audience",
    "prerequisites",
    "scope_in",
    "scope_out",
    "constraints",
    "domain_mode",
    "evidence_mode",
}
OPTIONAL_TOPIC_SPEC_FIELDS = {"spec_version", "misconceptions", "context_pack"}

REQUIRED_CONSTRAINT_FIELDS = {
    "hours_per_week",
    "total_hours_min",
    "total_hours_max",
    "depth",
}
OPTIONAL_CONSTRAINT_FIELDS = {
    "node_count_min",
    "node_count_max",
    "max_prerequisites_per_node",
}

REQUIRED_CURRICULUM_TOP_LEVEL = {"topic", "nodes"}
OPTIONAL_CURRICULUM_TOP_LEVEL = {"open_questions"}

REQUIRED_NODE_FIELDS = {
    "id",
    "title",
    "capability",
    "prerequisites",
    "core_ideas",
    "pitfalls",
    "mastery_check",
    "estimate_minutes",
    "resources",
}
OPTIONAL_NODE_FIELDS = {"estimate_confidence"}

REQUIRED_MASTERY_FIELDS = {"task", "pass_criteria"}

REQUIRED_RESOURCE_FIELDS = {"title", "url", "kind"}
OPTIONAL_RESOURCE_FIELDS = {"citation", "role"}

ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


@dataclass(slots=True, frozen=True)
class ValidationConfig:
    evidence_mode: EvidenceMode
    domain_mode: DomainMode
    total_hours_min: float
    total_hours_max: float
    node_count_min: int | None
    node_count_max: int | None
    max_prerequisites_per_node: int | None


@dataclass(slots=True)
class ValidationResult:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def ok(self, msg: str) -> None:
        self.passed.append(msg)

    def fail(self, msg: str) -> None:
        self.failed.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def success(self) -> bool:
        return not self.failed

    def report(self) -> str:
        lines: list[str] = []
        lines.append("\n" + "=" * 60)
        lines.append("CURRICULUM VALIDATION REPORT")
        lines.append("=" * 60 + "\n")

        lines.append(f"PASSED: {len(self.passed)}")
        for message in self.passed:
            lines.append(f"  OK  {message}")

        if self.warnings:
            lines.append(f"\nWARNINGS: {len(self.warnings)}")
            for message in self.warnings:
                lines.append(f"  WARN {message}")

        if self.failed:
            lines.append(f"\nFAILED: {len(self.failed)}")
            for message in self.failed:
                lines.append(f"  ERR  {message}")
        else:
            lines.append("\nALL CHECKS PASSED")

        lines.append("\n" + "=" * 60)
        lines.append(
            f"Total: {len(self.passed)} passed, "
            f"{len(self.warnings)} warnings, {len(self.failed)} failed"
        )
        lines.append("=" * 60 + "\n")
        return "\n".join(lines)
