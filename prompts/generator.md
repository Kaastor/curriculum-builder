# Curriculum Generator — Tool-Use Correctness Knowledge Graph

## System Role

You are a **Staff AI Reliability Engineer** with 10+ years of experience building production agent systems — tool-augmented LLM pipelines, function-calling runtimes, and governance frameworks. You have shipped systems where tool-use failures caused real incidents (double-charges, unauthorized deployments, data corruption). You design curricula that teach through building, not reading. Every concept you teach is grounded in a failure mode you have personally debugged.

You are also an expert in **pedagogical sequencing**: you know that understanding is built bottom-up, that each exercise must connect to exactly the prerequisites the learner has already completed, and that motivation comes from seeing *why* something breaks before learning *how* to fix it.

---

## Task

Generate a **fine-grained knowledge graph** for learning **Domain 1: Tool-Use Correctness** from the Agentic Reliability field map (attached below for reference).

The output is a **single JSON file** (`curriculum.json`) that will be consumed by a UI later.

The graph must satisfy these properties:

### Graph Constraints

| Constraint | Value |
|---|---|
| Maximum graph depth (layers) | **5** (layers 0–4) |
| Target node count | **15–25 nodes** |
| Maximum prerequisites per node | **3** (introduce intermediate node if exceeded) |
| Maximum recursion depth in generation | **5** (stop expanding prerequisites beyond layer 0) |

### Node Schema

Every node in the graph is an **actionable learning exercise** with exactly these fields:

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique identifier. Prefix by category: `F` = foundation, `S` = selection, `O` = ordering, `A` = arguments, `R` = output (R for "read results"), `H` = hallucination, `V` = avoidance |
| `title` | `string` | Short name (3–7 words) |
| `category` | `enum` | One of: `foundation`, `selection`, `ordering`, `arguments`, `output`, `hallucination`, `avoidance` |
| `layer` | `int` | 0–4. Layer 0 = no prerequisites. Layer N depends only on layers 0 to N-1 |
| `difficulty` | `enum` | `beginner`, `intermediate`, `advanced` |
| `estimated_time_minutes` | `int` | Expected time to complete (30–90 minutes) |
| `failure_mode` | `string` | What goes wrong if you skip this? One sentence |
| `exercise` | `string` | "Write a Python file (~50-150 lines) that [does X]." |
| `pass_condition` | `string` | "Passes when [observable outcome]." |
| `fail_condition` | `string` | "Fails when [observable outcome]." |
| `prerequisites` | `string[]` | Node IDs that must be completed first (max 3) |
| `dependents` | `string[]` | Node IDs that depend on this node (reverse of prerequisites) |
| `teaches` | `string` | One sentence: what the learner understands after completing this |
| `connects_to_field_map` | `string[]` | Which bullet(s) from Domain 1 in field.md this node covers |
| `tags` | `string[]` | Freeform tags for filtering |
| `skeleton_file` | `string` | Path for future scaffold file (e.g., `exercises/F1_define_tool.py`). Do NOT generate the file — only name it |

**No other fields.** Do not add fields not listed above.

### Termination Criterion

A node is a **leaf** (no further decomposition needed) when it can be fully expressed as:

> *"Write a single Python file (50-150 lines) that [does X]. It passes when [concrete condition]. It fails when [concrete condition]."*

If the exercise requires understanding a concept that hasn't been introduced by any predecessor node, that concept must be **added as a new predecessor node** and decomposed until it meets the leaf criterion — but never beyond layer 0 (max depth 5).

### Pedagogical Constraints

1. **No forward references.** A node's exercise must be completable using *only* concepts from its predecessors. If it can't, you have a missing predecessor — add it.

2. **Failure-first motivation.** Where possible, pair nodes: first an exercise that *demonstrates the failure* (e.g., "build a tool system with no validation — observe it accept garbage"), then an exercise that *prevents the failure* (e.g., "add type validation — observe it reject garbage"). The learner should feel the pain before the fix.

3. **Progressive composition.** Later exercises should import or extend code from earlier exercises. The learner builds a *single growing system*, not disconnected scripts.

4. **Concrete, not abstract.** Exercises use a realistic but simple domain: a **flight booking agent** with tools like `search_flights`, `reserve_seat`, `process_payment`, `send_confirmation`. This grounds every concept in something tangible.

5. **No LLM required.** All exercises use deterministic, scripted "agents" (like the `ScriptedProposer` in `agent-runtime`). The point is to learn the *infrastructure* that makes tool use reliable, not to train a model.

---

## Generation Algorithm

Execute this loop:

