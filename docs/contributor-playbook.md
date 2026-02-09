# Contributor Playbook

This document defines engineering standards for safe and reviewable changes.

## 1. Engineering Expectations

- Keep changes small and composable when possible.
- Prefer explicit typed contracts over ad-hoc dictionary mutation.
- Preserve deterministic behavior unless change intent explicitly modifies it.
- Keep CLI modules thin; move logic into importable modules.
- Update docs in the same change set when behavior changes.

```mermaid
flowchart TD
    A[change idea] --> B[define boundary and impact]
    B --> C[implement minimal coherent change]
    C --> D[update tests/docs]
    D --> E[run make gate]
    E --> F[review-ready]
```

## 2. Change-Type Workflow

### Documentation-only

Required:
- verify links and paths
- run `make gate`

### Validator rule changes

Required:
- add/update tests covering passing and failing fixtures
- verify no unintended rule-order regressions
- run `make gate`

### Orchestration flow changes

Required:
- test stage progression and stale artifact refresh behavior
- verify command contracts (`validate|plan|iterate|run`)
- run `make gate`

### Agent runtime/provider changes

Required:
- test retries/timeouts/error mapping
- test structured output parsing failures
- verify both happy path and failure path
- run `make gate`

### Schema/contract changes

Required:
- update contract docs
- add parser/validator tests
- document fresh-run impact
- run `make gate`

```mermaid
flowchart TD
    A[change category] --> B{type}
    B -->|docs-only| C[link check + gate]
    B -->|validator| D[rule tests + ordering checks + gate]
    B -->|orchestration| E[stage/contract tests + gate]
    B -->|agent/provider| F[retry/timeout/error tests + gate]
    B -->|schema| G[contract docs + parser tests + fresh-run note + gate]
```

## 3. Testing Strategy by Risk

Low risk:
- narrow unit tests for touched utility functions

Medium risk:
- unit tests + integration path tests for affected commands/modules

High risk:
- targeted regression tests + full `make gate`
- manual smoke run of orchestration flow when feasible

```mermaid
flowchart TD
    A[risk assessment] --> B{risk level}
    B -->|low| C[focused unit tests]
    B -->|medium| D[unit + integration tests]
    B -->|high| E[regression tests + smoke run + gate]
```

## 4. Review Readiness Flow

A review-ready change should include:
- clear intent and boundary of change
- explicit tradeoffs for non-obvious decisions
- tests proving expected behavior
- documentation updates for any contract/path changes

```mermaid
flowchart TD
    A[prepare PR] --> B[intent + boundary clear]
    B --> C[tradeoffs documented]
    C --> D[tests included]
    D --> E[docs updated]
    E --> F[gate green]
    F --> G[request review]
```

## 5. Definition of Done Flow

- behavior works as intended
- tests updated when feasible
- docs updated if behavior/contracts changed
- `make gate` passes

```mermaid
flowchart TD
    A[implemented change] --> B{behavior correct}
    B -- no --> A
    B -- yes --> C{tests/docs updated}
    C -- no --> A
    C -- yes --> D[run make gate]
    D --> E{pass}
    E -- no --> A
    E -- yes --> F[done]
```

## 6. Anti-Pattern Detection Flow

Avoid:
- silent contract drift without docs/tests
- embedding business logic in CLI wrappers
- bypassing typed parsers at module boundaries
- introducing non-deterministic behavior without rationale
- deleting unknown files to silence checks

```mermaid
flowchart TD
    A[proposed implementation] --> B{introduces anti-pattern?}
    B -- yes --> C[refactor before merge]
    B -- no --> D[continue]
```
