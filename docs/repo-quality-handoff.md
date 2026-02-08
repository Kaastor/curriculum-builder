# Repo Quality Handoff (Failure Analysis + Next Approach)

## Implementation status (2026-02-08)

Implemented in code:

1. Added optional generic `context_pack` contract in topic spec model + validator.
2. Extended resolver request contract with node/context signals.
3. Added deterministic `RepoLocalResolver` and composite fallback resolver.
4. Upgraded node generation with stage-specific capability/core ideas/mastery tasks.
5. Replaced flat minute distribution with deterministic weighted estimate allocation.
6. Extended quality validator with actionability, repetition, and resource-relevance checks.
7. Added regression tests for context-pack validation, local resolver behavior, deterministic output, and mastery actionability checks.
8. Implemented iterative LLM-first optimizer architecture (`propose -> critique -> judge -> repair`) with deterministic acceptance.
9. Added optimization trace artifact emission: `outputs/reviews/optimization_trace.json`.
10. Added deterministic learner-path coherence check to validator quality stage.

Verification:

- `make test` passed.
- `make gate` passed.

## Why the generated curriculum quality was low

The system passed validation but produced low instructional quality because the current generator optimizes for deterministic structure, not deep domain specificity.

Root causes:

1. Template-heavy node content:
- `learning_compiler/agent/node_builder.py` generates repetitive capability/core-ideas/mastery text from fixed templates.

2. Index-based graph construction:
- Prerequisites are generated from node index rules, not semantic dependency reasoning.

3. Generic resource selection:
- `learning_compiler/agent/research.py` uses a small keyword router and often falls back to generic sources.

4. Flat effort modeling:
- Minutes are distributed almost uniformly in `learning_compiler/agent/spec.py`.

5. Validator quality bar is mostly structural:
- Current validators enforce schema/graph/evidence minimums, but do not enforce strong domain relevance or actionable implementation tasks.

## Product direction (required)

The system must remain **generic**, but support high-quality **domain-specific** output when context is provided (for this repo or any other domain).

No migration layer should be added. Keep the fresh-run PoC policy:
- strict contracts
- no backward-compat migrations
- regenerate runs when contracts evolve

## End goal

Build a generic generator with pluggable context/resolvers and stronger quality checks so that:

1. Generic topic with no context still works.
2. Domain context pack (like this repo) yields concrete, implementation-driven curriculum.
3. Output remains deterministic and passes `make gate`.
4. Quality is measurably better: specific resources, non-template mastery tasks, and non-flat estimates.

## New approach (target architecture)

### 1) Context Pack (optional, generic interface)

Add a structured optional context input (for any domain), e.g.:
- local docs/modules to prioritize
- preferred source types
- required skill outcomes

If no context pack is provided, use current generic behavior.

### 2) Pluggable Resource Resolvers

Keep current deterministic resolver as default.

Add optional resolvers:
- `RepoLocalResolver`: pulls from local repo docs/code landmarks
- future external resolver(s) for non-local domains

Resolver selection should be config-driven, not hardcoded for this repo.

### 3) Instructional Quality Upgrades in Generator

Improve node generation so it includes:
- concrete implementation outcomes (change/test/validate artifacts)
- less repetitive text patterns
- estimate granularity based on task complexity and dependency depth

### 4) Validator extensions (quality, not only structure)

Add optional checks for:
- resource relevance to topic/context
- mastery checks requiring actionable outputs
- anti-template repetition thresholds
- suspiciously flat estimate distributions

## Immediate implementation plan (next session)

1. Add context-pack model + loader (domain-agnostic contract).
2. Extend resolver contract to accept context signals.
3. Implement `RepoLocalResolver` using local file references (README, AGENTS, key modules, tests).
4. Update generator/node builder to produce implementation-first mastery checks.
5. Add richer estimate model (depth/complexity-aware, deterministic).
6. Add validator rules for relevance/actionability/repetition.
7. Add regression tests for new behavior.
8. Update docs (`README.md`, this file, and agentic map) after code changes.
9. Run `make gate`.

## Acceptance criteria

- For a repo-focused topic spec, generated resources include repo-relevant sources.
- Mastery checks include concrete outputs (e.g., code change + test + gate run).
- Estimates are not uniformly flat for multi-node curricula.
- Determinism tests still pass.
- `make gate` passes.

## Session restart instructions

If starting from a fresh context:

1. Read:
- `AGENTS.md`
- `docs/agentic-engineering-map.md`
- `docs/repo-quality-handoff.md` (this file)

2. Continue from “Immediate implementation plan”.

3. Maintain constraints:
- no migrations
- no destructive git operations
- keep changes generic and plugin-based
- update docs at the end
