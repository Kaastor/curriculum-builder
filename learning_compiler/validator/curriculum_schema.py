"""Schema-level curriculum checks."""

from __future__ import annotations

from collections import Counter
from typing import Any

from learning_compiler.validator.helpers import is_non_empty_str, is_number
from learning_compiler.validator.types import (
    ID_PATTERN,
    OPTIONAL_CURRICULUM_TOP_LEVEL,
    OPTIONAL_NODE_FIELDS,
    OPTIONAL_RESOURCE_FIELDS,
    REQUIRED_CURRICULUM_TOP_LEVEL,
    REQUIRED_MASTERY_FIELDS,
    REQUIRED_NODE_FIELDS,
    REQUIRED_RESOURCE_FIELDS,
    VALID_RESOURCE_KINDS,
    VALID_RESOURCE_ROLES,
    ValidationResult,
)


def check_top_level_structure(data: dict[str, Any], result: ValidationResult) -> None:
    missing = sorted(REQUIRED_CURRICULUM_TOP_LEVEL - set(data.keys()))
    if missing:
        result.fail(f"Missing top-level keys: {missing}")
    else:
        result.ok("All required top-level keys present")

    extra = sorted(set(data.keys()) - REQUIRED_CURRICULUM_TOP_LEVEL - OPTIONAL_CURRICULUM_TOP_LEVEL)
    if extra:
        result.fail(f"Unexpected top-level keys: {extra}")

    topic = data.get("topic")
    if not is_non_empty_str(topic):
        result.fail("topic must be a non-empty string")
    else:
        result.ok("topic is populated")


def check_node_schema(nodes: list[dict[str, Any]], result: ValidationResult) -> None:
    for node in nodes:
        if not isinstance(node, dict):
            result.fail("Each node must be an object")
            continue

        node_id = str(node.get("id", "???"))
        keys = set(node.keys())
        missing = sorted(REQUIRED_NODE_FIELDS - keys)
        extra = sorted(keys - REQUIRED_NODE_FIELDS - OPTIONAL_NODE_FIELDS)
        if missing:
            result.fail(f"Node {node_id}: missing fields {missing}")
        if extra:
            result.fail(f"Node {node_id}: unexpected fields {extra}")
        if not missing and not extra:
            result.ok(f"Node {node_id}: schema keys valid")

        if not is_non_empty_str(node.get("id")):
            result.fail(f"Node {node_id}: id must be non-empty string")
        elif not ID_PATTERN.match(str(node["id"])):
            result.fail(f"Node {node_id}: id format invalid")

        for field in ("title", "capability"):
            if not is_non_empty_str(node.get(field)):
                result.fail(f"Node {node_id}: {field} must be non-empty string")

        prereqs = node.get("prerequisites")
        if not isinstance(prereqs, list):
            result.fail(f"Node {node_id}: prerequisites must be a list")
        else:
            for idx, prereq_id in enumerate(prereqs):
                if not is_non_empty_str(prereq_id):
                    result.fail(f"Node {node_id}: prerequisites[{idx}] must be non-empty string")

        for field in ("core_ideas", "pitfalls"):
            value = node.get(field)
            if not isinstance(value, list):
                result.fail(f"Node {node_id}: {field} must be a list")
            else:
                for idx, item in enumerate(value):
                    if not is_non_empty_str(item):
                        result.fail(f"Node {node_id}: {field}[{idx}] must be non-empty string")

        mastery = node.get("mastery_check")
        if not isinstance(mastery, dict):
            result.fail(f"Node {node_id}: mastery_check must be an object")
        else:
            mastery_missing = sorted(REQUIRED_MASTERY_FIELDS - set(mastery.keys()))
            if mastery_missing:
                result.fail(f"Node {node_id}: mastery_check missing keys {mastery_missing}")
            for field in REQUIRED_MASTERY_FIELDS:
                if field in mastery and not is_non_empty_str(mastery[field]):
                    result.fail(f"Node {node_id}: mastery_check.{field} must be non-empty string")

        estimate = node.get("estimate_minutes")
        if not is_number(estimate):
            result.fail(f"Node {node_id}: estimate_minutes must be a number")
        elif float(estimate) <= 0:
            result.fail(f"Node {node_id}: estimate_minutes must be > 0")

        confidence = node.get("estimate_confidence")
        if confidence is not None:
            if not is_number(confidence):
                result.fail(f"Node {node_id}: estimate_confidence must be a number when provided")
            elif float(confidence) < 0 or float(confidence) > 1:
                result.fail(f"Node {node_id}: estimate_confidence must be in [0, 1]")

        resources = node.get("resources")
        if not isinstance(resources, list):
            result.fail(f"Node {node_id}: resources must be a list")
            continue

        for idx, resource in enumerate(resources):
            if not isinstance(resource, dict):
                result.fail(f"Node {node_id}: resources[{idx}] must be an object")
                continue

            resource_keys = set(resource.keys())
            missing_resource_keys = sorted(REQUIRED_RESOURCE_FIELDS - resource_keys)
            extra_resource_keys = sorted(
                resource_keys - REQUIRED_RESOURCE_FIELDS - OPTIONAL_RESOURCE_FIELDS
            )
            if missing_resource_keys:
                result.fail(f"Node {node_id}: resources[{idx}] missing keys {missing_resource_keys}")
            if extra_resource_keys:
                result.fail(
                    f"Node {node_id}: resources[{idx}] has unexpected keys {extra_resource_keys}"
                )

            for field in ("title", "url"):
                if field in resource and not is_non_empty_str(resource[field]):
                    result.fail(f"Node {node_id}: resources[{idx}].{field} must be non-empty string")

            kind = resource.get("kind")
            if kind not in VALID_RESOURCE_KINDS:
                result.fail(
                    f"Node {node_id}: resources[{idx}].kind must be one of {sorted(VALID_RESOURCE_KINDS)}"
                )

            role = resource.get("role")
            if role is not None and role not in VALID_RESOURCE_ROLES:
                result.fail(
                    f"Node {node_id}: resources[{idx}].role must be one of {sorted(VALID_RESOURCE_ROLES)}"
                )


def check_unique_ids_and_titles(nodes: list[dict[str, Any]], result: ValidationResult) -> None:
    ids = [str(node.get("id", "")) for node in nodes if isinstance(node, dict)]
    titles = [str(node.get("title", "")) for node in nodes if isinstance(node, dict)]

    duplicate_ids = sorted([item for item, count in Counter(ids).items() if item and count > 1])
    if duplicate_ids:
        result.fail(f"Duplicate node IDs: {duplicate_ids}")
    else:
        result.ok("All node IDs unique")

    duplicate_titles = sorted(
        [item for item, count in Counter(titles).items() if item and count > 1]
    )
    if duplicate_titles:
        result.fail(f"Duplicate node titles: {duplicate_titles}")
    else:
        result.ok("All node titles unique")
