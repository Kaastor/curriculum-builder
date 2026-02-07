# Prompt System

Use this folder as a staged system, not standalone prompts.

## Entry Point

- Start with `workflow.md`

## Files

- `workflow.md` - end-to-end operating flow and gates
- `topic_spec.md` - single source of truth input contract
- `curriculum_generator.md` - generates `curriculum.json`
- `structural_validator.md` - structural integrity review of generated curriculum
- `curriculum_validator.md` - pedagogical review of generated curriculum
- `repo_generator.md` - multi-phase repository generation (`plan`, `scaffold`, `full`)

## Recommended Run Order

1. Author `topic_spec.json` from `topic_spec.md`
2. Run curriculum generation
3. Run structural validation (`structural_validator.md`)
4. Run pedagogical validation (`curriculum_validator.md`)
5. Run repository generation in phases:
   - `plan`
   - `scaffold`
   - `full`
6. Run final quality gate in generated repository

## Operator Checklist

- [ ] Topic spec invariants satisfied
- [ ] Curriculum includes failure-first, transfer, and retention nodes
- [ ] Pedagogical review has no unresolved blocking findings
- [ ] Repository phase outputs pass their phase gates
- [ ] Final repository gate is green
