# concepts_to_edges

Given normalized concept candidates:

1. Infer prerequisite edges only when dependency is strong.
2. Keep uncertain order as soft edges (`recommended_before` or `related`).
3. Ensure hard prerequisite edges form a DAG.
4. Emit deterministic tie-break decisions and confidence values.

Output shape target:
- `hard_edges[]`: `{source_id, target_id, relation="prerequisite", confidence, reason}`
- `soft_edges[]`: `{source_id, target_id, relation, confidence, reason}`
- `topological_order[]`
- `phases[][]`
- `ambiguities[]`

