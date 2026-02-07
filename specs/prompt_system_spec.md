# Prompt System Rework Spec

## Metadata

- Owner: Codex + user
- Started: 2026-02-07
- Status: Completed
- Scope: Prompt system + workflow coherence for general coding topics

## Problem Statement

The repository has good standalone prompts, but the full flow does not yet feel like a single cohesive system. Some constraints are implicit or duplicated, and usage steps are not centralized into one easy workflow.

## Goals

1. Make prompts operate as one coherent system (single source of truth + clear handoffs).
2. Make usage easy: one documented workflow from topic idea -> curriculum -> review -> repository.
3. Improve prompt reliability with explicit invariants and anti-drift rules.
4. Keep output quality high for practical coding learning (testable artifacts, transfer, retention).

## Non-Goals

- Building a full orchestration app.
- Rewriting UI logic.
- Introducing network-based dependencies.

## Definition of Done

- [x] A single workflow document exists that explains end-to-end usage with exact inputs/outputs.
- [x] `prompts/topic_spec.md` is explicit about invariants (uniqueness, required mappings, defaults).
- [x] `prompts/curriculum_generator.md` uses dynamic constraints (no topic-specific hardcoding) and enforces pattern coverage.
- [x] `prompts/repo_generator.md` supports coherent phased generation (plan -> skeleton -> full implementation) to improve reliability.
- [x] `prompts/curriculum_validator.md` requires evidence-backed findings with node references for WEAK/FAIL items.
- [x] Root docs reference the new workflow entry point.
- [x] `make test`, `make validate`, and `make gate` pass after changes.

## Work Plan / Notepad

| ID | Task | Status | Notes |
|---|---|---|---|
| W1 | Create unified workflow guide under `prompts/` | DONE | Added `prompts/workflow.md` as entry point |
| W2 | Strengthen `topic_spec` contract and invariants | DONE | Added strict invariants, defaults, and capstone/category rules |
| W3 | Refactor curriculum generator prompt for dynamic + enforceable output | DONE | Added preflight validation and `pattern_coverage_map` requirements |
| W4 | Refactor repo generator prompt into phased workflow | DONE | Added `plan`/`scaffold`/`full` modes with phase DoD |
| W5 | Tighten curriculum validator prompt scoring/evidence rules | DONE | Added severity model and mandatory evidence rules |
| W6 | Update README references and quickstart | DONE | Added prompt quickstart and prompt system docs |
| W7 | Run checks and record verification | DONE | `make test`, `make validate`, `make gate` all green |
| W8 | Add prompt-native structural validation stage | DONE | Added `prompts/structural_validator.md` and integrated into docs/workflow |

## Decisions Log

- 2026-02-07: Use `topic_spec.json` as the single input contract for all prompt stages.

## Open Questions

- None at the moment.

## Progress Log

- 2026-02-07: Spec file created. Starting W1.
- 2026-02-07: Completed W1 by adding `prompts/workflow.md`. Starting W2.
- 2026-02-07: Completed W2 and W3 with stricter topic contract and dynamic curriculum generator.
- 2026-02-07: Completed W4-W6 (phased repo generation, stricter validator, docs/quickstart updates). Starting W7 verification.
- 2026-02-07: Completed W7. Full verification passed (`make test`, `make validate`, `make gate`).
- 2026-02-07: Final re-check after cleanup also passed (`make gate`).
- 2026-02-07: Started W8 to make structural validation first-class in prompt workflow.
- 2026-02-07: Completed W8 with `prompts/structural_validator.md` and workflow wiring.
- 2026-02-07: Final system gate after W8 passed (`make gate`).
