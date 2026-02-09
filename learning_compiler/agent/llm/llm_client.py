"""Public LLM client facade for proposer/repair stages.

This module preserves the historical import surface while delegating
implementation details to focused submodules.
"""

from __future__ import annotations

import os
from pathlib import Path
import shlex

from learning_compiler.agent import llm_remote as _llm_remote
from learning_compiler.agent.llm_codex import CodexExecLLMClient, CodingAgentLLMClient
from learning_compiler.agent.llm_internal import InternalLLMClient
from learning_compiler.agent.llm_remote import RemoteLLMClient
from learning_compiler.agent.llm_schema import schema_for
from learning_compiler.agent.llm_types import LLMClient, LLMRequest
from learning_compiler.agent.model_policy import ModelPolicy, ModelProvider
from learning_compiler.config import load_config

# Backward-compatible symbol used by tests that monkeypatch URL opens.
urllib_request = _llm_remote.urllib_request


def _schema_for(schema_name: str) -> dict[str, object]:
    """Backward-compatible schema helper alias."""
    return schema_for(schema_name)


def build_llm_client(policy: ModelPolicy, workdir: Path | None = None) -> LLMClient:
    if policy.provider == ModelProvider.REMOTE_LLM:
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        return RemoteLLMClient(base_url=base_url)
    if policy.provider == ModelProvider.CODEX_EXEC:
        config = load_config()
        cmd = tuple(part for part in shlex.split(config.coding_agent_cmd.strip()) if part)
        return CodexExecLLMClient(command=cmd, workdir=(workdir or config.repo_root))
    return InternalLLMClient()


__all__ = [
    "LLMRequest",
    "LLMClient",
    "InternalLLMClient",
    "RemoteLLMClient",
    "CodexExecLLMClient",
    "CodingAgentLLMClient",
    "build_llm_client",
    "_schema_for",
    "urllib_request",
]
