"""Shared error taxonomy for learning compiler modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    INVALID_ARGUMENT = "invalid_argument"
    NOT_FOUND = "not_found"
    VALIDATION_FAILED = "validation_failed"
    STAGE_CONFLICT = "stage_conflict"
    IO_ERROR = "io_error"
    CONFIG_ERROR = "config_error"
    INTERNAL_ERROR = "internal_error"


@dataclass(slots=True)
class LearningCompilerError(Exception):
    """Base typed error with stable machine-readable code."""

    code: ErrorCode
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"[{self.code.value}] {self.message}"

    def exit_code(self) -> int:
        return {
            ErrorCode.INVALID_ARGUMENT: 2,
            ErrorCode.NOT_FOUND: 3,
            ErrorCode.VALIDATION_FAILED: 4,
            ErrorCode.STAGE_CONFLICT: 5,
            ErrorCode.IO_ERROR: 6,
            ErrorCode.CONFIG_ERROR: 7,
            ErrorCode.INTERNAL_ERROR: 10,
        }.get(self.code, 10)


class ConfigError(LearningCompilerError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(ErrorCode.CONFIG_ERROR, message, details or {})


class NotFoundError(LearningCompilerError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(ErrorCode.NOT_FOUND, message, details or {})


class StageConflictError(LearningCompilerError):
    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(ErrorCode.STAGE_CONFLICT, message, details or {})
