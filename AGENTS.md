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
- After making changes, update documentation (`README.md` and related `docs/`) in the same change set.
- Documentation quality bar is staff-level: documents should explain architecture, design rationale/tradeoffs, contracts/invariants, and operational behavior clearly.
- Document all flows with Mermaid diagrams to provide comprehensive end-to-end flow understanding (happy path, alternate paths, and failure/recovery paths where applicable).
- Before handoff, validate that every Mermaid diagram introduced or modified in the change set compiles successfully.
- Canonical home for detailed technical documentation is `docs/`; keep `README.md` concise as an entrypoint and doc index.
- After making changes, remove dead paths, dead code, and unnecessary code introduced or revealed by the change.
- Do not edit `.env` / secrets files.
- Do not run destructive git operations unless explicitly requested.

## PoC Priority
- This repository is a PoC; prioritize validating core logic and orchestration correctness over polish.
- Main goal: make the product output (curriculum) the highest quality possible.
- Primary goal: use this PoC as the best practical environment for learning agentic engineering deeply through real implementation and reliability work.
- Optimize for fast, reliable feedback on behavior (tests/validation), and defer non-essential refinements.
- No backward-compatible run metadata migrations: keep a strict fresh-run contract and re-initialize local runs when metadata/artifact schemas change.

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
- `prompts/`: Prompt specifications for topic spec, generation, validation, and orchestration.
- `runs/`: Run-oriented workspace for topic specs, generated artifacts, and logs.
- `scripts/validator.py`: Validator CLI entrypoint.
- `scripts/orchestration.py`: Orchestration CLI entrypoint (`init|status|next|validate|plan|iterate|run|archive|list`).
- `learning_compiler/agent/generator.py`: Agent-owned curriculum generation from `topic_spec.json`.
- `learning_compiler/agent/optimizer.py`: Iterative loop controller (`propose -> critique -> judge -> repair`).
- `learning_compiler/agent/planning/proposer.py`: Draft curriculum proposer stage.
- `learning_compiler/agent/quality/pedagogy_critic.py`: Pedagogical/learner-path critic diagnostics.
- `learning_compiler/agent/quality/model.py`: Deterministic acceptance judge and score aggregation.
- `learning_compiler/agent/quality/rules.py`: Graph-oriented deterministic quality rules.
- `learning_compiler/agent/quality/content_rules.py`: Content/actionability/relevance quality rules.
- `learning_compiler/agent/quality/actions.py`: Typed repair action contracts.
- `learning_compiler/agent/quality/planner.py`: Diagnostics-to-actions planner.
- `learning_compiler/agent/quality/executor.py`: Deterministic repair action executor.
- `learning_compiler/agent/model_policy.py`: Model/runtime policy controls for optimizer.
- `learning_compiler/agent/llm/client.py`: Stable LLM facade + provider factory.
- `learning_compiler/agent/llm/remote.py`: Remote LLM provider implementation (Responses API).
- `learning_compiler/agent/llm/codex.py`: `codex exec` provider implementation.
- `learning_compiler/agent/llm/schema.py` / `learning_compiler/agent/llm/prompt.py`: Shared structured schema and prompt/parse helpers.
- `learning_compiler/agent/llm/types.py`: Shared LLM request/client type contracts.
- `learning_compiler/agent/quality/trace.py`: Optimization trace schema and serializer.
- `learning_compiler/agent/planning/spec.py`: Topic-spec normalization and deterministic generation inputs.
- `learning_compiler/agent/planning/node_builder.py`: Node-level curriculum content construction.
- `learning_compiler/agent/resources/resolver.py`: Resource resolver interface + deterministic resolver implementation.
- `learning_compiler/agent/contracts.py`: Generation protocol for dependency-injected generators.
- `learning_compiler/domain/models.py`: Typed domain models for topic spec and curriculum artifacts.
- `learning_compiler/api.py`: Stable public API facade for agent/validator/orchestration.
- `learning_compiler/errors.py`: Shared typed error taxonomy and exit-code mapping.
- `learning_compiler/config.py`: Centralized app config loading from environment/defaults.
- `learning_compiler/markdown_scope.py`: Shared markdown phrase extraction helpers for scope-driven flows.
- `learning_compiler/validator/core.py`: Validator orchestration entrypoint.
- `learning_compiler/validator/topic_spec.py`: Topic spec contract checks + validator config derivation.
- `learning_compiler/validator/curriculum_schema.py`: Curriculum schema-level checks.
- `learning_compiler/validator/curriculum_graph.py`: DAG and structural constraint checks.
- `learning_compiler/validator/curriculum_evidence.py`: Evidence/open-question checks.
- `learning_compiler/validator/curriculum_quality.py`: DAG progression, node quality, and estimate granularity checks.
- `learning_compiler/validator/types.py`: Validator enums, constants, and result/config types.
- `learning_compiler/validator/helpers.py`: Primitive validator helper predicates.
- `learning_compiler/orchestration/cli.py`: Orchestration parser and CLI dispatch.
- `learning_compiler/orchestration/commands/basic.py`: Basic lifecycle commands (`init|status|next|list|archive`).
- `learning_compiler/orchestration/commands/pipeline.py`: Pipeline commands (`validate|plan|iterate|run`).
- `learning_compiler/orchestration/commands/utils.py`: Shared command argument helpers.
- `learning_compiler/orchestration/scope/args.py`: Scope CLI argument parsing and mode validation helpers.
- `learning_compiler/orchestration/scope/selection.py`: Scope file path resolution and selected-scope extraction.
- `learning_compiler/orchestration/scope/topic_spec.py`: Scope text to `topic_spec` synthesis logic.
- `learning_compiler/orchestration/scope/pipeline.py`: Scope ingestion pipeline and artifact emission.
- `learning_compiler/orchestration/types.py`: Orchestration enums and typed path contracts.
- `learning_compiler/orchestration/fs.py`: Filesystem/env/run loading helpers.
- `learning_compiler/orchestration/events.py`: Standardized run event schema.
- `learning_compiler/orchestration/stage.py`: Stage inference/sync logic.
- `learning_compiler/orchestration/exec.py`: Validator execution helpers.
- `learning_compiler/orchestration/planning.py`: Deterministic topology, planning, and diff computations.
- `scripts/static_checks.py`: Static architecture-boundary checks.
- `scripts/coverage_check.py`: Stdlib trace-based statement coverage check.
- `scripts/gate.sh`: Canonical local quality gate.
- `tests/`: Regression checks for fixtures and tooling (`tests/fixtures/curriculum.json`).


