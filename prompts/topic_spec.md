# Topic Spec Contract

## Purpose

`topic_spec.json` is the single source of truth for the prompt system.
It defines topic scope, constraints, quality bars, and assessment targets.

Used by:
- `prompts/curriculum_generator.md`
- `prompts/curriculum_validator.md`
- `prompts/repo_generator.md`
- `prompts/workflow.md`

---

## Required JSON Shape

```json
{
  "spec_version": "1.0",
  "topic_id": "string_slug",
  "topic_name": "Human-readable topic name",
  "domain_ref": "Source reference",
  "target_role": "Learner profile",
  "language": "python|typescript|go|rust|java|...",
  "project_type": "library|backend_api|frontend_app|cli|data_pipeline",
  "scenario": "Primary realistic scenario",
  "transfer_scenario": "Secondary scenario for transfer exercises",
  "prerequisites": ["required prior knowledge"],
  "outcome": "End-state capability",
  "failure_modes": [
    {
      "key": "short_snake_case",
      "label": "Display label",
      "description": "What goes wrong",
      "production_impact": "Why it matters",
      "example": "Concrete example",
      "must_cover_in_capstone": true
    }
  ],
  "design_patterns": [
    {
      "key": "short_snake_case",
      "name": "Pattern name",
      "problem": "Problem solved",
      "minimum_coverage": 1
    }
  ],
  "exercise_categories": [
    {
      "key": "foundation",
      "prefix": "F",
      "description": "Category purpose",
      "supports_exercise_types": ["write"],
      "is_capstone": false
    }
  ],
  "constraints": {
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
    "allow_external_services": false,
    "target_total_hours_min": 12,
    "target_total_hours_max": 24
  },
  "assessment": {
    "capstone_required_failure_modes": ["failure_mode_keys"],
    "mastery_threshold": "Objective pass threshold",
    "transfer_task_required": true,
    "max_uncaught_failure_modes": 1
  },
  "repo_preferences": {
    "repo_name": "optional-repo-name",
    "package_name": "optional_package_name",
    "use_makefile": true
  }
}
```

---

## Mandatory Invariants

1. `spec_version` must be `1.0`.
2. `topic_id` must be lowercase snake/kebab slug and globally unique per topic.
3. `failure_modes[*].key` must be unique snake_case.
4. `design_patterns[*].key` must be unique snake_case.
5. `exercise_categories[*].key` must be unique.
6. `exercise_categories[*].prefix` must be unique, uppercase, and must not be `MS`.
7. Exactly one category must have `is_capstone: true`.
8. The capstone category must support `integrate` in `supports_exercise_types`.
9. `assessment.capstone_required_failure_modes` must be a non-empty subset of `failure_modes[*].key`.
10. `constraints.node_count_min <= constraints.node_count_max`.
11. `constraints.debug_read_min <= constraints.debug_read_max`.
12. `constraints.capstone_layer` must be in `[0, constraints.max_layers - 1]`.
13. If `allow_external_services` is `false`, exercises and tests must be runnable offline.
14. `transfer_scenario` must differ materially from `scenario`.

---

## Defaults (if omitted)

- `spec_version`: `1.0`
- `constraints.max_layers`: `5`
- `constraints.node_count_min`: `18`
- `constraints.node_count_max`: `25`
- `constraints.max_prerequisites_per_node`: `3`
- `constraints.exercise_time_min_minutes`: `30`
- `constraints.exercise_time_max_minutes`: `90`
- `constraints.debug_read_min`: `2`
- `constraints.debug_read_max`: `3`
- `constraints.capstone_exactly`: `1`
- `constraints.capstone_layer`: `4`
- `constraints.allow_external_services`: `false`
- `constraints.target_total_hours_min`: `12`
- `constraints.target_total_hours_max`: `24`
- `assessment.transfer_task_required`: `true`
- `assessment.max_uncaught_failure_modes`: `1`
- `repo_preferences.use_makefile`: `true`

---

## Authoring Checklist

Before running generators:
- [ ] Failure modes are concrete and observable.
- [ ] Design patterns map to failure modes and not generic buzzwords.
- [ ] Category prefixes are unique and intuitive.
- [ ] Capstone required failure modes reflect actual production risk.
- [ ] Scenarios are realistic and technically executable.

---

## Minimal Example

```json
{
  "spec_version": "1.0",
  "topic_id": "python_testing",
  "topic_name": "Practical Python Testing",
  "domain_ref": "quality-map.md § T1",
  "target_role": "Backend developer",
  "language": "python",
  "project_type": "library",
  "scenario": "Order pricing and checkout service",
  "transfer_scenario": "Subscription billing renewals",
  "prerequisites": ["Python functions", "virtual environments", "basic CLI"],
  "outcome": "Design and maintain a reliable, fast test suite for production changes.",
  "failure_modes": [
    {
      "key": "fragile_assertions",
      "label": "Fragile Assertions",
      "description": "Assertions pass for incorrect behavior.",
      "production_impact": "Regressions escape into releases.",
      "example": "Asserting truthy response instead of contract fields.",
      "must_cover_in_capstone": true
    },
    {
      "key": "slow_feedback",
      "label": "Slow Feedback",
      "description": "Feedback cycle is too slow for local use.",
      "production_impact": "Developers skip tests.",
      "example": "No tiered test strategy.",
      "must_cover_in_capstone": true
    },
    {
      "key": "flaky_state",
      "label": "Flaky State",
      "description": "Nondeterminism causes inconsistent test results.",
      "production_impact": "Build trust in tests collapses.",
      "example": "Time-dependent fixtures without control.",
      "must_cover_in_capstone": false
    }
  ],
  "design_patterns": [
    {
      "key": "test_pyramid",
      "name": "Test Pyramid",
      "problem": "Too many expensive integration tests.",
      "minimum_coverage": 2
    },
    {
      "key": "deterministic_fixtures",
      "name": "Deterministic Fixtures",
      "problem": "Nondeterministic state creates flaky tests.",
      "minimum_coverage": 1
    }
  ],
  "exercise_categories": [
    {
      "key": "foundation",
      "prefix": "F",
      "description": "Core test primitives and contracts",
      "supports_exercise_types": ["write"],
      "is_capstone": false
    },
    {
      "key": "failure_demo",
      "prefix": "D",
      "description": "Reproduce key testing failures",
      "supports_exercise_types": ["write", "debug"],
      "is_capstone": false
    },
    {
      "key": "mitigation",
      "prefix": "M",
      "description": "Implement safeguards",
      "supports_exercise_types": ["write", "debug", "read"],
      "is_capstone": false
    },
    {
      "key": "capstone",
      "prefix": "C",
      "description": "Integrate patterns end to end",
      "supports_exercise_types": ["integrate"],
      "is_capstone": true
    }
  ],
  "constraints": {
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
    "allow_external_services": false,
    "target_total_hours_min": 12,
    "target_total_hours_max": 24
  },
  "assessment": {
    "capstone_required_failure_modes": ["fragile_assertions", "slow_feedback"],
    "mastery_threshold": "Capstone passes and transfer suite >=80%.",
    "transfer_task_required": true,
    "max_uncaught_failure_modes": 1
  },
  "repo_preferences": {
    "repo_name": "python-testing-learning",
    "package_name": "python_testing",
    "use_makefile": true
  }
}
```
