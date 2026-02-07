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
