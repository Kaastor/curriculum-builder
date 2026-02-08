# Topic Spec Contract (Phase One)

`topic_spec.json` is the source of truth for the learning compiler.

## Required Shape

```json
{
  "spec_version": "1.0",
  "goal": "what learner can do",
  "audience": "who this is for",
  "prerequisites": ["prior knowledge"],
  "scope_in": ["explicitly included"],
  "scope_out": ["explicitly excluded"],
  "constraints": {
    "hours_per_week": 6,
    "total_hours_min": 16,
    "total_hours_max": 24,
    "depth": "survey|practical|mastery",
    "node_count_min": 8,
    "node_count_max": 20,
    "max_prerequisites_per_node": 3
  },
  "domain_mode": "mature|frontier",
  "evidence_mode": "minimal|standard|strict",
  "misconceptions": ["optional"]
}
```

## Invariants

1. `spec_version` must be `1.0`.
2. `total_hours_min <= total_hours_max`.
3. `hours_per_week > 0`.
4. `depth` must be one of `survey|practical|mastery`.
5. `domain_mode` must be `mature|frontier`.
6. `evidence_mode` must be `minimal|standard|strict`.
7. `node_count_min <= node_count_max` when both are provided.
8. `max_prerequisites_per_node >= 1` when provided.

## Authoring Notes

- Keep scope boundaries explicit to prevent curriculum drift.
- Prefer concrete prerequisites over vague experience labels.
- `misconceptions` should capture costly misunderstandings.
- Re-running with same spec should produce comparable curriculum structure.

## Field Guide

`spec_version`
- Type: string.
- Use: contract version for validator compatibility.
- Rule: set to `"1.0"`.

`goal`
- Type: string.
- Use: target capability at the end of the plan.
- Write as: observable outcome, not a vague interest.
- Good: `"Design and justify a Bayesian decision rule for product launch choices."`

`audience`
- Type: string.
- Use: who the curriculum is written for.
- Include: role + baseline context.

`prerequisites`
- Type: array of strings.
- Use: required prior knowledge before starting node N1.
- Keep concrete: concepts/tools, not generic labels like `"beginner"` or `"smart people"`.

`scope_in`
- Type: array of strings.
- Use: topics/capabilities explicitly included in this run.
- Purpose: anchors decomposition and prevents omissions.

`scope_out`
- Type: array of strings.
- Use: topics explicitly excluded.
- Purpose: protects time budget and prevents drift.

`constraints`
- Type: object.
- Use: hard limits for planner and validator.

`constraints.hours_per_week`
- Type: number (> 0).
- Use: weekly learning budget.

`constraints.total_hours_min`
- Type: number (> 0).
- Use: minimum total runtime target.

`constraints.total_hours_max`
- Type: number (> 0).
- Use: maximum total runtime target.

`constraints.depth`
- Type: enum (`survey|practical|mastery`).
- Use: expected granularity and rigor.

`constraints.node_count_min` (optional)
- Type: integer.
- Use: lower bound for DAG node count.

`constraints.node_count_max` (optional)
- Type: integer.
- Use: upper bound for DAG node count.

`constraints.max_prerequisites_per_node` (optional)
- Type: integer (>= 1).
- Use: cap branching complexity and reduce prerequisite overload.

`domain_mode`
- Type: enum (`mature|frontier`).
- Use: controls how uncertainty is handled.
- `mature`: stable body of knowledge.
- `frontier`: conflicting/unfinished knowledge likely.

`evidence_mode`
- Type: enum (`minimal|standard|strict`).
- Use: strictness dial for evidence requirements.
- `minimal`: >=1 resource per node.
- `standard`: >=2 resources with definition + example anchoring.
- `strict`: citation-backed claims + confidence + explicit open questions.

`misconceptions` (optional)
- Type: array of strings.
- Use: known traps to explicitly address in node pitfalls/mastery checks.
