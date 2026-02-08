# Agentic Engineering Field Map

## Why this document

This guide maps the major fields of agentic AI engineering to this repository so you can build the curriculum system and deliberately level up as an engineer at the same time.

## Core fields of agentic engineering

| Field | What it is | What it solves | Typical problems |
| --- | --- | --- | --- |
| Strategy and Planning (Proposer/Brain) | Task decomposition, plan generation, next-action selection, and policy for what to do first. | Turns user intent into executable steps instead of single-shot outputs. | Hallucinated plans, brittle decomposition, weak prioritization under constraints, poor long-horizon coherence. |
| State and Memory | Modeling and persistence of run state, artifacts, progress, and reusable context across iterations. | Enables multi-step work, resumability, and historical continuity. | Context drift, stale memory, schema drift, replay mismatch, hidden coupling between state and logic. |
| Tooling and Execution Runtime | Tool interfaces, command dispatch, orchestration flow, retries, idempotency, and stage transitions. | Converts plans into real side effects safely and repeatably. | Partial failures, double-apply bugs, non-idempotent operations, race/order issues, weak failure recovery. |
| Reliability and Safety | Input/output contracts, validation, guardrails, typed errors, fallback behavior, and policy boundaries. | Prevents silent corruption and unsafe or low-trust outputs. | False positives/negatives in validation, over-restrictive guardrails, uncaught edge cases, unclear failure semantics. |
| Evaluation and Quality Engineering | Regression tests, fixture-based evaluation, deterministic checks, and quality gates. | Detects quality regressions before release and supports safe iteration speed. | Goodhart metrics, flaky tests, low coverage of real failure modes, tests that miss behavior regressions. |
| Observability and Operations | Structured events, run metadata, traces, timing, cost/latency visibility, and operational workflows. | Makes failures diagnosable and operations predictable. | Missing telemetry, noisy logs, hard-to-reconstruct incidents, inability to measure performance tradeoffs. |
| Human Interface and Product Control | CLI/UI affordances, explainability of next steps, confidence cues, and human override paths. | Keeps humans in control and improves trust and adoption. | Opaque behavior, poor UX for interventions, low discoverability of system state and rationale. |

## Mental map: where each field lives in this repo

## 1) Strategy and Planning

- Primary code:
  - `learning_compiler/agent/generator.py`
  - `learning_compiler/agent/spec.py`
  - `learning_compiler/agent/node_builder.py`
  - `learning_compiler/orchestration/planning.py`
  - `prompts/curriculum_generator.md`
  - `prompts/orchestration.md`
- What you should practice here:
  - Improve deterministic plan quality under constrained topic specs.
  - Make planning explainable (why this node/order now).
  - Keep decomposition robust to sparse or noisy spec inputs.
- Real engineering depth you will hit:
  - Tradeoffs between plan optimality, determinism, and simplicity.
  - Controlling strategy behavior without overfitting to single fixtures.

## 2) State and Memory

- Primary code:
  - `learning_compiler/orchestration/fs.py`
  - `learning_compiler/orchestration/types.py`
  - `learning_compiler/orchestration/meta.py`
  - `runs/` artifacts and `run.json` lifecycle
- What you should practice here:
  - Keeping run metadata contracts explicit and strict.
  - Keeping state transitions explicit and auditable.
  - Recovering quickly by re-initializing incompatible local runs.
- Real engineering depth you will hit:
  - Preventing hidden state drift and stale artifact coupling.
  - Designing contracts that are simple enough to evolve safely in PoC mode.

## 3) Tooling and Execution Runtime

- Primary code:
  - `learning_compiler/orchestration/cli.py`
  - `learning_compiler/orchestration/commands_basic.py`
  - `learning_compiler/orchestration/commands_pipeline.py`
  - `learning_compiler/orchestration/exec.py`
  - `learning_compiler/orchestration/stage.py`
  - `scripts/orchestration.py`
- What you should practice here:
  - Strong command contracts (`init|status|next|validate|plan|iterate|run|archive|list`).
  - Idempotent command behavior and resilient retries.
  - Clean separation between CLI parsing and business logic.
- Real engineering depth you will hit:
  - Partial pipeline failure handling and recovery semantics.
  - Stage synchronization and correctness under repeated invocations.

## 4) Reliability and Safety

- Primary code:
  - `learning_compiler/validator/core.py`
  - `learning_compiler/validator/topic_spec.py`
  - `learning_compiler/validator/curriculum_schema.py`
  - `learning_compiler/validator/curriculum_graph.py`
  - `learning_compiler/validator/curriculum_evidence.py`
  - `learning_compiler/validator/curriculum_quality.py`
  - `learning_compiler/errors.py`
  - `prompts/structural_validator.md`
