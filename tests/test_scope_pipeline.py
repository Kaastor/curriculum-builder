from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from learning_compiler.errors import LearningCompilerError
from learning_compiler.agent.concept_dag_builder import build_concept_dag
from learning_compiler.agent.scope_artifacts import parse_scope_artifact
from learning_compiler.agent.scope_contracts import ScopeArtifactType, ScopeIngestMode
from learning_compiler.agent.scope_policy import ScopeProfile, scope_policy_for_profile
from learning_compiler.agent.scope_extractor import extract_scope
from learning_compiler.agent.scope_pipeline import compile_scope_document
from learning_compiler.validator.topic_spec import validate_topic_spec_contract


SCOPE_MARKDOWN = """# Agentic Engineering Roadmap

## Foundations
- Python tooling discipline
- Deterministic testing strategy

## Runtime and Safety
We need loop control, tool policies, and safe side-effect boundaries.
- ReAct loop controller
- Circuit breaker patterns
- Policy enforcement for tool calls

## Evaluation
- Scenario-based regression evaluation
- Observability and runbooks
"""


class ScopePipelineTests(unittest.TestCase):
    def test_extract_scope_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            scope_path = Path(tmp_dir) / "scope.md"
            scope_path.write_text(SCOPE_MARKDOWN, encoding="utf-8")

            first = extract_scope(scope_path, mode=ScopeIngestMode.FULL)
            second = extract_scope(scope_path, mode=ScopeIngestMode.FULL)

            self.assertEqual(first.to_dict(), second.to_dict())
            self.assertGreater(len(first.items), 4)
            self.assertGreater(len(first.concepts), 4)

    def test_build_concept_dag_keeps_hard_edges_acyclic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            scope_path = Path(tmp_dir) / "scope.md"
            scope_path.write_text(SCOPE_MARKDOWN, encoding="utf-8")
            extraction = extract_scope(scope_path, mode=ScopeIngestMode.SEED_LIST)

            dag = build_concept_dag(extraction.concepts)
            order_index = {node_id: index for index, node_id in enumerate(dag.topological_order)}

            self.assertEqual(len(dag.concepts), len(dag.topological_order))
            for edge in dag.hard_edges:
                self.assertLess(order_index[edge.source_id], order_index[edge.target_id])

    def test_compile_scope_document_generates_valid_topic_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            scope_path = Path(tmp_dir) / "scope.md"
            scope_path.write_text(SCOPE_MARKDOWN, encoding="utf-8")

            compiled = compile_scope_document(
                scope_path,
                mode=ScopeIngestMode.SECTION,
                section_filters=("runtime", "evaluation"),
                policy=scope_policy_for_profile(ScopeProfile.BALANCED),
            )

            errors = validate_topic_spec_contract(compiled.topic_spec)
            self.assertEqual([], errors)
            self.assertGreater(len(compiled.scope_dag.payload["nodes"]), 2)
            self.assertIn("scope_in", compiled.topic_spec)
            self.assertGreater(len(compiled.topic_spec["scope_in"]), 2)
            self.assertEqual("1.0", compiled.scope_concepts.schema_version)
            self.assertEqual("scope_dag", compiled.scope_dag.artifact_type.value)

    def test_section_mode_requires_section_filters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            scope_path = Path(tmp_dir) / "scope.md"
            scope_path.write_text(SCOPE_MARKDOWN, encoding="utf-8")

            with self.assertRaises(LearningCompilerError):
                extract_scope(scope_path, mode=ScopeIngestMode.SECTION)

    def test_front_matter_lines_are_not_extracted_as_scope_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            scope_path = Path(tmp_dir) / "scope.md"
            scope_path.write_text(
                (
                    "---\n"
                    'title: "Atlas"\n'
                    'version: "1.0"\n'
                    "---\n"
                    "# Focus\n"
                    "- Learning loops\n"
                ),
                encoding="utf-8",
            )

            extracted = extract_scope(scope_path, mode=ScopeIngestMode.FULL)
            texts = {item.text for item in extracted.items}
            self.assertNotIn('title: "Atlas"', texts)
            self.assertNotIn('version: "1.0"', texts)
            self.assertIn("Focus", texts)
            self.assertIn("Learning loops", texts)

    def test_scope_artifact_parser_enforces_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            scope_path = Path(tmp_dir) / "scope.md"
            scope_path.write_text(SCOPE_MARKDOWN, encoding="utf-8")
            compiled = compile_scope_document(scope_path)

            parsed = parse_scope_artifact(
                compiled.scope_concepts.to_dict(),
                expected_type=ScopeArtifactType.CONCEPTS,
            )
            self.assertEqual("scope_concepts", parsed.artifact_type.value)

            with self.assertRaises(LearningCompilerError):
                parse_scope_artifact(
                    compiled.scope_concepts.to_dict(),
                    expected_type=ScopeArtifactType.DAG,
                )


if __name__ == "__main__":
    unittest.main()
