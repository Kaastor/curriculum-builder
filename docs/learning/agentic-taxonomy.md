# Agentic Engineering — Practical Taxonomy for Becoming Expert-Level

This is a **coverage-first** map of the field, written for someone who wants to build agentic systems that survive contact with reality: messy data, flaky tools, impatient users, security reviews, and 3am incidents.

For pass/fail graduation criteria for production readiness, use:
- `docs/learning/agentic-readiness-standard.md`
For system-level integration model, contracts, and the canonical 30/60/90 execution plan, use:
- `docs/learning/agentic-system.md`
For staff-level judgment, decision quality, and anti-pattern playbooks, use:
- `docs/learning/agentic-manifesto.md`

## Context assumptions (since placeholders weren’t filled)

* **Learner level assumed:** **Intermediate** (I include beginner on-ramps and advanced deepening paths per topic)
* **Target domains covered:** **General + coding agents + enterprise automation + research agents**
* **Stack assumptions:** **Stack-agnostic**, but examples implicitly fit common stacks (Python/TypeScript, REST/GraphQL, queues, databases, vector stores, CI/CD, containerized deployments)
* **Constraints:** None specified → I optimize for **completeness** and **production relevance**, not minimal time

## Multi-pass build note (as requested)

* **Pass A (top-down):** Foundations → Architecture → Implementation → Operations
* **Pass B (bottom-up):** Failure modes + incident/debugging realities embedded in *every leaf*, plus a dedicated ops leaf for failure playbooks
* **Pass D (gap scan):** Added missing-but-common production topics (governance, data retention, change management, regression control, supply-chain risk, “unknown unknown” frontier list) and flagged confidence where appropriate

---

# A) Taxonomy Tree (depth ≤ 4)

**Legend:** each node shows **Name — one-line scope — Confidence**.
Leaves are marked **[Leaf]** and have full playbooks in section B.

## T1 Foundations — the physics of agentic systems — **High**

### T1.1 Conceptual foundations — how to think about agents — **High**

* **T1.1.1 Autonomy & agent mental models** — define “agent”, autonomy spectrum, and control loops — **High** **[Leaf]**
* **T1.1.2 LLM behavior & limitations** — stochastic generation, context limits, instruction hierarchy — **High** **[Leaf]**

### T1.2 Engineering foundations — baseline skills agents require — **High**

* **T1.2.1 Tool/API contracts & structured I/O** — schemas, types, tool calling, determinism surfaces — **High** **[Leaf]**
* **T1.2.2 Retrieval & knowledge basics** — embeddings/RAG basics, grounding, provenance — **High** **[Leaf]**
* **T1.2.3 Reliability & distributed systems basics** — timeouts, retries, idempotency, queues — **High** **[Leaf]**

### T1.3 Human & risk foundations — people, harm, and responsibility — **High**

* **T1.3.1 Human-in-the-loop & UX basics** — approvals, review loops, trust calibration — **High** **[Leaf]**
* **T1.3.2 Security & threat modeling basics** — prompt injection, tool abuse, least privilege — **High** **[Leaf]**
* **T1.3.3 Privacy, ethics, and compliance primer** — PII, retention, audit, fairness, accountability — **Med** **[Leaf]**

---

## T2 Architecture & Design — designing an agent that can ship — **High**

### T2.1 Product & requirements — choosing the right problems — **High**

* **T2.1.1 Use-case framing & automation boundary** — where autonomy ends, humans begin — **High** **[Leaf]**
* **T2.1.2 Metrics, SLOs & acceptance criteria** — define success, failure, and “good enough” — **High** **[Leaf]**
* **T2.1.3 Unfamiliar-domain onboarding protocol** — structured discovery and risk mapping for domains you have not worked in before — **High** **[Leaf]**

### T2.2 Core agent architecture — the internal organs — **High**

* **T2.2.1 Agent patterns & orchestration** — ReAct, planners, workflows, state machines — **High** **[Leaf]**
* **T2.2.2 Planning & decision design** — decomposition, constraints, heuristics, routing — **High** **[Leaf]**
* **T2.2.3 Tool & environment architecture** — tool layer, permissions, sandboxes, environment models — **High** **[Leaf]**
* **T2.2.4 Control-loop engineering & runtime contracts** — explicit loop state, stop policies, replan triggers, and enforcement checkpoints — **High** **[Leaf]**

### T2.3 Knowledge & memory architecture — state across time — **High**

* **T2.3.1 Memory & state architecture** — session/run/task state, persistence strategy — **High** **[Leaf]**
* **T2.3.2 Knowledge architecture** — RAG vs KB vs KG, freshness, provenance — **High** **[Leaf]**
* **T2.3.3 Data governance architecture** — access control, retention, lineage, redaction — **Med** **[Leaf]**

### T2.4 Safety, validation & collaboration architecture — staying sane — **High**

* **T2.4.1 Validation & repair architecture** — validators, judges, fallbacks, escalations — **High** **[Leaf]**
* **T2.4.2 Safety architecture** — guardrails, policy enforcement, sandboxing strategy — **High** **[Leaf]**
* **T2.4.3 Multi-agent & human collaboration architecture** — roles, protocols, approvals, coordination — **Med** **[Leaf]**
* **T2.4.4 Trust boundary & assumption-ledger architecture** — explicit trusted/untrusted components and enforceable assumptions — **High** **[Leaf]**
* **T2.4.5 Execution governance boundary architecture** — policy decision + enforcement mediation for side effects — **High** **[Leaf]**
* **T2.4.6 Formal assurance & critical-path verification** — model critical invariants, verify high-risk flows, and produce assurance evidence — **High** **[Leaf]**

### T2.5 Quality & visibility architecture — seeing and measuring — **High**

* **T2.5.1 Observability & evaluation architecture** — traces, audit logs, eval loops, feedback — **High** **[Leaf]**

---

## T3 Implementation & Integration — building the thing that actually runs — **High**

### T3.1 Reasoning & prompting implementation — getting useful cognition — **High**

* **T3.1.1 Prompt/instruction engineering & context management** — prompts, context packing, prompt hygiene — **High** **[Leaf]**
* **T3.1.2 Planning, reflection & repair loops in code** — replan/reflect/terminate logic — **High** **[Leaf]**

### T3.2 Tooling implementation — actions that touch the world — **High**

* **T3.2.1 Structured outputs, tool calling & schema enforcement** — JSON schemas, parsers, constrained decoding — **High** **[Leaf]**
* **T3.2.2 Tool adapters & side-effect-safe execution** — idempotency, retries, transactional patterns — **High** **[Leaf]**
* **T3.2.3 Sandboxing & permissioning implementation** — OS/code/browser sandboxes, secrets, scopes — **High** **[Leaf]**
* **T3.2.4 Enterprise integrations & automation** — SaaS connectors, RPA, queues, approval gates — **Med** **[Leaf]**
* **T3.2.5 Effect typing & commitment semantics implementation** — classify action impact and bind policy/approval/idempotency to effect class — **High** **[Leaf]**

### T3.3 Memory & knowledge implementation — storage that doesn’t rot — **High**

* **T3.3.1 State persistence & run bookkeeping** — event sourcing, checkpoints, reproducibility — **High** **[Leaf]**
* **T3.3.2 Retrieval & RAG implementation** — chunking, embeddings, reranking, grounding quality — **High** **[Leaf]**
* **T3.3.3 Memory writing & consolidation** — summarization, forgetting, corrections, conflict handling — **Med** **[Leaf]**

### T3.4 Quality engineering implementation — proving it works — **High**

* **T3.4.1 Validation & judging implementation** — tests/rules + LLM judges + calibration — **High** **[Leaf]**
* **T3.4.2 Evaluation harness & CI** — datasets, simulations, regression gates — **High** **[Leaf]**
* **T3.4.3 Online evaluation & experimentation** — A/B tests, bandits, human feedback — **Med** **[Leaf]**
* **T3.4.4 Conformance reporting & scorecards** — executable evidence for hard invariants + utility tradeoffs — **High** **[Leaf]**
* **T3.4.5 Evaluation protocol rigor (causal + comparable)** — paired-seed comparisons, ablations, metamorphic checks — **High** **[Leaf]**

### T3.5 Scale & cost implementation — performance without bankruptcy — **High**

* **T3.5.1 Multi-agent runtime implementation** — messaging, shared memory, coordination runtime — **Med** **[Leaf]**
* **T3.5.2 Performance & cost optimization** — caching, batching, routing, token budgets — **High** **[Leaf]**

---

## T4 Operations, Governance & Maturity — running agents in production — **High**

### T4.1 Running agents reliably — infra + release + incident muscle — **High**

* **T4.1.1 Deployment, scaling & infrastructure operations** — environments, queues, rate limits, secrets — **High** **[Leaf]**
* **T4.1.2 Versioning, release management & rollback** — model/prompt/tool versions, canaries, rollback — **High** **[Leaf]**
* **T4.1.3 Production observability & SLO management** — dashboards, alerts, audits, error budgets — **High** **[Leaf]**
* **T4.1.4 Incident response, debugging & failure-mode playbooks** — common incidents + triage patterns — **High** **[Leaf]**
* **T4.1.5 Safe degradation profiles & bounded autonomy operations** — deterministic behavior tightening under uncertainty/failure — **High** **[Leaf]**
* **T4.1.6 Disaster recovery & continuity engineering** — RTO/RPO targets, failover strategy, restore drills, and resilience under regional/provider failures — **High** **[Leaf]**

### T4.2 Risk & compliance in production — staying allowed to exist — **High**

* **T4.2.1 Security, privacy & compliance operations** — red teaming, audits, retention, legal/IP/vendor — **Med** **[Leaf]**
* **T4.2.2 Supply-chain and dependency governance** — provider, model, prompt, and package risk controls with provenance and update discipline — **High** **[Leaf]**

### T4.3 People & org systems — adoption is a systems problem — **High**

* **T4.3.1 Org/process: AgentOps/LLMOps operating model & adoption** — roles, change mgmt, training, ROI — **High** **[Leaf]**

### T4.4 Frontier topics — unknown unknown magnets — **Med**

* **T4.4.1 Emerging & unknown-unknown candidates** — frontier patterns + “often missed” risks — **Low** **[Leaf]**

---

# B) Leaf Playbooks (every leaf includes required fields)

Below, each leaf includes:

* **Definition**
* **Why it matters in real systems**
* **Typical failure modes**
* **Key design decisions/tradeoffs**
* **Observable metrics/signals**
* **Required prerequisites**
* **Artifacts to produce**
* **Hands-on exercises** (1 beginner, 1 advanced)

---

## T1.1.1 Autonomy & agent mental models — **High**

* **Definition:** A practical model of an “agent” as a **control loop** (sense → think → act → observe → update) with **bounded autonomy** and explicit termination/hand-off conditions.
* **Why it matters:** Most production failures come from fuzzy boundaries: agents acting when they shouldn’t, or failing to act when they must.
* **Typical failure modes:**

  * “Agent” is really a workflow, but treated like adaptive reasoning → unpredictable behavior.
  * No explicit termination condition → infinite loops / runaway costs.
  * Hidden autonomy (agent silently does impactful actions).
