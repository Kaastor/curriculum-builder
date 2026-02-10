# Agentic Mental Map

This is a living document used to build practical, transferable expertise in agentic engineering.

How to use this file:
- keep each section concise and explicit
- link every abstract concept to concrete code in this repo
- update after experiments, not only after reading

## 1) Control Loop

Purpose:
- 

Repo mapping:
- `learning_compiler/agent/optimizer.py`
- `learning_compiler/agent/generator.py`

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## 2) Planning

Purpose:
- 

Repo mapping:
- `learning_compiler/orchestration/planning.py`
- `learning_compiler/orchestration/pipeline.py`

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## 3) Tool Execution Substrate

Purpose:
- 

Repo mapping:
- `learning_compiler/agent/llm/client.py`
- `learning_compiler/agent/llm/codex.py`
- `learning_compiler/agent/llm/remote.py`

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## 4) State and Artifacts

Purpose:
- 

Repo mapping:
- `learning_compiler/orchestration/pipeline.py`
- `learning_compiler/orchestration/stage.py`
- `runs/<run_id>/...`

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## 5) Validation and Judge Authority

Purpose:
- 

Repo mapping:
- `learning_compiler/agent/quality/model.py`
- `learning_compiler/validator/core.py`
- `learning_compiler/validator/*`

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## 6) Repair and Self-Correction

Purpose:
- 

Repo mapping:
- `learning_compiler/agent/quality/planner.py`
- `learning_compiler/agent/quality/executor.py`
- `learning_compiler/agent/quality/actions.py`

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## 7) Reliability (Timeouts, Retries, Fallbacks)

Purpose:
- 

Repo mapping:
- `learning_compiler/agent/model_policy.py`
- `learning_compiler/agent/llm/client.py`
- `learning_compiler/agent/llm/remote.py`
- `learning_compiler/agent/llm/codex.py`

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## 8) Observability and Traceability

Purpose:
- 

Repo mapping:
- `learning_compiler/agent/quality/trace.py`
- `learning_compiler/orchestration/events.py`
- `runs/<run_id>/outputs/reviews/optimization_trace.json`

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## 9) Evaluation and Benchmarks

Purpose:
- 

Repo mapping:
- `tests/`
- `scripts/coverage_check.py`
- `scripts/gate.sh`

Benchmark set (to fill):
- 

Scoring rubric (to fill):
- scope coverage:
- prerequisite coherence:
- progression quality:
- actionability:
- run-to-run stability:

## 10) Cost and Latency Governance

Purpose:
- 

Repo mapping:
- `learning_compiler/agent/model_policy.py`
- provider config and environment variables

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## 11) Safety and Constraints

Purpose:
- 

Repo mapping:
- `learning_compiler/errors.py`
- `learning_compiler/validator/*`
- orchestration stage and artifact checks

Invariants:
- 

Failure modes:
- 

Tradeoffs:
- 

## Weekly Reflection Template

Week:

What I changed:
- 

What I expected:
- 

What actually happened:
- 

What principle I learned:
- 

What I will change next:
- 
