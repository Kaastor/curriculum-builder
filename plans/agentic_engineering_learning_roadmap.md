# Agentic Engineering Learning Roadmap

## Goal

Build staff-level understanding of agentic engineering while using this repository as a practical lab.

Outcome target:
- You can explain each major agent pattern from first principles.
- You can map each pattern to concrete code paths in this repo.
- You can improve DAG generation quality using measurable evaluation, not intuition.

## Working Rule

For the next 4-6 weeks:
- limit feature work to small, testable changes
- prioritize understanding, tracing, and evaluation quality
- document all learnings in one living map

## Main Artifact You Will Maintain

Create and maintain:
- `docs/learning/agentic-mental-map.md`

Each section should contain:
- purpose
- failure modes
- tradeoffs
- pattern choices
- where this is implemented in this repo
- tests/evals that verify it

Core sections:
1. Control Loop
2. Planning
3. Tool Execution Substrate
4. State/Memory/Artifacts
5. Validation and Judge Authority
6. Repair/Self-correction
7. Reliability (timeouts/retries/fallbacks)
8. Observability and Traceability
9. Evaluation and Benchmarks
10. Cost/Latency Governance
11. Safety/Constraints

## Phase Plan

### Phase 1 (Week 1): System Comprehension Baseline

Goal:
- understand this system end-to-end without adding complexity

Actions:
1. Read in order:
   - `README.md`
   - `docs/architecture.md`
   - `docs/orchestration.md`
   - `docs/agent-runtime.md`
   - `docs/scope-ingestion.md`
   - `docs/adr/README.md` + ADRs
2. Run one full deterministic flow:
   - `AGENT_PROVIDER=internal python3.11 scripts/orchestration.py run <run_id> --scope-file <scope.md>`
3. Explain every artifact under `runs/<run_id>/` and why it exists.
4. Fill first version of `docs/learning/agentic-mental-map.md`.

Exit criteria:
- you can narrate `run -> generate -> validate -> plan -> iterate` from memory
- you can explain stage transitions and failure points

### Phase 2 (Week 2): Pattern-to-Code Mapping

Goal:
- internalize why each component exists and what problem it solves

Actions:
1. For each critical module, create a short component card (in the mental map):
   - Trigger
   - Inputs/Outputs
   - Invariants
   - Failure surface
   - Why needed
2. Cover at least:
   - `learning_compiler/orchestration/pipeline.py`
   - `learning_compiler/agent/optimizer.py`
   - `learning_compiler/agent/quality/model.py`
   - `learning_compiler/validator/core.py`
3. Link each card to at least one test file that validates behavior.

Exit criteria:
- you can answer “what breaks if we delete this component?”
- all major components have explicit rationale notes

### Phase 3 (Week 3): Evaluation Discipline

Goal:
- replace vibe judgment with objective quality measurement

Actions:
1. Build benchmark set (5-10 representative scope docs).
2. Define scoring rubric for generated DAG:
   - scope coverage
   - prerequisite coherence
   - progression quality
   - actionability of mastery checks
   - stability across reruns
3. Run baseline and capture scores in `docs/learning/benchmark-baseline.md`.

Exit criteria:
- every generation change can be compared to baseline
- you can detect regressions quickly

### Phase 4 (Week 4): Controlled Improvement Loop

Goal:
- improve DAG generation quality through hypothesis-driven iterations

Actions per iteration:
1. Write one hypothesis.
2. Apply one small change.
3. Run benchmark set + `make gate`.
4. Record result and keep/revert based on evidence.

Rules:
- no broad refactors during this phase unless blocking
- one variable changed per iteration

Exit criteria:
- measurable DAG quality improvement on benchmark set
- no gate regressions

### Phase 5 (Week 5+): Transfer Learning to New System

Goal:
- prove knowledge is generalizable beyond this repository

Actions:
1. Build a tiny new agentic mini-project using the same patterns.
2. Reuse your mental map sections as architecture template.
3. Compare design decisions and tradeoffs to this repo.

Exit criteria:
- you can design an agentic system without copying this codebase
- you can justify architecture choices with clear tradeoffs

## Daily/Weekly Cadence

Daily (60-90 min):
1. 20 min concept reading
2. 30 min code tracing
3. 20 min experiment
4. 10 min notes update

Weekly:
1. pick one focus pattern
2. run benchmark before/after
3. write one short architecture reflection in `docs/learning/`

## Decision Rule: Learn vs Build

Use this gate:
- If you cannot explain stage transitions, judge logic, and failure handling without reading code -> learn first.
- If you can explain them and have benchmark metrics -> proceed with focused improvements.

Current recommendation:
- prioritize learning + evaluation setup first, then optimize DAG generation.

## Success Criteria (Expert Trajectory)

You are on expert track when:
1. You predict failure modes before running code.
2. You describe tradeoffs between at least two agent-loop designs.
3. You improve DAG quality with benchmarked evidence.
4. You transfer same architecture patterns into a new project.
5. You can review another agent system and quickly locate structural weaknesses.

