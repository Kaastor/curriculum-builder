# ADR-0004: Direct Scope Passthrough for Scope-First Mode

- Status: Accepted
- Date: 2026-02-09

## Context

Users may provide unordered scope markdown at mixed granularity. We need a robust path that works predictably without a complex pre-DAG heuristic stage.

## Decision

Scope ingestion selects content (`full|section|seed-list`), synthesizes a valid topic spec, and feeds selected scope directly into generation context. No separate heuristic concept-to-DAG builder runs in orchestration scope mode.

Implemented in:
- `learning_compiler/orchestration/scope.py`
- `learning_compiler/agent/spec.py`
- `learning_compiler/agent/proposer.py`
- `learning_compiler/agent/repair_executor.py`

## Consequences

Positive:
- simple and reliable scope path
- lower orchestration complexity
- clear artifact traceability (`scope_concepts.json`, `scope_dag.json`)

Negative:
- document-structure bias may remain for prose-heavy sources
- no explicit concept canonicalization layer

## Alternatives Considered

- Heuristic concept extraction and edge inference before generation:
  - deferred; adds complexity and additional failure modes.
