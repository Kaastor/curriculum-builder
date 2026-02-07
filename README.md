# curriculum-builder

Static inspector UI for curriculum graphs generated from `prompts/generator.md`.

## Commands

- `make setup` - local environment note (Python 3.10+).
- `make dev` - start local server at `http://localhost:4173/app/`.
- `make test` - run automated tests.
- `make validate` - run strict structural validation for `data/curriculum.json`.
- `make gate` - full quality gate (syntax check + validation + tests).

## Data

- Primary dataset: `data/curriculum.json`
- Mock dataset for UI development: `data/reliability/curriculum.mock.json`

The inspector can also load any local curriculum JSON file via file input.

## Agentic Loop

1. Implement in small, constrained changes.
2. Run `make test` while iterating.
3. Run `make gate` before handoff.
4. Keep docs and tests updated when behavior changes.
