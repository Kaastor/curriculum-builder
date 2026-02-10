You are a Staff+ Agentic Systems Architect and Learning Design expert.

Task:
Given the taxonomy document below, produce a new companion document that helps me internalize the system deeply and operationally.

Input taxonomy:
{{PASTE docs/learning/agentic-taxonomy.md HERE}}

Primary objective:
Create a document that optimizes these 5 outcomes:
1) Stable mental model
2) Explicit cross-topic relationships
3) Canonical implementation primitives
4) Lower ambiguity during design decisions
5) Reliable transfer to unfamiliar domains

Critical constraints:
- Do NOT duplicate the taxonomy leaf content.
- Taxonomy remains source-of-truth for topic depth.
- Reference taxonomy by IDs (e.g., T2.2.4, T3.4.5) everywhere relevant.
- Produce practical engineering guidance, not motivational text.
- Use precise language, explicit assumptions, and decision criteria.
- Every Mermaid diagram must be valid Mermaid syntax.

Output file target:
`docs/learning/agentic-system-reference.md`

Required structure (exact sections):
1. Purpose and How to Use This Document
2. Canonical Mental Model (single-page compressed model)
3. End-to-End System Architecture (boundaries, responsibilities, invariants)
4. Cross-Topic Interaction Map (how planning/runtime/safety/evals/ops influence each other)
5. Canonical Primitive Catalog
   - data contracts
   - control-loop contracts
   - tool contracts
   - policy contracts
   - evaluation contracts
   - observability contracts
6. Design Decision Protocol
   - step-by-step decision flow
   - tradeoff matrix
   - failure-first review checklist
7. Unfamiliar Domain Transfer Protocol
   - 24h / 72h / 2-week execution plan
   - assumption ledger
   - risk decomposition
   - evidence required before autonomy increase
8. Internalization System
   - active recall questions
   - weekly drills
   - artifact-first learning loop
   - "definition of understood" criteria
9. 30/60/90 Day Application Plan linked to taxonomy IDs
10. Appendix
   - mapping table: section -> taxonomy IDs
   - glossary of canonical terms used in this document only

Diagram requirements:
- Include at least 6 Mermaid diagrams:
  1) global control loop
  2) architecture boundaries
  3) decision protocol flow
  4) failure classification + response path
  5) domain transfer workflow
  6) learning/internalization loop
- Diagrams must use only standard Mermaid features and compile cleanly.

Quality bar:
- Staff-level documentation quality.
- Dense, rigorous, implementation-oriented.
- Must be directly usable as a reference while building/reviewing real systems.

Final output:
Return only the full markdown content for `docs/learning/agentic-system-reference.md`.