* **Key design decisions/tradeoffs:**

  * Autonomy level: **suggestion-only** vs **auto-execute** vs **auto-execute with approvals**.
  * Loop shape: single loop vs hierarchical (manager/worker) vs state machine.
  * “Definition of done”: strict validators vs “good enough” heuristics.
* **Observable metrics/signals:**

  * Average steps per task; loop iterations; termination reasons.
  * Action rate (tools invoked per task), and % requiring human override.
  * Cost per successful completion; abandonment rate.
* **Required prerequisites:** Basic programming; understanding of APIs/tools (see **T1.2.1**).
* **Artifacts to produce:**

  * Agent “autonomy contract” doc (what it can/can’t do).
  * State diagram of control loop and termination conditions.
  * Risk register for action classes (read/write/delete/external).
* **Hands-on exercises:**

  * *Beginner:* Implement a toy agent loop with a max-step limit and explicit “done” criteria; log every step and termination reason.
  * *Advanced:* Design a 3-level autonomy policy (suggest / approve / auto) for an enterprise workflow (e.g., email + ticketing) and simulate 50 scenarios to validate boundaries.

---

## T1.1.2 LLM behavior & limitations — **High**

* **Definition:** Understanding LLMs as **probabilistic sequence predictors** shaped by context, prompts, tool outputs, and sampling parameters (temperature/top-p), with hard constraints like context window and non-determinism.
* **Why it matters:** You can’t engineer reliability without respecting how models actually fail: hallucinations, instruction drift, sensitivity to phrasing, and brittle long-context behavior.
* **Typical failure modes:**

  * “Confident nonsense” due to missing grounding.
  * Instruction conflicts (system vs developer vs user) → policy bypass.
  * Context overflow → truncated crucial constraints.
  * Randomness causes flaky behavior across runs.
* **Key design decisions/tradeoffs:**

  * Temperature low (stability) vs high (creativity/exploration).
  * Long context stuffing vs retrieval-based grounding (see **T1.2.2**, **T3.3.2**).
  * Single-call “genius prompt” vs iterative plan-act-validate loops.
* **Observable metrics/signals:**

  * Output variance across seeds/runs.
  * Policy violation rate; hallucination rate (measured via validators).
  * Context usage (% of window used; truncation events).
* **Required prerequisites:** None beyond basic LLM usage; pairs well with **T3.1.1**.
* **Artifacts to produce:**

  * “Model behavior notes” doc: what this model tends to mess up.
  * Prompt conflict matrix (system/dev/user constraints).
  * Reproducibility plan (seeds, logs, snapshotting).
* **Hands-on exercises:**

  * *Beginner:* Run the same prompt 30 times at two temperatures; measure variance and identify failure clusters.
  * *Advanced:* Build a “prompt diff test” harness: change one line in the system prompt and quantify regressions on a fixed eval set.

---

## T1.2.1 Tool/API contracts & structured I/O — **High**

* **Definition:** Designing tools as **contracts**: typed inputs, typed outputs, clear error semantics, and safe defaults—so the agent’s “thinking” can reliably translate into “doing”.
* **Why it matters:** Tools are where agents meet reality. Contract ambiguity turns into brittle prompts, silent corruption, or accidental destructive actions.
* **Typical failure modes:**

  * Underspecified tool inputs → agent guesses fields incorrectly.
  * Tool returns unstructured blobs → agent mis-parses and acts wrongly.
  * Error handling missing → agent loops on the same failing call.
* **Key design decisions/tradeoffs:**

  * Strict schemas (reliable) vs flexible inputs (convenient but risky).
  * Fail-fast vs fail-soft (fallback behaviors).
  * Tool granularity: many small tools vs fewer powerful tools (blast radius).
* **Observable metrics/signals:**

  * Tool call success rate; retry rate; parse error rate.
  * Schema validation failures (inputs/outputs).
  * Time spent per tool call; p95 tool latency.
* **Required prerequisites:** Basic API design; JSON; strongly recommended **T1.2.3**.
* **Artifacts to produce:**

  * Tool spec: schema, examples, error codes, idempotency notes.
  * Contract tests for tool adapters.
  * “Blast radius” classification per tool (read/write/delete/external).
* **Hands-on exercises:**

  * *Beginner:* Define 3 tools with JSON schemas and write a validator that rejects invalid calls.
  * *Advanced:* Implement a tool adapter that normalizes errors into a stable taxonomy and supports safe retries + idempotency keys.

---

## T1.2.2 Retrieval & knowledge basics — **High**

* **Definition:** Methods for grounding outputs in external knowledge: embeddings, vector search, keyword search, reranking, citations, and provenance-aware retrieval (often called **RAG**: Retrieval-Augmented Generation).
* **Why it matters:** Without retrieval, agents hallucinate. With sloppy retrieval, agents hallucinate *with confidence and footnotes*.
* **Typical failure modes:**

  * Garbage retrieval (wrong chunks) → confidently wrong answers.
  * Stale knowledge (outdated docs) → incorrect actions.
  * Over-retrieval (too much) → context dilution.
* **Key design decisions/tradeoffs:**

  * Vector vs hybrid search (keyword + vector).
  * Chunk size and overlap vs recall/precision.
  * Reranking models vs latency/cost.
* **Observable metrics/signals:**

  * Retrieval precision/recall proxies (human labels, heuristics).
  * “Answer supported by retrieved sources” rate.
  * Retrieval latency, hit rate, and context token share.
* **Required prerequisites:** Basic data handling; ties to **T3.3.2** for implementation.
* **Artifacts to produce:**

  * Knowledge source registry (owners, freshness SLA).
  * Chunking/embedding config docs.
  * Retrieval eval set with labeled “good sources”.
* **Hands-on exercises:**

  * *Beginner:* Build a mini RAG over 50 documents; test 20 queries; measure “correct source retrieved?” manually.
  * *Advanced:* Implement hybrid retrieval + reranking and show measurable improvement on a labeled retrieval benchmark.

---

## T1.2.3 Reliability & distributed systems basics — **High**

* **Definition:** The reliability toolbox needed because agent systems are **distributed systems**: retries, timeouts, backoff, circuit breakers, queues, idempotency, rate limiting, and consistency models.
* **Why it matters:** Agents amplify tool flakiness. A 1% tool failure becomes a 20% task failure across multi-step plans unless engineered.
* **Typical failure modes:**

  * Retry storms; cascading failures.
  * Partial actions (tool succeeded but response lost) → duplicates.
  * Unbounded concurrency → rate limit lockouts.
* **Key design decisions/tradeoffs:**

  * At-least-once vs exactly-once semantics (usually you fake exactly-once with idempotency).
  * Sync vs async execution; queue-based decoupling.
  * Consistency vs latency vs availability (classic distributed tradeoffs).
* **Observable metrics/signals:**

  * Error budgets; p95/p99 latencies; queue depth.
  * Retry counts; circuit breaker trips.
  * Duplicate action detection rate.
* **Required prerequisites:** Basic backend engineering; pairs with **T3.2.2** and **T4.1.1**.
* **Artifacts to produce:**

  * Reliability design doc (timeouts, retries, idempotency strategy).
  * Runbook for upstream outages and rate limiting.
  * Load test reports.
* **Hands-on exercises:**

  * *Beginner:* Wrap a flaky API with retries + exponential backoff + timeout; show improved success rate.
  * *Advanced:* Design an idempotent “create ticket” tool with idempotency keys and simulate packet loss + retries.

---

## T1.3.1 Human-in-the-loop & UX basics — **High**

* **Definition:** Designing human involvement as a first-class system component: approvals, review, overrides, explanations, and clear responsibility boundaries.
* **Why it matters:** Real autonomy is a liability without UX that makes human oversight easy, fast, and correct.
* **Typical failure modes:**

  * Approval fatigue (humans click through) → safety theater.
  * Overconfidence UX (agent sounds certain) → misplaced trust.
  * Poor interruptibility (no “stop the agent now”) → runaway actions.
* **Key design decisions/tradeoffs:**

  * When to ask humans: before action, after draft, on uncertainty spikes.
  * Explanations: short vs detailed; include evidence and action previews.
  * Defaults: “safe by default” vs “fast by default”.
* **Observable metrics/signals:**

  * Approval time; override rate; user-reported trust.
  * Escalation frequency; “I didn’t mean to do that” incidents.
  * Task completion with vs without human intervention.
* **Required prerequisites:** Product thinking; connects to **T2.4.3** and **T2.1.1**.
* **Artifacts to produce:**

  * Human decision points map (what, when, who).
  * UX copy guidelines for uncertainty and citations.
  * Training/FAQ for reviewers.
* **Hands-on exercises:**

  * *Beginner:* Add an approval step before any “write” tool call; show the action preview.
  * *Advanced:* Implement an uncertainty-triggered escalation: auto-run low-risk steps, request approval for high-risk actions based on tool classification.

---

## T1.3.2 Security & threat modeling basics — **High**

* **Definition:** Systematic identification of how agents can be exploited: prompt injection, data exfiltration, tool misuse, privilege escalation, and supply-chain risks.
* **Why it matters:** Agents are attractive targets: they can read lots of data and take actions. Attackers love that combo.
* **Typical failure modes:**

  * Prompt injection via retrieved docs → “Ignore previous instructions”.
  * Tool injection (malicious tool outputs) → agent executes harmful steps.
  * Over-broad tool permissions → catastrophic blast radius.
* **Key design decisions/tradeoffs:**

  * Least privilege vs convenience (spoiler: least privilege wins).
  * Static allowlists vs dynamic policy engines.
  * Isolation strategy: per-user, per-task, per-tenant sandboxes.
* **Observable metrics/signals:**

  * Policy violation attempts; blocked tool calls.
  * Secrets access events; unusual retrieval patterns.
  * Red-team findings and time-to-fix.
* **Required prerequisites:** Basic security concepts; pairs with **T2.4.2**, **T3.2.3**.
* **Artifacts to produce:**

  * Threat model (assets, attackers, entry points, mitigations).
  * Tool permission matrix + justification.
  * Security test cases for prompt injection.
* **Hands-on exercises:**

  * *Beginner:* Create a list of 10 prompt injection strings and test your agent’s resistance.
  * *Advanced:* Implement a policy layer that blocks tool calls based on user role, tool risk class, and content signals (e.g., requests for secrets).

---

## T1.3.3 Privacy, ethics, and compliance primer — **Med**

* **Definition:** Handling user/company data responsibly (PII, sensitive data, retention), respecting legal/compliance constraints, and designing accountability for agent actions.
* **Why it matters:** Production agents inevitably touch sensitive data. Compliance failures can kill the entire program.
* **Typical failure modes:**

  * Logging PII in prompts/traces.
  * Training data leakage via vendor tools.
  * Retention policy mismatch (data kept “forever” by accident).
* **Key design decisions/tradeoffs:**

  * Minimize data sent to models vs functionality.
  * On-prem / VPC deployments vs managed services.
  * Redaction and pseudonymization strategy.
