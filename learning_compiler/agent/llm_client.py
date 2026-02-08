"""LLM client contracts for proposer/critic/repair stages."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shlex
import subprocess
import tempfile
from typing import Any, Protocol

from learning_compiler.agent.model_policy import ModelPolicy, ModelProvider
from learning_compiler.config import load_config
from learning_compiler.errors import ErrorCode, LearningCompilerError


@dataclass(slots=True, frozen=True)
class LLMRequest:
    stage: str
    schema_name: str
    payload: dict[str, Any]


class LLMClient(Protocol):
    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, Any]:
        """Run one structured stage request and return a JSON mapping."""


class InternalLLMClient:
    """Deterministic placeholder client for internal heuristic mode."""

    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, Any]:
        return {
            "stage": request.stage,
            "schema_name": request.schema_name,
            "model": policy.model_id,
            "status": "ok",
        }


def _schema_for(schema_name: str) -> dict[str, Any]:
    if schema_name in {"proposer_curriculum_v1", "repair_curriculum_v1"}:
        return {
            "type": "object",
            "required": ["curriculum"],
            "properties": {
                "curriculum": {
                    "type": "object",
                    "required": ["topic", "nodes"],
                    "properties": {
                        "topic": {"type": "string"},
                        "nodes": {"type": "array"},
                        "open_questions": {"type": "array"},
                    },
                    "additionalProperties": True,
                }
            },
            "additionalProperties": True,
        }
    return {"type": "object"}


def _build_prompt(request: LLMRequest) -> str:
    payload = json.dumps(request.payload, indent=2, sort_keys=True)
    scope_hint = ""
    if isinstance(request.payload.get("scope_document"), dict):
        scope_hint = (
            "If scope_document.text is provided, ground node titles, ordering, and mastery checks "
            "in that source document; treat draft_curriculum as scaffolding only.\n"
        )
    return (
        "You are generating structured curriculum-engineering output.\n"
        "Return ONLY JSON that conforms to the provided schema.\n"
        f"{scope_hint}"
        f"Stage: {request.stage}\n"
        f"Schema: {request.schema_name}\n"
        "Input payload:\n"
        f"{payload}\n"
    )


class CodingAgentLLMClient:
    """Codex CLI-backed JSON client for coding_agent mode."""

    def __init__(
        self,
        command: tuple[str, ...],
        workdir: Path,
    ) -> None:
        self._command = command
        self._workdir = workdir

    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, Any]:
        if not self._command:
            raise LearningCompilerError(
                ErrorCode.CONFIG_ERROR,
                "CODING_AGENT_CMD is empty; cannot run coding_agent mode.",
            )

        prompt = _build_prompt(request)
        schema = _schema_for(request.schema_name)
        last_error = "unknown coding-agent failure"
        attempts = max(1, policy.retry_budget + 1)
        for _ in range(attempts):
            with tempfile.TemporaryDirectory(prefix="coding-agent-") as tmp_dir:
                tmp_path = Path(tmp_dir)
                schema_path = tmp_path / "response_schema.json"
                output_path = tmp_path / "output.json"
                schema_path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")

                cmd = [
                    *self._command,
                    "exec",
                    "-",
                    "--skip-git-repo-check",
                    "--sandbox",
                    "read-only",
                    "--output-schema",
                    str(schema_path),
                    "--output-last-message",
                    str(output_path),
                ]
                if policy.model_id and policy.model_id != "internal-heuristic-v1":
                    cmd.extend(["--model", policy.model_id])

                try:
                    proc = subprocess.run(
                        cmd,
                        input=prompt,
                        text=True,
                        capture_output=True,
                        timeout=policy.timeout_seconds,
                        cwd=self._workdir,
                        check=False,
                    )
                except subprocess.TimeoutExpired:
                    last_error = f"coding-agent timed out after {policy.timeout_seconds}s"
                    continue

                if proc.returncode != 0:
                    stderr = proc.stderr.strip() or proc.stdout.strip()
                    last_error = stderr or f"coding-agent command failed with exit {proc.returncode}"
                    continue

                if not output_path.exists():
                    last_error = "coding-agent did not produce --output-last-message file"
                    continue

                raw = output_path.read_text(encoding="utf-8").strip()
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    last_error = "coding-agent output is not valid JSON"
                    continue

                if not isinstance(payload, dict):
                    last_error = "coding-agent output root must be object"
                    continue
                return payload

        raise LearningCompilerError(
            ErrorCode.INTERNAL_ERROR,
            "coding_agent mode failed to return valid structured JSON.",
            {"last_error": last_error, "stage": request.stage},
        )


def build_llm_client(policy: ModelPolicy, workdir: Path | None = None) -> LLMClient:
    if policy.provider == ModelProvider.CODING_AGENT:
        config = load_config()
        cmd = tuple(part for part in shlex.split(config.coding_agent_cmd.strip()) if part)
        return CodingAgentLLMClient(command=cmd, workdir=(workdir or config.repo_root))
    return InternalLLMClient()
