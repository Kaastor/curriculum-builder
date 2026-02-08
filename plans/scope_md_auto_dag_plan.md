# Scope-First Auto-DAG Implementation Plan

## Goal

Enable users to provide only an unordered scope document (e.g. `scope.md` or `docs/agentic-engineering-atlas.md`, mixed detail levels), then automatically produce:
- actionable learning nodes
- prerequisite-safe DAG
- phase-ordered curriculum artifacts consumable by the existing pipeline

Primary contract:
`scope document -> concept extraction -> actionable nodes -> hard-prereq DAG -> curriculum.json -> validate -> plan`

## Why This Change

Current flow assumes users can provide structured intent in `topic_spec.json`. Many users only know "what I want to learn," not decomposition or order. This feature makes unordered scope lists the default entry path while preserving deterministic quality checks.

## Product Behavior

Input expectations:
- Source can be any markdown document path (including `docs/agentic-engineering-atlas.md`).
- Input may be bullets, prose sections, or mixed.
- Items can be broad ("distributed systems") or narrow ("Raft leader election").

System behavior:
- Decompose broad items into atomic learnable concepts.
- Keep already-atomic items stable.
- Create actionable nodes (clear capability + mastery check + estimate).
- Infer ordering automatically.
- Keep uncertainty internal; user does not need to edit a DAG.

Outputs:
- `runs/<id>/scope_concepts.json`
- `runs/<id>/scope_dag.json`
- generated/normalized `runs/<id>/topic_spec.json`
- downstream `curriculum.json`, validation artifacts, and `plan.json`

Input modes:
- Full document mode: extract from the whole file.
- Section mode: extract only selected headings.
- Seed-list mode: use only explicit bullets under a designated heading (for tighter scope).

## Architecture Changes

New modules:
- `learning_compiler/agent/scope_extractor.py`
- `learning_compiler/agent/concept_dag_builder.py`
- `learning_compiler/agent/scope_contracts.py` (typed dataclasses/enums for scope concepts/edges/confidence)

Updated modules:
- `learning_compiler/agent/spec.py` (add scope-derived spec normalization path)
- `learning_compiler/orchestration/commands_pipeline.py` (wire new scope-first pipeline entry)
- `learning_compiler/orchestration/command_utils.py` (CLI argument helpers for `--scope`)
- `learning_compiler/validator/curriculum_graph.py` (reuse existing DAG checks on generated curriculum)
- `learning_compiler/validator/topic_spec.py` (accept scope-derived normalized topic specs)

Prompts:
- `prompts/scope_to_concepts.md`
- `prompts/concepts_to_edges.md`

## Work Packages

### WP1 - Scope artifact contract and parsing
- Add markdown scope loader with deterministic parsing rules for headings, bullets, and prose sentences.
- Define typed models:
  - `ScopeItem`
  - `ConceptCandidate`
  - `ConceptEdgeCandidate` (`prerequisite|recommended_before|related`)
- Normalize whitespace, duplicates, and stable IDs.
- Add source metadata (`source_path`, `heading_path`, `line_span`) for traceability.

Acceptance:
- Same `scope.md` always produces identical normalized input objects.

### WP2 - Concept extraction and granularity normalization
- Implement extraction from scope items into concept candidates.
- Split broad concepts until each candidate is independently learnable/testable.
- Preserve traceability from concept to original scope line(s).
- Add "field map" filtering for atlas-style documents to avoid ingesting meta text not meant as learner scope.

Acceptance:
- Mixed-granularity input yields atomic concepts with no unresolved "too broad" nodes.

### WP3 - Actionable node formulation
- Convert concepts into curriculum-ready nodes using existing node-building patterns.
- Ensure each node has:
  - capability statement
  - mastery check
  - estimate minutes (+ confidence if configured)
  - optional resource placeholders for later retrieval stages

Acceptance:
- Node-level validator rules pass for generated node bodies.

### WP4 - Deterministic edge inference and hard DAG construction
- Infer candidate edges with confidence scores.
- Promote only high-confidence prerequisites to hard edges.
- Store lower-confidence relations as soft edges (`recommended_before` / `related`).
- Enforce acyclicity with deterministic tie-breaking and cycle repair rules.

Acceptance:
- Hard prerequisite graph is always a DAG.
- Repeated runs with same inputs produce stable topology.

### WP5 - Pipeline wiring (scope-first default path)
- Add orchestration entry supporting scope input (new command or flag).
- Support `--scope-file docs/agentic-engineering-atlas.md` and optional section selectors.
- Generate `topic_spec.json` from scope-derived graph, then run existing generation/validation/planning flow.
- Keep existing `topic_spec.json` path intact for expert/dev usage and tests.

Acceptance:
- User can run end-to-end from only `scope.md` with no manual ordering.

### WP6 - Validation + diagnostics integration
- Reuse validator gates for schema/graph/evidence.
- Add diagnostics artifacts:
  - ambiguity list
  - promoted vs soft-edge report
  - cycle-repair decisions

Acceptance:
- Failed/uncertain cases produce actionable deterministic diagnostics.

### WP7 - Tests and determinism coverage
- Unit tests:
  - scope parser normalization
  - concept splitting thresholds
  - edge promotion and cycle resolution
- Integration test:
  - `scope.md -> topic_spec.json -> curriculum.json -> validate -> plan`
- Regression fixtures for stable IDs/topology.

Acceptance:
- New tests pass locally and under `make gate`.

### WP8 - Documentation updates
- Update `README.md` with scope-first workflow.
- Add/extend docs in `docs/`:
  - input authoring guide for `scope.md`
  - deterministic behavior and known limitations
  - troubleshooting ambiguous scope inputs

Acceptance:
- New user can run scope-first flow from docs without inspecting code.

## Determinism Rules

- Use stable slug/hash IDs for scope items and concepts.
- No global randomness; if randomness is required, use seeded local RNG.
- Preserve stable ordering when scores tie (lexicographic ID tie-break).
- Persist decision traces for replay/debug.

## Open Design Decisions

1. CLI UX:
- `orchestration run --scope-file runs/<id>/scope.md`
- `orchestration run --scope-file docs/agentic-engineering-atlas.md --scope-section "Part I"`
- or dedicated `orchestration scope-run ...`

2. Confidence policy:
- static threshold vs profile-based threshold (`fast|balanced|strict`)

3. Decomposition depth cap:
- hard max split depth to avoid over-fragmentation

4. Atlas filtering strategy:
- how aggressively to ignore definitions/meta/method-taxonomy prose when converting to learner action nodes

## Rollout Plan

1. Ship behind optional scope flag.
2. Validate on curated fixtures in `tests/fixtures/`.
3. Promote to default entry path after deterministic regression stability.

## Definition of Done

Done when all are true:
- Users can provide unordered mixed-detail `scope.md` as the only input.
- System outputs actionable nodes and a valid prerequisite DAG automatically.
- Existing validator/planner pipeline remains green.
- Docs and tests are updated.
- `make gate` passes.
