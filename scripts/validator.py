#!/usr/bin/env python3
"""
Curriculum JSON Validator - Structural Integrity Checks.

Usage:
    python scripts/validator.py [path/to/curriculum.json] [--topic-spec path/to/topic_spec.json]

Exit codes:
    0 - all checks passed
    1 - one or more checks failed
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# --- Constants -----------------------------------------------------------------

VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
VALID_EXERCISE_TYPES = {"write", "debug", "read", "integrate"}

REQUIRED_NODE_FIELDS = {
    "id",
    "title",
    "category",
    "layer",
    "difficulty",
    "estimated_time_minutes",
    "exercise_type",
    "failure_mode",
    "exercise",
    "pass_condition",
    "fail_condition",
    "reference_hint",
    "prerequisites",
    "dependents",
    "teaches",
    "connects_to_field_map",
    "tags",
    "skeleton_file",
}

DEFAULT_VALID_CATEGORIES = {
    "foundation",
    "selection",
    "ordering",
    "arguments",
    "output",
    "hallucination",
    "avoidance",
    "debug",
    "capstone",
}

DEFAULT_CATEGORY_PREFIXES = {
    "foundation": "F",
    "selection": "S",
    "ordering": "O",
    "arguments": "A",
    "output": "R",
    "hallucination": "H",
    "avoidance": "V",
    "debug": "D",
    "capstone": "C",
}

DEFAULT_REQUIRED_COVERAGE_KEYS = {
    "choosing_wrong_tool",
    "wrong_call_order",
    "malformed_arguments",
    "output_misinterpretation",
    "tool_hallucination",
    "tool_avoidance",
}

DEFAULT_CONSTRAINTS = {
    "max_layers": 5,
    "node_count_min": 18,
    "node_count_max": 25,
    "max_prerequisites_per_node": 3,
    "exercise_time_min_minutes": 30,
    "exercise_time_max_minutes": 90,
    "debug_read_min": 2,
    "debug_read_max": 3,
    "capstone_exactly": 1,
    "capstone_layer": 4,
    "allow_external_services": False,
    "target_total_hours_min": 12,
    "target_total_hours_max": 24,
}

PLACEHOLDER_STRINGS = {
    "replace with topic name",
    "internal-map-or-source",
    "e.g. backend_developer",
    "primary scenario",
    "different but related scenario",
    "prerequisite 1",
    "prerequisite 2",
    "what learner can do after completing this curriculum.",
    "define objective mastery criteria.",
    "optional-repo-name",
    "optional_package_name",
    "example failure mode",
    "example pattern",
}

PLACEHOLDER_KEYS = {"replace_with_topic_id", "example_failure_mode", "example_pattern"}

TOPIC_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


# --- Helpers -------------------------------------------------------------------


@dataclass
class ValidationConfig:
    valid_categories: set[str]
    category_prefixes: dict[str, str]
    required_coverage_keys: set[str]
    pattern_minimum_coverage: dict[str, int]
    max_layer: int
    min_nodes: int
    max_nodes: int
    max_prereqs: int
    time_min: int
    time_max: int
    debug_read_min: int
    debug_read_max: int
    capstone_exactly: int
    capstone_layer: int
    capstone_category_key: str
    target_total_hours_min: int
    target_total_hours_max: int
    transfer_required: bool
    capstone_required_failure_modes: set[str]
    topic_spec_provided: bool


class ValidationResult:
    def __init__(self) -> None:
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.warnings: list[str] = []

    def ok(self, msg: str) -> None:
        self.passed.append(msg)

    def fail(self, msg: str) -> None:
        self.failed.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def report(self) -> str:
        lines: list[str] = []
        lines.append(f"\n{'='*60}")
        lines.append("CURRICULUM VALIDATION REPORT")
        lines.append(f"{'='*60}\n")

        lines.append(f"✅ PASSED: {len(self.passed)}")
        for message in self.passed:
            lines.append(f"   ✅ {message}")

        if self.warnings:
            lines.append(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            for message in self.warnings:
                lines.append(f"   ⚠️  {message}")

        if self.failed:
            lines.append(f"\n❌ FAILED: {len(self.failed)}")
            for message in self.failed:
                lines.append(f"   ❌ {message}")
        else:
            lines.append("\n🎉 ALL CHECKS PASSED")

        lines.append(f"\n{'='*60}")
        lines.append(
            f"Total: {len(self.passed)} passed, "
            f"{len(self.warnings)} warnings, "
            f"{len(self.failed)} failed"
        )
        lines.append(f"{'='*60}\n")
        return "\n".join(lines)

    @property
    def success(self) -> bool:
        return len(self.failed) == 0


def _int_or_default(value: Any, default: int) -> int:
    return value if isinstance(value, int) else default


def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _looks_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    if not normalized:
        return True
    if normalized in PLACEHOLDER_STRINGS:
        return True
    return normalized.startswith("replace_with_") or normalized in PLACEHOLDER_KEYS


def validate_topic_spec_contract(topic_spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(topic_spec, dict):
        return ["topic_spec must be a JSON object"]

    required_top_level = {
        "topic_id",
        "topic_name",
        "domain_ref",
        "target_role",
        "language",
        "project_type",
        "scenario",
        "transfer_scenario",
        "prerequisites",
        "outcome",
        "failure_modes",
        "design_patterns",
        "exercise_categories",
        "assessment",
    }
    missing_top_level = sorted(required_top_level - set(topic_spec.keys()))
    if missing_top_level:
        errors.append(f"Missing topic_spec keys: {missing_top_level}")
        return errors

    spec_version = topic_spec.get("spec_version", "1.0")
    if spec_version != "1.0":
        errors.append("spec_version must be '1.0'")

    topic_id = str(topic_spec.get("topic_id", "")).strip()
    if not TOPIC_ID_PATTERN.match(topic_id):
        errors.append("topic_id must be a lowercase snake/kebab slug")
    elif _looks_placeholder(topic_id):
        errors.append("topic_id must not use template placeholder value")

    required_str_fields = [
        "topic_name",
        "domain_ref",
        "target_role",
        "language",
        "project_type",
        "scenario",
        "transfer_scenario",
        "outcome",
    ]
    for field in required_str_fields:
        value = topic_spec.get(field)
        if not _is_non_empty_str(value):
            errors.append(f"{field} must be a non-empty string")
            continue
        if _looks_placeholder(str(value)):
            errors.append(f"{field} must not use template placeholder value")

    scenario = str(topic_spec.get("scenario", "")).strip()
    transfer_scenario = str(topic_spec.get("transfer_scenario", "")).strip()
    if scenario and transfer_scenario and scenario == transfer_scenario:
        errors.append("transfer_scenario must differ from scenario")

    prerequisites = topic_spec.get("prerequisites")
    if not isinstance(prerequisites, list) or not prerequisites:
        errors.append("prerequisites must be a non-empty list")
    else:
        for idx, item in enumerate(prerequisites):
            if not _is_non_empty_str(item):
                errors.append(f"prerequisites[{idx}] must be a non-empty string")
            elif _looks_placeholder(str(item)):
                errors.append(f"prerequisites[{idx}] must not use template placeholder value")

    failure_modes = topic_spec.get("failure_modes")
    if not isinstance(failure_modes, list) or not failure_modes:
        errors.append("failure_modes must be a non-empty list")
        failure_mode_keys: set[str] = set()
    else:
        failure_mode_keys = set()
        for idx, item in enumerate(failure_modes):
            if not isinstance(item, dict):
                errors.append(f"failure_modes[{idx}] must be an object")
                continue
            for field in (
                "key",
                "label",
                "description",
                "production_impact",
                "example",
                "must_cover_in_capstone",
            ):
                if field not in item:
                    errors.append(f"failure_modes[{idx}].{field} missing")
            key = str(item.get("key", "")).strip()
            if not SNAKE_CASE_PATTERN.match(key):
                errors.append(f"failure_modes[{idx}].key must be snake_case")
            elif key in failure_mode_keys:
                errors.append(f"failure_modes key duplicated: {key}")
            elif _looks_placeholder(key):
                errors.append("failure_modes key must not use template placeholder value")
            else:
                failure_mode_keys.add(key)
            if not isinstance(item.get("must_cover_in_capstone"), bool):
                errors.append(f"failure_modes[{idx}].must_cover_in_capstone must be boolean")

    design_patterns = topic_spec.get("design_patterns")
    if not isinstance(design_patterns, list):
        errors.append("design_patterns must be a list")
        design_pattern_keys: set[str] = set()
    else:
        design_pattern_keys = set()
        for idx, item in enumerate(design_patterns):
            if not isinstance(item, dict):
                errors.append(f"design_patterns[{idx}] must be an object")
                continue
            for field in ("key", "name", "problem", "minimum_coverage"):
                if field not in item:
                    errors.append(f"design_patterns[{idx}].{field} missing")
            key = str(item.get("key", "")).strip()
            if not SNAKE_CASE_PATTERN.match(key):
                errors.append(f"design_patterns[{idx}].key must be snake_case")
            elif key in design_pattern_keys:
                errors.append(f"design_patterns key duplicated: {key}")
            elif _looks_placeholder(key):
                errors.append("design_patterns key must not use template placeholder value")
            else:
                design_pattern_keys.add(key)
            minimum = item.get("minimum_coverage")
            if not isinstance(minimum, int) or minimum < 1:
                errors.append(f"design_patterns[{idx}].minimum_coverage must be int >= 1")

    categories = topic_spec.get("exercise_categories")
    if not isinstance(categories, list) or not categories:
        errors.append("exercise_categories must be a non-empty list")
        category_keys: set[str] = set()
    else:
        category_keys = set()
        category_prefixes: set[str] = set()
        capstone_count = 0
        capstone_supports_integrate = False
        for idx, item in enumerate(categories):
            if not isinstance(item, dict):
                errors.append(f"exercise_categories[{idx}] must be an object")
                continue
            for field in ("key", "prefix", "description", "supports_exercise_types", "is_capstone"):
                if field not in item:
                    errors.append(f"exercise_categories[{idx}].{field} missing")
            key = str(item.get("key", "")).strip()
            prefix = str(item.get("prefix", "")).strip()
            if not key:
                errors.append(f"exercise_categories[{idx}].key must be non-empty")
            elif key in category_keys:
                errors.append(f"exercise_categories key duplicated: {key}")
            else:
                category_keys.add(key)

            if not prefix or not prefix.isupper() or prefix == "MS":
                errors.append(f"exercise_categories[{idx}].prefix must be uppercase and not 'MS'")
            elif prefix in category_prefixes:
                errors.append(f"exercise_categories prefix duplicated: {prefix}")
            else:
                category_prefixes.add(prefix)

            supports = item.get("supports_exercise_types")
            if not isinstance(supports, list) or not supports:
                errors.append(f"exercise_categories[{idx}].supports_exercise_types must be a non-empty list")

            is_capstone = item.get("is_capstone")
            if not isinstance(is_capstone, bool):
                errors.append(f"exercise_categories[{idx}].is_capstone must be boolean")
            elif is_capstone:
                capstone_count += 1
                if isinstance(supports, list) and "integrate" in supports:
                    capstone_supports_integrate = True

        if capstone_count != 1:
            errors.append("Exactly one exercise category must have is_capstone=true")
        if capstone_count == 1 and not capstone_supports_integrate:
            errors.append("Capstone category must include 'integrate' in supports_exercise_types")

    constraints_raw = topic_spec.get("constraints", {})
    if constraints_raw is None:
        constraints_raw = {}
    if not isinstance(constraints_raw, dict):
        errors.append("constraints must be an object")
        constraints: dict[str, Any] = {}
    else:
        constraints = constraints_raw

    def _int_with_default(name: str) -> int:
        value = constraints.get(name, DEFAULT_CONSTRAINTS[name])
        if not isinstance(value, int):
            errors.append(f"constraints.{name} must be int")
            return int(DEFAULT_CONSTRAINTS[name])
        return int(value)

    max_layers = _int_with_default("max_layers")
    node_count_min = _int_with_default("node_count_min")
    node_count_max = _int_with_default("node_count_max")
    debug_read_min = _int_with_default("debug_read_min")
    debug_read_max = _int_with_default("debug_read_max")
    capstone_layer = _int_with_default("capstone_layer")
    _int_with_default("max_prerequisites_per_node")
    _int_with_default("exercise_time_min_minutes")
    _int_with_default("exercise_time_max_minutes")
    _int_with_default("capstone_exactly")
    _int_with_default("target_total_hours_min")
    _int_with_default("target_total_hours_max")
    allow_external_services = constraints.get(
        "allow_external_services", DEFAULT_CONSTRAINTS.get("allow_external_services", False)
    )
    if not isinstance(allow_external_services, bool):
        errors.append("constraints.allow_external_services must be boolean")

    if (
        node_count_min is not None
        and node_count_max is not None
        and node_count_min > node_count_max
    ):
        errors.append("constraints.node_count_min must be <= node_count_max")
    if (
        debug_read_min is not None
        and debug_read_max is not None
        and debug_read_min > debug_read_max
    ):
        errors.append("constraints.debug_read_min must be <= debug_read_max")
    if (
        max_layers is not None
        and capstone_layer is not None
        and (capstone_layer < 0 or capstone_layer >= max_layers)
    ):
        errors.append("constraints.capstone_layer must be in [0, max_layers-1]")

    assessment = topic_spec.get("assessment")
    required_assessment = {
        "capstone_required_failure_modes",
        "mastery_threshold",
    }
    if not isinstance(assessment, dict):
        errors.append("assessment must be an object")
        assessment = {}
    else:
        missing_assessment = sorted(required_assessment - set(assessment.keys()))
        if missing_assessment:
            errors.append(f"assessment missing keys: {missing_assessment}")

    capstone_required = assessment.get("capstone_required_failure_modes")
    if not isinstance(capstone_required, list) or not capstone_required:
        errors.append("assessment.capstone_required_failure_modes must be a non-empty list")
    else:
        unknown = [key for key in capstone_required if key not in failure_mode_keys]
        if unknown:
            errors.append(
                "assessment.capstone_required_failure_modes contains unknown keys: "
                f"{sorted(set(unknown))}"
            )

    if not _is_non_empty_str(assessment.get("mastery_threshold")):
        errors.append("assessment.mastery_threshold must be a non-empty string")
    transfer_required = assessment.get("transfer_task_required", True)
    if not isinstance(transfer_required, bool):
        errors.append("assessment.transfer_task_required must be boolean")
    max_uncaught = assessment.get("max_uncaught_failure_modes", 1)
    if not isinstance(max_uncaught, int):
        errors.append("assessment.max_uncaught_failure_modes must be int")

    repo_preferences = topic_spec.get("repo_preferences", {})
    if repo_preferences is None:
        repo_preferences = {}
    if not isinstance(repo_preferences, dict):
        errors.append("repo_preferences must be an object")
    else:
        use_makefile = repo_preferences.get("use_makefile", True)
        if not isinstance(use_makefile, bool):
            errors.append("repo_preferences.use_makefile must be boolean")

    return errors


def build_validation_config(topic_spec: dict[str, Any] | None) -> ValidationConfig:
    if not topic_spec:
        max_layers = DEFAULT_CONSTRAINTS["max_layers"]
        return ValidationConfig(
            valid_categories=set(DEFAULT_VALID_CATEGORIES),
            category_prefixes=dict(DEFAULT_CATEGORY_PREFIXES),
            required_coverage_keys=set(DEFAULT_REQUIRED_COVERAGE_KEYS),
            pattern_minimum_coverage={},
            max_layer=max_layers - 1,
            min_nodes=DEFAULT_CONSTRAINTS["node_count_min"],
            max_nodes=DEFAULT_CONSTRAINTS["node_count_max"],
            max_prereqs=DEFAULT_CONSTRAINTS["max_prerequisites_per_node"],
            time_min=DEFAULT_CONSTRAINTS["exercise_time_min_minutes"],
            time_max=DEFAULT_CONSTRAINTS["exercise_time_max_minutes"],
            debug_read_min=DEFAULT_CONSTRAINTS["debug_read_min"],
            debug_read_max=DEFAULT_CONSTRAINTS["debug_read_max"],
            capstone_exactly=DEFAULT_CONSTRAINTS["capstone_exactly"],
            capstone_layer=DEFAULT_CONSTRAINTS["capstone_layer"],
            capstone_category_key="capstone",
            target_total_hours_min=DEFAULT_CONSTRAINTS["target_total_hours_min"],
            target_total_hours_max=DEFAULT_CONSTRAINTS["target_total_hours_max"],
            transfer_required=False,
            capstone_required_failure_modes=set(),
            topic_spec_provided=False,
        )

    constraints = topic_spec.get("constraints", {}) if isinstance(topic_spec.get("constraints"), dict) else {}
    assessment = topic_spec.get("assessment", {}) if isinstance(topic_spec.get("assessment"), dict) else {}
    categories = topic_spec.get("exercise_categories", []) if isinstance(topic_spec.get("exercise_categories"), list) else []
    failure_modes = topic_spec.get("failure_modes", []) if isinstance(topic_spec.get("failure_modes"), list) else []
    design_patterns = topic_spec.get("design_patterns", []) if isinstance(topic_spec.get("design_patterns"), list) else []

    valid_categories = {
        str(item.get("key", "")).strip()
        for item in categories
        if isinstance(item, dict) and str(item.get("key", "")).strip()
    }

    category_prefixes: dict[str, str] = {}
    for item in categories:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key", "")).strip()
        prefix = str(item.get("prefix", "")).strip()
        if key:
            category_prefixes[key] = prefix

    capstone_categories = [
        str(item.get("key", "")).strip()
        for item in categories
        if isinstance(item, dict) and item.get("is_capstone") is True and str(item.get("key", "")).strip()
    ]
    if capstone_categories:
        capstone_category_key = capstone_categories[0]
    elif "capstone" in valid_categories:
        capstone_category_key = "capstone"
    else:
        capstone_category_key = sorted(valid_categories)[-1]

    coverage_keys = {
        str(item.get("key", "")).strip()
        for item in failure_modes
        if isinstance(item, dict) and str(item.get("key", "")).strip()
    }

    pattern_minimum_coverage: dict[str, int] = {}
    for item in design_patterns:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key", "")).strip()
        if not key:
            continue
        minimum = _int_or_default(item.get("minimum_coverage"), 1)
        pattern_minimum_coverage[key] = max(1, minimum)

    max_layers = max(1, _int_or_default(constraints.get("max_layers"), DEFAULT_CONSTRAINTS["max_layers"]))

    capstone_required_failure_modes = {
        str(item).strip()
        for item in assessment.get("capstone_required_failure_modes", [])
        if str(item).strip()
    }

    return ValidationConfig(
        valid_categories=valid_categories,
        category_prefixes=category_prefixes,
        required_coverage_keys=coverage_keys,
        pattern_minimum_coverage=pattern_minimum_coverage,
        max_layer=max_layers - 1,
        min_nodes=_int_or_default(constraints.get("node_count_min"), DEFAULT_CONSTRAINTS["node_count_min"]),
        max_nodes=_int_or_default(constraints.get("node_count_max"), DEFAULT_CONSTRAINTS["node_count_max"]),
        max_prereqs=_int_or_default(
            constraints.get("max_prerequisites_per_node"),
            DEFAULT_CONSTRAINTS["max_prerequisites_per_node"],
        ),
        time_min=_int_or_default(
            constraints.get("exercise_time_min_minutes"),
            DEFAULT_CONSTRAINTS["exercise_time_min_minutes"],
        ),
        time_max=_int_or_default(
            constraints.get("exercise_time_max_minutes"),
            DEFAULT_CONSTRAINTS["exercise_time_max_minutes"],
        ),
        debug_read_min=_int_or_default(constraints.get("debug_read_min"), DEFAULT_CONSTRAINTS["debug_read_min"]),
        debug_read_max=_int_or_default(constraints.get("debug_read_max"), DEFAULT_CONSTRAINTS["debug_read_max"]),
        capstone_exactly=_int_or_default(constraints.get("capstone_exactly"), DEFAULT_CONSTRAINTS["capstone_exactly"]),
        capstone_layer=_int_or_default(constraints.get("capstone_layer"), DEFAULT_CONSTRAINTS["capstone_layer"]),
        capstone_category_key=capstone_category_key,
        target_total_hours_min=_int_or_default(
            constraints.get("target_total_hours_min"),
            DEFAULT_CONSTRAINTS["target_total_hours_min"],
        ),
        target_total_hours_max=_int_or_default(
            constraints.get("target_total_hours_max"),
            DEFAULT_CONSTRAINTS["target_total_hours_max"],
        ),
        transfer_required=bool(assessment.get("transfer_task_required", True)),
        capstone_required_failure_modes=capstone_required_failure_modes,
        topic_spec_provided=True,
    )


# --- Checks --------------------------------------------------------------------


def check_top_level_structure(data: dict[str, Any], r: ValidationResult, cfg: ValidationConfig) -> None:
    required = {
        "domain",
        "domain_ref",
        "scenario",
        "metadata",
        "nodes",
        "edges",
        "learning_path",
        "milestones",
        "coverage_map",
        "pattern_coverage_map",
    }

    missing = required - set(data.keys())
    if missing:
        r.fail(f"Missing top-level keys: {sorted(missing)}")
    else:
        r.ok("All top-level keys present")


def check_metadata(data: dict[str, Any], r: ValidationResult, cfg: ValidationConfig) -> None:
    meta = data.get("metadata", {})
    if not isinstance(meta, dict):
        r.fail("metadata must be an object")
        return

    for field in ("generated", "node_count", "edge_count", "max_depth"):
        if field not in meta:
            r.fail(f"metadata.{field} missing")

    node_count = meta.get("node_count")
    if isinstance(node_count, int):
        actual = len(data.get("nodes", []))
        if node_count != actual:
            r.fail(f"metadata.node_count={node_count} but nodes has {actual}")
        else:
            r.ok(f"metadata.node_count matches actual ({actual})")
    else:
        r.fail(f"metadata.node_count should be int, got {type(node_count).__name__}")

    edge_count = meta.get("edge_count")
    if isinstance(edge_count, int):
        actual = len(data.get("edges", []))
        if edge_count != actual:
            r.fail(f"metadata.edge_count={edge_count} but edges has {actual}")
        else:
            r.ok(f"metadata.edge_count matches actual ({actual})")
    else:
        r.fail(f"metadata.edge_count should be int, got {type(edge_count).__name__}")

    max_depth = meta.get("max_depth")
    if isinstance(max_depth, int):
        if max_depth > cfg.max_layer:
            r.fail(f"metadata.max_depth={max_depth} exceeds configured max layer {cfg.max_layer}")
    else:
        r.fail(f"metadata.max_depth should be int, got {type(max_depth).__name__}")


def check_node_count(nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig) -> None:
    n = len(nodes)
    if cfg.min_nodes <= n <= cfg.max_nodes:
        r.ok(f"Node count {n} within [{cfg.min_nodes}, {cfg.max_nodes}]")
    else:
        r.fail(f"Node count {n} outside [{cfg.min_nodes}, {cfg.max_nodes}]")


def check_node_schema(nodes: list[dict[str, Any]], r: ValidationResult) -> None:
    for node in nodes:
        nid = node.get("id", "???")
        fields = set(node.keys())
        missing = REQUIRED_NODE_FIELDS - fields
        extra = fields - REQUIRED_NODE_FIELDS
        if missing:
            r.fail(f"Node {nid}: missing fields {sorted(missing)}")
        if extra:
            r.fail(f"Node {nid}: extra fields {sorted(extra)}")
        if not missing and not extra:
            r.ok(f"Node {nid}: schema correct (18 fields)")


def check_id_prefixes(nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig) -> None:
    errors = 0
    for node in nodes:
        nid = str(node.get("id", ""))
        category = str(node.get("category", ""))
        expected_prefix = cfg.category_prefixes.get(category)
        if expected_prefix is None:
            continue
        if not expected_prefix:
            r.fail(f"Node {nid}: category '{category}' has no configured prefix")
            errors += 1
            continue
        if not nid.startswith(expected_prefix):
            r.fail(
                f"Node {nid}: category '{category}' expects prefix '{expected_prefix}', got '{nid}'"
            )
            errors += 1
    if errors == 0:
        r.ok("All node IDs match configured category prefixes")


def check_enums(nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig) -> None:
    errors = 0
    for node in nodes:
        nid = node.get("id", "???")

        category = node.get("category")
        if category not in cfg.valid_categories:
            r.fail(f"Node {nid}: invalid category '{category}'")
            errors += 1

        difficulty = node.get("difficulty")
        if difficulty not in VALID_DIFFICULTIES:
            r.fail(f"Node {nid}: invalid difficulty '{difficulty}'")
            errors += 1

        exercise_type = node.get("exercise_type")
        if exercise_type not in VALID_EXERCISE_TYPES:
            r.fail(f"Node {nid}: invalid exercise_type '{exercise_type}'")
            errors += 1

    if errors == 0:
        r.ok("All category, difficulty, and exercise_type values valid")


def check_exercise_distribution(nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig) -> None:
    debug_read = [n for n in nodes if n.get("exercise_type") in ("debug", "read")]
    capstone_nodes = [n for n in nodes if n.get("exercise_type") == "integrate"]

    if len(debug_read) < cfg.debug_read_min:
        r.fail(
            f"Only {len(debug_read)} debug/read nodes - need at least {cfg.debug_read_min}"
        )
    elif len(debug_read) > cfg.debug_read_max:
        r.warn(
            f"{len(debug_read)} debug/read nodes - expected {cfg.debug_read_min}-{cfg.debug_read_max}"
        )
    else:
        r.ok(
            f"{len(debug_read)} debug/read nodes (within {cfg.debug_read_min}-{cfg.debug_read_max} range)"
        )

    min_debug_layer = max(0, cfg.capstone_layer - 1)
    debug_layer_errors = 0
    for node in debug_read:
        layer = node.get("layer")
        if not isinstance(layer, int) or layer < min_debug_layer:
            r.fail(
                f"Debug/read node {node.get('id', '???')} at layer {layer} - should be at layer >= {min_debug_layer}"
            )
            debug_layer_errors += 1
    if debug_read and debug_layer_errors == 0:
        r.ok("All debug/read nodes are in upper layers")

    if len(capstone_nodes) != cfg.capstone_exactly:
        r.fail(
            f"{len(capstone_nodes)} integrate nodes - expected exactly {cfg.capstone_exactly}"
        )
        return

    errors = 0
    for capstone in capstone_nodes:
        cid = capstone.get("id", "???")
        if capstone.get("layer") != cfg.capstone_layer:
            r.fail(f"Capstone {cid} at layer {capstone.get('layer')} - must be {cfg.capstone_layer}")
            errors += 1
        if capstone.get("category") != cfg.capstone_category_key:
            r.fail(
                f"Capstone {cid} has category '{capstone.get('category')}' - must be '{cfg.capstone_category_key}'"
            )
            errors += 1
    if errors == 0:
        r.ok(
            f"Capstone count and placement match (count={cfg.capstone_exactly}, layer={cfg.capstone_layer}, category={cfg.capstone_category_key})"
        )


def check_reference_hints(nodes: list[dict[str, Any]], r: ValidationResult) -> None:
    errors = 0
    for node in nodes:
        nid = node.get("id", "???")
        hint = str(node.get("reference_hint", ""))
        if len(hint.strip()) < 20:
            r.fail(f"Node {nid}: reference_hint is missing or too short ({len(hint.strip())} chars)")
            errors += 1
    if errors == 0:
        r.ok("All nodes have non-trivial reference_hint (>=20 chars)")


def check_layers(nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig) -> None:
    node_map = {n["id"]: n for n in nodes if isinstance(n, dict) and "id" in n}
    errors = 0

    for node in nodes:
        nid = node.get("id", "???")
        layer = node.get("layer")
        if not isinstance(layer, int) or layer < 0 or layer > cfg.max_layer:
            r.fail(f"Node {nid}: layer={layer} outside [0, {cfg.max_layer}]")
            errors += 1
            continue

        prereqs = node.get("prerequisites", [])
        if not isinstance(prereqs, list):
            r.fail(f"Node {nid}: prerequisites must be a list")
            errors += 1
            continue

        if layer == 0 and prereqs:
            r.fail(f"Node {nid}: layer=0 but has prerequisites {prereqs}")
            errors += 1

        for prereq_id in prereqs:
            parent = node_map.get(prereq_id)
            if parent is None:
                continue
            parent_layer = parent.get("layer", -1)
            if parent_layer >= layer:
                r.fail(
                    f"Node {nid} (layer {layer}) has prerequisite {prereq_id} (layer {parent_layer}) - must be strictly lower"
                )
                errors += 1

    if errors == 0:
        r.ok("All layer values valid and prerequisites respect layer ordering")


def check_time_estimates(nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig) -> None:
    errors = 0
    for node in nodes:
        nid = node.get("id", "???")
        estimated = node.get("estimated_time_minutes")
        if not isinstance(estimated, int) or estimated < cfg.time_min or estimated > cfg.time_max:
            r.warn(f"Node {nid}: estimated_time={estimated} outside [{cfg.time_min}, {cfg.time_max}]")
            errors += 1
    if errors == 0:
        r.ok(f"All time estimates within [{cfg.time_min}, {cfg.time_max}] minutes")


def check_prerequisite_count(nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig) -> None:
    errors = 0
    for node in nodes:
        nid = node.get("id", "???")
        prereqs = node.get("prerequisites", [])
        if not isinstance(prereqs, list):
            continue
        if len(prereqs) > cfg.max_prereqs:
            r.fail(f"Node {nid}: {len(prereqs)} prerequisites exceeds max {cfg.max_prereqs}")
            errors += 1
    if errors == 0:
        r.ok(f"All nodes have <={cfg.max_prereqs} prerequisites")


def check_id_references(nodes: list[dict[str, Any]], edges: list[dict[str, Any]], r: ValidationResult) -> None:
    node_ids = {n["id"] for n in nodes if isinstance(n, dict) and "id" in n}
    errors = 0

    for node in nodes:
        nid = node.get("id", "???")
        for prereq_id in node.get("prerequisites", []):
            if prereq_id not in node_ids:
                r.fail(f"Node {nid}: prerequisite '{prereq_id}' does not exist")
                errors += 1
        for dependent_id in node.get("dependents", []):
            if dependent_id not in node_ids:
                r.fail(f"Node {nid}: dependent '{dependent_id}' does not exist")
                errors += 1

    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        if source not in node_ids:
            r.fail(f"Edge from '{source}' - node does not exist")
            errors += 1
        if target not in node_ids:
            r.fail(f"Edge to '{target}' - node does not exist")
            errors += 1

    if errors == 0:
        r.ok("All ID references valid")


def check_dependents_inverse(nodes: list[dict[str, Any]], r: ValidationResult) -> None:
    expected_dependents: dict[str, set[str]] = defaultdict(set)
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            continue
        for prereq_id in node.get("prerequisites", []):
            expected_dependents[prereq_id].add(node_id)

    errors = 0
    for node in nodes:
        node_id = node.get("id", "???")
        actual = set(node.get("dependents", []))
        expected = expected_dependents.get(node_id, set())
        if actual != expected:
            r.fail(
                f"Node {node_id}: dependents={sorted(actual)} but expected {sorted(expected)} from prerequisites inverse"
            )
            errors += 1

    if errors == 0:
        r.ok("dependents[] is exact inverse of prerequisites[] for all nodes")


def check_edges_match_prerequisites(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]], r: ValidationResult
) -> None:
    node_edges: set[tuple[str, str]] = set()
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            continue
        for prereq_id in node.get("prerequisites", []):
            node_edges.add((prereq_id, node_id))

    array_edges: set[tuple[str, str]] = set()
    malformed_edges = 0
    for edge in edges:
        source = edge.get("from")
        target = edge.get("to")
        if not source or not target:
            r.fail(f"Malformed edge object missing from/to: {edge}")
            malformed_edges += 1
            continue
        array_edges.add((source, target))

    missing_in_array = node_edges - array_edges
    extra_in_array = array_edges - node_edges

    if missing_in_array:
        r.fail(f"Edges missing from edges array: {sorted(missing_in_array)}")
    if extra_in_array:
        r.fail(f"Extra edges in array not in prerequisites: {sorted(extra_in_array)}")
    if not missing_in_array and not extra_in_array and malformed_edges == 0:
        r.ok("Edges array matches prerequisite relationships exactly")


def check_no_cycles(nodes: list[dict[str, Any]], r: ValidationResult) -> None:
    adj: dict[str, list[str]] = {
        n["id"]: list(n.get("prerequisites", []))
        for n in nodes
        if isinstance(n, dict) and "id" in n
    }
    visited: set[str] = set()
    in_stack: set[str] = set()
    has_cycle = False

    def dfs(node_id: str) -> bool:
        nonlocal has_cycle
        if node_id in in_stack:
            has_cycle = True
            return True
        if node_id in visited:
            return False

        visited.add(node_id)
        in_stack.add(node_id)
        for prereq_id in adj.get(node_id, []):
            if dfs(prereq_id):
                return True
        in_stack.discard(node_id)
        return False

    for node_id in adj:
        dfs(node_id)

    if has_cycle:
        r.fail("Circular dependency detected")
    else:
        r.ok("No circular dependencies (valid DAG)")


def check_reachability(nodes: list[dict[str, Any]], r: ValidationResult) -> None:
    node_map = {n["id"]: n for n in nodes if isinstance(n, dict) and "id" in n}
    layer0 = {n["id"] for n in nodes if n.get("layer") == 0 and "id" in n}

    reachable: set[str] = set()
    queue = list(layer0)
    while queue:
        node_id = queue.pop(0)
        if node_id in reachable:
            continue
        reachable.add(node_id)
        for dependent_id in node_map.get(node_id, {}).get("dependents", []):
            if dependent_id not in reachable:
                queue.append(dependent_id)

    unreachable = set(node_map.keys()) - reachable
    if unreachable:
        r.fail(f"Nodes not reachable from any layer-0 node: {sorted(unreachable)}")
    else:
        r.ok("All nodes reachable from layer-0 roots")


def check_topological_order(data: dict[str, Any], nodes: list[dict[str, Any]], r: ValidationResult) -> None:
    topo = data.get("learning_path", {}).get("topological_order", [])
    if not isinstance(topo, list):
        r.fail("learning_path.topological_order must be a list")
        return

    node_ids = {n["id"] for n in nodes if isinstance(n, dict) and "id" in n}
    topo_set = set(topo)

    missing = node_ids - topo_set
    extra = topo_set - node_ids
    if missing:
        r.fail(f"topological_order missing nodes: {sorted(missing)}")
        return
    if extra:
        r.fail(f"topological_order has unknown nodes: {sorted(extra)}")
        return

    position = {nid: i for i, nid in enumerate(topo)}
    errors = 0
    for node in nodes:
        node_id = node.get("id")
        if not node_id:
            continue
        for prereq_id in node.get("prerequisites", []):
            if position.get(prereq_id, -1) >= position.get(node_id, -1):
                r.fail(
                    f"topological_order: {prereq_id} (pos {position.get(prereq_id)}) should come before {node_id} (pos {position.get(node_id)})"
                )
                errors += 1

    if errors == 0:
        r.ok("topological_order respects all prerequisites")


def check_coverage_map(
    data: dict[str, Any], nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig
) -> None:
    cmap = data.get("coverage_map", {})
    if not isinstance(cmap, dict):
        r.fail("coverage_map must be an object")
        return

    node_ids = {n["id"] for n in nodes if isinstance(n, dict) and "id" in n}
    required = cfg.required_coverage_keys

    missing_keys = required - set(cmap.keys())
    extra_keys = set(cmap.keys()) - required

    if missing_keys:
        r.fail(f"coverage_map missing keys: {sorted(missing_keys)}")
    if extra_keys:
        r.fail(f"coverage_map has unexpected keys: {sorted(extra_keys)}")
    if not missing_keys and not extra_keys:
        r.ok(f"coverage_map keys match expected set ({len(required)} keys)")

    errors = 0
    keys_to_check = sorted(required) if required else sorted(cmap.keys())
    for key in keys_to_check:
        ids = cmap.get(key)
        if not isinstance(ids, list):
            r.fail(f"coverage_map['{key}'] must be a list")
            errors += 1
            continue
        if not ids:
            r.fail(f"coverage_map['{key}'] is empty - no nodes cover this key")
            errors += 1
        for node_id in ids:
            if node_id not in node_ids:
                r.fail(f"coverage_map['{key}'] references unknown node '{node_id}'")
                errors += 1

    if errors == 0:
        r.ok("coverage_map: all referenced node IDs exist and no empty entries")


def check_pattern_coverage_map(
    data: dict[str, Any], nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig
) -> None:
    pmap = data.get("pattern_coverage_map")
    if pmap is None:
        r.fail("pattern_coverage_map missing")
        return
    if not isinstance(pmap, dict):
        r.fail("pattern_coverage_map must be an object")
        return

    node_ids = {n["id"] for n in nodes if isinstance(n, dict) and "id" in n}
    errors = 0
    required_keys = set(cfg.pattern_minimum_coverage.keys())
    missing_keys: set[str] = set()
    extra_keys: set[str] = set()
    if cfg.topic_spec_provided:
        missing_keys = required_keys - set(pmap.keys())
        extra_keys = set(pmap.keys()) - required_keys
        if missing_keys:
            r.fail(f"pattern_coverage_map missing keys: {sorted(missing_keys)}")
        if extra_keys:
            r.fail(f"pattern_coverage_map has unexpected keys: {sorted(extra_keys)}")
        if not missing_keys and not extra_keys:
            r.ok(f"pattern_coverage_map keys match expected set ({len(required_keys)} keys)")

    keys_to_check = sorted(required_keys) if cfg.topic_spec_provided else sorted(pmap.keys())
    for key in keys_to_check:
        ids = pmap.get(key)
        if not isinstance(ids, list):
            r.fail(f"pattern_coverage_map['{key}'] must be a list")
            errors += 1
            continue

        minimum = cfg.pattern_minimum_coverage.get(key, 0)
        if len(ids) < minimum:
            r.fail(
                f"pattern_coverage_map['{key}'] has {len(ids)} nodes, below minimum_coverage={minimum}"
            )
            errors += 1

        for node_id in ids:
            if node_id not in node_ids:
                r.fail(f"pattern_coverage_map['{key}'] references unknown node '{node_id}'")
                errors += 1

    if errors == 0 and not missing_keys and not extra_keys:
        r.ok("pattern_coverage_map satisfies key coverage and node ID validity")


def check_capstone_required_failure_modes(
    data: dict[str, Any], nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig
) -> None:
    if not cfg.capstone_required_failure_modes:
        return

    capstone_nodes = {
        n.get("id")
        for n in nodes
        if n.get("exercise_type") == "integrate" and n.get("category") == cfg.capstone_category_key
    }
    capstone_nodes.discard(None)

    if not capstone_nodes:
        r.fail("No capstone nodes found for capstone-required failure mode checks")
        return

    cmap = data.get("coverage_map", {})
    if not isinstance(cmap, dict):
        r.fail("coverage_map must be an object")
        return

    errors = 0
    for failure_mode_key in sorted(cfg.capstone_required_failure_modes):
        covered = set(cmap.get(failure_mode_key, []))
        if not covered.intersection(capstone_nodes):
            r.fail(
                f"capstone_required_failure_mode '{failure_mode_key}' is not covered by any capstone node"
            )
            errors += 1

    if errors == 0:
        r.ok("All capstone-required failure modes are covered by capstone nodes")


def check_milestones(data: dict[str, Any], nodes: list[dict[str, Any]], r: ValidationResult) -> None:
    milestones = data.get("milestones", [])
    if not isinstance(milestones, list):
        r.fail("milestones must be a list")
        return

    node_ids = {n["id"] for n in nodes if isinstance(n, dict) and "id" in n}
    errors = 0

    for milestone in milestones:
        milestone_id = milestone.get("id", "???")
        if not str(milestone_id).startswith("MS"):
            r.fail(f"Milestone '{milestone_id}' does not use 'MS' prefix")
            errors += 1
        for node_id in milestone.get("nodes", []):
            if node_id not in node_ids:
                r.fail(f"Milestone {milestone_id} references unknown node '{node_id}'")
                errors += 1

    milestone_nodes: set[str] = set()
    for milestone in milestones:
        milestone_nodes.update(milestone.get("nodes", []))
    uncovered = node_ids - milestone_nodes
    if uncovered:
        r.warn(f"Nodes not in any milestone: {sorted(uncovered)}")

    if errors == 0:
        r.ok("Milestones use MS prefix and reference valid nodes")


def check_unique_ids(nodes: list[dict[str, Any]], r: ValidationResult) -> None:
    ids = [n.get("id") for n in nodes if isinstance(n, dict)]
    counts = Counter(ids)
    dupes = sorted([node_id for node_id, count in counts.items() if node_id and count > 1])
    if dupes:
        r.fail(f"Duplicate node IDs: {dupes}")
    else:
        r.ok("All node IDs unique")


def check_string_quality(nodes: list[dict[str, Any]], r: ValidationResult) -> None:
    errors = 0
    for node in nodes:
        node_id = node.get("id", "???")
        for field in (
            "exercise",
            "pass_condition",
            "fail_condition",
            "failure_mode",
            "teaches",
            "reference_hint",
        ):
            value = str(node.get(field, ""))
            if len(value.strip()) < 10:
                r.warn(f"Node {node_id}: '{field}' is too short or empty: '{value}'")
                errors += 1
    if errors == 0:
        r.ok("All text fields are non-trivially populated")


def check_learning_path_estimate(data: dict[str, Any], r: ValidationResult, cfg: ValidationConfig) -> None:
    learning_path = data.get("learning_path", {})
    if not isinstance(learning_path, dict):
        r.fail("learning_path must be an object")
        return

    total_hours = learning_path.get("estimated_total_hours")
    if not isinstance(total_hours, (int, float)):
        r.warn("learning_path.estimated_total_hours missing or not numeric")
        return

    min_hours = max(0, cfg.target_total_hours_min)
    max_hours = max(min_hours, cfg.target_total_hours_max)

    if total_hours < min_hours or total_hours > max_hours:
        r.warn(
            f"estimated_total_hours={total_hours} outside target range [{min_hours}, {max_hours}]"
        )
    else:
        r.ok(f"estimated_total_hours within [{min_hours}, {max_hours}]")


def check_tag_signals(nodes: list[dict[str, Any]], r: ValidationResult, cfg: ValidationConfig) -> None:
    if cfg.transfer_required:
        has_transfer = any("transfer" in (n.get("tags") or []) for n in nodes)
        if not has_transfer:
            r.fail("Transfer task required by topic spec, but no node has 'transfer' tag")
        else:
            r.ok("Transfer requirement satisfied by tagged transfer node")

    recall_review_nodes = [
        n
        for n in nodes
        if any(tag in {"recall", "review"} for tag in (n.get("tags") or []))
    ]
    if not recall_review_nodes and cfg.topic_spec_provided:
        r.warn("No node tagged 'recall' or 'review' for retention practice")
    elif recall_review_nodes:
        upper_layer = [n for n in recall_review_nodes if isinstance(n.get("layer"), int) and n.get("layer") > 0]
        if upper_layer:
            r.ok("Retention signal present with recall/review tags in non-foundation layers")
        else:
            r.warn("Recall/review tags exist, but only in layer 0")


# --- Main ----------------------------------------------------------------------


def validate(path: Path, topic_spec_path: Path | None = None) -> ValidationResult:
    result = ValidationResult()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        result.ok(f"JSON parsed successfully from {path}")
    except json.JSONDecodeError as exc:
        result.fail(f"Invalid JSON: {exc}")
        return result

    topic_spec: dict[str, Any] | None = None
    if topic_spec_path is not None:
        try:
            topic_spec = json.loads(topic_spec_path.read_text(encoding="utf-8"))
            result.ok(f"Topic spec parsed successfully from {topic_spec_path}")
        except FileNotFoundError:
            result.fail(f"Topic spec not found: {topic_spec_path}")
            return result
        except json.JSONDecodeError as exc:
            result.fail(f"Invalid topic spec JSON: {exc}")
            return result

        spec_errors = validate_topic_spec_contract(topic_spec)
        if spec_errors:
            for error in spec_errors:
                result.fail(f"topic_spec contract error: {error}")
            return result
        result.ok("Topic spec contract is valid")

    cfg = build_validation_config(topic_spec)

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    if not isinstance(nodes, list):
        result.fail("nodes must be an array")
        return result
    if not isinstance(edges, list):
        result.fail("edges must be an array")
        return result

    check_top_level_structure(data, result, cfg)
    check_metadata(data, result, cfg)
    check_unique_ids(nodes, result)
    check_node_count(nodes, result, cfg)
    check_node_schema(nodes, result)
    check_id_prefixes(nodes, result, cfg)
    check_enums(nodes, result, cfg)
    check_exercise_distribution(nodes, result, cfg)
    check_reference_hints(nodes, result)
    check_layers(nodes, result, cfg)
    check_time_estimates(nodes, result, cfg)
    check_prerequisite_count(nodes, result, cfg)
    check_id_references(nodes, edges, result)
    check_dependents_inverse(nodes, result)
    check_edges_match_prerequisites(nodes, edges, result)
    check_no_cycles(nodes, result)
    check_reachability(nodes, result)
    check_topological_order(data, nodes, result)
    check_coverage_map(data, nodes, result, cfg)
    check_pattern_coverage_map(data, nodes, result, cfg)
    check_capstone_required_failure_modes(data, nodes, result, cfg)
    check_milestones(data, nodes, result)
    check_string_quality(nodes, result)
    check_learning_path_estimate(data, result, cfg)
    check_tag_signals(nodes, result, cfg)

    return result


def parse_args() -> argparse.Namespace:
    default_path = Path(__file__).resolve().parent.parent / "data" / "curriculum.json"
    parser = argparse.ArgumentParser(description="Validate curriculum JSON")
    parser.add_argument(
        "curriculum_path",
        nargs="?",
        default=str(default_path),
        help="Path to curriculum JSON (default: data/curriculum.json)",
    )
    parser.add_argument(
        "--topic-spec",
        dest="topic_spec_path",
        help="Optional topic_spec.json path for topic-specific constraints",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    curriculum_path = Path(args.curriculum_path)
    topic_spec_path = Path(args.topic_spec_path) if args.topic_spec_path else None

    if not curriculum_path.exists():
        print(f"❌ File not found: {curriculum_path}")
        sys.exit(1)

    result = validate(curriculum_path, topic_spec_path)
    print(result.report())
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
