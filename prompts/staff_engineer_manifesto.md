You are a principal/staff engineer with deep experience building and operating production-grade agentic systems.

Goal:
Write a document called **"Staff Engineer Manifesto for Agentic Systems"** that captures hard-earned, non-obvious engineering wisdom and teaches how to think about the field from first principles.
The document must be fully general and cross-domain: no project-specific assumptions, no repository-specific language, no dependency on local files.

Optional context input:
- Taxonomy (optional): {{paste taxonomy here}}
- System reference doc (optional): {{paste system doc here}}

Output format:
- Return one Markdown document only.
- Target file name: `staff-engineer-manifesto.md`
- Tone: rigorous, practical, direct, zero fluff.
- Audience: engineers aiming for staff-level judgment and delivery reliability.

Critical addition (must include):
Add a strong opening section that teaches:
1. **How to start thinking about agentic engineering correctly**
2. **How to build a first mental map of the field**
3. **What beginners usually misunderstand and how to avoid that**
4. **How to reason in systems (boundaries, invariants, failure modes, evidence)**
5. **How to separate timeless principles from stack/vendor trends**

Hard requirements:
1. Separate content into:
   - **Timeless principles** (cross-stack/domain)
   - **Context-dependent heuristics** (when they apply, when they fail)
2. Include both:
   - **Sourced references** (books/papers/docs with URL)
   - **Expert synthesis** from model knowledge
3. Every claim must be labeled as:
   - `[Reference-backed]`
   - `[Synthesis]`
   - `[Hypothesis]` (if uncertain/emerging)
   Labeling rule:
   - label at paragraph or subsection level, not every sentence.
4. For each major principle include:
   - why it matters
   - failure mode if ignored
   - concrete implementation pattern
   - review questions a staff engineer asks
5. Include explicit sections on:
   - system boundaries and trust assumptions
   - control loops and bounded autonomy
   - development loop blueprint (`design -> implement -> validate -> eval -> observe -> postmortem -> harden`)
   - loop types and when to use them (feature, reliability, incident, evaluation, governance)
   - exit criteria for each loop (what "done" means before moving on)
   - common loop failures and corrective actions
   - tool contracts, side effects, idempotency
   - evaluation/conformance rigor (causal comparisons, regressions)
   - observability, incidents, rollback, safe degradation
   - governance/compliance in high-stakes domains
   - org design, ownership, decision quality
   - learning loops and avoiding cargo-culting patterns
6. Add "red flags and anti-patterns":
   - at least 20 patterns
   - each with detection signal + corrective action
7. Add "decision protocol":
   - step-by-step protocol for major architecture choices
   - required evidence before increasing autonomy
8. Add "staff calibration":
   - mid vs senior vs staff behavioral differences
   - measurable indicators of staff-level performance
9. Add "unfamiliar domain entry playbook":
   - first 24h / 72h / 2 weeks
10. End with:
   - compact checklists: before ship, after incident, quarterly health review
   - prioritized reading list with rationale for each source

Pedagogical requirements (strict):
- The document must teach, not only state conclusions.
- For each major section, enforce this teaching sequence:
  1) concept
  2) intuition
  3) failure case
  4) implementation pattern
  5) exercise
  6) self-check
- For each major section, include two tracks:
  - **Beginner path** (minimum viable understanding)
  - **Advanced path** (staff-level depth)
- Include at least one worked scenario per major section:
  - "bad approach" vs "corrected approach"
- Include active recall questions:
  - 5-7 questions per major section
  - include common wrong answer + correction for each question
- Include practice labs:
  - each lab must include objective, setup, steps, expected artifact, and pass criteria
- Include section-end checkpoint summaries:
  - key takeaways
  - common mistakes
  - what to implement next
- Include an explicit weekly learning cadence:
  - study tasks
  - build tasks
  - evaluation tasks
  - reflection artifacts
- Include a proficiency rubric per major section:
  - novice / competent / staff indicators

Source-of-truth contract (strict):
- If taxonomy is provided:
  - treat taxonomy as source of truth for coverage/depth ("what to learn").
- If system reference is provided:
  - treat system doc as source of truth for operational protocols/contracts ("how to implement/run").
- Manifesto must focus on judgment layer:
  - philosophy, decision quality, tradeoff framing, anti-pattern recognition, escalation logic, staff heuristics.

Non-duplication and delta mode (strict):
- Do not restate existing loop protocols, primitive schemas, or execution plans from provided docs.
- If context docs are provided, produce only the delta:
  - what is missing, underemphasized, or poorly connected.
- Include a required section: **"Delta vs Provided Docs"**
  - table columns:
    1) Manifesto section
    2) Why this is not duplicate
    3) Link-back target in provided docs (if any)
    4) Unique value added
- Overlap rule:
  - if estimated overlap with provided docs exceeds 25%, rewrite to increase uniqueness.

Decision-quality and staff-judgment requirements:
- Include a dedicated section:
  - **"Decision Quality Under Ambiguity"** with:
    - how to frame ambiguous choices,
    - how to set falsifiable assumptions,
    - escalation triggers,
    - stop-building / start-hardening criteria.
- Include a dedicated section:
  - **"Progression Ladder: Junior -> Senior -> Staff"**
    - common failure patterns per level,
    - what changes in decision behavior,
    - observable proof of level transition.

Generality constraints (strict):
- Do not reference any specific project/repository/files/folder structure.
- Do not assume a single stack, framework, or vendor.
- When examples are needed, use neutral placeholders (e.g., "Tool A", "Policy Engine", "Runtime Kernel").
- Include guidance that works for startups, enterprise, and high-stakes regulated contexts.
- Distinguish what is universally true from what is context-dependent.

Mental map requirements:
- Include at least 3 Mermaid diagrams:
  1) field-level mental model (domains + feedback loops)
  2) runtime/governance boundary map
  3) decision/evidence loop (design -> eval -> ops -> learn)
- Keep diagrams syntactically valid and implementation-oriented.

Reference policy:
- Prefer primary/high-signal sources.
- Include URL for each reference.
- Do not fabricate citations.
- If not strongly source-backed, mark as `[Synthesis]` or `[Hypothesis]`.

Quality bar:
- Must read like a staff engineer's internal operating manual.
- Must be directly usable in architecture reviews, design docs, and incident retros.
- Must function as a general "knowledge dump" you could hand to any engineer entering the field.
- Must complement (not replace) taxonomy/system docs when those are provided.
