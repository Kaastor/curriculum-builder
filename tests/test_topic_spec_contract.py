from __future__ import annotations

import unittest

from learning_compiler.validator.topic_spec import validate_topic_spec_contract


def _base_topic_spec() -> dict[str, object]:
    return {
        "spec_version": "1.0",
        "goal": "Design reliable orchestration loops for deterministic curriculum generation.",
        "audience": "Engineers with Python and testing experience",
        "prerequisites": ["python", "testing"],
        "scope_in": ["planning", "validation", "generation"],
        "scope_out": ["frontend animation systems"],
        "constraints": {
            "hours_per_week": 6,
            "total_hours_min": 12,
            "total_hours_max": 20,
            "depth": "practical",
            "node_count_min": 6,
            "node_count_max": 10,
            "max_prerequisites_per_node": 3,
        },
        "domain_mode": "mature",
        "evidence_mode": "standard",
    }


class TopicSpecContractTests(unittest.TestCase):
    def test_context_pack_accepts_valid_shape(self) -> None:
        topic_spec = _base_topic_spec()
        topic_spec["context_pack"] = {
            "domain": "software-systems",
            "focus_terms": ["agentic", "reliability"],
            "local_paths": ["README.md", "learning_compiler/validator/core.py"],
            "preferred_resource_kinds": ["doc", "spec"],
            "required_outcomes": ["code change", "test update"],
        }

        self.assertEqual([], validate_topic_spec_contract(topic_spec))

    def test_context_pack_rejects_unexpected_keys(self) -> None:
        topic_spec = _base_topic_spec()
        topic_spec["context_pack"] = {"mystery": "field"}

        errors = validate_topic_spec_contract(topic_spec)
        self.assertIn("context_pack has unexpected keys", "\n".join(errors))

    def test_context_pack_rejects_non_list_entries(self) -> None:
        topic_spec = _base_topic_spec()
        topic_spec["context_pack"] = {"focus_terms": "agentic"}

        errors = validate_topic_spec_contract(topic_spec)
        self.assertIn("context_pack.focus_terms must be a list", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
