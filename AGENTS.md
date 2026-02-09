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
- `learning_compiler/agent/proposer.py`: Draft curriculum proposer stage.
- `learning_compiler/agent/pedagogy_critic.py`: Pedagogical/learner-path critic diagnostics.
- `learning_compiler/agent/quality_model.py`: Deterministic acceptance judge and score aggregation.
- `learning_compiler/agent/quality_rules.py`: Graph-oriented deterministic quality rules.
- `learning_compiler/agent/quality_content_rules.py`: Content/actionability/relevance quality rules.
- `learning_compiler/agent/repair_actions.py`: Typed repair action contracts.
- `learning_compiler/agent/repair_planner.py`: Diagnostics-to-actions planner.
- `learning_compiler/agent/repair_executor.py`: Deterministic repair action executor.
- `learning_compiler/agent/model_policy.py`: Model/runtime policy controls for optimizer.
- `learning_compiler/agent/llm_client.py`: Stable LLM facade + provider factory.
- `learning_compiler/agent/llm_remote.py`: Remote LLM provider implementation (Responses API).
- `learning_compiler/agent/llm_codex.py`: `codex exec` provider implementation.
- `learning_compiler/agent/llm_schema.py` / `learning_compiler/agent/llm_prompt.py`: Shared structured schema and prompt/parse helpers.
- `learning_compiler/agent/llm_types.py`: Shared LLM request/client type contracts.
- `learning_compiler/agent/trace.py`: Optimization trace schema and serializer.
- `learning_compiler/agent/spec.py`: Topic-spec normalization and deterministic generation inputs.
- `learning_compiler/agent/node_builder.py`: Node-level curriculum content construction.
- `learning_compiler/agent/research.py`: Resource resolver interface + deterministic resolver implementation.
- `learning_compiler/agent/contracts.py`: Generation protocol for dependency-injected generators.
- `learning_compiler/domain/models.py`: Typed domain models for topic spec and curriculum artifacts.
- `learning_compiler/api.py`: Stable public API facade for agent/validator/orchestration.
- `learning_compiler/errors.py`: Shared typed error taxonomy and exit-code mapping.
- `learning_compiler/config.py`: Centralized app config loading from environment/defaults.
- `learning_compiler/validator/core.py`: Validator orchestration entrypoint.
- `learning_compiler/validator/topic_spec.py`: Topic spec contract checks + validator config derivation.
- `learning_compiler/validator/curriculum_schema.py`: Curriculum schema-level checks.
- `learning_compiler/validator/curriculum_graph.py`: DAG and structural constraint checks.
- `learning_compiler/validator/curriculum_evidence.py`: Evidence/open-question checks.
- `learning_compiler/validator/curriculum_quality.py`: DAG progression, node quality, and estimate granularity checks.
- `learning_compiler/validator/types.py`: Validator enums, constants, and result/config types.
- `learning_compiler/validator/helpers.py`: Primitive validator helper predicates.
- `learning_compiler/orchestration/cli.py`: Orchestration parser and CLI dispatch.
- `learning_compiler/orchestration/commands_basic.py`: Basic lifecycle commands (`init|status|next|list|archive`).
- `learning_compiler/orchestration/commands_pipeline.py`: Pipeline commands (`validate|plan|iterate|run`).
- `learning_compiler/orchestration/command_utils.py`: Shared command argument helpers.
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

- Quality bar: default to **staff-level engineering quality** for every change.
- Write code that is clean, modular, and maintainable by someone new to the project.
- Prefer explicit module boundaries and single-responsibility functions over dense, multi-purpose code paths.
- Optimize for readability first: clear naming, predictable control flow, and minimal hidden coupling.
- Leave the codebase better than you found it: reduce complexity when touching nearby code.
- Keep production modules compact and reviewable:
  - target roughly <= 250 LOC per module
  - if a file grows beyond that, split by responsibility (types/fs/stage/commands/etc.)
  - keep CLI entrypoints thin and move business logic to importable modules
- Prefer package-first structure:
  - `scripts/` should contain thin executable wrappers only
  - reusable logic belongs under `learning_compiler/` organized by domain (`agent`, `orchestration`, `validator`, etc.)
- Python **3.11** only.
- Keep types **strict** (repo runs `mypy` in strict mode).
- Use `@dataclass(slots=True, frozen=True)` for immutable protocol objects where appropriate.
- Prefer `Enum` for closed sets (phases, effects, profiles, violation types).
- Avoid “stringly-typed” behavior. If you add a new protocol field, model it explicitly.
- Determinism is a feature:
  - use seeded RNG (`random.Random(seed)`) or the existing `FaultPlan`
  - do not use global randomness
  - ensure replay/trace hashes remain stable when expected
- Keep functions small; keep modules cohesive; write short docstrings where intent is non-obvious.

## When Stuck
- Report: what was done, what remains, and what blocks progress.
- List 2-3 hypotheses and run the fastest discriminating check next.
