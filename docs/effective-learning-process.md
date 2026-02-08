# Effective Learning Process (Agentic Engineering)

## Main Goal

Become a **staff-level agentic engineering practitioner** who:
- understands the field end-to-end (strategy, runtime, reliability, evaluation, operations),
- knows the major patterns and when to use them,
- can design, implement, and harden agentic systems for real use cases with strong engineering quality.

## Purpose

Use this repo as a deliberate practice environment to learn agentic engineering at staff level:
- strategy + planning
- execution/runtime
- reliability + evaluation
- observability + operations

Main principle: **learn by changing the system and validating behavior**, not by passive reading.

## Learning Method

For every learning task, use this loop:

1. Pick one pattern.
2. Predict behavior before changes.
3. Make one small implementation change.
4. Add or update one focused test.
5. Run validation:
   - `make test`
   - `make gate`
6. Inspect artifacts (`curriculum.json`, `optimization_trace.json`, `validation_report.md`).
7. Write a short note: what changed, what failed, what you learned.

## Pattern-First Study Order

Study in this order so concepts connect naturally:

1. **System flow and state machine**
- Files: `learning_compiler/orchestration/*`, `scripts/orchestration.py`
- Goal: understand stages, freshness checks, run lifecycle.

2. **Generation loop**
- Files: `learning_compiler/agent/optimizer.py`, `proposer.py`, `pedagogy_critic.py`, `quality_model.py`, `repair_*`
- Goal: understand `propose -> critique -> judge -> repair`.

3. **Quality and validation gates**
- Files: `learning_compiler/validator/*`
- Goal: understand deterministic acceptance and failure boundaries.

4. **Resource and context relevance**
- Files: `learning_compiler/agent/research.py`, `learning_compiler/domain/models.py`
- Goal: understand contextual grounding and evidence quality.

5. **Reliability and operations**
- Files: `learning_compiler/errors.py`, `scripts/gate.sh`, run artifacts in `runs/<run_id>/outputs/reviews/`
- Goal: understand typed failures, traceability, and regression safety.

## Weekly Plan (4 Weeks)

### Week 1: Understand the pipeline
1. Run one full orchestration flow.
2. Trace each stage output and why it exists.
3. Document one failure mode per stage.

### Week 2: Improve DAG quality
1. Modify one quality rule (small change).
2. Add tests proving improvement.
3. Re-run and compare `optimization_trace.json`.

### Week 3: Improve reliability
1. Add one timeout/retry/failure-path improvement.
2. Add regression tests for failure handling.
3. Ensure `make gate` stays green.

### Week 4: Improve instructional quality
1. Improve one pedagogical signal (atomicity/coherence/actionability).
2. Add tests and compare before/after outputs.
3. Write a short quality assessment note.

## Practice Rules

1. Keep each PR/change small and reviewable.
2. Never skip tests for behavior changes.
3. Never accept “looks better” without measurable checks.
4. Keep determinism where required.
5. Always update docs when behavior changes.

## What “Good Learning” Looks Like

You are learning effectively when you can:

1. Explain why each module exists and what failure it prevents.
2. Predict impact of a rule change before running.
3. Add improvements without breaking gates.
4. Debug low-quality DAGs using artifacts, not guesswork.
5. Translate architecture decisions into explicit tradeoffs.

## Recommended Session Template

For each coding session:

1. Objective (one sentence).
2. Pattern being practiced.
3. Files touched.
4. Tests added/updated.
5. `make test` result.
6. `make gate` result.
7. Key learning (3 bullets max).
