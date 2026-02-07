# AGENTS.md

## Quickstart (single source of truth)
- Setup: `make setup`
- Dev: `make dev`
- Test: `make test`
- Validate curriculum JSON: `make validate`
- Gate (must pass before handoff): `make gate`

## Working Agreements
- Keep the loop closed: run relevant checks while implementing and run `make gate` before handoff.
- Prefer small, reviewable changes. If a change is broad, propose a plan first.
- Ask before adding new production dependencies.
- Do not edit `.env` / secrets files.
- Do not run destructive git operations unless explicitly requested.

## PoC Priority
- This repository is a PoC; prioritize validating core logic and workflow correctness over polish.
- Optimize for fast, reliable feedback on behavior (tests/validation), and defer non-essential refinements.

## Definition Of Done
- Feature behavior works as requested.
- If behavior changed, update `README.md` and related docs.
- If feasible, add or update tests.
- Run `make gate` and keep it green.

## Git Hygiene
- Keep commits atomic and list paths explicitly.
- Conventional Commit types: `feat|fix|refactor|chore|docs|test|build|ci|perf|style`.
- Never delete unknown files to silence lint/type errors.

## Architecture Map
- `app/`: Static curriculum inspector UI (`index.html`, `styles.css`, `main.js`).
- `data/`: Curriculum JSON used by validator and UI (`data/curriculum.json`).
- `prompts/`: Prompt specifications for curriculum generation and review.
- `workflows/`: Run-oriented workspace for topic specs, generated artifacts, and logs.
- `scripts/validator.py`: Structural validator for curriculum JSON.
- `scripts/workflow.py`: Workflow CLI (`init|status|next|validate|run|archive|list`).
- `scripts/gate.sh`: Canonical local quality gate.
- `tests/`: Regression checks for data and tooling.

## When Stuck
- Report: what was done, what remains, and what blocks progress.
- List 2-3 hypotheses and run the fastest discriminating check next.
