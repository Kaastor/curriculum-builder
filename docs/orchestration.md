# Orchestration

This document specifies orchestration lifecycle behavior and command contracts.

## 1. Scope

Orchestration code lives under `learning_compiler/orchestration/` and is exposed by `scripts/orchestration.py`.

Main responsibilities:
- initialize run workspaces
- synchronize run stage from artifacts
- execute pipeline commands (`validate`, `plan`, `iterate`, `run`)
- persist reports and lifecycle events

## 2. Run Directory Contract

Per run (`runs/<run_id>/`):
- `inputs/topic_spec.json`
- `inputs/scope.md`
- `outputs/curriculum/curriculum.json`
- `outputs/curriculum/previous_curriculum.json`
- `outputs/reviews/optimization_trace.json`
- `outputs/reviews/validation_report.md`
- `outputs/reviews/diff_report.json`
- `outputs/plan/plan.json`
- `logs/events.jsonl`
- `logs/validation.ok`
- `scope_concepts.json`
- `scope_dag.json`
- `run.json`

## 3. Command Map (All Commands)

```mermaid
flowchart TD
    A[orchestration CLI] --> B{command}

    B --> I[init]
    B --> S[status]
    B --> N[next]
    B --> V[validate]
    B --> P[plan]
    B --> T[iterate]
    B --> R[run]
    B --> L[list]
    B --> AR[archive]

    I --> I1[create run dirs + template files + run.json]
    S --> S1[load run + sync stage + print artifact status]
    N --> N1[load run + sync stage + print next action]
    V --> V1[sync stage + validator + validation report]
    P --> P1[validate first]
    P1 --> P2[build and write plan]
    T --> T1[validate first]
    T1 --> T2[refresh plan if stale]
    T2 --> T3[compute and write diff]
    R --> R1[optional scope synthesis]
    R1 --> R2[generate curriculum]
    R2 --> R3[validate]
    R3 --> R4[plan]
    R4 --> R5[diff]
    L --> L1[list run directories]
    AR --> AR1[tar.gz archive]
```

## 4. Per-Command Flows

### `init`

Behavior:
- creates run folder structure
- copies topic spec template into `inputs/topic_spec.json`
- creates scope template in `inputs/scope.md`
- initializes `run.json` and first event in `logs/events.jsonl`

```mermaid
flowchart TD
    A[init <name>] --> B[resolve runs dir]
    B --> C{template exists}
    C -- no --> D[config_error]
    C -- yes --> E[create run_id + directory tree]
    E --> F[copy topic_spec template]
    F --> G[write scope template]
    G --> H[write run.json + events.jsonl]
    H --> I[print paths]
```

### `status`

Behavior:
- loads `run.json`
- syncs stage from artifacts
- reports artifact availability and scope artifact validity

```mermaid
flowchart TD
    A[status <run_id>] --> B[load run metadata]
    B --> C[sync stage from artifacts]
    C --> D[persist run.json if changed]
    D --> E[evaluate artifact flags]
    E --> F[print status summary]
```

### `next`

Behavior:
- loads and syncs stage
- prints next recommended command based on current stage

```mermaid
flowchart TD
    A[next <run_id>] --> B[load run + sync stage]
    B --> C{stage}
    C -->|initialized| D[fill topic_spec or use --scope-file]
    C -->|spec_ready| E[run generation]
    C -->|generated| F[run validate]
    C -->|validated| G[run plan]
    C -->|planned| H[run iterate]
    C -->|iterated| I[completed]
```

### `validate`

Behavior:
- syncs stage
- validates topic spec contract
- invokes validator subprocess
- writes `validation_report.md`
- writes/removes `logs/validation.ok` marker

```mermaid
flowchart TD
    A[validate <run_id>] --> B[load + sync stage]
    B --> C{topic_spec contract valid}
    C -- no --> D[exit 1]
    C -- yes --> E{curriculum exists}
    E -- no --> F[exit 1]
    E -- yes --> G[run validator subprocess]
    G --> H[write validation_report.md]
    H --> I{return code == 0?}
    I -- yes --> J[write validation.ok + advance stage]
    I -- no --> K[remove validation.ok + resync stage]
```

### `plan`

Behavior:
- runs `validate` first
- on successful validation, computes deterministic plan
- writes `outputs/plan/plan.json`

```mermaid
flowchart TD
    A[plan <run_id>] --> B[validate flow]
    B --> C{validation success}
    C -- no --> D[exit 1]
    C -- yes --> E[parse topic_spec + curriculum]
    E --> F[build_plan]
    F --> G[write plan.json + stage planned]
```

