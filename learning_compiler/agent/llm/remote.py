"""Remote Responses-API backed LLM client."""

from __future__ import annotations

import json
import os
from urllib import error as urllib_error
from urllib.parse import urlparse
from urllib import request as urllib_request

from learning_compiler.agent.llm.llm_prompt import build_prompt, extract_remote_payload
from learning_compiler.agent.llm.llm_schema import schema_for
from learning_compiler.agent.llm.llm_types import LLMRequest
from learning_compiler.agent.model_policy import ModelPolicy
from learning_compiler.errors import ErrorCode, LearningCompilerError


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

    def _build_http_request(self, payload: dict[str, object], api_key: str) -> urllib_request.Request:
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

    def run_json(self, request: LLMRequest, policy: ModelPolicy) -> dict[str, object]:
        api_key = self._resolve_api_key()
        payload: dict[str, object] = {
            "model": policy.model_id,
            "input": build_prompt(request),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "learning_compiler_output",
                    "schema": schema_for(request.schema_name),
                    "strict": True,
                }
            },
        }
        attempts = max(1, policy.retry_budget + 1)
        last_error: dict[str, object] = {"reason": "unknown remote_llm failure"}
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
        return extract_remote_payload(parsed)
