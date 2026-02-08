"""Policy profiles for scope-document synthesis behavior."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ScopeProfile(str, Enum):
    FAST = "fast"
    BALANCED = "balanced"
    DEEP = "deep"


@dataclass(slots=True, frozen=True)
class ScopeSynthesisPolicy:
    profile: ScopeProfile
    max_concepts: int
    max_scope_in_items: int
    max_prerequisites: int
    max_focus_terms: int
    min_node_count: int
    max_node_count_cap: int
    min_total_hours: float
    max_ambiguity_notes: int
    hours_per_week: float
    artifact_schema_version: str

    def snapshot(self) -> dict[str, str | int | float]:
        return {
            "profile": self.profile.value,
            "max_concepts": self.max_concepts,
            "max_scope_in_items": self.max_scope_in_items,
            "max_prerequisites": self.max_prerequisites,
            "max_focus_terms": self.max_focus_terms,
            "min_node_count": self.min_node_count,
            "max_node_count_cap": self.max_node_count_cap,
            "min_total_hours": self.min_total_hours,
            "max_ambiguity_notes": self.max_ambiguity_notes,
            "hours_per_week": self.hours_per_week,
            "artifact_schema_version": self.artifact_schema_version,
        }


def scope_policy_for_profile(profile: ScopeProfile = ScopeProfile.BALANCED) -> ScopeSynthesisPolicy:
    if profile == ScopeProfile.FAST:
        return ScopeSynthesisPolicy(
            profile=profile,
            max_concepts=80,
            max_scope_in_items=24,
            max_prerequisites=3,
            max_focus_terms=6,
            min_node_count=6,
            max_node_count_cap=18,
            min_total_hours=8.0,
            max_ambiguity_notes=2,
            hours_per_week=5.0,
            artifact_schema_version="1.0",
        )
    if profile == ScopeProfile.DEEP:
        return ScopeSynthesisPolicy(
            profile=profile,
            max_concepts=180,
            max_scope_in_items=60,
            max_prerequisites=6,
            max_focus_terms=12,
            min_node_count=8,
            max_node_count_cap=32,
            min_total_hours=16.0,
            max_ambiguity_notes=6,
            hours_per_week=7.0,
            artifact_schema_version="1.0",
        )
    return ScopeSynthesisPolicy(
        profile=ScopeProfile.BALANCED,
        max_concepts=120,
        max_scope_in_items=40,
        max_prerequisites=4,
        max_focus_terms=8,
        min_node_count=6,
        max_node_count_cap=24,
        min_total_hours=10.0,
        max_ambiguity_notes=3,
        hours_per_week=6.0,
        artifact_schema_version="1.0",
    )