### `iterate`

Behavior:
- runs `validate` first
- refreshes plan if plan/validation markers are stale
- computes diff against previous curriculum
- writes `outputs/reviews/diff_report.json`

```mermaid
flowchart TD
    A[iterate <run_id>] --> B[validate flow]
    B --> C{validation success}
    C -- no --> D[exit 1]
    C -- yes --> E{plan current and validation current}
    E -- no --> F[rebuild plan]
    E -- yes --> G[skip plan rebuild]
    F --> H[compute diff]
    G --> H
    H --> I[write diff_report.json + stage iterated]
```

### `run`

Behavior:
- optional: synthesize topic spec from scope input
- generate curriculum
- validate
- plan
- diff

If validation fails, `run` exits non-zero and skips plan/diff.

```mermaid
flowchart TD
    A[run <run_id>] --> B[load context + sync stage]
    B --> C{--scope-file provided}
    C -- yes --> D[resolve and validate scope selection]
    D --> E[synthesize topic_spec + scope artifacts]
    E --> F[stage -> spec_ready]
    C -- no --> G{stage is initialized}
    G -- yes --> H[stage_conflict error]
    G -- no --> I[continue with existing topic_spec]
    F --> J[generate curriculum]
    I --> J
    J --> K[validate curriculum]
    K --> L{validation success}
    L -- no --> M[stop with exit 1]
    L -- yes --> N[build plan]
    N --> O[compute diff]
    O --> P[stage -> iterated]
```

## 5. Stage Synchronization and Freshness

Stage is inferred from artifact freshness, not only historical command order.

Current checks:
- `spec_ready`: `topic_spec.json` passes contract validation
- `generated`: curriculum exists
- `validated`: `validation.ok` is current relative to spec/curriculum/report
- `planned`: `plan.json` is current relative to spec/curriculum
- `iterated`: `diff_report.json` is current relative to current/previous curriculum

```mermaid
flowchart TD
    A[infer_stage_from_artifacts] --> B[initialized]
    B --> C{topic_spec ready}
    C -- no --> Z[initialized]
    C -- yes --> D[spec_ready]
    D --> E{curriculum exists}
    E -- no --> Z1[spec_ready]
    E -- yes --> F[generated]
    F --> G{validation current}
    G -- no --> Z2[generated]
    G -- yes --> H[validated]
    H --> I{plan current}
    I -- no --> Z3[validated]
    I -- yes --> J[planned]
    J --> K{diff current}
    K -- no --> Z4[planned]
    K -- yes --> L[iterated]
```

## 6. Planning and Diff Rules

Planning (`build_plan`):
- typed parse of topic spec and curriculum
- deterministic topological order
- week count bounded to `[2, 4]`
- weekly node allocation by minute capacity
- injects mastery deliverables and rolling review items

```mermaid
flowchart TD
    A[topic_spec + curriculum] --> B[parse typed models]
    B --> C[topological node order]
    C --> D[compute weekly budget + week count]
    D --> E[pack nodes into week buckets]
    E --> F[attach deliverables + review carry-over]
    F --> G[plan.json]
```

Diff (`compute_diff`):
- node set delta: added/removed
- field-level node changes
- total time delta
- critical-path change detection

```mermaid
flowchart TD
    A[previous curriculum] --> C[normalize + index by node_id]
    B[current curriculum] --> C
    C --> D[compute added/removed ids]
    C --> E[compute changed fields per shared id]
    C --> F[sum estimate_minutes delta]
    C --> G[compute previous/current critical path]
    D --> H[diff_report.json]
    E --> H
    F --> H
    G --> H
```

Precision note:
- `estimate_minutes` is treated as numeric, including fractional values.

## 7. Failure and Recovery Flow

```mermaid
flowchart TD
    A[pipeline command fails] --> B{failure class}
    B -->|spec missing/incomplete| C[complete topic_spec or provide --scope-file]
    B -->|curriculum missing| D[run generation via run]
    B -->|validator failure| E[inspect validation_report.md and repair inputs]
    B -->|stale artifacts| F[rerun validate -> plan -> iterate]
    B -->|metadata incompatible| G[archive + reinitialize run]
    C --> H[rerun command]
    D --> H
    E --> H
    F --> H
    G --> H
```

## 8. Operational Playbook Flow

```mermaid
flowchart TD
    A[start diagnosis] --> B[status]
    B --> C[validate]
    C --> D{passes}
    D -- no --> E[fix using validation report]
    E --> C
    D -- yes --> F[plan]
    F --> G[iterate]
    G --> H[done]
```
