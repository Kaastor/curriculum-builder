from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from learning_compiler.agent.llm_client import CodingAgentLLMClient, LLMRequest, build_llm_client
from learning_compiler.agent.model_policy import ModelPolicy, ModelProvider, default_model_policy
from learning_compiler.config import reset_config_cache


class CodingAgentModeTests(unittest.TestCase):
    def test_default_model_policy_uses_internal_provider(self) -> None:
        previous = os.environ.pop("AGENT_PROVIDER", None)
        reset_config_cache()
        try:
            policy = default_model_policy()
        finally:
            if previous is not None:
                os.environ["AGENT_PROVIDER"] = previous
            reset_config_cache()
        self.assertEqual(ModelProvider.INTERNAL, policy.provider)

    def test_default_model_policy_parses_coding_agent_provider(self) -> None:
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
        self.assertEqual(ModelProvider.CODING_AGENT, policy.provider)
        self.assertEqual("codex", policy.model_id)

    def test_coding_agent_client_accepts_structured_json_from_stub_command(self) -> None:
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

            client = CodingAgentLLMClient(
                command=("python3.11", str(stub)),
                workdir=tmp,
            )
            policy = ModelPolicy(
                provider=ModelProvider.CODING_AGENT,
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

    def test_build_llm_client_uses_coding_agent_when_provider_selected(self) -> None:
        previous_provider = os.environ.get("AGENT_PROVIDER")
        previous_cmd = os.environ.get("CODING_AGENT_CMD")
        os.environ["AGENT_PROVIDER"] = "coding_agent"
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

        self.assertIsInstance(client, CodingAgentLLMClient)


if __name__ == "__main__":
    unittest.main()