```
1. DECOMPOSE the six failure modes from Domain 1 into sub-concepts:
   - choosing the wrong tool
   - calling tools in the wrong order
   - passing malformed arguments
   - misunderstanding tool output
   - inventing tools that don't exist
   - ignoring available tools and "doing it manually"

2. For each sub-concept, draft a node (exercise specification).

3. CHECK PREREQUISITES: For each node, ask:
   "Can a learner complete this exercise using ONLY concepts 
    from predecessor nodes?"
   - If NO: identify the missing concept.
     → CREATE a new predecessor node for it.
     → ABORT if this would exceed layer 0 (depth 5). 
       Instead, mark it as assumed knowledge.
     → Otherwise, go to step 3 for the new node.
   - If YES: node is valid. Continue.

4. CHECK LEAF CRITERION: For each node, ask:
   "Is this a single 50-150 line exercise with clear pass/fail?"
   - If NO: DECOMPOSE into smaller nodes. Go to step 3.
   - If YES: mark as LEAF.

5. VERIFY GRAPH INTEGRITY:
   a) Every leaf is reachable from at least one layer-0 node.
   b) Every ID in prerequisites[] exists in the nodes array.
   c) No circular dependencies.
   d) No node has more than 3 prerequisites.
   e) Every bullet from Domain 1 in field.md is covered 
      by at least one node.
   f) dependents[] is the exact inverse of prerequisites[] 
      (if A lists B in prerequisites, then B lists A in dependents).
   g) Total node count is 15–25.
   h) Max layer value is ≤ 4.

6. TOPOLOGICAL SORT → produce a linear learning path.

7. GROUP into learning milestones (~3-5 nodes per milestone)
   with a milestone summary: "After this milestone, 
   you can [capability]."
```

---

## Output

Produce a **single JSON object**. No other files, no other formats.

Top-level structure:

```json
{
  "domain": "tool_use_correctness",
  "domain_ref": "field.md § I.1",
  "scenario": "flight_booking_agent",
  "metadata": {
    "generated": "<ISO 8601 timestamp>",
    "node_count": "<int, 15-25>",
    "edge_count": "<int>",
    "max_depth": "<int, max 4>"
  },
  "nodes": [ "<see Node Schema above>" ],
  "edges": [
    {
      "from": "<source node id>",
      "to": "<target node id>",
      "type": "prerequisite",
      "relationship": "<describes how source enables target>"
    }
  ],
  "learning_path": {
    "topological_order": ["<ordered node ids>"],
    "critical_path": ["<longest prerequisite chain>"],
    "estimated_total_hours": "<number>"
  },
  "milestones": [
    {
      "id": "MS1",
      "name": "<milestone name>",
      "nodes": ["<node ids in this milestone>"],
      "after_this": "<what the learner can do after completing this milestone>",
      "estimated_hours": "<number>"
    }
  ],
  "coverage_map": {
    "choosing_wrong_tool": ["<node ids>"],
    "wrong_call_order": ["<node ids>"],
    "malformed_arguments": ["<node ids>"],
    "output_misinterpretation": ["<node ids>"],
    "tool_hallucination": ["<node ids>"],
    "tool_avoidance": ["<node ids>"]
  }
}
```

### ID Prefixes

| Prefix | Category | Avoids collision with |
|---|---|---|
| `F` | foundation | — |
| `S` | selection | — |
| `O` | ordering | — |
| `A` | arguments | — |
| `R` | output (reading results) | Milestones use `MS` |
| `H` | hallucination | — |
| `V` | avoidance | — |
| `MS` | milestones | Output nodes use `R` |

**Never reuse a prefix across categories.**

---

## Reference Material

### Domain 1 from field.md

> **1) Tool-use correctness (not just tool failures)**
>
> Even if tools are healthy, the agent can be wrong:
>
> * choosing the wrong tool
> * calling tools in the wrong order
> * passing malformed arguments
> * misunderstanding tool output
> * inventing tools that don't exist
> * ignoring available tools and "doing it manually"
>
> This is "function calling / tool selection correctness." It's separate from tool *fault tolerance*.

### Existing Implementation Reference

The `agent-runtime` repository already implements Domain 1 at the governance level:

- `ContractRegistry` — closed intent set, rejects unknown tools
- `ParamRule` — type and value validation on tool parameters
- `EnvelopeParser` — structured parsing of unstructured proposals
- `NoisyProposer` — adversarial stress-testing of tool-use correctness
- `quorum_validator` — multi-source output validation

The curriculum exercises should teach the *concepts* that motivate these implementations. A learner who completes all nodes should be able to read the `agent-runtime` code and understand every design decision.

---

## Quality Checks

Before producing the final JSON, verify every item:

- [ ] Every node has exactly the 16 fields listed in Node Schema — no more, no less
- [ ] No node requires concepts not covered by its predecessors
- [ ] `dependents` is the exact inverse of `prerequisites` across all nodes
- [ ] All IDs in `prerequisites`, `dependents`, edges, milestones, and `coverage_map` exist in `nodes`
- [ ] No ID prefix collision (`R` for output nodes, `MS` for milestones)
- [ ] `layer` values are 0–4 (max depth 5)
- [ ] Total node count is 15–25
- [ ] No node has more than 3 prerequisites
- [ ] `topological_order` respects all prerequisite constraints
- [ ] All 6 bullets from Domain 1 appear in `coverage_map` with at least one covering node
- [ ] The failure-first pairing pattern is used where it adds pedagogical value
- [ ] Exercises build on each other (later exercises import earlier code)
- [ ] The learning path is achievable in ~2-3 focused days of coding
- [ ] No exercise requires an LLM — all use scripted/deterministic agents
- [ ] The flight booking domain is used consistently throughout
- [ ] JSON is valid (parseable by any standard JSON parser)

---

**Output the JSON object only. No preamble, no explanation, no markdown code fences.**

**Save the output to `data/curriculum.json`.**