* **Observable metrics/signals:**

  * PII detection hits in logs; redaction coverage.
  * Data retention compliance checks pass rate.
  * Audit requests turnaround time.
* **Required prerequisites:** Basic data handling + security awareness; see **T2.3.3**.
* **Artifacts to produce:**

  * Data classification policy for prompts, memory, logs.
  * Retention schedule + deletion procedures.
  * DPIA-style assessment (if applicable) / privacy review checklist.
* **Hands-on exercises:**

  * *Beginner:* Add PII redaction to logs and verify with test cases.
  * *Advanced:* Implement “selective disclosure”: agent uses sensitive fields internally but outputs only masked versions, with audit traces.

---

## T2.1.1 Use-case framing & automation boundary — **High**

* **Definition:** Turning “we want an agent” into a crisp use case: inputs, outputs, constraints, risks, and where automation must stop (handoff points).
* **Why it matters:** The fastest way to fail is picking tasks that are too ambiguous, too high-risk, or too integration-heavy for your maturity level.
* **Typical failure modes:**

  * Wrong problem: automation of judgment-heavy tasks without clear criteria.
  * Hidden integration complexity (permissions, data access).
  * Misaligned stakeholder expectations (agent as magic).
* **Key design decisions/tradeoffs:**

  * Start with narrow, high-volume, low-risk tasks.
  * “Assist” vs “automate”: drafts vs execution.
  * Boundary decisions: what requires human approval.
* **Observable metrics/signals:**

  * Task eligibility rate (how often agent can proceed).
  * Human intervention rate and reasons.
  * Business value metrics (cycle time reduction, cost savings).
* **Required prerequisites:** None; ties to **T1.1.1** and **T1.3.1**.
* **Artifacts to produce:**

  * Use-case one-pager with autonomy boundaries.
  * RACI (who is responsible for what decisions).
  * Risk/impact assessment per action type.
* **Hands-on exercises:**

  * *Beginner:* Write 3 use-case one-pagers and explicitly define “stop conditions” for each.
  * *Advanced:* Convert one use case into a full “automation boundary spec” including tool permissions and escalation policy.

---

## T2.1.2 Metrics, SLOs & acceptance criteria — **High**

* **Definition:** Defining measurable success: task-level quality, safety, latency, cost, and reliability. **SLO** = Service Level Objective (a reliability target).
* **Why it matters:** Without metrics, you can’t improve, can’t ship safely, and can’t stop regressions.
* **Typical failure modes:**

  * “It feels better” shipping without evals → silent regressions.
  * Single metric obsession (accuracy) ignores safety/cost/latency.
  * Metric gaming (agent optimizes proxy).
* **Key design decisions/tradeoffs:**

  * Choose a balanced scorecard: quality + safety + cost + latency.
  * Hard gates vs soft monitoring.
  * “Gold” human labels vs cheaper automated evaluation.
* **Observable metrics/signals:**

  * Task success rate; defect rate; escalation rate.
  * p95 latency; cost per task; tool call counts.
  * Safety incidents; policy violation attempts.
* **Required prerequisites:** Basic measurement literacy; connects to **T2.5.1**, **T3.4.2**, **T4.1.3**.
* **Artifacts to produce:**

  * Metric spec (definitions, data sources, dashboards).
  * Acceptance test suite + thresholds.
  * Error budget policy tied to release gating.
* **Hands-on exercises:**

  * *Beginner:* Define 10 metrics for an agent and instrument at least 5.
  * *Advanced:* Create a release gate that blocks deployment if eval quality drops >X or safety violations rise >Y.

---

## T2.1.3 Unfamiliar-domain onboarding protocol — **High**

* **Definition:** A repeatable protocol for entering an unfamiliar domain: extracting constraints, mapping risks, discovering source-of-truth systems, and setting bounded delivery scope before implementation.
* **Why it matters:** Most failures in unfamiliar domains come from wrong assumptions early, not from coding mistakes later.
* **Typical failure modes:**

  * Building with generic patterns that violate domain-specific constraints.
  * Missing hard regulatory or safety requirements until late integration.
  * Confusing stakeholder language and shipping the wrong capability.
* **Key design decisions/tradeoffs:**

  * Discovery depth vs delivery speed in first sprint.
  * Broad interviews vs targeted risk-first discovery.
  * Conservative boundary (assist mode) vs early automation.
* **Observable metrics/signals:**

  * Time to first validated domain constraint map.
  * Number of late-stage requirement surprises.
  * Rework ratio caused by misunderstood domain assumptions.
* **Required prerequisites:** **T2.1.1**, **T2.1.2**, **T2.4.4**.
* **Artifacts to produce:**

  * Domain onboarding brief (glossary, constraints, critical workflows, risk register).
  * Source-of-truth inventory with owners and freshness expectations.
  * First-48h unknowns list with validation plan.
* **Hands-on exercises:**

  * *Beginner:* Pick an unfamiliar domain and produce a one-page onboarding brief with top 10 constraints.
  * *Advanced:* Run a 5-day delivery spike in an unfamiliar domain, logging assumption changes and quantifying rework from corrected assumptions.

---

## T2.2.1 Agent patterns & orchestration — **High**

* **Definition:** High-level control designs: single-loop agents (ReAct), plan-then-execute, hierarchical agents (manager/workers), and workflow/state-machine orchestrations.
* **Why it matters:** Orchestration is your “operating system.” It determines debuggability, reliability, and blast radius.
* **Typical failure modes:**

  * Free-form loop without structure → unreproducible failures.
  * Too rigid workflow → brittle to edge cases and ambiguity.
  * Hidden state transitions → impossible debugging.
* **Key design decisions/tradeoffs:**

  * Graph/state machine (predictable) vs free-form reasoning (flexible).
  * Central orchestrator vs decentralized agent autonomy.
  * Step granularity: coarse steps reduce overhead but hide failures.
* **Observable metrics/signals:**

  * Transition frequencies; unexpected state transitions.
  * Step failure rate by node; mean steps to completion.
  * Debug time per incident.
* **Required prerequisites:** **T1.1.1**, **T1.2.3**.
* **Artifacts to produce:**

  * Orchestration diagram (nodes, transitions, invariants).
  * Termination and retry strategy per node.
  * “What can go wrong” table per state.
* **Hands-on exercises:**

  * *Beginner:* Implement a 5-state agent workflow (intake → plan → act → verify → finalize).
  * *Advanced:* Build a hierarchical agent where a “manager” delegates to specialized workers and uses verification before merging outputs.

---

## T2.2.2 Planning & decision design — **High**

* **Definition:** Designing how an agent chooses actions: decomposition, prioritization, constraints, risk-aware routing, and when to ask for help.
* **Why it matters:** Planning quality largely determines tool efficiency, safety, and success on multi-step tasks.
* **Typical failure modes:**

  * Shallow plans → thrashing between tools.
  * Overplanning → expensive token burn with no action.
  * Ignoring constraints (time, permissions, safety).
* **Key design decisions/tradeoffs:**

  * Greedy vs search-based planning (Tree-of-Thought-style search).
  * Single-shot plan vs replanning after each observation.
  * Risk-aware routing: different models/tools per risk class.
* **Observable metrics/signals:**

  * Plan-to-execution ratio (planning tokens vs action tokens).
  * Replan count; tool thrash rate.
  * Constraint violation attempts.
* **Required prerequisites:** **T1.1.2**, **T2.2.1**.
* **Artifacts to produce:**

  * Planning policy doc (when to plan, depth limits).
  * Constraint list (hard vs soft).
  * Decision logs (why tool X was chosen).
* **Hands-on exercises:**

  * *Beginner:* Add a “plan” step that enumerates tasks and selects tools.
  * *Advanced:* Implement risk-aware model routing: lightweight model for drafting, stronger model for verification/high-risk decisions.

---

## T2.2.3 Tool & environment architecture — **High**

* **Definition:** Designing the tool layer and the environment the agent operates in: adapters, permission boundaries, sandboxes, and “world state” representations (what’s true right now).
* **Why it matters:** Tool architecture determines **blast radius**, **auditability**, and integration friction.
* **Typical failure modes:**

  * Tool sprawl without governance → inconsistent behavior and security gaps.
  * No environment model → agent repeats actions or misinterprets results.
  * Unclear side effects → hard-to-debug partial failures.
* **Key design decisions/tradeoffs:**

  * Thin wrapper vs thick adapter (where logic lives).
  * Central policy enforcement vs per-tool checks.
  * Read-only tools separated from write tools (recommended).
* **Observable metrics/signals:**

  * Tool coverage (how many tasks require manual workarounds).
  * Permission-denied rates; policy block rates.
  * Side-effect incidents (duplicates, unintended edits).
* **Required prerequisites:** **T1.2.1**, **T1.3.2**.
* **Artifacts to produce:**

  * Tool catalog + risk classification.
  * Permission matrix and sandbox architecture.
  * Environment state schema (what is stored as truth).
* **Hands-on exercises:**

  * *Beginner:* Design a tool catalog with read/write separation and explicit permissions.
  * *Advanced:* Implement a “world state” store that records tool effects and prevents duplicate actions via state checks.

---

## T2.2.4 Control-loop engineering & runtime contracts — **High**

* **Definition:** Engineering the control loop as a contract-driven runtime subsystem: explicit state machine, loop budgets, stop/escape conditions, replan rules, and policy checkpoints before side effects.
* **Why it matters:** Control loops are the execution spine. If loop semantics are implicit, reliability and safety degrade under complexity.
* **Typical failure modes:**

  * Loop logic spread across modules without a canonical state model.
  * Retry/replan behavior creates hidden infinite loops.
  * Side-effecting steps execute without pre-action policy mediation.
* **Key design decisions/tradeoffs:**

  * Event-driven state machine vs simpler linear loop.
  * Aggressive replanning vs bounded deterministic fallback.
  * Single global budget vs per-phase budgets (plan, act, verify, repair).
* **Observable metrics/signals:**

  * Termination reason distribution (`success`, `budget_exhausted`, `policy_denied`, `failed_validation`).
  * Loop efficiency (useful actions / total steps).
  * Recovery success rate after loop perturbations.
* **Required prerequisites:** **T1.1.1**, **T1.2.3**, **T2.4.5**.
* **Artifacts to produce:**

  * Runtime state machine contract with transition invariants.
  * Loop budget policy and stop-condition matrix.
  * Failure/recovery matrix tied to typed errors and policy outcomes.
* **Hands-on exercises:**

  * *Beginner:* Implement a typed loop state model with explicit stop conditions and structured termination logs.
  * *Advanced:* Add deterministic replan + recovery semantics with chaos scenarios; prove no unbounded loop behavior in stress tests.

---

## T2.3.1 Memory & state architecture — **High**

* **Definition:** Designing what the system remembers across turns and runs: session state, task state, intermediate artifacts, and long-lived memory (episodic/semantic/procedural).
* **Why it matters:** Most real tasks require persistence: “what did we already do?”, “what’s the latest status?”, “what are the user’s preferences?”
* **Typical failure modes:**

  * Stale memory → wrong actions.
  * Over-retention → privacy risk + context pollution.
  * Memory conflicts (two facts disagree) with no resolution strategy.