## Code quality and style rules (staff-level defaults)

### General
- Default to staff-level engineering quality.
- Optimize for readability and maintainability by a new teammate.
- Prefer simple, explicit control flow and single-responsibility design.
- Leave the codebase better than you found it (reduce complexity in touched areas).

### Project structure
- Package-first:
  - `scripts/` contains thin executable wrappers only.
  - reusable logic lives under `learning_compiler/`, organized by domain (e.g., `agent/`, `orchestration/`, `validator/`).
- Keep CLI entrypoints thin; move business logic into importable modules.

### Module boundaries and size
- Modules SHOULD stay cohesive and reviewable (guideline: ~<= 250 LOC).
- If a module grows large, split by responsibility (types/fs/stage/commands/etc.).

### Python and typing
- Python 3.11 only.
- Types MUST be strict (`mypy --strict`); avoid `Any` unless isolated at boundaries.
- Avoid stringly-typed behavior: new protocol fields MUST be modeled explicitly.
- Prefer:
  - `@dataclass(slots=True, frozen=True)` for immutable value/protocol objects (when appropriate).
  - `Enum` for closed sets (phases, effects, profiles, violation types).
  - `Literal` / `NewType` / `TypedDict` where they encode real invariants.

### Purity, I/O, and side effects
- Modules MUST be safe to import: no import-time side effects.
- Keep I/O at the edges; core logic SHOULD be pure/portable when possible.
- No hidden global state; pass dependencies explicitly (RNG, config, clients).

### Determinism
- Determinism is a feature:
  - use a seeded RNG (`random.Random(seed)`) or the existing `FaultPlan`.
  - do not use global randomness.
  - keep replay/trace hashes stable when expected.

### Errors and APIs
- Use explicit error contracts:
  - prefer small project exception types.
  - no bare `except`.
  - no silent `None`/`False` failures as control flow.
- Keep public APIs small and stable; keep helpers private (prefix `_`).

### Design style
- Prefer composition + `Protocol` interfaces over deep inheritance.

### Documentation
- Keep functions small; keep modules cohesive.
- Write short docstrings when intent/constraints are non-obvious.

## When Stuck
- Report: what was done, what remains, and what blocks progress.
- List 2-3 hypotheses and run the fastest discriminating check next.
