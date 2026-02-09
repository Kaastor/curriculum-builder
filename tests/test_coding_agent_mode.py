from __future__ import annotations

import os
import tempfile
import unittest
from unittest import mock
from pathlib import Path
from urllib import error as urllib_error

from learning_compiler.agent.llm.client import (
    CodexExecLLMClient,
    LLMRequest,
    RemoteLLMClient,
    _schema_for,
    build_llm_client,
)
from learning_compiler.errors import ErrorCode, LearningCompilerError
from learning_compiler.agent.model_policy import ModelPolicy, ModelProvider, default_model_policy
from learning_compiler.config import reset_config_cache


class CodingAgentModeTests(unittest.TestCase):
    def test_curriculum_schema_defines_node_items_for_codex_structured_output(self) -> None:
        schema = _schema_for("proposer_curriculum_v1")
        curriculum = schema["properties"]["curriculum"]
        nodes = curriculum["properties"]["nodes"]
        self.assertEqual("array", nodes["type"])
        self.assertIn("items", nodes)
        self.assertEqual("object", nodes["items"]["type"])

    def test_default_model_policy_uses_codex_exec_provider(self) -> None:
        previous = os.environ.pop("AGENT_PROVIDER", None)
        reset_config_cache()
        try:
            policy = default_model_policy()
        finally:
            if previous is not None:
                os.environ["AGENT_PROVIDER"] = previous
            reset_config_cache()
        self.assertEqual(ModelProvider.CODEX_EXEC, policy.provider)

    def test_default_model_policy_parses_legacy_coding_agent_alias(self) -> None:
        previous_provider = os.environ.get("AGENT_PROVIDER")
        previous_model = os.environ.get("AGENT_MODEL")
        os.environ["AGENT_PROVIDER"] = "coding_agent"
        os.environ["AGENT_MODEL"] = "codex"
        reset_config_cache()
        try:
            policy = default_model_policy()
        finally:
            if previous_provider is None:
                os.environ.pop("AGENT_PROVIDER", None)
            else:
                os.environ["AGENT_PROVIDER"] = previous_provider
            if previous_model is None:
                os.environ.pop("AGENT_MODEL", None)
            else:
                os.environ["AGENT_MODEL"] = previous_model
            reset_config_cache()
        self.assertEqual(ModelProvider.CODEX_EXEC, policy.provider)
        self.assertEqual("codex", policy.model_id)

    def test_default_model_policy_leaves_codex_exec_model_unset(self) -> None:
        previous_provider = os.environ.get("AGENT_PROVIDER")
        previous_model = os.environ.get("AGENT_MODEL")
        os.environ["AGENT_PROVIDER"] = "codex_exec"
        os.environ.pop("AGENT_MODEL", None)
        reset_config_cache()
        try:
            policy = default_model_policy()
        finally:
            if previous_provider is None:
                os.environ.pop("AGENT_PROVIDER", None)
            else:
                os.environ["AGENT_PROVIDER"] = previous_provider
            if previous_model is None:
                os.environ.pop("AGENT_MODEL", None)
            else:
                os.environ["AGENT_MODEL"] = previous_model
            reset_config_cache()
        self.assertEqual(ModelProvider.CODEX_EXEC, policy.provider)
        self.assertEqual("", policy.model_id)
        self.assertEqual(300, policy.timeout_seconds)

    def test_codex_exec_client_accepts_structured_json_from_stub_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            stub = tmp / "stub_coding_agent.py"
            stub.write_text(
                (
                    "import json,sys\n"
                    "args=sys.argv\n"
                    "idx=args.index('--output-last-message')+1\n"
                    "out=args[idx]\n"
                    "with open(out,'w',encoding='utf-8') as f:\n"
                    "  json.dump({'curriculum':{'topic':'stub','nodes':[]}},f)\n"
                ),
                encoding="utf-8",
            )

            client = CodexExecLLMClient(
                command=("python3.11", str(stub)),
                workdir=tmp,
            )
            policy = ModelPolicy(
                provider=ModelProvider.CODEX_EXEC,
                model_id="codex",
                temperature=0.0,
                max_iterations=2,
                max_actions_per_iteration=2,
                target_score=80,
                timeout_seconds=10,
                retry_budget=1,
                schema_version="1.0",
            )

            response = client.run_json(
                LLMRequest(
                    stage="proposer",
                    schema_name="proposer_curriculum_v1",
                    payload={"draft_curriculum": {"topic": "x", "nodes": []}},
                ),
                policy,
            )

            self.assertIn("curriculum", response)
            self.assertEqual("stub", response["curriculum"]["topic"])

    def test_codex_exec_reports_config_error_for_chatgpt_unsupported_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            stub = tmp / "stub_coding_agent_error.py"
            stub.write_text(
                (
                    "import sys\n"
                    "sys.stderr.write('{\"detail\":\"The \\'codex\\' model is not supported when using Codex with a ChatGPT account.\"}')\n"
                    "raise SystemExit(1)\n"
                ),
                encoding="utf-8",
            )
            client = CodexExecLLMClient(
                command=("python3.11", str(stub)),
                workdir=tmp,
            )
            policy = ModelPolicy(
                provider=ModelProvider.CODEX_EXEC,
                model_id="codex",
                temperature=0.0,
                max_iterations=2,
                max_actions_per_iteration=2,
                target_score=80,
                timeout_seconds=10,
                retry_budget=1,
                schema_version="1.0",
            )

            with self.assertRaises(LearningCompilerError) as raised:
                client.run_json(
                    LLMRequest(
                        stage="proposer",
                        schema_name="proposer_curriculum_v1",
                        payload={"draft_curriculum": {"topic": "x", "nodes": []}},
                    ),
                    policy,
                )
            self.assertEqual(ErrorCode.CONFIG_ERROR, raised.exception.code)

    def test_build_llm_client_uses_codex_exec_when_provider_selected(self) -> None:
        previous_provider = os.environ.get("AGENT_PROVIDER")
        previous_cmd = os.environ.get("CODING_AGENT_CMD")
        os.environ["AGENT_PROVIDER"] = "codex_exec"
        os.environ["CODING_AGENT_CMD"] = "codex"
        reset_config_cache()
        try:
            policy = default_model_policy()
            client = build_llm_client(policy)
        finally:
            if previous_provider is None:
                os.environ.pop("AGENT_PROVIDER", None)
            else:
                os.environ["AGENT_PROVIDER"] = previous_provider
            if previous_cmd is None:
                os.environ.pop("CODING_AGENT_CMD", None)
            else:
                os.environ["CODING_AGENT_CMD"] = previous_cmd
            reset_config_cache()

        self.assertIsInstance(client, CodexExecLLMClient)

    def test_codex_exec_sets_writable_codex_home_when_missing(self) -> None:
        previous_codex_home = os.environ.pop("CODEX_HOME", None)
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp = Path(tmp_dir)
                stub = tmp / "stub_coding_agent_env.py"
                stub.write_text(
                    (
                        "import json,os,sys\n"
                        "args=sys.argv\n"
                        "idx=args.index('--output-last-message')+1\n"
                        "out=args[idx]\n"
                        "home=os.environ.get('CODEX_HOME','')\n"
                        "with open(out,'w',encoding='utf-8') as f:\n"
                        "  json.dump({'curriculum':{'topic':home,'nodes':[]}},f)\n"
                    ),
                    encoding="utf-8",
                )

                client = CodexExecLLMClient(
                    command=("python3.11", str(stub)),
                    workdir=tmp,
                )
                policy = ModelPolicy(
                    provider=ModelProvider.CODEX_EXEC,
                    model_id="codex",
                    temperature=0.0,
                    max_iterations=2,
                    max_actions_per_iteration=2,
                    target_score=80,
                    timeout_seconds=10,
                    retry_budget=1,
                    schema_version="1.0",
                )
                response = client.run_json(
                    LLMRequest(
                        stage="proposer",
                        schema_name="proposer_curriculum_v1",
                        payload={"draft_curriculum": {"topic": "x", "nodes": []}},
                    ),
                    policy,
                )

                expected = str((tmp / ".codex-runtime").resolve())
                self.assertEqual(expected, response["curriculum"]["topic"])
        finally:
            if previous_codex_home is not None:
                os.environ["CODEX_HOME"] = previous_codex_home

    def test_build_llm_client_uses_remote_llm_when_provider_selected(self) -> None:
        previous_provider = os.environ.get("AGENT_PROVIDER")
        os.environ["AGENT_PROVIDER"] = "remote_llm"
        reset_config_cache()
        try:
            policy = default_model_policy()
            client = build_llm_client(policy)
        finally:
            if previous_provider is None:
                os.environ.pop("AGENT_PROVIDER", None)
            else:
                os.environ["AGENT_PROVIDER"] = previous_provider
            reset_config_cache()
        self.assertIsInstance(client, RemoteLLMClient)

    def test_remote_llm_client_requires_openai_api_key(self) -> None:
        previous_key = os.environ.pop("OPENAI_API_KEY", None)
        client = RemoteLLMClient(base_url="https://api.openai.com/v1")
        policy = ModelPolicy(
            provider=ModelProvider.REMOTE_LLM,
            model_id="gpt-4.1-mini",
            temperature=0.0,
            max_iterations=2,
            max_actions_per_iteration=2,
            target_score=80,
            timeout_seconds=10,
            retry_budget=1,
            schema_version="1.0",
        )
        try:
            with self.assertRaises(LearningCompilerError) as raised:
                client.run_json(
                    LLMRequest(
                        stage="proposer",
                        schema_name="proposer_curriculum_v1",
                        payload={"draft_curriculum": {"topic": "x", "nodes": []}},
                    ),
                    policy,
                )
            self.assertEqual(ErrorCode.CONFIG_ERROR, raised.exception.code)
        finally:
            if previous_key is not None:
                os.environ["OPENAI_API_KEY"] = previous_key

    @mock.patch("learning_compiler.agent.llm.client.urllib_request.urlopen")
    def test_remote_llm_client_parses_output_text_json(self, mock_urlopen: mock.MagicMock) -> None:
        previous_key = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "test-key"
        try:
            mock_response = mock.MagicMock()
            mock_response.read.return_value = (
                b'{"output_text":"{\\"curriculum\\":{\\"topic\\":\\"remote\\",\\"nodes\\":[]}}"}'
            )
            mock_urlopen.return_value.__enter__.return_value = mock_response

            client = RemoteLLMClient(base_url="https://api.openai.com/v1")
            policy = ModelPolicy(
                provider=ModelProvider.REMOTE_LLM,
                model_id="gpt-4.1-mini",
                temperature=0.0,
                max_iterations=2,
                max_actions_per_iteration=2,
                target_score=80,
                timeout_seconds=10,
                retry_budget=1,
                schema_version="1.0",
            )
            response = client.run_json(
                LLMRequest(
                    stage="proposer",
                    schema_name="proposer_curriculum_v1",
                    payload={"draft_curriculum": {"topic": "x", "nodes": []}},
                ),
                policy,
            )
            self.assertEqual("remote", response["curriculum"]["topic"])
        finally:
            if previous_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = previous_key

    @mock.patch("learning_compiler.agent.llm.client.urllib_request.urlopen")
    def test_remote_llm_client_retries_urlerror_with_retry_budget(
        self,
        mock_urlopen: mock.MagicMock,
    ) -> None:
        previous_key = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "test-key"
        try:
            mock_response = mock.MagicMock()
            mock_response.read.return_value = (
                b'{"output_text":"{\\"curriculum\\":{\\"topic\\":\\"retry-ok\\",\\"nodes\\":[]}}"}'
            )
            success_ctx = mock.MagicMock()
            success_ctx.__enter__.return_value = mock_response
            mock_urlopen.side_effect = [urllib_error.URLError("temporary"), success_ctx]

            client = RemoteLLMClient(base_url="https://api.openai.com/v1")
            policy = ModelPolicy(
                provider=ModelProvider.REMOTE_LLM,
                model_id="gpt-4.1-mini",
                temperature=0.0,
                max_iterations=2,
                max_actions_per_iteration=2,
                target_score=80,
                timeout_seconds=10,
                retry_budget=1,
                schema_version="1.0",
            )
            response = client.run_json(
                LLMRequest(
                    stage="proposer",
                    schema_name="proposer_curriculum_v1",
                    payload={"draft_curriculum": {"topic": "x", "nodes": []}},
                ),
                policy,
            )

            self.assertEqual("retry-ok", response["curriculum"]["topic"])
            self.assertEqual(2, mock_urlopen.call_count)
        finally:
            if previous_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = previous_key

    def test_remote_llm_client_rejects_invalid_base_url(self) -> None:
        previous_key = os.environ.get("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = "test-key"
        try:
            client = RemoteLLMClient(base_url="")
            policy = ModelPolicy(
                provider=ModelProvider.REMOTE_LLM,
                model_id="gpt-4.1-mini",
                temperature=0.0,
                max_iterations=2,
                max_actions_per_iteration=2,
                target_score=80,
                timeout_seconds=10,
                retry_budget=1,
                schema_version="1.0",
            )
            with self.assertRaises(LearningCompilerError) as raised:
                client.run_json(
                    LLMRequest(
                        stage="proposer",
                        schema_name="proposer_curriculum_v1",
                        payload={"draft_curriculum": {"topic": "x", "nodes": []}},
                    ),
                    policy,
                )
            self.assertEqual(ErrorCode.CONFIG_ERROR, raised.exception.code)
        finally:
            if previous_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = previous_key


if __name__ == "__main__":
    unittest.main()