* **Key design decisions/tradeoffs:**

  * What is canonical truth: DB vs memory summaries vs tool outputs.
  * Write frequency: every step vs only after validation.
  * Forgetting strategy and retention windows.
* **Observable metrics/signals:**

  * Memory hit rate; stale-memory incidents.
  * Context token share used by memory vs task.
  * Correction rate (how often memory is overwritten).
* **Required prerequisites:** **T1.2.2**, **T1.3.3** (privacy).
* **Artifacts to produce:**

  * State model (entities, lifetimes, ownership).
  * Memory write policy (when, what, how validated).
  * Retention and deletion rules.
* **Hands-on exercises:**

  * *Beginner:* Implement session state with a simple store and show it persists user preferences.
  * *Advanced:* Build conflict-aware memory: store claims with timestamps/sources and implement resolution rules.

---

## T2.3.2 Knowledge architecture — **High**

* **Definition:** Designing knowledge sources: documents, databases, knowledge graphs, APIs, and retrieval strategies, with provenance and freshness controls.
* **Why it matters:** Agents often fail not because they “can’t reason,” but because they reason from the wrong or outdated source.
* **Typical failure modes:**

  * Source-of-truth confusion (docs vs DB vs ticket system).
  * Knowledge drift (docs updated but embeddings not reindexed).
  * Poisoned sources (malicious or low-quality content).
* **Key design decisions/tradeoffs:**

  * RAG vs structured DB queries vs curated KB.
  * Freshness SLAs and reindex cadence.
  * Citation requirements vs speed.
* **Observable metrics/signals:**

  * Knowledge freshness age; index lag.
  * Retrieval success on known queries.
  * Citation coverage rate.
* **Required prerequisites:** **T1.2.2**, **T3.3.2**.
* **Artifacts to produce:**

  * Knowledge source registry (owners + refresh schedule).
  * “Source-of-truth hierarchy” doc.
  * Content quality and poisoning checks.
* **Hands-on exercises:**

  * *Beginner:* Build a small knowledge registry and require the agent to cite sources.
  * *Advanced:* Implement incremental indexing with freshness monitoring and alerts when index lag exceeds threshold.

---

## T2.3.3 Data governance architecture — **Med**

* **Definition:** Designing policies and mechanisms for data access, lineage, retention, redaction, and audit—across prompts, memory, tool outputs, and logs.
* **Why it matters:** Governance is what makes your system deployable in regulated or enterprise contexts.
* **Typical failure modes:**

  * Sensitive data appears in logs/traces.
  * “Shadow memory” stores persist data outside approved systems.
  * Inability to answer “who accessed what, when, and why”.
* **Key design decisions/tradeoffs:**

  * Centralized governance layer vs per-service enforcement.
  * Granularity of access control (per user/role/tenant/task).
  * Retention windows vs debugging needs.
* **Observable metrics/signals:**

  * Redaction coverage; audit log completeness.
  * Access-denied and policy-block events.
  * Data deletion request fulfillment time.
* **Required prerequisites:** **T1.3.3**, **T4.2.1** (ops compliance).
* **Artifacts to produce:**

  * Data flow diagrams (DFDs) for prompts/memory/logs.
  * Access control model (RBAC/ABAC) + audit plan.
  * Retention + deletion SOPs.
* **Hands-on exercises:**

  * *Beginner:* Map data flows for a simple agent and identify where PII could leak.
  * *Advanced:* Implement attribute-based access control (ABAC) for tool usage and ensure audit logs capture decision rationale.

---

## T2.4.1 Validation & repair architecture — **High**

* **Definition:** System-level design for detecting wrong outputs/actions and recovering: validators, test execution, judges, fallbacks, retries, and human escalation.
* **Why it matters:** Agents fail. The question is whether they fail **safely** and **recoverably**.
* **Typical failure modes:**

  * No validation → silent wrong results.
  * Validation exists but is non-actionable (no repair path).
  * Over-repair loops → infinite retries and cost blowups.
* **Key design decisions/tradeoffs:**

  * Deterministic validators first; LLM judges as backup.
  * Repair strategies: re-prompt vs re-plan vs tool-based verification.
  * Escalation thresholds and “give up” criteria.
* **Observable metrics/signals:**

  * Validation pass rate; repair attempt count.
  * Escalation rate and root causes.
  * “Fixed after repair” success rate.
* **Required prerequisites:** **T2.1.2**, **T1.2.3**.
* **Artifacts to produce:**

  * Validation map: what is validated at each step.
  * Repair decision tree + termination rules.
  * Escalation templates for humans.
* **Hands-on exercises:**

  * *Beginner:* Add a validator (schema + basic checks) and retry with a corrected prompt on failure.
  * *Advanced:* Build a multi-stage repair system: deterministic checks → tool-based verification → human escalation, with strict loop limits.

---

## T2.4.2 Safety architecture — **High**

* **Definition:** Designing enforcement of safety and policy: restricted actions, content policies, permissioning, sandboxing, and monitoring for policy violations.
* **Why it matters:** A capable agent without safety architecture is a footgun with autocomplete.
* **Typical failure modes:**

  * Prompt injection bypasses “don’t do X”.
  * Unsafe tool access (e.g., file system, prod DB) available by default.
  * Policy is only in prompt text (no hard enforcement).
* **Key design decisions/tradeoffs:**

  * Hard guards (policy engine) vs soft guards (prompting).
  * Safety boundaries at tool layer vs orchestration layer (ideally both).
  * “Deny by default” vs “allow by default” (choose deny).
* **Observable metrics/signals:**

  * Blocked actions; attempted policy violations.
  * Security review findings.
  * Safety incident rate and severity.
* **Required prerequisites:** **T1.3.2**, **T2.2.3**.
* **Artifacts to produce:**

  * Safety policy spec + enforcement points.
  * Guardrail test suite (known attacks, jailbreaks).
  * Permission boundary diagram.
* **Hands-on exercises:**

  * *Beginner:* Implement a denylist of high-risk tools unless explicitly approved.
  * *Advanced:* Add a policy engine that inspects planned actions + context and blocks/rewrites requests; evaluate against an adversarial suite.

---

## T2.4.3 Multi-agent & human collaboration architecture — **Med**

* **Definition:** Designing multiple roles (agents + humans) working together: delegation, reviews, consensus, escalation paths, and shared state.
* **Why it matters:** Many real systems need specialization (planner/coder/reviewer) and human accountability.
* **Typical failure modes:**

  * Role confusion (agents overwrite each other’s goals).
  * Deadlocks (agents waiting on each other).
  * Human review becomes bottleneck or rubber stamp.
* **Key design decisions/tradeoffs:**

  * Topologies: manager-worker, peer debate, committee voting.
  * Shared memory vs isolated contexts.
  * Human placement: approval gates vs sampling-based audits.
* **Observable metrics/signals:**

  * Coordination overhead (messages/steps).
  * Disagreement rate and resolution time.
  * Human workload and throughput.
* **Required prerequisites:** **T1.3.1**, **T2.2.1**.
* **Artifacts to produce:**

  * Role definitions + responsibilities.
  * Protocol spec (message formats, termination).
  * Escalation ladder (who decides when).
* **Hands-on exercises:**

  * *Beginner:* Create a 2-agent system (draft + reviewer) and require reviewer approval before final output.
  * *Advanced:* Implement a manager that decomposes tasks and assigns workers, then merges outputs with explicit conflict resolution rules.

---

## T2.4.4 Trust boundary & assumption-ledger architecture — **High**

* **Definition:** Defining explicit trust boundaries (what is trusted vs untrusted) and maintaining an assumption ledger that states why each boundary is considered safe and how it is verified.
* **Why it matters:** Reliability claims are meaningless if you cannot state which components are allowed to be wrong and which components must enforce invariants.
* **Typical failure modes:**

  * Untrusted tool output treated as authoritative truth.
  * Implicit trust in prompts/model behavior without enforcement.
  * Architecture drift bypasses the intended mediation path.
* **Key design decisions/tradeoffs:**

  * Granularity: coarse boundary diagrams vs component-level trust annotations.
  * Static assumptions (simple) vs runtime-validated assumptions (safer).
  * Single centralized ledger vs per-team ledgers with federation rules.
* **Observable metrics/signals:**

  * Coverage of components with explicit trust classification.
  * Number of incidents caused by violated/untracked assumptions.
  * % of high-risk paths with boundary enforcement tests.
* **Required prerequisites:** **T1.3.2**, **T2.2.3**, **T2.4.2**.
* **Artifacts to produce:**

  * Trust-boundary diagram with trusted/untrusted data flow labels.
  * Assumption ledger (assumption, owner, validation test, review cadence).
  * Boundary bypass regression tests.
* **Hands-on exercises:**

  * *Beginner:* Draw trust boundaries for one agent workflow and annotate where untrusted data enters and where policy is enforced.
  * *Advanced:* Create an assumption manifest plus tests that fail when a new tool path bypasses policy mediation.

---

## T2.4.5 Execution governance boundary architecture — **High**

* **Definition:** Designing a first-class governance boundary that separates **policy decision** (allow/deny/requires approval) from **enforcement** (blocking/allowing actual side effects).
* **Why it matters:** Prompt-level rules are advisory. A governance boundary is the enforceable control plane for real-world actions.
* **Typical failure modes:**

  * Decision and enforcement mixed in one component, creating bypass paths.
  * Inconsistent rule application across tools.
  * “Requires approval” decisions not persisted as protocol artifacts.
* **Key design decisions/tradeoffs:**

  * PDP/PEP split (more explicit) vs embedded checks (simpler but riskier).
  * Declarative policy rules vs imperative rule code.
  * Synchronous enforcement vs queued enforcement with human gates.
* **Observable metrics/signals:**

  * Policy decision distribution (allow/deny/approval).
  * Blocked high-impact action attempts.
  * Approval latency and approval override rate.
* **Required prerequisites:** **T2.4.2**, **T1.3.1**, **T3.2.3**.
* **Artifacts to produce:**

  * `PolicyInput`/`PolicyDecision` schema contracts.
  * Governance boundary architecture doc (decision path + enforcement path).
  * Approval protocol artifacts (request/decision/audit trail).
* **Hands-on exercises:**

  * *Beginner:* Add a policy boundary that denies all write actions by default and emits structured decision logs.
  * *Advanced:* Implement PDP/PEP mediation with approval states and prove via tests that denied actions cannot execute through any runtime path.

---

## T2.4.6 Formal assurance & critical-path verification — **High**

* **Definition:** Applying formal and semi-formal assurance methods to critical paths: invariant modeling, contract verification, model checking where feasible, and assurance cases linking claims to evidence.
* **Why it matters:** For high-impact workflows, testing alone is insufficient. You need stronger guarantees for safety and correctness properties.
* **Typical failure modes:**

  * Critical invariants defined in prose but not machine-checked.
  * Safety claims cannot be traced to executable evidence.
  * Verification done once and not maintained after architecture changes.
