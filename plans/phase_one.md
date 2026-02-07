# Phase One: Learning Compiler (Execution Spec)

## Goal

Build a reusable pipeline that maps any topic into a coherent mastery path.

Pipeline spine:
`Spec -> Map -> Validate -> Plan -> Iterate`

Evidence strictness is a dial:
`minimal | standard | strict`

No exercises in phase one.

## Phase Scope

In scope:
- topic spec contract
- canonical concept DAG generation
- structural and evidence validation
- 2-4 week execution plan generation
- rerun + diff loop

Out of scope:
- exercise generation
- adaptive personalization
- external integrations beyond resource URLs/citations
- major UI redesign

## Stage Contracts

| Stage | Input | Output | Primary owner | Blocking failures |
|---|---|---|---|---|
| Spec | `topic_spec.json` | `topic_spec.validated.json` (optional normalized copy) | Code validator | schema errors, placeholders, invalid bounds |
| Map | validated topic spec | `curriculum.json` (canonical DAG only) | LLM proposer + code guardrails | missing required node fields, invalid prereqs |
| Validate | topic spec + curriculum | `validation_report.json` + markdown summary | Code validators | any `ERROR` |
| Plan | validated curriculum + constraints | `plan.json` | Code | time budget overflow, unschedulable DAG |
| Iterate | previous run artifacts + changed spec/map | `diff_report.json` + updated artifacts | Code | diff cannot be computed, artifact mismatch |

## Artifact Schemas (v1)

### `topic_spec.json` (required fields)
- `spec_version`: string (`"1.0"`)
- `goal`: string
- `audience`: string
- `prerequisites`: string[]
- `scope_in`: string[]
- `scope_out`: string[]
- `constraints`: object
- `constraints.hours_per_week`: number
- `constraints.total_hours_min`: number
- `constraints.total_hours_max`: number
- `constraints.depth`: enum (`survey`, `practical`, `mastery`)
- `domain_mode`: enum (`mature`, `frontier`)
- `evidence_mode`: enum (`minimal`, `standard`, `strict`)
- `misconceptions`: string[] (optional)

### `curriculum.json` (canonical only)
- `topic`: string
- `nodes`: array of:
- `id`: string
- `title`: string
- `capability`: string
- `prerequisites`: string[]
- `core_ideas`: string[]
- `pitfalls`: string[]
- `mastery_check.task`: string
- `mastery_check.pass_criteria`: string
- `estimate_minutes`: number
- `estimate_confidence`: number in `[0,1]` (optional)
- `resources`: array of:
- `title`: string
- `url`: string
- `kind`: enum (`doc`, `paper`, `video`, `book`, `spec`, `other`)
- `citation`: string (required in strict mode for claim-bearing resources)

Derived only (never persisted as source of truth):
- topo order
- layers/phases
- milestones
- critical path
- total time
- coverage reports

### `plan.json`
- `duration_weeks`: integer in `[2,4]`
- `weekly_budget_minutes`: number
- `weeks`: array of:
- `week`: integer
- `nodes`: string[]
- `deliverables`: array of per-node mastery outputs
- `review`: spaced review items (optional)

### `diff_report.json`
- `added_nodes`: string[]
- `removed_nodes`: string[]
- `changed_nodes`: array of `{id, changed_fields[]}`
- `time_delta_minutes`: number
- `critical_path_changed`: boolean

## Evidence Mode Matrix

| Mode | Node-level requirement | Curriculum-level requirement | Blocking rule |
|---|---|---|---|
| minimal | each node has >=1 resource | all nodes covered | missing resource on any node = `ERROR` |
| standard | each node has >=2 resources | at least one definition source + one example source per node | missing either source type = `ERROR` |
| strict | standard rules + citations for claim-bearing resources + `estimate_confidence` | contradictions represented as explicit open-question nodes | uncited claim or unresolved contradiction = `ERROR` |

## Validation Severity And Exit Codes

Severity:
- `ERROR`: blocks pipeline
- `WARN`: allowed, must be listed
- `INFO`: non-blocking diagnostics

Exit codes:
- `0`: no errors
- `1`: one or more errors
- `2`: invalid input artifacts (parse/schema failure)

## Work Packages (Implementation Order)

WP1 - Spec contract
- Update: `workflows/templates/topic_spec.template.json`, `prompts/topic_spec.md`, `scripts/validator.py`
- Add strict schema checks for new fields and enums
- Acceptance: invalid/missing spec fields fail with actionable errors

WP2 - Canonical curriculum schema
- Update: `prompts/curriculum_generator.md`, `data/curriculum.json`, `scripts/validator.py`, `app/main.js`
- Remove exercise-centric fields and coverage maps from canonical schema
- Acceptance: validator accepts only canonical+allowed top-level fields

WP3 - Structural validator pass
- Update: `scripts/validator.py`
- Keep: DAG, cycle, reachability, unique IDs/titles, time/constraint checks
- Acceptance: deterministic structural report with stable error codes/messages

WP4 - Evidence validator pass
- Update: `scripts/validator.py`, docs/prompts
- Implement mode-specific rules from matrix
- Acceptance: mode switch changes checks without forking pipeline

WP5 - Planner
- Add: planning generator module (script) + `plan.json` output
- Update: `scripts/workflow.py`, workflow templates
- Acceptance: produces 2-4 week schedule and node deliverables within constraints

WP6 - Iterate + diff
- Add: diff computation script/report
- Update: `scripts/workflow.py` stage flow and status output
- Acceptance: reruns produce machine-readable diffs and comparable artifacts

WP7 - Cleanup
- Remove phase-one irrelevant prompts/logic (pedagogical-review gating, exercise-specific remnants)
- Acceptance: workflow aligns only to `Spec -> Map -> Validate -> Plan -> Iterate`

## Test Plan

Unit:
- topic spec schema and invariant checks
- DAG validity (cycle, missing prereq, orphan)
- evidence-mode checks (`minimal`, `standard`, `strict`)
- planning constraints (time/week bounds)
- diff accuracy

Integration:
- happy path: full pipeline succeeds
- strict mode with citation failure
- frontier mode with open-question node requirement
- rerun with small spec change emits expected diff

Fixtures:
- one mature-domain fixture
- one frontier-domain fixture

## Definition Of Done

Done when all are true:
- pipeline stages run end-to-end with current make/workflow commands
- schemas above are enforced and documented
- tests cover structural, evidence, planning, and diff behavior
- `make gate` passes
- docs describe only phase-one loop and remove phase-two ideas

## Iteration Rules

Rerun triggers:
- topic spec changes
- curriculum proposal changes
- validator logic changes

Stability requirement:
- identical inputs produce semantically equivalent outputs (ordering can vary only where declared non-semantic)

Diff requirement on rerun:
- node add/remove/change summary
- total time delta
- critical path change flag
