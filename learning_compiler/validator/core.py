"""Curriculum validator orchestration entrypoint."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from learning_compiler.validator.curriculum_evidence import check_evidence, check_open_questions
from learning_compiler.validator.curriculum_graph import (
    check_no_cycles,
    check_node_count,
    check_prerequisite_integrity,
    check_reachability,
    check_total_hours,
)
from learning_compiler.validator.curriculum_quality import (
    check_graph_progression,
    check_learner_path_coherence,
    check_node_quality,
    check_repetition,
    check_resource_relevance,
    check_time_granularity,
)
from learning_compiler.validator.curriculum_schema import (
    check_node_schema,
    check_top_level_structure,
    check_unique_ids_and_titles,
)
from learning_compiler.validator.topic_spec import build_validation_config, validate_topic_spec_contract
from learning_compiler.validator.types import ValidationResult


def validate(path: Path, topic_spec_path: Path | None = None) -> ValidationResult:
    result = ValidationResult()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        result.ok(f"JSON parsed successfully from {path}")
    except FileNotFoundError:
        result.fail(f"Curriculum file not found: {path}")
        return result
    except json.JSONDecodeError as exc:
        result.fail(f"Invalid curriculum JSON: {exc}")
        return result

    if not isinstance(data, dict):
        result.fail("curriculum root must be an object")
        return result

    topic_spec: dict[str, Any] | None = None
    if topic_spec_path is not None:
        try:
            parsed_topic_spec = json.loads(topic_spec_path.read_text(encoding="utf-8"))
            result.ok(f"Topic spec parsed successfully from {topic_spec_path}")
        except FileNotFoundError:
            result.fail(f"Topic spec not found: {topic_spec_path}")
            return result
        except json.JSONDecodeError as exc:
            result.fail(f"Invalid topic spec JSON: {exc}")
            return result

        spec_errors = validate_topic_spec_contract(parsed_topic_spec)
        if spec_errors:
            for error in spec_errors:
                result.fail(f"topic_spec contract error: {error}")
            return result

        result.ok("Topic spec contract is valid")
        topic_spec = parsed_topic_spec if isinstance(parsed_topic_spec, dict) else None

    config = build_validation_config(topic_spec)

    check_top_level_structure(data, result)

    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        result.fail("nodes must be an array")
        return result

    check_node_schema(nodes, result)
    check_unique_ids_and_titles(nodes, result)
    check_prerequisite_integrity(nodes, result, config)
    check_no_cycles(nodes, result)
    check_reachability(nodes, result)
    check_graph_progression(nodes, result)
    check_node_count(nodes, result, config)
    check_total_hours(nodes, result, config)
    check_node_quality(nodes, result)
    check_repetition(nodes, result)
    check_time_granularity(nodes, result)
    check_learner_path_coherence(nodes, result)
    check_evidence(nodes, result, config)
    check_resource_relevance(nodes, topic_spec, result)
    check_open_questions(data, nodes, result, config)

    return result