* **Key design decisions/tradeoffs:**

  * Full formal methods (strong guarantees, high cost) vs targeted critical-path verification.
  * Runtime assertions vs offline model/property checking.
  * Proof strength vs development velocity under release pressure.
* **Observable metrics/signals:**

  * Coverage of critical paths with formal/contract verification.
  * Number of invariant violations detected pre-release vs production.
  * Assurance artifact freshness after system changes.
* **Required prerequisites:** **T2.4.1**, **T2.4.4**, **T3.4.4**.
* **Artifacts to produce:**

  * Critical invariant catalog with severity and ownership.
  * Verification specification for high-impact workflows.
  * Assurance case linking claims -> tests/checks -> conformance evidence.
* **Hands-on exercises:**

  * *Beginner:* Write machine-checkable pre/postcondition contracts for two high-risk actions and enforce them in CI.
  * *Advanced:* Model one critical workflow (state machine + invariants), run property checks, and publish an assurance case tied to release gates.

---

## T2.5.1 Observability & evaluation architecture — **High**

* **Definition:** Designing the measurement nervous system: tracing, logs, audit trails, quality evaluation pipelines, feedback capture, and dashboards tied to SLOs.
* **Why it matters:** If you can’t see it, you can’t debug it, and it will fail in production in creative ways.
* **Typical failure modes:**

  * Missing traces → incidents become archaeology.
  * Logging too much sensitive data → compliance incident.
  * No eval loop → quality decays unnoticed.
* **Key design decisions/tradeoffs:**

  * What to log (minimum useful) and how to redact.
  * Sampling strategy vs full-fidelity traces.
  * Offline eval vs online monitoring vs both.
* **Observable metrics/signals:**

  * Trace coverage (% runs traced end-to-end).
  * Metric freshness; dashboard latency.
  * Feedback volume and resolution time.
* **Required prerequisites:** **T2.1.2**, **T1.3.3**.
* **Artifacts to produce:**

  * Telemetry spec (spans, attributes, redaction rules).
  * Eval architecture doc (datasets, cadence, gating).
  * Dashboard and alert definitions tied to SLOs.
* **Hands-on exercises:**

  * *Beginner:* Add end-to-end tracing to an agent run and display steps/tool calls in a timeline.
  * *Advanced:* Build a continuous eval pipeline that runs nightly on a regression set and pages the team on statistically significant drops.

---

## T3.1.1 Prompt/instruction engineering & context management — **High**

* **Definition:** Writing stable instructions and managing context: system/developer/user roles, delimiters, few-shot examples, tool instructions, and context packing (summaries/retrieval).
* **Why it matters:** Prompting is not “copywriting.” It’s interface design between ambiguous language and brittle downstream behavior.
* **Typical failure modes:**

  * Prompt drift across versions without tests.
  * Instruction collisions (“do X” vs “never do X”).
  * Context stuffing causes the model to ignore key constraints.
* **Key design decisions/tradeoffs:**

  * Long prompt with all rules vs short prompt with retrieval of policies.
  * Few-shot examples vs cost/latency.
  * Fixed templates vs dynamic prompting.
* **Observable metrics/signals:**

  * Instruction-following success rate on eval set.
  * Token counts by segment (system/dev/user/memory/retrieval).
  * Rate of “asked for clarification” vs “hallucinated”.
* **Required prerequisites:** **T1.1.2**, **T1.2.2**.
* **Artifacts to produce:**

  * Prompt library with versioning and change logs.
  * Prompt unit tests (golden outputs or rubric scores).
  * Context budget spec and packing strategy.
* **Hands-on exercises:**

  * *Beginner:* Create a prompt template with explicit sections (goal, constraints, tools, output format) and test on 10 tasks.
  * *Advanced:* Implement context packing that selects among memory/retrieval/tool outputs under a strict token budget and measure impact on quality/latency.

---

## T3.1.2 Planning, reflection & repair loops in code — **High**

* **Definition:** Implementing iterative cognition: plan → act → observe → reflect → replan, with termination, uncertainty handling, and loop limits.
* **Why it matters:** Most non-trivial tasks require course correction. A single-shot answer is fragile; loops make it robust—if bounded.
* **Typical failure modes:**

  * Infinite loops on ambiguous tasks.
  * Reflection that produces words, not actions (“I should do better”).
  * Repair that changes the wrong thing (overfitting to validator).
* **Key design decisions/tradeoffs:**

  * When to reflect: every step vs on failure vs on uncertainty spikes.
  * Bounded compute: max steps, max tokens, max retries per tool.
  * Replan triggers: tool errors, validation failures, missing info.
* **Observable metrics/signals:**

  * Loop iteration counts; termination reason distribution.
  * Repair success rate; “gave up” rate.
  * Cost per successful completion.
* **Required prerequisites:** **T2.2.2**, **T2.4.1**.
* **Artifacts to produce:**

  * Loop policy doc (limits, triggers, escalation).
  * Replay tooling for step-by-step reproduction.
  * Repair outcome logs (before/after).
* **Hands-on exercises:**

  * *Beginner:* Add a max-step + “ask user” fallback when missing required info.
  * *Advanced:* Implement adaptive reflection: only reflect when validator confidence is low or when tool errors occur; show reduced cost with same quality.

---

## T3.2.1 Structured outputs, tool calling & schema enforcement — **High**

* **Definition:** Getting the model to emit reliably parseable outputs (JSON/YAML/etc) and enforcing schemas with validators/parsers, including recovery from malformed outputs.
* **Why it matters:** Structured output is how you turn language into reliable automation.
* **Typical failure modes:**

  * Invalid JSON; missing required fields.
  * “Creative” field names; wrong types.
  * Schema matches but semantics wrong (e.g., wrong ID).
* **Key design decisions/tradeoffs:**

  * Strict schemas (reliable) vs flexible (more robust to variation but harder to validate).
  * Repair strategy: re-ask vs partial parse vs constrained decoding.
  * Human-readable outputs vs machine-first outputs.
* **Observable metrics/signals:**

  * Parse failure rate; schema validation failures.
  * Repair attempts per output.
  * Downstream tool error rates caused by bad args.
* **Required prerequisites:** **T1.2.1**, **T3.1.1**.
* **Artifacts to produce:**

  * Schema definitions and examples.
  * Parser + schema validation tests.
  * Fallback behavior spec on parse failure.
* **Hands-on exercises:**

  * *Beginner:* Create a schema for a “plan” object and enforce it; add a retry prompt on parse failure.
  * *Advanced:* Implement a robust “parse-and-repair” layer that extracts partial structured data from messy outputs and requests only missing fields.

---

## T3.2.2 Tool adapters & side-effect-safe execution — **High**

* **Definition:** Wrapping tools with safe execution semantics: retries, timeouts, idempotency keys, transactional patterns, and normalization of errors/results.
* **Why it matters:** Tool calls create side effects. “Retry” can become “duplicate purchase” unless engineered.
* **Typical failure modes:**

  * Duplicate actions due to retries.
  * Partial completion with lost acknowledgements.
  * Silent tool failures treated as success.
* **Key design decisions/tradeoffs:**

  * Idempotency strategy per tool (create/update/delete).
  * Compensating actions vs strict transactional DB operations.
  * Error taxonomy: how many error types the agent sees.
* **Observable metrics/signals:**

  * Duplicate detection rate; rollback/compensation rate.
  * Tool error distribution; mean time to recovery.
  * Side-effect incidents (high severity).
* **Required prerequisites:** **T1.2.3**, **T1.2.1**.
* **Artifacts to produce:**

  * Tool wrapper library with standard behaviors.
  * Error taxonomy and guidelines.
  * Idempotency and compensation playbooks.
* **Hands-on exercises:**

  * *Beginner:* Wrap one tool with timeout + retries + structured errors.
  * *Advanced:* Implement idempotency keys for “create resource” and compensating actions for “update resource,” then simulate failures to prove safety.

---

## T3.2.3 Sandboxing & permissioning implementation — **High**

* **Definition:** Enforcing execution boundaries: sandboxed code execution, restricted file/network access, secret management, per-user/tenant isolation, and permission-scoped tools.
* **Why it matters:** Sandboxing turns “agent with tools” into something you can safely run without hoping nothing goes wrong.
* **Typical failure modes:**

  * Secret leakage into prompts/logs.
  * Sandbox escape via misconfiguration.
  * Over-privileged tools reachable from low-trust contexts.
* **Key design decisions/tradeoffs:**

  * Isolation level: process/container/VM; per task vs shared.
  * Network policy: allowlist domains; block exfil paths.
  * Secret access: short-lived tokens; scoped credentials.
* **Observable metrics/signals:**

  * Denied permission events; suspicious file/network access.
  * Secret access logs; token issuance frequency.
  * Security test pass rate (escape attempts).
* **Required prerequisites:** **T1.3.2**, **T2.2.3**.
* **Artifacts to produce:**

  * Sandbox threat model and config docs.
  * Permission matrix for tools and environments.
  * Security regression tests for sandbox policies.
* **Hands-on exercises:**

  * *Beginner:* Create a sandboxed “run code” tool that disallows network and limits CPU/time.
  * *Advanced:* Implement per-user isolation + scoped secrets; prove that one user’s agent cannot access another’s data via tests.

---

## T3.2.4 Enterprise integrations & automation — **Med**

* **Definition:** Integrating agents into enterprise systems: SaaS APIs, ticketing, CRM/ERP, document systems, identity/access, RPA for legacy UIs, and approval workflows.
* **Why it matters:** “Agent works in demo” often dies on “but can it open SAP?” Integration is where production lives.
* **Typical failure modes:**

  * API permission mismatch; brittle auth flows.
  * RPA flakiness due to UI changes.
  * Missing audit trails for regulated actions.
* **Key design decisions/tradeoffs:**

  * API-first vs RPA fallback.
  * Central integration platform vs bespoke connectors.
  * Synchronous automation vs queued workflow with approvals.
* **Observable metrics/signals:**

  * Connector reliability; auth failure rates.
  * RPA success rate; mean time to repair UI selectors.
  * Audit completeness for critical actions.
* **Required prerequisites:** **T1.2.1**, **T4.2.1** (compliance).
* **Artifacts to produce:**

  * Connector catalog (owners, auth type, scopes).
  * Approval workflow specs.
  * Audit log mapping to business actions.
* **Hands-on exercises:**

  * *Beginner:* Integrate an agent with a simple SaaS API and implement read-only queries.
  * *Advanced:* Build an approval-gated “write” flow that logs every action for audit, including who approved and what changed.

---

## T3.2.5 Effect typing & commitment semantics implementation — **High**

* **Definition:** Implementing explicit effect classes for actions (for example `READ`, `REVERSIBLE`, `IRREVERSIBLE`, `HIGH_IMPACT`) and binding execution controls to those classes.
* **Why it matters:** Side effects are not equal. Effect-aware execution prevents treating “read docs” and “delete customer data” as equivalent operations.
* **Typical failure modes:**

  * Tool names used as risk proxy; dangerous operations hidden behind benign names.
  * Retries on non-idempotent high-impact actions.
  * Missing approval requirements for irreversible commits.
