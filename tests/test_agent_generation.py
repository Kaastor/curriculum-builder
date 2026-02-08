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
        self.assertGreaterEqual(len(resolver.requests), len(nodes))
        self.assertEqual("Stub Definition", nodes[0]["resources"][0]["title"])
        self.assertEqual("standard", resolver.requests[0].evidence_mode)
        self.assertEqual("N1", resolver.requests[0].node_id)

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

    def test_context_pack_local_paths_enable_local_resolver(self) -> None:
        topic_spec = base_topic_spec()
        topic_spec["context_pack"] = {
            "domain": "repo-engineering",
            "focus_terms": ["orchestration", "validation"],
            "local_paths": [
                "README.md",
                "learning_compiler/agent/generator.py",
                "/etc/hosts",
            ],
            "required_outcomes": ["implementation note"],
        }

        curriculum = generate_curriculum(topic_spec)
        first_resources = curriculum["nodes"][0]["resources"]
        self.assertTrue(first_resources, "expected resources on first node")
        self.assertTrue(
            any(str(resource["url"]).startswith("local://") for resource in first_resources),
            "expected at least one local repo resource when context_pack.local_paths is provided",
        )
        self.assertTrue(
            all("etc/hosts" not in str(resource["url"]) for resource in first_resources),
            "resolver must ignore local_paths outside the repository root",
        )

    def test_generate_curriculum_file_writes_optimization_trace_for_run_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            run_dir = Path(tmp_dir) / "runs" / "20260208-000000-sample"
            topic_path = run_dir / "inputs" / "topic_spec.json"
            curriculum_path = run_dir / "outputs" / "curriculum" / "curriculum.json"
            topic_path.parent.mkdir(parents=True, exist_ok=True)
            topic_path.write_text(json.dumps(base_topic_spec()), encoding="utf-8")

            generate_curriculum_file(topic_path, curriculum_path)

            trace_path = run_dir / "outputs" / "reviews" / "optimization_trace.json"
            self.assertTrue(trace_path.exists())
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertIn("iterations", trace)
            self.assertIn("stop_reason", trace)


if __name__ == "__main__":
    unittest.main()
