# Prompt System Workflow

This is the single entry point for running the prompt system end to end.

## Goal

Turn a coding topic into:
1. a validated curriculum graph,
2. a pedagogical review,
3. a runnable learning repository.

## System Inputs

- `topic_spec.json` (contract in `prompts/topic_spec.md`)
- optional domain references (notes, docs, incidents, code snippets)

## System Outputs

- `data/curriculum.json`
- `reviews/curriculum_review.md`
- `<topic_id>-learning/` (generated learning repository)

## Stage 0 - Prepare Topic Spec

Use `prompts/topic_spec.md`.

Checklist:
- failure modes are concrete and testable
- exercise categories include capstone category
- category prefixes are unique
- constraints and assessment thresholds are explicit

## Stage 1 - Generate Curriculum

Use `prompts/curriculum_generator.md` with:
- `topic_spec.json`
- optional reference material

Output:
- `data/curriculum.json`

Required properties:
- valid DAG
- failure-first + mitigation coverage
- transfer and retention nodes included
- explicit coverage for failure modes and design patterns

## Stage 2 - Validate Curriculum

### 2A. Structural validation

Use `prompts/structural_validator.md` with:
- `topic_spec.json`
- `data/curriculum.json`

Output:
- `reviews/structural_validation.md`

Optional local quick check:
- `make validate` (useful for local baseline fixture compatibility)

### 2B. Pedagogical validation

Use `prompts/curriculum_validator.md` with:
- `topic_spec.json`
- `data/curriculum.json`

Output:
- `reviews/curriculum_review.md`

Rule:
- Resolve all `FAIL` and all high-impact `WEAK` findings before moving to Stage 3.

## Stage 3 - Generate Repository

Use `prompts/repo_generator.md` with `generation_mode` in this order:

1. `plan`
- produce file manifest + generation strategy + risk list

2. `scaffold`
- generate project skeleton, exercise stubs, tests skeleton, scripts

3. `full`
- generate complete implementation, solutions, docs, and pass quality checks

Output:
- `<topic_id>-learning/`

## Stage 4 - Final Quality Gate

Inside generated repository:
- run `make gate`
- run progress/check scripts
- verify capstone and transfer tasks are runnable

## Operating Rules

- Keep `topic_spec.json` as single source of truth.
- Do not hardcode topic-specific failure modes in generator/repo prompts.
- Keep all exercises testable with observable pass/fail behavior.
- Prefer deterministic execution and offline reproducibility.

## Fast Path (for experienced users)

1. Fill `topic_spec.json`
2. Run curriculum generation
3. Run structural + pedagogical validation
4. Run repo generation (`plan` -> `scaffold` -> `full`)
5. Run final gate