* **Key design decisions/tradeoffs:**

  * Central effect classifier vs per-tool local classification.
  * Static effect classes vs context-dependent dynamic effects.
  * Strict fail-closed behavior vs adaptive fallback under uncertainty.
* **Observable metrics/signals:**

  * Action distribution by effect class.
  * Policy denials and approval requests by effect class.
  * Duplicate irreversible action incidents.
* **Required prerequisites:** **T1.2.1**, **T3.2.2**, **T2.4.5**.
* **Artifacts to produce:**

  * Effect taxonomy enum and classifier rules.
  * Idempotency/approval/trace requirements matrix by effect class.
  * Regression tests asserting effect classification and policy routing.
* **Hands-on exercises:**

  * *Beginner:* Classify existing tools into effect classes and enforce stricter logging for non-read actions.
  * *Advanced:* Implement context-aware effect classification (for example update action classified as `HIGH_IMPACT` when target record is production-critical) and test policy outcomes.

---

## T3.3.1 State persistence & run bookkeeping — **High**

* **Definition:** Recording everything needed to reproduce and audit agent behavior: run IDs, step logs, tool inputs/outputs, versions, and checkpoints.
* **Why it matters:** Without bookkeeping, you can’t debug incidents, satisfy audits, or understand regressions.
* **Typical failure modes:**

  * Missing correlation IDs → can’t trace across services.
  * Overlogging sensitive data → privacy incident.
  * No version capture → can’t reproduce behavior after updates.
* **Key design decisions/tradeoffs:**

  * Event sourcing (append-only) vs mutable state.
  * Full-fidelity logs vs sampled logs (privacy + cost).
  * What is stored raw vs summarized/redacted.
* **Observable metrics/signals:**

  * Trace completeness; % runs reproducible.
  * Storage volume and retention compliance.
  * Debug turnaround time.
* **Required prerequisites:** **T2.5.1**, **T1.3.3**.
* **Artifacts to produce:**

  * Run schema (IDs, versions, metadata).
  * Redaction and retention rules.
  * Replay tool for reproducing runs.
* **Hands-on exercises:**

  * *Beginner:* Add run IDs and log each step with timestamps and tool calls.
  * *Advanced:* Implement deterministic replay: given a run ID, reconstruct the exact prompts, tool outputs, and decisions (as much as possible) with version snapshots.

---

## T3.3.2 Retrieval & RAG implementation — **High**

* **Definition:** Implementing retrieval pipelines: ingestion, chunking, embedding, indexing, hybrid search, reranking, citation formatting, and “answer grounded in sources” behavior.
* **Why it matters:** RAG is often the difference between a helpful agent and a hallucination machine.
* **Typical failure modes:**

  * Bad chunking → missing context.
  * Embedding drift after model changes → retrieval collapse.
  * Reranker improves relevance but kills latency.
* **Key design decisions/tradeoffs:**

  * Chunk size/overlap and metadata strategy.
  * Hybrid retrieval vs vector-only.
  * Citation requirements and confidence thresholds.
* **Observable metrics/signals:**

  * Retrieval metrics (precision@k proxies), grounded-answer rate.
  * Index lag; ingest error rate.
  * Latency per retrieval stage.
* **Required prerequisites:** **T1.2.2**, **T2.3.2**.
* **Artifacts to produce:**

  * RAG config doc + rationale.
  * Labeled retrieval eval set.
  * Monitoring for index freshness and drift.
* **Hands-on exercises:**

  * *Beginner:* Implement chunking + embeddings + top-k retrieval and show citations.
  * *Advanced:* Add reranking + hybrid retrieval and run an evaluation demonstrating measurable improvement vs baseline.

---

## T3.3.3 Memory writing & consolidation — **Med**

* **Definition:** Deciding what the agent stores as memory, how it summarizes, how it corrects mistakes, and how it forgets—while preventing “memory poisoning” and privacy leaks.
* **Why it matters:** Memory improves personalization and long tasks, but it can also permanently store wrong or sensitive data.
* **Typical failure modes:**

  * Storing hallucinations as facts.
  * Storing secrets/PII.
  * Memory bloat and irrelevant recall.
* **Key design decisions/tradeoffs:**

  * Write only after validation vs write opportunistically.
  * Store raw vs store summary vs store structured facts with sources.
  * Forgetting: time-based, relevance-based, user-controlled deletion.
* **Observable metrics/signals:**

  * Memory correction rate; stale-memory incidents.
  * User complaints about “it keeps bringing up irrelevant things”.
  * PII detection hits in memory store.
* **Required prerequisites:** **T2.3.1**, **T1.3.3**.
* **Artifacts to produce:**

  * Memory write policy + validation requirements.
  * Memory schema (claims with provenance and timestamps).
  * Deletion/export tools for user requests.
* **Hands-on exercises:**

  * *Beginner:* Store 3 user preferences and retrieve them later; add a “forget” command.
  * *Advanced:* Implement “memory as claims”: each stored fact includes a source, confidence, and expiry; resolve conflicts and demonstrate safe deletion.

---

## T3.4.1 Validation & judging implementation — **High**

* **Definition:** Building validators (schemas, rules, unit tests) and judges (rubrics, LLM-as-judge, disagreement handling) into the execution path.
* **Why it matters:** This is where “agent seems smart” turns into “agent is correct often enough to trust.”
* **Typical failure modes:**

  * Overreliance on LLM judges → noisy and gameable.
  * Validators too strict → false negatives and user frustration.
  * Judge drift after model updates → score instability.
* **Key design decisions/tradeoffs:**

  * Deterministic checks first; probabilistic judges second.
  * Rubric design: task-specific vs general.
  * Disagreement policy: majority vote, tie-breaker model, or human escalation.
* **Observable metrics/signals:**

  * Validator pass rates; judge agreement rates.
  * Correlation of judge score with human ratings.
  * “Shipped bugs” escaping validation.
* **Required prerequisites:** **T2.4.1**, **T1.2.1**.
* **Artifacts to produce:**

  * Validator library + unit tests.
  * Judge rubrics + calibration report.
  * Disagreement handling playbook.
* **Hands-on exercises:**

  * *Beginner:* Add schema + rule checks for outputs (length, required fields, allowed values).
  * *Advanced:* Build a calibrated LLM judge: collect human labels for 100 samples, tune rubric/prompt, and measure judge-human correlation.

---

## T3.4.2 Evaluation harness & CI — **High**

* **Definition:** A repeatable offline evaluation system: datasets, scenario generators, simulation harnesses, regression tests, and CI gates for prompts/models/tools.
* **Why it matters:** Agentic systems are non-deterministic and change-prone. CI is your immune system.
* **Typical failure modes:**

  * Eval set too small or unrepresentative.
  * Test leakage: you optimize for the eval and fail in reality.
  * CI too slow/expensive so people bypass it.
* **Key design decisions/tradeoffs:**

  * Golden tests vs rubric scoring vs hybrid.
  * Simulation for tool environments vs live integration tests.
  * Cost/latency budgets for CI.
* **Observable metrics/signals:**

  * Regression detection rate; false alarm rate.
  * Eval runtime/cost per commit.
  * Coverage across task types and failure modes.
* **Required prerequisites:** **T2.1.2**, **T2.5.1**.
* **Artifacts to produce:**

  * Eval dataset and documentation (source, splits, limitations).
  * CI pipeline with gates and reports.
  * Scenario taxonomy mapping to risks.
* **Hands-on exercises:**

  * *Beginner:* Build a 50-case eval set and run it on every prompt change.
  * *Advanced:* Create a simulated tool environment with failure injection (timeouts, wrong data) and add it to CI to test agent resilience.

---

## T3.4.3 Online evaluation & experimentation — **Med**

* **Definition:** Measuring and improving in production: A/B tests, bandits (adaptive experiments), user feedback loops, drift detection, and safe rollouts.
* **Why it matters:** Offline evals never cover all user behavior. Online experiments are how you learn safely.
* **Typical failure modes:**

  * A/B tests without guardrails → ship a faster but unsafe variant.
  * Feedback spam/low quality → misleading signals.
  * Metric shifts due to seasonality mistaken for regressions.
* **Key design decisions/tradeoffs:**

  * Experiment unit: user, session, task.
  * Guardrail metrics (safety, cost, latency) vs primary metric.
  * Bandits (fast learning) vs A/B (clean inference).
* **Observable metrics/signals:**

  * Uplift in success rate; changes in escalation/incident rates.
  * User satisfaction; complaint volume.
  * Drift indicators (input distribution changes, tool errors).
* **Required prerequisites:** **T4.1.3**, **T2.1.2**.
* **Artifacts to produce:**

  * Experiment design docs + dashboards.
  * Guardrail thresholds and auto-stop criteria.
  * Feedback triage process.
* **Hands-on exercises:**

  * *Beginner:* Add a thumbs-up/down feedback capture and review weekly.
  * *Advanced:* Run an A/B test comparing two orchestration strategies and implement auto-rollback when guardrails degrade.

---

## T3.4.4 Conformance reporting & scorecards — **High**

* **Definition:** Producing executable conformance artifacts that report hard invariants (safety/boundedness/compliance) and utility outcomes (quality/latency/cost) for each release or run cohort.
* **Why it matters:** Teams often claim “safe and reliable” without measurable evidence. Conformance scorecards turn claims into auditable facts.
* **Typical failure modes:**

  * Compliance evidence spread across dashboards/spreadsheets with no single source of truth.
  * Utility metrics improve while hard invariants silently regress.
  * Reports are manually produced and therefore stale or incomplete.
* **Key design decisions/tradeoffs:**

  * Per-run vs per-release conformance granularity.
  * Hard gates on invariants vs warning-only mode for experimentation.
  * Human-readable reports vs machine-consumable artifacts (best: both).
* **Observable metrics/signals:**

  * % releases with complete conformance artifact.
  * Hard invariant pass rate over time.
  * Ratio of blocked deployments due to conformance failures.
* **Required prerequisites:** **T3.4.1**, **T3.4.2**, **T4.2.1**.
* **Artifacts to produce:**

  * Conformance schema (`invariants`, `utility_metrics`, `metadata`, `exceptions`).
  * Automated conformance generation in CI/CD.
  * Release gate policy referencing conformance thresholds.
* **Hands-on exercises:**

  * *Beginner:* Create a conformance JSON for each CI run with at least 5 invariant checks and 3 utility metrics.
  * *Advanced:* Gate deployment on conformance rules and implement exception workflow requiring explicit risk sign-off.

---

## T3.4.5 Evaluation protocol rigor (causal + comparable) — **High**

* **Definition:** Designing eval protocols that produce comparable and causal insights: paired-seed comparisons, controlled budgets, ablations, and metamorphic tests for harness quality.
* **Why it matters:** Raw benchmark wins can be artifacts of randomness, budget differences, or data leakage. Protocol rigor prevents false confidence.
* **Typical failure modes:**

  * Comparing two methods with unequal token/tool budgets.
  * Reporting average scores without variance or confidence intervals.
  * Eval harness bugs mistaken for model/runtime improvements.
