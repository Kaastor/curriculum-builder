# scope_to_concepts

Given an unordered learning scope document:

1. Extract candidate concepts from headings, bullets, and key prose statements.
2. Normalize to atomic concepts suitable for independent mastery checks.
3. Keep traceability to source sections/lines.
4. Prefer concise concept titles over long narrative phrases.
5. Mark low-confidence concepts when decomposition is uncertain.

Output shape target:
- `concepts[]`: `{id, title, source_item_ids[], confidence}`

