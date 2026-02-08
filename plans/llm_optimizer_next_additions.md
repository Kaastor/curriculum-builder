# LLM Optimizer: Next Additions Backlog

Purpose:
- Track the high-value hardening items discussed after agreeing on the LLM-first DAG design.
- Implement these after core proposer/critic/judge/repair loop is running.

Related design:
- `docs/iterative-dag-curriculum-design.md`

## Priority A (reliability + contracts)

1. Typed interfaces and schemas across optimizer components.
- Add strict request/response models for:
  - proposer output
  - critic diagnostics
  - repair plan
  - repair executor output
- Add versioned rule IDs for quality checks.

2. Failure policy matrix.
- Define behavior for:
  - provider timeout
  - malformed JSON
  - partial repair failure
  - critic/judge disagreement
- For each: retry policy, fallback/fail mode, user-facing error message.

3. Model policy hardening.
- Centralize and enforce:
  - pinned model id
  - `temperature=0`
  - strict JSON schema
  - retry/timeout budgets
- Fail closed when schema validation fails.

## Priority B (evaluation quality)

1. Learner path coherence implementation.
- Add deterministic checks for:
  - hidden prerequisites
  - concept jump size
  - workload jump smoothness
  - backtracking/redundancy
- Add LLM novice-student simulation pass.
- Merge into `learner_path_coherence` score.

2. Candidate comparison for near-optimal path.
- When multiple repaired candidates exist, score all valid candidates.
- Keep best-scoring valid DAG.

3. Coherence acceptance thresholds.
- Add required threshold (default `>= 80`).
- Enforce hidden prerequisite violations = `0`.

## Priority C (ops/SLO visibility)

1. Reliability SLOs.
- Add measurable targets for:
  - success rate
  - max iteration count
  - p95 generation latency
  - malformed-output failure rate

2. Cost/runtime budgets.
- Add per-run token/time budget caps.
- Enforce hard stop with explicit error code when exceeded.

3. Optimization telemetry.
- Extend `optimization_trace.json` with:
  - latency per iteration
  - token usage per stage (if available)
  - stop reason categories

## Priority D (security + safety)

1. Input/path guardrails for context references.
- Strict allowlist for repo-local paths.
- Reject external/system paths in local resolver context.

2. Prompt-injection resilience for local artifact content.
- Sanitize/segment context and prevent instructions from embedded docs/code being treated as system policy.

3. Secrets/PII safety checks.
- Add pre-prompt filter for obvious secrets in included context snippets.

## Priority E (tests and gate)

1. Deterministic acceptance fixtures.
- Add golden acceptance tests against fixed inputs and fixed model policy.
- Assert stable pass/fail decision even when wording varies.

2. Fault-injection tests.
- Simulate timeout/malformed JSON/retry exhaustion paths.
- Assert typed errors and no corrupt artifacts.

3. Coherence regression tests.
- Verify repaired DAG improves coherence score over baseline draft.

4. Gate integration.
- Ensure new optimizer reliability/eval tests run under `make gate`.

## Suggested execution order

1. Priority A
2. Priority B
3. Priority E
4. Priority C
5. Priority D

Rationale:
- First make the loop safe and contract-stable.
- Then improve learning-path quality.
- Then lock quality with tests before adding more ops/security layers.