* **Key design decisions/tradeoffs:**

  * Paired-seed deterministic comparisons vs broader random stress tests.
  * Aggregate metrics simplicity vs per-scenario diagnostics depth.
  * Fast smoke eval cadence vs slower causal deep-dive cadence.
* **Observable metrics/signals:**

  * Variance across repeated runs on same scenarios.
  * Ablation deltas that isolate component contribution.
  * Metamorphic test pass rate for harness integrity.
* **Required prerequisites:** **T3.4.2**, **T2.1.2**, **T2.5.1**.
* **Artifacts to produce:**

  * Eval protocol spec (budget parity, seeding policy, statistical reporting).
  * Ablation plan template and comparator script.
  * Metamorphic test suite for evaluator correctness.
* **Hands-on exercises:**

  * *Beginner:* Run paired-seed comparisons for two prompt variants under equal budgets and report variance, not just means.
  * *Advanced:* Build a causal ablation matrix (remove one subsystem at a time) and include metamorphic tests that intentionally perturb inputs to validate harness sensitivity.

---

## T3.5.1 Multi-agent runtime implementation — **Med**

* **Definition:** Implementing coordination: message passing, shared memory/blackboard, scheduling, task allocation, consensus, and deadlock prevention.
* **Why it matters:** Multi-agent systems can boost performance and robustness, but they also multiply complexity and failure surfaces.
* **Typical failure modes:**

  * Deadlocks, livelocks, “debate forever.”
  * Conflicting actions from different agents.
  * Shared memory corruption or race conditions.
* **Key design decisions/tradeoffs:**

  * Central coordinator vs peer-to-peer.
  * Shared state vs isolated state + explicit merge.
  * Coordination algorithms: auctions, voting, role specialization.
* **Observable metrics/signals:**

  * Coordination overhead (messages/steps).
  * Conflict rate and resolution time.
  * Duplicate/contradictory actions.
* **Required prerequisites:** **T2.4.3**, **T1.2.3**.
* **Artifacts to produce:**

  * Protocol definition (message schema, lifetimes).
  * Deadlock prevention rules (timeouts, max rounds).
  * Shared memory consistency model.
* **Hands-on exercises:**

  * *Beginner:* Implement two agents (writer/reviewer) with a simple message protocol.
  * *Advanced:* Build a coordinator that assigns tasks to 3 worker agents based on estimated cost/latency and merges results with conflict detection.

---

## T3.5.2 Performance & cost optimization — **High**

* **Definition:** Engineering for speed and cost: caching, batching, streaming, prompt compression, model routing, token budgeting, and minimizing unnecessary tool calls.
* **Why it matters:** Production agents can become financially unviable without optimization. Latency also determines UX success.
* **Typical failure modes:**

  * Cost runaway from loops or over-retrieval.
  * Latency spikes due to serial tool calls.
  * Aggressive caching serves stale or unsafe results.
* **Key design decisions/tradeoffs:**

  * Cache scope (per user/tenant/global) and invalidation strategy.
  * Use smaller models for low-risk tasks; larger for high-risk.
  * Parallelization vs consistency (race conditions).
* **Observable metrics/signals:**

  * Cost per task; tokens per stage; p95 latency.
  * Cache hit rate; stale-cache incident rate.
  * Tool call counts and parallelism factor.
* **Required prerequisites:** **T1.2.3**, **T2.1.2**.
* **Artifacts to produce:**

  * Latency budget per pipeline stage.
  * Cost dashboards + anomaly alerts.
  * Caching policy doc + invalidation rules.
* **Hands-on exercises:**

  * *Beginner:* Add simple caching for retrieval results and measure latency reduction.
  * *Advanced:* Implement model routing + prompt compression and show a controlled reduction in cost while maintaining eval quality.

---

## T4.1.1 Deployment, scaling & infrastructure operations — **High**

* **Definition:** Operating the runtime: environments (dev/stage/prod), secrets, networking, queues, concurrency, rate limits, autoscaling, and safe access to dependencies.
* **Why it matters:** Many agent failures are just classic ops failures wearing an LLM costume.
* **Typical failure modes:**

  * Rate limiting collapses throughput.
  * Secrets mismanagement → breaches.
  * Scaling bugs → thundering herds, queue explosions.
* **Key design decisions/tradeoffs:**

  * Serverless vs containers vs long-running workers.
  * Sync request/response vs async job model for long tasks.
  * Backpressure strategy when dependencies degrade.
* **Observable metrics/signals:**

  * Queue depth; worker utilization; error rates.
  * Rate limit events; dependency latencies.
  * Secret access anomalies.
* **Required prerequisites:** **T1.2.3**, **T3.3.1**.
* **Artifacts to produce:**

  * Infra-as-code and environment parity checklist.
  * Scaling and rate limit runbooks.
  * Dependency map and fallback plan.
* **Hands-on exercises:**

  * *Beginner:* Deploy an agent service with separate dev/stage configs and basic rate limiting.
  * *Advanced:* Implement async job orchestration with queues + backpressure; chaos-test dependency outages and show graceful degradation.

---

## T4.1.2 Versioning, release management & rollback — **High**

* **Definition:** Managing change across models, prompts, tools, retrieval indexes, and policies with versioning, canaries, feature flags, and rollback criteria.
* **Why it matters:** Agent systems regress easily. Safe release machinery prevents “we changed one prompt and broke everything.”
* **Typical failure modes:**

  * Untracked prompt edits → mystery regressions.
  * Model update changes behavior silently.
  * Rollback doesn’t restore indexes/policies → partial rollback failures.
* **Key design decisions/tradeoffs:**

  * Immutable versions vs mutable configs.
  * Canary scope and duration.
  * Rollback triggers: SLO breach, eval drop, incident spikes.
* **Observable metrics/signals:**

  * Regression rate post-release; rollback frequency.
  * Version adoption distribution (who is on which version).
  * Eval score trends across versions.
* **Required prerequisites:** **T3.4.2**, **T2.1.2**.
* **Artifacts to produce:**

  * Versioning scheme (models/prompts/tools/indexes).
  * Release checklist + automated gates.
  * Rollback playbook including data/index rollback.
* **Hands-on exercises:**

  * *Beginner:* Add semantic versioning to prompts and log the version for every run.
  * *Advanced:* Implement canary releases with automated rollback on guardrail breaches, and prove with a simulated regression.

---

## T4.1.3 Production observability & SLO management — **High**

* **Definition:** Running dashboards and alerts tied to SLOs: latency, cost, quality proxies, tool reliability, safety events, and user satisfaction.
* **Why it matters:** Production is where edge cases breed. Observability is how you catch them before users do.
* **Typical failure modes:**

  * Alert storms with low signal.
  * No audit trace for actions.
  * Metrics tracked but not actionable.
* **Key design decisions/tradeoffs:**

  * High-cardinality tracing vs cost.
  * Sampling strategy vs forensic completeness.
  * Redaction vs debug depth.
* **Observable metrics/signals:**

  * SLO compliance; error budget burn rate.
  * Action counts by risk class; escalation rates.
  * p95 latency and cost anomalies.
* **Required prerequisites:** **T2.5.1**, **T1.3.3**.
* **Artifacts to produce:**

  * SLO definitions + error budget policy.
  * Dashboards per stakeholder (ops/product/security).
  * Audit log retention and access procedures.
* **Hands-on exercises:**

  * *Beginner:* Create a dashboard for task success rate, latency, and tool error rate.
  * *Advanced:* Implement anomaly detection for cost spikes and automatically switch the agent into “safe mode” (reduced autonomy) when triggered.

---

## T4.1.4 Incident response, debugging & failure-mode playbooks — **High**

* **Definition:** Operational discipline for failures: triage, reproduction, containment, rollback, postmortems, and a catalog of common agent failure modes with mitigations.
* **Why it matters:** Agents fail in weird ways. You need repeatable response patterns or you’ll drown in one-off chaos.
* **Typical failure modes (bottom-up catalog):**

  * Infinite loops / runaway tool calls.
  * Prompt injection incidents.
  * Partial tool failures causing duplicate actions.
  * Retrieval drift or poisoning.
  * Model behavior shift after provider update.
  * Silent degradation (quality slowly drops).
* **Key design decisions/tradeoffs:**

  * Automatic safe-mode triggers vs human-only toggles.
  * Reproduction fidelity: replay from logs vs synthetic reproduction.
  * Postmortem depth vs speed; blameless culture vs accountability.
* **Observable metrics/signals:**

  * Mean time to detect (MTTD) / resolve (MTTR).
  * Incident frequency/severity; top root causes.
  * “Near miss” counts (blocked by guardrails).
* **Required prerequisites:** **T3.3.1**, **T4.1.3**.
* **Artifacts to produce:**

  * Incident runbooks (by failure mode).
  * Postmortem template + action item tracking.
  * “Kill switch” and safe-mode operational procedures.
* **Hands-on exercises:**

  * *Beginner:* Write a runbook for “agent stuck in loop” including detection and containment.
  * *Advanced:* Run a “game day” where you inject tool failures and prompt injections into staging; measure MTTR and improve runbooks.

---

## T4.1.5 Safe degradation profiles & bounded autonomy operations — **High**

* **Definition:** Operating with explicit runtime profiles (for example `NORMAL`, `RESTRICTED`, `SAFE_HOLD`) that monotonically tighten admissible actions as uncertainty, incidents, or policy risk increase.
* **Why it matters:** Under stress, many systems fail open. Safe degradation ensures systems fail predictably and conservatively.
* **Typical failure modes:**

  * “Safe mode” exists in docs but is not executable in runtime.
  * Profile transitions are ad hoc and irreversible without operator visibility.
  * High-impact actions still execute in degraded states.
* **Key design decisions/tradeoffs:**

  * Triggering strategy: automatic thresholds vs manual operator control vs hybrid.
  * Profile strictness granularity (few broad profiles vs many specific profiles).
  * Recovery policy: immediate re-enable vs staged requalification.
* **Observable metrics/signals:**

  * Count/duration of degraded-profile periods.
  * Number of blocked high-impact actions while degraded.
  * MTTR from degraded mode back to normal with explicit requalification.
* **Required prerequisites:** **T4.1.3**, **T4.1.4**, **T2.4.5**.
* **Artifacts to produce:**

  * Profile policy spec with monotonic admissibility rules.
  * Transition matrix (trigger, required evidence, operator controls).
  * Profile transition audit logs and automated tests.
* **Hands-on exercises:**

  * *Beginner:* Add a `RESTRICTED` mode that disables write/high-impact tools and expose mode status in dashboards.
  * *Advanced:* Implement automated profile switching based on anomaly + policy signals, with monotonicity checks and human override protocol.

---

## T4.1.6 Disaster recovery & continuity engineering — **High**

* **Definition:** Designing and operating continuity mechanisms for major failures: region/provider outages, datastore corruption, queue backlog collapse, and recovery with explicit `RTO`/`RPO` targets.
* **Why it matters:** Reliable systems are defined by behavior during major failures, not only normal operation.
* **Typical failure modes:**

  * No restore path validated for critical state/artifacts.
  * Failover plan exists but was never tested end-to-end.
  * Recovery restores service but violates governance or data integrity guarantees.
