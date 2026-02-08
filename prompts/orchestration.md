# Orchestration (Phase One)

Orchestration is a tooling layer around the curriculum agent.

Pipeline:
`Spec -> Generate -> Validate -> Plan -> Iterate`

## Run Artifacts

Inputs:
- `workflows/runs/<run_id>/inputs/topic_spec.json`

Outputs:
- `workflows/runs/<run_id>/outputs/curriculum/curriculum.json`
- `workflows/runs/<run_id>/outputs/reviews/validation_report.md`
- `workflows/runs/<run_id>/outputs/plan/plan.json`
- `workflows/runs/<run_id>/outputs/reviews/diff_report.json`

## Commands

- initialize: `python3 scripts/orchestration.py init "<topic-slug>"`
- validate: `python3 scripts/orchestration.py validate <run_id>`
- plan: `python3 scripts/orchestration.py plan <run_id>`
- iterate (diff): `python3 scripts/orchestration.py iterate <run_id>`
- full pipeline: `python3 scripts/orchestration.py run <run_id>`

## Ownership

- `learning_compiler.agent` owns curriculum generation.
- `learning_compiler.validator` is the hard quality gate.
- `learning_compiler.orchestration` stores artifacts and coordinates reproducible runs.
