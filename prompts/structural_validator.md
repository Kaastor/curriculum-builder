# Validation Prompt (Compiler Style)

Validate `curriculum.json` against `topic_spec.json`.

## Blocking Checks

1. Topic spec contract validity.
2. Curriculum schema validity.
3. DAG integrity (missing prereqs, cycles, reachability).
4. Node/title uniqueness.
5. Constraint compliance (node count bounds if provided, total hours range).
6. Evidence-mode compliance:
- `minimal`: >=1 resource per node
- `standard`: >=2 resources + `definition` and `example` roles
- `strict`: standard rules + citations + `estimate_confidence` + `open_questions` structure

## Output

Provide:
- verdict: `PASS` or `FAIL`
- list of blocking failures
- list of warnings
- suggested fix order

Do not evaluate style preferences. Focus on deterministic acceptance criteria.
