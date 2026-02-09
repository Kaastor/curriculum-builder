from __future__ import annotations

import os
import unittest

from learning_compiler.agent.llm.llm_payloads import (
    compact_curriculum_for_llm,
    compact_topic_spec_for_llm,
    scope_document_payload,
)


class LLMPayloadTests(unittest.TestCase):
    def test_compact_curriculum_keeps_open_questions_when_requested(self) -> None:
        compact = compact_curriculum_for_llm(
            {
                "topic": "T",
                "nodes": [{"id": "N1", "title": "A", "prerequisites": [], "estimate_minutes": 30}],
                "open_questions": "not-a-list",
            },
            include_open_questions_if_present=True,
        )
        self.assertIn("open_questions", compact)
        self.assertEqual("not-a-list", compact["open_questions"])

    def test_compact_curriculum_uses_list_only_by_default(self) -> None:
        compact = compact_curriculum_for_llm(
            {
                "topic": "T",
                "nodes": [{"id": "N1", "title": "A", "prerequisites": [], "estimate_minutes": 30}],
                "open_questions": "not-a-list",
            },
        )
        self.assertNotIn("open_questions", compact)

    def test_compact_topic_spec_limits_list_fields(self) -> None:
        topic_spec = {
            "goal": "g",
            "audience": "a",
            "domain_mode": "mature",
            "evidence_mode": "minimal",
            "spec_version": "1.0",
            "prerequisites": [str(idx) for idx in range(100)],
            "scope_in": [str(idx) for idx in range(100)],
        }
        compact = compact_topic_spec_for_llm(topic_spec)
        self.assertEqual(24, len(compact["prerequisites"]))
        self.assertEqual(60, len(compact["scope_in"]))

    def test_scope_document_payload_truncates_by_configured_limit(self) -> None:
        previous = os.environ.get("AGENT_SCOPE_TEXT_MAX_CHARS")
        os.environ["AGENT_SCOPE_TEXT_MAX_CHARS"] = "2000"
        try:
            payload = scope_document_payload("scope.md", "x" * 2100)
        finally:
            if previous is None:
                os.environ.pop("AGENT_SCOPE_TEXT_MAX_CHARS", None)
            else:
                os.environ["AGENT_SCOPE_TEXT_MAX_CHARS"] = previous
        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertTrue(payload["truncated"])
        self.assertEqual(2100, payload["source_chars"])
        self.assertIn("[scope truncated for LLM payload]", payload["text"])
