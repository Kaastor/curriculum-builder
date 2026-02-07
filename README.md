# curriculum-builder

Static inspector UI for curriculum graphs generated from `prompts/generator.md`.

## UI Features

- Interactive dependency graph powered by Cytoscape (pan, zoom, click-to-inspect, fit-to-view).
- Layer explorer, searchable node table, coverage map, learning path, and milestones.
- Filter sync across graph + detail panels (layer/category/exercise type).
- Starts from `data/curriculum.json` and supports loading a local curriculum JSON file.

## Commands

- `make setup` - local environment note (Python 3.10+).
- `make dev` - start local server at `http://localhost:4173/app/`.
- `make test` - run automated tests.
- `make validate` - run strict structural validation for `data/curriculum.json`.
- `make gate` - full quality gate (syntax check + validation + tests).

## Data

- Primary dataset: `data/curriculum.json`
- Mock dataset for UI development: `data/reliability/curriculum.mock.json`

The inspector starts with `data/curriculum.json` and you can switch datasets with the `Load curriculum` file picker.

Note: Cytoscape is loaded from a CDN in `app/index.html`; if offline, the app keeps working except for the graph panel.

## Agentic Loop

1. Implement in small, constrained changes.
2. Run `make test` while iterating.
3. Run `make gate` before handoff.
4. Keep docs and tests updated when behavior changes.
