# Prompt System Workflow

This is the single entry point for running the prompt system end to end.

## Goal

Turn a coding topic into:
1. a validated curriculum graph,
2. a structural validation report,
3. a pedagogical review.

## Stage -1 - Initialize Run Folder

Create a new isolated run folder:

- `make workflow-start RUN_NAME="<topic-slug>"`
- equivalent: `python3 scripts/workflow.py init "<topic-slug>"`

This creates:
- `workflows/runs/<run_id>/inputs/topic_spec.json`
- `workflows/runs/<run_id>/references/`
- `workflows/runs/<run_id>/outputs/{curriculum,reviews}/`
- `workflows/runs/<run_id>/logs/`

## System Inputs (Per Run)

- `workflows/runs/<run_id>/inputs/topic_spec.json` (contract in `prompts/topic_spec.md`)
- optional references in `workflows/runs/<run_id>/references/`

## System Outputs (Per Run)

- `workflows/runs/<run_id>/outputs/curriculum/curriculum.json`
- `workflows/runs/<run_id>/outputs/reviews/structural_validation.md`
- `workflows/runs/<run_id>/outputs/reviews/curriculum_review.md`

## Stage 0 - Prepare Topic Spec

Use `prompts/topic_spec.md`.

Checklist:
- failure modes are concrete and testable
- exercise categories include capstone category
- category prefixes are unique
- constraints and assessment thresholds are explicit

## Stage 1 - Generate Curriculum

Use `prompts/curriculum_generator.md` with:
- `workflows/runs/<run_id>/inputs/topic_spec.json`
- optional reference material

Output:
- `workflows/runs/<run_id>/outputs/curriculum/curriculum.json`

Required properties:
- valid DAG
- failure-first + mitigation coverage
- transfer and retention nodes included
- explicit coverage for failure modes and design patterns

## Stage 2 - Validate Curriculum

### 2A. Structural validation

Use `prompts/structural_validator.md` with:
- `workflows/runs/<run_id>/inputs/topic_spec.json`
- `workflows/runs/<run_id>/outputs/curriculum/curriculum.json`

Output:
- `workflows/runs/<run_id>/outputs/reviews/structural_validation.md`

Optional local quick check:
- `make validate` (useful for local baseline fixture compatibility)

### 2B. Pedagogical validation

Use `prompts/curriculum_validator.md` with:
- `workflows/runs/<run_id>/inputs/topic_spec.json`
- `workflows/runs/<run_id>/outputs/curriculum/curriculum.json`

Output:
- `workflows/runs/<run_id>/outputs/reviews/curriculum_review.md`

Rule:
- Resolve all `FAIL` and all high-impact `WEAK` findings before finalizing the run.

## Operating Rules

- Keep `topic_spec.json` as single source of truth.
- Do not hardcode topic-specific failure modes in prompt logic.
- Keep all exercises testable with observable pass/fail behavior.
- Prefer deterministic execution and offline reproducibility.

## Fast Path (for experienced users)

1. Create a run with `make workflow-start RUN_NAME="<topic-slug>"`
2. Fill `workflows/runs/<run_id>/inputs/topic_spec.json`
3. Run curriculum generation
4. Run structural validation with `make workflow-validate RUN_ID="<run_id>"`
5. Run pedagogical validation
6. Optionally automate generation + validation with `make workflow-run RUN_ID="<run_id>"` once commands are configured
