"""Codex CLI-backed LLM client."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile

from learning_compiler.agent.llm.prompt import build_prompt
from learning_compiler.agent.llm.schema import schema_for
from learning_compiler.agent.llm.types import LLMRequest
from learning_compiler.agent.model_policy import ModelPolicy
from learning_compiler.errors import ErrorCode, LearningCompilerError


class CodexExecLLMClient:
    """Codex CLI-backed JSON client for codex_exec mode."""

    def __init__(
        self,
        command: tuple[str, ...],
        workdir: Path,
    ) -> None:
        self._command = command
        self._workdir = workdir

    def _command_env(self) -> dict[str, str]:
        env = dict(os.environ)
        if "CODEX_HOME" in env and env["CODEX_HOME"].strip():
            return env
        codex_home = self._workdir / ".codex-runtime"
        codex_home.mkdir(parents=True, exist_ok=True)
        env["CODEX_HOME"] = str(codex_home)
        return env

    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, object]:
        if not self._command:
            raise LearningCompilerError(
                ErrorCode.CONFIG_ERROR,
                "CODING_AGENT_CMD is empty; cannot run codex_exec mode.",
            )

        prompt = build_prompt(request)
        schema = schema_for(request.schema_name)
        last_error = "unknown codex-exec failure"
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
                        env=self._command_env(),
                        check=False,
                    )
                except subprocess.TimeoutExpired:
                    last_error = f"codex exec timed out after {policy.timeout_seconds}s"
                    continue

                if proc.returncode != 0:
                    stderr = proc.stderr.strip() or proc.stdout.strip()
                    last_error = stderr or f"codex exec failed with exit {proc.returncode}"
                    continue

                if not output_path.exists():
                    last_error = "codex exec did not produce --output-last-message file"
                    continue

                raw = output_path.read_text(encoding="utf-8").strip()
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    last_error = "codex exec output is not valid JSON"
                    continue

                if not isinstance(payload, dict):
                    last_error = "codex exec output root must be object"
                    continue
                return payload

        lowered_error = last_error.lower()
        if "model is not supported when using codex with a chatgpt account" in lowered_error:
            raise LearningCompilerError(
                ErrorCode.CONFIG_ERROR,
                "AGENT_MODEL is incompatible with ChatGPT-authenticated codex_exec.",
                {
                    "model": policy.model_id,
                    "hint": "Unset AGENT_MODEL to use the account default model, or pick a supported model.",
                    "last_error": last_error,
                    "stage": request.stage,
                },
            )
        raise LearningCompilerError(
            ErrorCode.INTERNAL_ERROR,
            "codex_exec mode failed to return valid structured JSON.",
            {"last_error": last_error, "stage": request.stage},
        )


class CodingAgentLLMClient(CodexExecLLMClient):
    """Backward-compatible alias for legacy coding_agent naming."""