* **Key design decisions/tradeoffs:**

  * Active-active vs active-passive failover.
  * Fast recovery vs strict consistency and data integrity.
  * Automated failover vs operator-controlled failover for high-risk domains.
* **Observable metrics/signals:**

  * Recovery time objective (RTO) attainment rate.
  * Recovery point objective (RPO) data loss incidents.
  * Restore drill success rate and time-to-stable-service.
* **Required prerequisites:** **T4.1.1**, **T4.1.3**, **T3.3.1**.
* **Artifacts to produce:**

  * Continuity architecture doc with RTO/RPO targets.
  * Backup/restore runbooks and failover decision matrix.
  * Quarterly restore/failover drill reports.
* **Hands-on exercises:**

  * *Beginner:* Define RTO/RPO for one agent service and execute a backup-restore drill.
  * *Advanced:* Simulate region/provider outage and demonstrate controlled failover with intact governance controls and post-recovery conformance checks.

---

## T4.2.1 Security, privacy & compliance operations — **Med**

* **Definition:** Ongoing security/compliance posture: red teaming, vulnerability management, access reviews, audit readiness, incident disclosure policies, legal/IP/vendor risk control.
* **Why it matters:** Shipping is not the end. Controls decay over time unless continuously exercised.
* **Typical failure modes:**

  * Drift in permissions (“temporary” access becomes permanent).
  * Vendor changes terms/behavior; compliance breaks silently.
  * Incomplete audit trails for sensitive actions.
* **Key design decisions/tradeoffs:**

  * Continuous red teaming vs periodic assessments.
  * Centralized policy enforcement vs team-managed controls.
  * Data minimization vs debugging richness.
* **Observable metrics/signals:**

  * Access review completion rate; least-privilege compliance.
  * Red-team findings backlog age.
  * Audit pass/fail and remediation cycle time.
* **Required prerequisites:** **T1.3.2**, **T1.3.3**, **T2.3.3**.
* **Artifacts to produce:**

  * Quarterly access review reports.
  * Security and compliance control mappings.
  * Vendor risk assessments + DPAs where needed.
* **Hands-on exercises:**

  * *Beginner:* Create a permission review checklist and apply it to your tool catalog.
  * *Advanced:* Build a red-team suite (prompt injections + tool misuse scenarios) that runs continuously in CI and gates releases.

---

## T4.2.2 Supply-chain and dependency governance — **High**

* **Definition:** Governing external dependencies across models, providers, prompts, tools, libraries, and datasets: provenance, update controls, trust policies, and rollback readiness.
* **Why it matters:** Complex agentic systems inherit risk from upstream components; uncontrolled dependency drift is a common root cause of production regressions.
* **Typical failure modes:**

  * Provider/model behavior changes silently degrade safety or quality.
  * Third-party prompt/tool packages introduce insecure behavior.
  * Dependency updates break contracts without compatibility detection.
* **Key design decisions/tradeoffs:**

  * Strict pinning and staged upgrades vs faster feature adoption.
  * Central dependency governance vs team-level autonomy.
  * Continuous upstream monitoring vs periodic review cadence.
* **Observable metrics/signals:**

  * Dependency drift detection time.
  * % dependencies with provenance metadata and owner assignment.
  * Regression incidents traced to upstream changes.
* **Required prerequisites:** **T4.1.2**, **T2.4.4**, **T4.2.1**.
* **Artifacts to produce:**

  * Dependency inventory with provenance, owner, and risk class.
  * Update policy (canary, compatibility checks, rollback criteria).
  * Upstream change monitoring and alerting plan.
* **Hands-on exercises:**

  * *Beginner:* Build a dependency inventory for your agent stack and classify top risks.
  * *Advanced:* Implement staged dependency rollout with automatic conformance re-checks and rollback on threshold breaches.

---

## T4.3.1 Org/process: AgentOps/LLMOps operating model & adoption — **High**

* **Definition:** The socio-technical system: team roles, ownership, review processes, training, support, governance, and measuring business impact.
* **Why it matters:** Many agent programs fail because they’re treated as a side project, not an operational product with accountability and support.
* **Typical failure modes:**

  * No clear owner for prompts/models/tools → chaos.
  * Users not trained → misuse + mistrust.
  * Shadow deployments by teams bypassing governance.
* **Key design decisions/tradeoffs:**

  * Central platform team vs embedded teams vs hybrid.
  * Review processes: lightweight vs heavyweight (match risk).
  * Support model: on-call rotation vs office-hours vs ticket queue.
* **Observable metrics/signals:**

  * Adoption rate; retention; user satisfaction.
  * Support ticket volume and resolution time.
  * Business KPIs tied to the use case (cycle time, revenue, cost).
* **Required prerequisites:** **T2.1.1**, **T4.1.4**.
* **Artifacts to produce:**

  * Operating model doc (roles: product, eng, security, legal).
  * Change management plan + training materials.
  * Business impact dashboard and quarterly review cadence.
* **Hands-on exercises:**

  * *Beginner:* Create an “agent user guide” and a support escalation path.
  * *Advanced:* Design an org operating model for a multi-team agent platform, including governance gates and shared tooling standards.

---

## T4.4.1 Emerging & unknown-unknown candidates — **Low**

* **Definition:** A living list of frontier topics and often-missed risks that may become critical as agents become more autonomous, interconnected, and regulated.
* **Why it matters:** Production failures often come from what teams didn’t know to ask about until it bit them.
* **Typical failure modes:**

  * “Silent regressions” due to upstream model/provider changes.
  * Prompt supply-chain risk (third-party prompts/tools/configs).
  * Agent-induced organizational drift (people stop checking outputs).
  * Evaluation contamination (training on your own eval outputs).
* **Key design decisions/tradeoffs:**

  * Build for change: abstraction layers and test gates vs speed.
  * Strong provenance tracking vs developer friction.
  * Continuous monitoring vs cost.
* **Observable metrics/signals:**

  * Change impact detection speed.
  * Unknown incident classes appearing over time.
  * “Human vigilance” indicators (review thoroughness, override quality).
* **Required prerequisites:** Broad familiarity with the entire taxonomy; especially **T4.1.2**, **T4.1.4**.
* **Artifacts to produce:**

  * “Frontier risk register” updated quarterly.
  * Provider change monitoring and regression test plan.
  * Post-incident “unknown unknown” capture process.
* **Hands-on exercises:**

  * *Beginner:* Maintain a “we didn’t anticipate this” log during testing and classify issues into new categories.
  * *Advanced:* Build a monitoring pipeline that detects provider/model behavior shifts using a fixed sentinel eval set and triggers safe-mode + investigation.

---

# C) Completeness Audit

## “What I covered” checklist across lifecycle (with taxonomy links)

* ✅ **Problem framing** — **T2.1.1**
* ✅ **Decomposition** — **T2.2.2**, **T3.1.2**
* ✅ **Planning** — **T2.2.2**, **T3.1.2**
* ✅ **Tool use** — **T1.2.1**, **T2.2.3**, **T3.2.1–T3.2.5**
* ✅ **Memory/state** — **T2.3.1**, **T3.3.1–T3.3.3**
* ✅ **Control loops** — **T1.1.1**, **T2.2.1**, **T2.2.4**, **T3.1.2**
* ✅ **Validation/judge** — **T2.4.1**, **T3.4.1**
* ✅ **Repair** — **T2.4.1**, **T3.1.2**
* ✅ **Safety** — **T2.4.2**, **T3.2.3**, **T4.2.1**
* ✅ **Eval** — **T2.5.1**, **T3.4.2–T3.4.3**
* ✅ **Observability** — **T2.5.1**, **T3.3.1**, **T4.1.3**
* ✅ **Reliability** — **T1.2.3**, **T4.1.1**, **T4.1.4**, **T4.1.6**
* ✅ **Deployment** — **T4.1.1**, **T4.1.2**, **T4.1.6**
* ✅ **Governance** — **T2.3.3**, **T4.2.1**, **T4.2.2**, **T4.3.1**
* ✅ **Unfamiliar-domain transfer protocol** — **T2.1.3**
* ✅ **Control-loop runtime contracts** — **T2.2.4**
* ✅ **Formal assurance for critical paths** — **T2.4.6**
* ✅ **Trust boundaries & explicit assumptions** — **T2.4.4**
* ✅ **Execution governance mediation (policy decision + enforcement)** — **T2.4.5**
* ✅ **Effect-typed side effects / commitment semantics** — **T3.2.5**
* ✅ **Conformance scorecards (hard invariants + utility evidence)** — **T3.4.4**
* ✅ **Eval protocol rigor (paired-seed, ablation, metamorphic)** — **T3.4.5**
* ✅ **Safe degradation profiles & bounded autonomy operations** — **T4.1.5**
* ✅ **Disaster recovery & continuity engineering** — **T4.1.6**
* ✅ **Supply-chain and dependency governance** — **T4.2.2**
* ✅ **Cost/latency** — **T3.5.2**, **T4.1.3**
* ✅ **Human-in-the-loop** — **T1.3.1**, **T2.4.3**
* ✅ **Multi-agent coordination** — **T2.4.3**, **T3.5.1**

## Likely missing or emerging topics (explicit list)

These are *still likely gaps or fast-moving areas* after the latest coverage pass:

* **Full-system formal guarantees beyond critical-path verification** — critical-path assurance is covered in **T2.4.6**, but whole-system proofs remain difficult in practice (Low/Med)
* **Model internals interpretability** (probing, logit lens, mechanistic interpretability) — mostly research-oriented (Low)
* **On-device / edge agents** (privacy + latency + offline constraints) — partially in **T4.1.1**, could expand (Med)
* **Regulatory regimes evolving quickly** (AI Act-like frameworks, sector-specific regs) — mentioned in **T1.3.3**/**T4.2.1** but needs ongoing updates (Low confidence because fast-moving)
* **Advanced economic mechanism design for multi-agent markets** (auctions, incentives at scale) — hinted in **T3.5.1** (Low)
* **Continuous learning / online memory learning** with safeguards — lightly in **T3.3.3** (Med/Low)
* **Human factors at org scale** (automation complacency, deskilling, accountability diffusion) — touched in **T4.4.1** (Med)

## Assumptions that limit completeness

* Assumes **text-first LLM agents**; multimodal agents (vision/audio/robotics) would add large branches (perception pipelines, physical safety, calibration).
* Assumes **tools are accessible** via APIs; heavy legacy environments may require deeper RPA + process mining branches.
* Assumes you can run **evaluation and logging**; extremely privacy-constrained settings may need specialized approaches (local inference, minimal telemetry).
* Assumes agents are used in **business/knowledge work**; scientific lab robotics or embedded systems change the threat model and control theory requirements.

---

# D) Application Plan Ownership

The canonical application roadmap and execution plan now lives only in:
- `docs/learning/agentic-system.md` (section `9. 30/60/90 Day Application Plan linked to taxonomy IDs`)

This taxonomy remains the source of truth for:
- coverage map
- leaf playbooks
- completeness audit
