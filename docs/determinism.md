# Determinism Policy

## Scope

The curriculum compiler is expected to be deterministic for a fixed input set:
- identical `topic_spec.json`
- identical code revision
- identical configured generator/resolver implementation

## Guarantees

- Agent generation is deterministic by default (`DeterministicResourceResolver`).
- Planner output is deterministic given a valid curriculum DAG.
- Diff output is deterministic for identical previous/current artifacts.

## Non-Guarantees

- Determinism is not guaranteed when a non-deterministic custom resolver or model backend is injected.
- Determinism is not guaranteed across materially different code revisions.

## Regression Enforcement

- `tests/test_agent_determinism.py` verifies repeated generation equality.
- `scripts/coverage_check.py` and `scripts/static_checks.py` run in `make gate` and CI.
