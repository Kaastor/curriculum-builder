"""LLM client contracts for proposer/critic/repair stages."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
from typing import Any, Protocol
from urllib import error as urllib_error
from urllib.parse import urlparse
from urllib import request as urllib_request

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
        resource_schema: dict[str, Any] = {
            "type": "object",
            "required": ["title", "url", "kind", "role", "citation"],
            "properties": {
                "title": {"type": "string"},
                "url": {"type": "string"},
                "kind": {"type": "string"},
                "role": {"type": "string"},
                "citation": {"type": ["string", "null"]},
            },
            "additionalProperties": False,
        }
        mastery_schema: dict[str, Any] = {
            "type": "object",
            "required": ["task", "pass_criteria"],
            "properties": {
                "task": {"type": "string"},
                "pass_criteria": {"type": "string"},
            },
            "additionalProperties": False,
        }
        node_schema: dict[str, Any] = {
            "type": "object",
            "required": [
                "id",
                "title",
                "capability",
                "core_ideas",
                "estimate_minutes",
                "prerequisites",
                "resources",
                "mastery_check",
                "pitfalls",
            ],
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "capability": {"type": "string"},
                "core_ideas": {"type": "array", "items": {"type": "string"}},
                "estimate_minutes": {"type": "number"},
                "prerequisites": {"type": "array", "items": {"type": "string"}},
                "resources": {"type": "array", "items": resource_schema},
                "mastery_check": mastery_schema,
                "pitfalls": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": False,
        }
        open_question_schema: dict[str, Any] = {
            "type": "object",
            "required": ["question", "related_nodes", "status"],
            "properties": {
                "question": {"type": "string"},
                "related_nodes": {"type": "array", "items": {"type": "string"}},
                "status": {"type": "string"},
            },
            "additionalProperties": False,
        }
        return {
            "type": "object",
            "required": ["curriculum"],
            "properties": {
                "curriculum": {
                    "type": "object",
                    "required": ["topic", "nodes", "open_questions"],
                    "properties": {
                        "topic": {"type": "string"},
                        "nodes": {"type": "array", "items": node_schema},
                        "open_questions": {
                            "type": ["array", "null"],
                            "items": open_question_schema,
                        },
                    },
                    "additionalProperties": False,
                }
            },
            "additionalProperties": False,
        }
    return {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }


def _build_prompt(request: LLMRequest) -> str:
    payload = json.dumps(
        request.payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
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


def _parse_json_mapping(raw: str) -> dict[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise LearningCompilerError(
            ErrorCode.INTERNAL_ERROR,
            "model output is not valid JSON.",
            {"error": str(exc)},
        ) from exc
    if not isinstance(payload, dict):
        raise LearningCompilerError(
            ErrorCode.INTERNAL_ERROR,
            "model output root must be object.",
        )
    return payload


def _extract_remote_payload(response_payload: dict[str, Any]) -> dict[str, Any]:
    output_text = response_payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return _parse_json_mapping(output_text)

    output = response_payload.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                block_json = block.get("json")
                if isinstance(block_json, dict):
                    return block_json
                block_text = block.get("text")
                if isinstance(block_text, str) and block_text.strip():
                    return _parse_json_mapping(block_text)

    raise LearningCompilerError(
        ErrorCode.INTERNAL_ERROR,
        "remote_llm did not return structured JSON content.",
        {"response_keys": sorted(str(key) for key in response_payload.keys())},
    )


class RemoteLLMClient:
    """OpenAI Responses API-backed JSON client for remote_llm mode."""

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key.strip() if isinstance(api_key, str) else ""

    def _resolve_api_key(self) -> str:
        if self._api_key:
            return self._api_key
        env_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if env_key:
            return env_key
        raise LearningCompilerError(
            ErrorCode.CONFIG_ERROR,
            "OPENAI_API_KEY is required for AGENT_PROVIDER=remote_llm.",
        )

    def _build_http_request(self, payload: dict[str, Any], api_key: str) -> urllib_request.Request:
        target_url = f"{self._base_url}/responses"
        parsed_url = urlparse(target_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise LearningCompilerError(
                ErrorCode.CONFIG_ERROR,
                "OPENAI_BASE_URL is invalid for AGENT_PROVIDER=remote_llm.",
                {"base_url": self._base_url},
            )
        try:
            return urllib_request.Request(
                url=target_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
        except ValueError as exc:
            raise LearningCompilerError(
                ErrorCode.CONFIG_ERROR,
                "OPENAI_BASE_URL is invalid for AGENT_PROVIDER=remote_llm.",
                {"base_url": self._base_url},
            ) from exc

    @staticmethod
    def _is_retryable_http_error(status_code: int) -> bool:
        return status_code >= 500 or status_code in {408, 409, 429}

    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, Any]:
        api_key = self._resolve_api_key()
        payload = {
            "model": policy.model_id,
            "input": _build_prompt(request),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "learning_compiler_output",
                    "schema": _schema_for(request.schema_name),
                    "strict": True,
                }
            },
        }
        attempts = max(1, policy.retry_budget + 1)
        last_error: dict[str, Any] = {"reason": "unknown remote_llm failure"}
        response_body = ""
        for attempt in range(1, attempts + 1):
            http_request = self._build_http_request(payload, api_key)
            try:
                with urllib_request.urlopen(http_request, timeout=policy.timeout_seconds) as response:
                    response_body = response.read().decode("utf-8")
                    break
            except urllib_error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                last_error = {"status_code": exc.code, "body": body, "attempt": attempt}
                if attempt == attempts or not self._is_retryable_http_error(exc.code):
                    raise LearningCompilerError(
                        ErrorCode.INTERNAL_ERROR,
                        "remote_llm request failed.",
                        last_error,
                    ) from exc
            except urllib_error.URLError as exc:
                reason = str(exc.reason) if exc.reason is not None else str(exc)
                last_error = {"reason": reason, "attempt": attempt}
                if attempt == attempts:
                    raise LearningCompilerError(
                        ErrorCode.INTERNAL_ERROR,
                        "remote_llm request failed.",
                        last_error,
                    ) from exc
        else:
            raise LearningCompilerError(
                ErrorCode.INTERNAL_ERROR,
                "remote_llm request failed.",
                last_error,
            )

        try:
            parsed = json.loads(response_body)
        except json.JSONDecodeError as exc:
            raise LearningCompilerError(
                ErrorCode.INTERNAL_ERROR,
                "remote_llm response is not valid JSON.",
            ) from exc
        if not isinstance(parsed, dict):
            raise LearningCompilerError(
                ErrorCode.INTERNAL_ERROR,
                "remote_llm response root must be object.",
            )
        return _extract_remote_payload(parsed)


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

    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, Any]:
        if not self._command:
            raise LearningCompilerError(
                ErrorCode.CONFIG_ERROR,
                "CODING_AGENT_CMD is empty; cannot run codex_exec mode.",
            )

        prompt = _build_prompt(request)
        schema = _schema_for(request.schema_name)
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


def build_llm_client(policy: ModelPolicy, workdir: Path | None = None) -> LLMClient:
    if policy.provider == ModelProvider.REMOTE_LLM:
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        return RemoteLLMClient(base_url=base_url)
    if policy.provider == ModelProvider.CODEX_EXEC:
        config = load_config()
        cmd = tuple(part for part in shlex.split(config.coding_agent_cmd.strip()) if part)
        return CodexExecLLMClient(command=cmd, workdir=(workdir or config.repo_root))
    return InternalLLMClient()