- What you should practice here:
  - Turning expectations into explicit contracts and typed failures.
  - Ensuring validators catch real defects, not cosmetic variance.
  - Defining clear fail/continue behavior in orchestration.
- Real engineering depth you will hit:
  - Balancing strictness with usefulness in PoC iterations.
  - Designing error taxonomies that stay stable as scope grows.

## 5) Evaluation and Quality Engineering

- Primary code:
  - `tests/` (especially determinism, orchestration, validator, fixture tests)
  - `tests/fixtures/curriculum.json`
  - `scripts/gate.sh`
  - `scripts/static_checks.py`
  - `scripts/coverage_check.py`
  - `docs/determinism.md`
- What you should practice here:
  - Add tests for each failure mode found in real runs.
  - Keep deterministic checks strong when expanding capabilities.
  - Treat `make gate` as release criteria, not optional hygiene.
- Real engineering depth you will hit:
  - Building evaluation signal that predicts production behavior.
  - Preventing regressions in non-deterministic-seeming workflows.

## 6) Observability and Operations

- Primary code:
  - `learning_compiler/orchestration/events.py`
  - `learning_compiler/orchestration/meta.py`
  - `learning_compiler/orchestration/exec.py`
  - `learning_compiler/config.py`
  - `runs/*/logs/` and run history
- What you should practice here:
  - Emit structured, useful events for each critical transition.
  - Make incident reconstruction possible from artifacts alone.
  - Track operational baselines (latency, retries, validation failure rates).
- Real engineering depth you will hit:
  - Detecting weak points early via telemetry, not intuition.
  - Designing logs/events that remain useful as workflow complexity grows.

## 7) Human Interface and Product Control

- Primary code:
  - `app/index.html`
  - `app/main.js`
  - `app/styles.css`
  - `README.md` and command UX in CLI modules
- What you should practice here:
  - Explain run state and next actions clearly for human operators.
  - Design override points where humans can intervene safely.
  - Keep UX aligned with deterministic and validation guarantees.
- Real engineering depth you will hit:
  - Translating internal complexity into actionable operator experience.
  - Avoiding interface drift from underlying runtime semantics.

## Progression plan (staff-level trajectory while building this system)

## Phase 1 (Weeks 1-2): Foundations and baselines

- Goals:
  - Internalize current architecture boundaries.
  - Establish deterministic and validation baselines.
- Deliverables:
  - Run `make gate` cleanly and understand each check purpose.
  - Document at least 5 real failure modes observed during usage.
  - Add at least 2 targeted regression tests for existing weak spots.
- Staff-level signal:
  - You can explain why each validator/test exists and what incident it prevents.

## Phase 2 (Weeks 3-4): Strategy plus runtime hardening

- Goals:
  - Improve planning quality and make execution behavior safer.
- Deliverables:
  - Implement one planning quality improvement in `planning.py` or agent generation flow.
  - Add idempotency/retry-safe behavior for one orchestration command path.
  - Add tests proving no behavior regression on current fixtures.
- Staff-level signal:
  - You can defend strategy changes with deterministic evidence, not intuition.

## Phase 3 (Weeks 5-6): Reliability and contract resilience

- Goals:
  - Strengthen failure semantics and run metadata contracts.
- Deliverables:
  - Extend validator or error taxonomy for a real defect class.
  - Tighten run metadata validation and document reset/re-init rules.
  - Capture failure handling decisions in docs for future contributors.
- Staff-level signal:
  - You can evolve contracts while keeping failure modes explicit and recoverable.

## Phase 4 (Weeks 7-8): Operability and human control

- Goals:
  - Make system behavior diagnosable and operator-friendly.
- Deliverables:
  - Improve structured event coverage for critical stage transitions.
  - Add or refine one operator-facing UX flow (CLI/app) for clarity.
  - Define and track 3 operational metrics (for example: validation pass rate, retry rate, median command latency).
- Staff-level signal:
  - You can reconstruct failures quickly and propose concrete operational fixes.

## Ongoing weekly loop (repeat indefinitely)

1. Pick one field focus for the week (strategy, reliability, runtime, etc.).
2. Implement one meaningful change in that field.
3. Add or update tests and run `make gate`.
4. Write a short engineering note:
   - What changed.
   - What failed first.
   - How validation/evals caught it.
   - What you would redesign next.

This loop is what forces deep understanding: you repeatedly close the gap between capability, correctness, and operability on real code paths.
