# Workflow (Phase One)

Pipeline spine:
`Spec -> Map -> Validate -> Plan -> Iterate`

## Run Artifacts

Inputs:
- `workflows/runs/<run_id>/inputs/topic_spec.json`
- `workflows/runs/<run_id>/inputs/automation.json`

Outputs:
- `workflows/runs/<run_id>/outputs/curriculum/curriculum.json`
- `workflows/runs/<run_id>/outputs/reviews/validation_report.md`
- `workflows/runs/<run_id>/outputs/plan/plan.json`
- `workflows/runs/<run_id>/outputs/reviews/diff_report.json`

## Commands

- initialize: `python3 scripts/workflow.py init "<topic-slug>"`
- validate: `python3 scripts/workflow.py validate <run_id>`
- plan: `python3 scripts/workflow.py plan <run_id>`
- iterate (diff): `python3 scripts/workflow.py iterate <run_id>`
- full pipeline: `python3 scripts/workflow.py run <run_id>`

## Automation Contract

`inputs/automation.json` contains:

```json
{
  "map_cmd": "<command that writes outputs/curriculum/curriculum.json>"
}
```

`map_cmd` is optional only when curriculum already exists at expected path.
