# Scope-First Input Guide

Use this mode when you only know **what** you want to learn, not the order.

## Input

Provide a markdown document (for example `runs/<run_id>/inputs/scope.md` or `docs/your-map.md`) containing unordered topics.

Mixed granularity is supported:
- broad topics
- specific techniques
- short prose sections

## Run

```bash
python3.11 scripts/orchestration.py run <run_id> --scope-file runs/<run_id>/inputs/scope.md
```

Optional scope selection controls:

```bash
python3.11 scripts/orchestration.py run <run_id> \
  --scope-file docs/agentic-engineering-atlas.md \
  --scope-mode section \
  --scope-section "Part I"
```

`--scope-mode` values:
- `full`: pass full markdown content into generation
- `section`: pass only matching heading sections (requires one or more `--scope-section`)
- `seed-list`: pass only list-like lines (bullets/numbered items)

## Artifacts

Scope-first mode writes:
- `runs/<run_id>/inputs/scope.md` (selected scope content used directly by generation)
- `runs/<run_id>/scope_concepts.json` (versioned envelope; scope-selection diagnostics under `payload`)
- `runs/<run_id>/scope_dag.json` (versioned envelope; direct-scope generation notes under `payload`)
- `runs/<run_id>/inputs/topic_spec.json` (synthesized orchestration contract)

Then normal outputs are generated:
- `outputs/curriculum/curriculum.json`
- `outputs/reviews/validation_report.md`
- `outputs/plan/plan.json`
- `outputs/reviews/diff_report.json`
