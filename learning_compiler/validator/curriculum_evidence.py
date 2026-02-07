"""Evidence-mode and open-question curriculum checks."""

from __future__ import annotations

from typing import Any

from learning_compiler.validator.helpers import is_non_empty_str, is_number
from learning_compiler.validator.types import DomainMode, EvidenceMode, ResourceRole, ValidationConfig, ValidationResult


def check_evidence(
    nodes: list[dict[str, Any]],
    result: ValidationResult,
    config: ValidationConfig,
) -> None:
    errors = 0

    for node in nodes:
        node_id = str(node.get("id", "???"))
        resources = node.get("resources", [])
        if not isinstance(resources, list):
            continue

        if len(resources) < 1:
            result.fail(f"Node {node_id}: minimal evidence requires at least 1 resource")
            errors += 1
            continue

        if config.evidence_mode in {EvidenceMode.STANDARD, EvidenceMode.STRICT}:
            if len(resources) < 2:
                result.fail(f"Node {node_id}: standard evidence requires at least 2 resources")
                errors += 1

            roles = {
                str(resource.get("role", ""))
                for resource in resources
                if isinstance(resource, dict)
            }
            if ResourceRole.DEFINITION.value not in roles:
                result.fail(
                    f"Node {node_id}: standard evidence requires a resource with role='definition'"
                )
                errors += 1
            if ResourceRole.EXAMPLE.value not in roles:
                result.fail(
                    f"Node {node_id}: standard evidence requires a resource with role='example'"
                )
                errors += 1

        if config.evidence_mode == EvidenceMode.STRICT:
            confidence = node.get("estimate_confidence")
            if not is_number(confidence):
                result.fail(f"Node {node_id}: strict evidence requires estimate_confidence")
                errors += 1

            for idx, resource in enumerate(resources):
                citation = resource.get("citation") if isinstance(resource, dict) else None
                if not is_non_empty_str(citation):
                    result.fail(f"Node {node_id}: resources[{idx}] missing citation in strict mode")
                    errors += 1

    if errors == 0:
        result.ok(f"Evidence checks passed for mode '{config.evidence_mode.value}'")


def check_open_questions(
    data: dict[str, Any],
    nodes: list[dict[str, Any]],
    result: ValidationResult,
    config: ValidationConfig,
) -> None:
    open_questions = data.get("open_questions")

    if config.evidence_mode != EvidenceMode.STRICT:
        if open_questions is not None and not isinstance(open_questions, list):
            result.fail("open_questions must be a list when provided")
        return

    if not isinstance(open_questions, list):
        result.fail("strict mode requires top-level open_questions list")
        return

    node_ids = {str(node.get("id")) for node in nodes if isinstance(node, dict)}
    errors = 0

    for idx, question in enumerate(open_questions):
        if not isinstance(question, dict):
            result.fail(f"open_questions[{idx}] must be an object")
            errors += 1
            continue

        required = {"question", "related_nodes", "status"}
        missing = sorted(required - set(question.keys()))
        if missing:
            result.fail(f"open_questions[{idx}] missing keys {missing}")
            errors += 1

        if not is_non_empty_str(question.get("question")):
            result.fail(f"open_questions[{idx}].question must be non-empty string")
            errors += 1

        related_nodes = question.get("related_nodes")
        if not isinstance(related_nodes, list) or not related_nodes:
            result.fail(f"open_questions[{idx}].related_nodes must be a non-empty list")
            errors += 1
        else:
            for node_id in related_nodes:
                if str(node_id) not in node_ids:
                    result.fail(
                        f"open_questions[{idx}].related_nodes references unknown node '{node_id}'"
                    )
                    errors += 1

        status = question.get("status")
        if status not in {"open", "resolved"}:
            result.fail(f"open_questions[{idx}].status must be 'open' or 'resolved'")
            errors += 1

    if config.domain_mode == DomainMode.FRONTIER and len(open_questions) == 0:
        result.warn("frontier + strict mode usually benefits from at least one open question")

    if errors == 0:
        result.ok("open_questions structure valid for strict mode")
