# ADR-0001: Artifact-Driven Stage Synchronization

- Status: Accepted
- Date: 2026-02-09

## Context

Run lifecycle state can drift if users edit artifacts manually, rerun partial commands, or recover from interrupted runs. A metadata-only stage model is fragile in this workflow.

## Decision

The system infers stage from current artifact presence/freshness on command entry and synchronizes `run.json` to that inferred stage.

Implemented in:
- `learning_compiler/orchestration/stage.py`

## Consequences

Positive:
- resilient to manual artifact edits
- safer partial reruns (`validate`, `plan`, `iterate`)
- metadata reflects filesystem truth

Negative:
- additional mtime-based checks on each command
- stage debugging requires understanding artifact dependencies

## Alternatives Considered

- Metadata-only stage progression:
  - rejected because it fails under manual edits and partial command recovery.
