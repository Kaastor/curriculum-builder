# Phase One: Agent-First Learning Compiler

## End Goal

Build a reusable **curriculum generation agent** that takes `topic_spec.json` and produces a validated, evidence-backed curriculum DAG plus an executable plan.

Primary contract:
`Topic Spec -> Agent Generate -> Validate -> Plan -> Iterate`

Design rule:
- Agent owns generation quality and evidence selection.
- Orchestration is only tooling (run storage, logs, reports, diff, replay).

## Product Boundaries

In scope:
- topic spec contract (`topic_spec.json`)
- agent-owned curriculum generation (concept DAG + mastery checks + resources)
- evidence strictness dial (`minimal | standard | strict`)
- deterministic validators (schema/graph/evidence)
- deterministic planner (2-4 week plan)
- rerun/diff tooling
- UI rendering of generated curriculum

Out of scope:
- exercise generation
- adaptive tutoring
- external integrations beyond web resources/citations
- major UI framework migration

## Architecture Target

### 1) Agent Layer (primary)
Location: `learning_compiler/agent/`

Responsibilities:
- parse and normalize `topic_spec.json`
- decompose topic into concept DAG
- assign prerequisites/capabilities/pitfalls/mastery checks
- retrieve and attach resources/citations per evidence mode
- emit canonical `curriculum.json`

Public API (phase one):
- `generate_curriculum(topic_spec_path: Path, output_path: Path) -> None`

### 2) Validator Layer (judge)
Location: `learning_compiler/validator/`

Responsibilities:
- enforce schema and graph constraints
- enforce evidence-mode rules
- fail loudly on invalid artifacts

### 3) Planner Layer (deterministic)
Location: `learning_compiler/orchestration/planning.py` (or `learning_compiler/planning/` if split)

Responsibilities:
- build 2-4 week schedule from validated DAG + constraints
- output per-node deliverables from mastery checks

### 4) Orchestration Tooling (secondary)
Location: `learning_compiler/orchestration/`

Responsibilities:
- run folders, metadata, status, logs
- replayable command wrappers (`init/status/run/validate/plan/iterate/archive`)
- diff reports between runs

Non-responsibility:
- orchestration does not decide curriculum content quality

## Canonical Artifacts

### `topic_spec.json`
Source of truth for generation intent and constraints.

### `curriculum.json`
Canonical concept DAG (minimal stored fields only):
- `topic`
- `nodes[]` with: `id`, `title`, `capability`, `prerequisites`, `core_ideas`, `pitfalls`, `mastery_check`, `estimate_minutes`, optional `estimate_confidence`, `resources[]`
- `open_questions[]` required in strict mode

Derived only (never source of truth):
- topological order
- milestones/layers
- critical path
- total time
- coverage summaries

### `plan.json`
Deterministic schedule and deliverables from validated curriculum.

### `diff_report.json`
Structural/time deltas across reruns.

## Evidence Dial (single pipeline)

- `minimal`: >=1 resource per node
- `standard`: >=2 resources per node with `definition` + `example`
- `strict`: standard + citations + `estimate_confidence` + explicit `open_questions`

No pipeline forks by mode; only validation strictness changes.

## Implementation Plan

### WP1 - Create explicit Agent module
- Add `learning_compiler/agent/` with generation entrypoint.
- Move generation logic out of orchestration command modules into agent module.
- Keep one callable path from CLI/tooling.

Acceptance:
- curriculum generation runs through `learning_compiler.agent` API.

### WP2 - Add retrieval interface for references
- Define retrieval adapter interface (search + select + normalize citation fields).
- Implement phase-one provider (web-backed when available, deterministic fallback otherwise).
- Ensure output always matches evidence-mode requirements.

Acceptance:
- strict mode outputs citation-complete resources and passes validator.

### WP3 - Keep validator as hard gate
- Preserve current structural/evidence checks.
- Ensure error messages are actionable and deterministic.

Acceptance:
- invalid curriculum fails with stable messages/exit code.

### WP4 - Rewire orchestration to be tooling-only
- `orchestration run` should call agent generation, then validate/plan/iterate.
- Keep run metadata and artifact history.
- Remove generation-quality logic from orchestration.

Acceptance:
- orchestration can be skipped; direct agent invocation still produces valid curriculum.

### WP5 - Tighten module boundaries and file size
- Split long files by responsibility.
- keep each module focused and reviewable.
- document boundaries in code comments/docstrings.

Acceptance:
- no single "god module" for pipeline control + generation + validation.

### WP6 - UI integration check
- Ensure UI reads latest curriculum artifact and renders graph correctly.
- no schema drift between agent output and UI input.

Acceptance:
- generated curriculum is visible in UI without manual edits.

### WP7 - Docs and contracts
- Update README with agent-first usage:
  - provide `topic_spec.json`
  - run generation command
  - inspect curriculum in UI
- Keep prompt docs concise and consistent with schema.

Acceptance:
- a new user can run end-to-end without manual curriculum authoring.

## Testing Strategy

Unit:
- topic spec contract
- DAG validity
- evidence mode behavior
- planner constraints
- diff correctness

Integration:
- end-to-end: spec -> agent generate -> validate -> plan -> iterate
- strict mode with missing citation fails
- rerun with spec change emits meaningful diff

Gate:
- `make gate` must pass before handoff

## Definition of Done (Phase One)

Done when all are true:
- Agent is the primary curriculum generator.
- Orchestration is optional tooling, not content authority.
- Strict mode can generate and validate citation-backed curriculum.
- Plan and diff artifacts are deterministic and usable.
- UI can display generated curriculum.
- README documents agent-first flow clearly.
