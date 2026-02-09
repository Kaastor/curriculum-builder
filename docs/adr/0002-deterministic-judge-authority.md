# ADR-0002: Deterministic Judge as Acceptance Authority

- Status: Accepted
- Date: 2026-02-09

## Context

LLM-only acceptance decisions are high variance and hard to debug. This project needs reproducible quality gates and predictable failure analysis.

## Decision

Use LLM-assisted proposal and repair, but make final acceptance deterministic through rule-based scoring and hard-fail diagnostics.

Implemented in:
- `learning_compiler/agent/quality/quality_model.py`
- `learning_compiler/agent/quality/quality_rules.py`
- `learning_compiler/agent/quality/quality_content_rules.py`

## Consequences

Positive:
- stable acceptance behavior across runs
- diagnosable quality regressions
- easier testing and CI confidence

Negative:
- rule tuning effort
- possible mismatch between deterministic scores and human perception in edge cases

## Alternatives Considered

- End-to-end LLM judge:
  - rejected due to low determinism and weak reproducibility.
