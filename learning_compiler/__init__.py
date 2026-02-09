"""Core package for curriculum builder tooling."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = ["AgentAPI", "OrchestrationAPI", "ValidatorAPI"]

if TYPE_CHECKING:
    from learning_compiler.api import AgentAPI, OrchestrationAPI, ValidatorAPI


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    from learning_compiler.api import AgentAPI, OrchestrationAPI, ValidatorAPI

    exports = {
        "AgentAPI": AgentAPI,
        "OrchestrationAPI": OrchestrationAPI,
        "ValidatorAPI": ValidatorAPI,
    }
    return exports[name]
