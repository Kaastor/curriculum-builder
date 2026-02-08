# curriculum-builder

Agent-first learning compiler for generating curriculum DAGs from `topic_spec.json`.

Pipeline:
`Spec -> Generate -> Validate -> Plan -> Iterate`

Evidence strictness dial:
`minimal | standard | strict`

## Scope

This repo focuses on:
- topic spec contract
- agent-owned curriculum generation (`curriculum.json`)
- deterministic validation (structural + evidence)
- deterministic 2-4 week plan output
- iteration diff report

Out of scope (phase one):
- exercise generation
- adaptive tutoring/personalization

## Architecture

- `learning_compiler/agent/`: curriculum generation logic and resource selection.
- `learning_compiler/validator/`: hard validation gate.
- `learning_compiler/orchestration/`: reproducible run tooling (artifacts, stage sync, planning, diff).
- `scripts/`: thin CLIs (`orchestration.py`, `validator.py`) and `gate.sh`.

## Canonical Artifacts

Per run (`workflows/runs/<run_id>/`):
- `inputs/topic_spec.json`
- `outputs/curriculum/curriculum.json`
- `outputs/reviews/validation_report.md`
- `outputs/plan/plan.json`
- `outputs/reviews/diff_report.json`

## Commands

General:
- `make setup`
- `make dev`
- `make test`
- `make validate`
- `make gate`

Orchestration:
- `make orchestration-start RUN_NAME="<topic-slug>"`
- `make orchestration-list`
- `make orchestration-status RUN_ID="<run_id>"`
- `make orchestration-next RUN_ID="<run_id>"`
- `make orchestration-validate RUN_ID="<run_id>"`
- `make orchestration-plan RUN_ID="<run_id>"`
- `make orchestration-iterate RUN_ID="<run_id>"`
- `make orchestration-run RUN_ID="<run_id>"`
- `make orchestration-archive RUN_ID="<run_id>"`

Direct CLI:
- `python3.11 scripts/orchestration.py init "<topic-slug>"`
- `python3.11 scripts/orchestration.py run <run_id>`
- `python3.11 scripts/orchestration.py validate <run_id>`
- `python3.11 scripts/orchestration.py plan <run_id>`
- `python3.11 scripts/orchestration.py iterate <run_id>`
- `python3.11 scripts/orchestration.py status <run_id>`
- `python3.11 scripts/orchestration.py next <run_id>`
- `python3.11 scripts/orchestration.py archive <run_id>`
- `python3.11 scripts/orchestration.py list`
- `python3.11 scripts/validator.py <curriculum.json> --topic-spec <topic_spec.json>`

## Generate a Curriculum

1. Start run:
   - `make orchestration-start RUN_NAME="quantum-neural-networks"`
2. Get run id:
   - `make orchestration-list`
3. Fill topic spec:
   - edit `workflows/runs/<run_id>/inputs/topic_spec.json`
4. Execute full pipeline (agent generates curriculum):
   - `make orchestration-run RUN_ID="<run_id>"`
5. Inspect outputs:
   - `workflows/runs/<run_id>/outputs/curriculum/curriculum.json`
   - `workflows/runs/<run_id>/outputs/reviews/validation_report.md`
   - `workflows/runs/<run_id>/outputs/plan/plan.json`
   - `workflows/runs/<run_id>/outputs/reviews/diff_report.json`

## Topic Spec Fields

Contract details: `prompts/topic_spec.md`.

Top-level fields:
- `spec_version`
- `goal`
- `audience`
- `prerequisites`
- `scope_in`
- `scope_out`
- `constraints`
- `domain_mode`
- `evidence_mode`
- `misconceptions` (optional)

`constraints` fields:
- `hours_per_week` (> 0)
- `total_hours_min` (> 0)
- `total_hours_max` (> 0)
- `depth` (`survey|practical|mastery`)
- `node_count_min` (optional int)
- `node_count_max` (optional int)
- `max_prerequisites_per_node` (optional int >= 1)

Enum meanings:
- `depth`:
  - `survey`: broad coverage.
  - `practical`: applied working depth.
  - `mastery`: deeper rigor and edge cases.
- `domain_mode`:
  - `mature`: stable domain.
  - `frontier`: evolving domain with contradictory/uncertain evidence.
- `evidence_mode`:
  - `minimal`: at least one resource per node.
  - `standard`: at least two resources per node with `definition` and `example` roles.
  - `strict`: standard requirements plus citations and confidence, with explicit `open_questions`.

## UI

Run local UI:

```bash
make dev
```

Open `http://localhost:4173/app/`.
- Default load: `data/curriculum.json`.
- To inspect generated run output, upload `workflows/runs/<run_id>/outputs/curriculum/curriculum.json` via file picker.

## Quality Gate

Run before handoff:

```bash
make gate
```
