"""Curriculum validator orchestration entrypoint."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from learning_compiler.validator.rules import RULES, ValidationContext
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

    nodes = data.get("nodes")
    if not isinstance(nodes, list):
        result.fail("nodes must be an array")
        return result

    context = ValidationContext(
        data=data,
        nodes=nodes,
        config=config,
        topic_spec=topic_spec,
    )
    for rule in RULES:
        if not rule.enabled:
            continue
        rule.run(context, result)

    return result
