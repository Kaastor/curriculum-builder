"""Topic spec contract validation and config derivation."""

from __future__ import annotations

from typing import Any

from learning_compiler.validator.helpers import coerce_int, is_non_empty_str, is_number, looks_placeholder
from learning_compiler.validator.types import (
    DomainMode,
    EvidenceMode,
    OPTIONAL_CONSTRAINT_FIELDS,
    OPTIONAL_TOPIC_SPEC_FIELDS,
    REQUIRED_CONSTRAINT_FIELDS,
    REQUIRED_TOPIC_SPEC_FIELDS,
    VALID_DEPTHS,
    VALID_DOMAIN_MODES,
    VALID_EVIDENCE_MODES,
    ValidationConfig,
)


def _parse_domain_mode(value: Any) -> DomainMode:
    try:
        return DomainMode(str(value))
    except ValueError:
        return DomainMode.MATURE


def _parse_evidence_mode(value: Any) -> EvidenceMode:
    try:
        return EvidenceMode(str(value))
    except ValueError:
        return EvidenceMode.MINIMAL


def validate_topic_spec_contract(topic_spec: object) -> list[str]:
    errors: list[str] = []

    if not isinstance(topic_spec, dict):
        return ["topic_spec must be a JSON object"]

    missing = sorted(REQUIRED_TOPIC_SPEC_FIELDS - set(topic_spec.keys()))
    if missing:
        errors.append(f"Missing topic_spec keys: {missing}")

    extra = sorted(
        set(topic_spec.keys()) - REQUIRED_TOPIC_SPEC_FIELDS - OPTIONAL_TOPIC_SPEC_FIELDS
    )
    if extra:
        errors.append(f"Unexpected topic_spec keys: {extra}")

    spec_version = topic_spec.get("spec_version", "1.0")
    if spec_version != "1.0":
        errors.append("spec_version must be '1.0'")

    for field in ("goal", "audience"):
        value = topic_spec.get(field)
        if not is_non_empty_str(value):
            errors.append(f"{field} must be a non-empty string")
        elif looks_placeholder(value):
            errors.append(f"{field} must not use placeholder text")

    for field in ("prerequisites", "scope_in", "scope_out"):
        value = topic_spec.get(field)
        if not isinstance(value, list):
            errors.append(f"{field} must be a list")
            continue
        for idx, item in enumerate(value):
            if not is_non_empty_str(item):
                errors.append(f"{field}[{idx}] must be a non-empty string")

    misconceptions = topic_spec.get("misconceptions")
    if misconceptions is not None:
        if not isinstance(misconceptions, list):
            errors.append("misconceptions must be a list when provided")
        else:
            for idx, item in enumerate(misconceptions):
                if not is_non_empty_str(item):
                    errors.append(f"misconceptions[{idx}] must be a non-empty string")

    constraints = topic_spec.get("constraints")
    if not isinstance(constraints, dict):
        errors.append("constraints must be an object")
        return errors

    constraints_missing = sorted(REQUIRED_CONSTRAINT_FIELDS - set(constraints.keys()))
    if constraints_missing:
        errors.append(f"constraints missing keys: {constraints_missing}")

    constraints_extra = sorted(
        set(constraints.keys()) - REQUIRED_CONSTRAINT_FIELDS - OPTIONAL_CONSTRAINT_FIELDS
    )
    if constraints_extra:
        errors.append(f"constraints has unexpected keys: {constraints_extra}")

    for field in ("hours_per_week", "total_hours_min", "total_hours_max"):
        value = constraints.get(field)
        if not is_number(value):
            errors.append(f"constraints.{field} must be a number")
        elif float(value) <= 0:
            errors.append(f"constraints.{field} must be > 0")

    total_min = constraints.get("total_hours_min")
    total_max = constraints.get("total_hours_max")
    if is_number(total_min) and is_number(total_max) and float(total_min) > float(total_max):
        errors.append("constraints.total_hours_min must be <= constraints.total_hours_max")

    depth = constraints.get("depth")
    if depth not in VALID_DEPTHS:
        errors.append(f"constraints.depth must be one of {sorted(VALID_DEPTHS)}")

    node_count_min = constraints.get("node_count_min")
    node_count_max = constraints.get("node_count_max")
    if node_count_min is not None and coerce_int(node_count_min) is None:
        errors.append("constraints.node_count_min must be int when provided")
    if node_count_max is not None and coerce_int(node_count_max) is None:
        errors.append("constraints.node_count_max must be int when provided")

    node_count_min_int = coerce_int(node_count_min)
    node_count_max_int = coerce_int(node_count_max)
    if node_count_min_int is not None and node_count_max_int is not None:
        if node_count_min_int > node_count_max_int:
            errors.append("constraints.node_count_min must be <= constraints.node_count_max")

    max_prereqs = constraints.get("max_prerequisites_per_node")
    if max_prereqs is not None:
        max_prereqs_int = coerce_int(max_prereqs)
        if max_prereqs_int is None or max_prereqs_int < 1:
            errors.append("constraints.max_prerequisites_per_node must be int >= 1 when provided")

    domain_mode = topic_spec.get("domain_mode")
    if domain_mode not in VALID_DOMAIN_MODES:
        errors.append(f"domain_mode must be one of {sorted(VALID_DOMAIN_MODES)}")

    evidence_mode = topic_spec.get("evidence_mode")
    if evidence_mode not in VALID_EVIDENCE_MODES:
        errors.append(f"evidence_mode must be one of {sorted(VALID_EVIDENCE_MODES)}")

    return errors


def build_validation_config(topic_spec: dict[str, Any] | None) -> ValidationConfig:
    if not topic_spec:
        return ValidationConfig(
            evidence_mode=EvidenceMode.MINIMAL,
            domain_mode=DomainMode.MATURE,
            total_hours_min=8.0,
            total_hours_max=40.0,
            node_count_min=None,
            node_count_max=None,
            max_prerequisites_per_node=None,
        )

    constraints = topic_spec.get("constraints", {})
    return ValidationConfig(
        evidence_mode=_parse_evidence_mode(topic_spec.get("evidence_mode", EvidenceMode.MINIMAL.value)),
        domain_mode=_parse_domain_mode(topic_spec.get("domain_mode", DomainMode.MATURE.value)),
        total_hours_min=float(constraints.get("total_hours_min", 8.0)),
        total_hours_max=float(constraints.get("total_hours_max", 40.0)),
        node_count_min=coerce_int(constraints.get("node_count_min")),
        node_count_max=coerce_int(constraints.get("node_count_max")),
        max_prerequisites_per_node=coerce_int(constraints.get("max_prerequisites_per_node")),
    )
