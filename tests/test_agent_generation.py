from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from learning_compiler.agent.generator import generate_curriculum, generate_curriculum_file
from learning_compiler.agent.research import ResourceRequest


class StubResolver:
    def __init__(self) -> None:
        self.requests: list[ResourceRequest] = []

    def resolve(self, request: ResourceRequest) -> list[dict[str, str]]:
        self.requests.append(request)
        return [
            {
                "title": "Stub Definition",
                "url": "https://example.org/definition",
                "kind": "doc",
                "role": "definition",
            },
            {
                "title": "Stub Example",
                "url": "https://example.org/example",
                "kind": "doc",
                "role": "example",
            },
        ]


def base_topic_spec() -> dict[str, object]:
    return {
        "spec_version": "1.0",
        "goal": "Build reliable deployment checklists for ML systems.",
        "audience": "ML engineers with production baseline knowledge",
        "prerequisites": ["python", "basic statistics"],
        "scope_in": ["monitoring", "rollback strategies", "deployment validation"],
        "scope_out": ["deep compiler internals"],
        "constraints": {
            "hours_per_week": 5,
            "total_hours_min": 10,
            "total_hours_max": 18,
            "depth": "practical",
            "node_count_min": 6,
            "node_count_max": 8,
            "max_prerequisites_per_node": 3,
        },
        "domain_mode": "mature",
        "evidence_mode": "standard",
        "misconceptions": ["Monitoring can be added after release"],
    }


class AgentGenerationTests(unittest.TestCase):
    def test_generate_curriculum_uses_injected_resolver(self) -> None:
        topic_spec = base_topic_spec()
        resolver = StubResolver()

        curriculum = generate_curriculum(topic_spec, resolver=resolver)

        self.assertIn("nodes", curriculum)
        nodes = curriculum["nodes"]
        self.assertEqual(len(nodes), len(resolver.requests))
        self.assertEqual("Stub Definition", nodes[0]["resources"][0]["title"])
        self.assertEqual("standard", resolver.requests[0].evidence_mode)

    def test_generate_curriculum_file_writes_output(self) -> None:
        resolver = StubResolver()

        with tempfile.TemporaryDirectory() as tmp_dir:
            topic_path = Path(tmp_dir) / "topic_spec.json"
            out_path = Path(tmp_dir) / "curriculum.json"
            topic_path.write_text(json.dumps(base_topic_spec()), encoding="utf-8")

            payload = generate_curriculum_file(topic_path, out_path, resolver=resolver)

            self.assertTrue(out_path.exists())
            loaded = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["topic"], loaded["topic"])
            self.assertGreater(len(loaded["nodes"]), 0)


if __name__ == "__main__":
    unittest.main()
