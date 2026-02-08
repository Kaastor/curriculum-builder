"""Typed orchestration primitives."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class Stage(str, Enum):
    INITIALIZED = "initialized"
    SPEC_READY = "spec_ready"
    GENERATED = "generated"
    VALIDATED = "validated"
    PLANNED = "planned"
    ITERATED = "iterated"


STAGE_ORDER = (
    Stage.INITIALIZED,
    Stage.SPEC_READY,
    Stage.GENERATED,
    Stage.VALIDATED,
    Stage.PLANNED,
    Stage.ITERATED,
)
STAGE_INDEX = {stage: idx for idx, stage in enumerate(STAGE_ORDER)}


@dataclass(slots=True, frozen=True)
class RunPaths:
    topic_spec: Path
    curriculum: Path
    previous_curriculum: Path
    event_log: Path
    validation_report: Path
    validation_pass_marker: Path
    plan: Path
    diff_report: Path
    run_meta: Path


def stage_from(value: Any) -> Stage:
    raw = str(value)
    if raw == "map_generated":
        return Stage.GENERATED
    try:
        return Stage(raw)
    except ValueError:
        return Stage.INITIALIZED
