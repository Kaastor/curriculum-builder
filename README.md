# curriculum-builder

Phase-one implementation of a reusable learning compiler.

Pipeline spine:
`Spec -> Map -> Validate -> Plan -> Iterate`

Evidence strictness is a dial:
`minimal | standard | strict`

## Scope

This repo focuses on:
- topic spec contract
- canonical concept DAG (`curriculum.json`)
- deterministic validation (structural + evidence)
- executable 2-4 week plan output
- iteration diff report

Out of scope in phase one:
- exercise generation
- pedagogical-review artifact gating
- personalization features

## Canonical Artifacts

Per run (`workflows/runs/<run_id>/`):

- `inputs/topic_spec.json`
- `inputs/automation.json`
- `outputs/curriculum/curriculum.json`
- `outputs/reviews/validation_report.md`
- `outputs/plan/plan.json`
- `outputs/reviews/diff_report.json`

## Code Layout

- `scripts/`: thin CLI entrypoints (`workflow.py`, `validator.py`) and `gate.sh`.
- `learning_compiler/validator/`: validator modules (`core`, `topic_spec`, `curriculum_schema`, `curriculum_graph`, `curriculum_evidence`).
- `learning_compiler/workflow/`: workflow orchestration modules (`cli`, `commands`, `stage`, `planning`, etc.).

## Commands

General:
- `make setup`
- `make dev`
- `make test`
- `make validate`
- `make gate`

Workflow:
- `make workflow-start RUN_NAME="<topic-slug>"`
- `make workflow-list`
- `make workflow-status RUN_ID="<run_id>"`
- `make workflow-next RUN_ID="<run_id>"`
- `make workflow-validate RUN_ID="<run_id>"`
- `make workflow-run RUN_ID="<run_id>"`
- `make workflow-archive RUN_ID="<run_id>"`

Direct CLI equivalents:
- `python3.11 scripts/workflow.py init "<topic-slug>"`
- `python3.11 scripts/workflow.py status <run_id>`
- `python3.11 scripts/workflow.py next <run_id>`
- `python3.11 scripts/workflow.py validate <run_id>`
- `python3.11 scripts/workflow.py plan <run_id>`
- `python3.11 scripts/workflow.py iterate <run_id>`
- `python3.11 scripts/workflow.py run <run_id>`
- `python3.11 scripts/workflow.py archive <run_id>`
- `python3.11 scripts/workflow.py list`
- `python3.11 scripts/validator.py <curriculum.json> --topic-spec <topic_spec.json>`

## Automation Config

`workflows/templates/automation.template.json`:

```json
{
  "map_cmd": "<command that generates outputs/curriculum/curriculum.json>"
}
```

`map_cmd` is optional only if curriculum already exists at the expected path.

## UI

Run local UI:

```bash
make dev
```

Open `http://localhost:4173/app/` to inspect DAG structure, layers, milestones, learning path, and node-level mastery checks/resources.

## Quality Gate

Before handoff run:

```bash
make gate
```

Gate includes:
- Python syntax check (`scripts/`, `learning_compiler/`, `tests/`)
- curriculum validation (`data/curriculum.json`)
- test suite (`tests/`)
