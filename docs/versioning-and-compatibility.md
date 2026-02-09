# Versioning and Compatibility Policy

This document defines compatibility expectations for artifacts, schemas, and run metadata.

## 1. Policy Summary

- This repository is a PoC with a strict fresh-run contract.
- Backward-compatible migrations for run metadata/artifacts are not required.
- When schema/contract changes are incompatible, create a new run.

```mermaid
flowchart TD
    A[contract/schema change] --> B{breaking?}
    B -- no --> C[continue same run]
    B -- yes --> D[fresh-run required]
```

## 2. Versioned Contracts Map

### Topic Spec

- Field: `spec_version`
- Current expected value: `1.0`
- Validator behavior: topic spec must satisfy required contract fields and types.

### Scope Artifacts

- Envelope field: `schema_version`
- Current expected value: `1.0`
- Envelope fields:
  - `artifact_type`
  - `source_path`
  - `mode`
  - `section_filters`
  - `policy_snapshot`
  - `payload`

### Optimization Trace

- Field: `schema_version`
- Source: model policy snapshot at generation time
- Current default value: `1.0`

### Run Metadata

- File: `runs/<run_id>/run.json`
- Parsed via typed model (`RunMeta`)
- Invalid or incompatible metadata is treated as non-recoverable for that run.

```mermaid
flowchart LR
    A[topic_spec.json] --> A1[spec_version]
    B[scope_concepts/scope_dag] --> B1[schema_version]
    C[optimization_trace.json] --> C1[schema_version]
    D[run.json] --> D1[typed RunMeta parse]
```

## 3. Compatibility Decision Flow

Rule A: New run for incompatible changes
- If parsing or contract checks fail due to schema evolution, reinitialize run.

Rule B: Derived artifact regeneration
- `plan.json` and `diff_report.json` are derived and may be regenerated anytime.

Rule C: Stage is artifact-driven
- Runtime stage is inferred from current artifact freshness, reducing dependence on historical command sequence.

```mermaid
flowchart TD
    A[load artifacts] --> B{parses + contracts valid}
    B -- no --> C[mark run incompatible]
    C --> D[archive + init fresh run]
    B -- yes --> E{derived artifacts stale}
    E -- yes --> F[regenerate plan/diff]
    E -- no --> G[continue pipeline]
```

## 4. Change Classification Flow

### Non-breaking changes (same run can continue)

- documentation-only updates
- internal refactors with unchanged file formats
- validator rule tuning with same artifact structure

### Potentially breaking changes (prefer fresh run)

- required topic spec field changes
- run metadata shape changes
- scope artifact envelope shape/version changes
- curriculum schema changes used by validator/planner

```mermaid
flowchart TD
    A[change proposal] --> B{touches serialized contracts?}
    B -- no --> C[non-breaking path]
    B -- yes --> D{parser/validator behavior changed?}
    D -- no --> C
    D -- yes --> E[potentially breaking path]
    E --> F[document fresh-run guidance]
```

## 5. Release and Merge Flow

Before merge for contract-affecting changes:
1. update relevant docs (`README.md`, `docs/*`)
2. add/adjust tests for parsing/validation behavior
3. run `make gate`
4. mention fresh-run requirement in change summary

```mermaid
flowchart TD
    A[contract-affecting change] --> B[update docs]
    B --> C[update tests]
    C --> D[run make gate]
    D --> E{gate passes}
    E -- no --> C
    E -- yes --> F[include fresh-run note]
    F --> G[merge-ready]
```

## 6. Incompatible Run Recovery Flow

If an existing run becomes incompatible:
- archive if needed: `python3.11 scripts/orchestration.py archive <run_id>`
- initialize new run: `python3.11 scripts/orchestration.py init "<name>"`
- rerun pipeline from clean artifacts

```mermaid
flowchart TD
    A[incompatible run] --> B[archive old run]
    B --> C[initialize new run]
    C --> D[recreate inputs]
    D --> E[run pipeline]
```
