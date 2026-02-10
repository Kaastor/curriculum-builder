# curriculum-builder

Agent-first learning compiler that turns a `topic_spec.json` (or `scope.md`) into:
- a validated curriculum DAG
- a deterministic learning plan
- a diff report against prior curriculum

Core loop:
`Spec -> Generate -> Validate -> Plan -> Iterate`

## Quickstart

- `make setup`
- `make orchestration-start RUN_NAME="my-topic"`
- choose one input path:
  - edit `runs/<run_id>/inputs/topic_spec.json`
  - or use `--scope-file` at run time
- `make orchestration-run RUN_ID="<run_id>"`
- inspect `runs/<run_id>/outputs/curriculum/curriculum.json`

Scope-first quickstart:

```bash
python3.11 scripts/orchestration.py run <run_id> --scope-file docs/agentic-engineering-atlas.md
```

## Common Commands

General:
- `make setup`
- `make dev`
- `make test`
- `make validate`
- `make gate`

Orchestration:
- `make orchestration-start RUN_NAME="<topic-slug>"`
- `make orchestration-list`
- `make orchestration-status RUN_ID="<run_id>"`
- `make orchestration-next RUN_ID="<run_id>"`
- `make orchestration-run RUN_ID="<run_id>"`

Direct CLI:
- `python3.11 scripts/orchestration.py init "<topic-slug>"`
- `python3.11 scripts/orchestration.py run <run_id>`
- `python3.11 scripts/orchestration.py run <run_id> --scope-file <path/to/scope.md>`
- `python3.11 scripts/orchestration.py validate <run_id>`
- `python3.11 scripts/orchestration.py plan <run_id>`
- `python3.11 scripts/orchestration.py iterate <run_id>`
- `python3.11 scripts/validator.py [curriculum.json] --topic-spec <topic_spec.json>`

## Detailed Documentation

Core technical docs:
- `docs/architecture.md`: system architecture, boundaries, patterns, invariants, and diagrams.
- `docs/orchestration.md`: run lifecycle, command contracts, artifact freshness, and recovery paths.
- `docs/agent-runtime.md`: optimization loop, provider modes (`codex_exec`, `remote_llm`, `internal`), retries/timeouts, and troubleshooting.
- `docs/scope-ingestion.md`: `scope.md` ingestion modes, selection semantics, synthesized topic spec behavior, and limitations.
- `docs/versioning-and-compatibility.md`: schema and artifact compatibility policy, fresh-run contract, and change impact rules.

Supporting docs:
- `docs/contributor-playbook.md`
- `docs/incident-runbook.md`
- `docs/adr/README.md`
- `docs/agentic-engineering-atlas.md`
- `docs/learning/agentic-mental-map.md`
- `docs/learning/agentic-taxonomy.md`
- `docs/learning/agentic-readiness-standard.md`
- `plans/agentic_engineering_learning_roadmap.md`

## Topic Spec Contract

Detailed contract is in `prompts/topic_spec.md`.

Top-level fields:
- `spec_version`
- `goal`
- `audience`
- `prerequisites`
- `scope_in`
- `scope_out`
- `constraints`
- `domain_mode`
- `evidence_mode`
- `misconceptions` (optional)
- `context_pack` (optional)

## UI

- Run `make dev`
- Open `http://localhost:4173/app/`
- Default behavior: loads latest generated run curriculum
- Fallback: load local JSON via file picker

## Quality Gate

Run before handoff:

```bash
make gate
```
