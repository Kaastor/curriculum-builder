"""Node construction helpers for curriculum generation."""

from __future__ import annotations

import re
from enum import Enum

from learning_compiler.agent.research import ResourceRequest, ResourceResolver
from learning_compiler.agent.spec import GenerationSpec
from learning_compiler.domain import CurriculumNode, MasteryCheck, Resource


class NodeStage(str, Enum):
    FOUNDATION = "foundation"
    APPLICATION = "application"
    INTEGRATION = "integration"
    VALIDATION = "validation"


def _stage_for_index(index: int, total: int) -> NodeStage:
    if total <= 3:
        return (NodeStage.FOUNDATION, NodeStage.APPLICATION, NodeStage.VALIDATION)[
            min(index, 2)
        ]
    if index <= max(1, total // 4):
        return NodeStage.FOUNDATION
    if index <= max(2, (total * 2) // 4):
        return NodeStage.APPLICATION
    if index <= max(3, (total * 3) // 4):
        return NodeStage.INTEGRATION
    return NodeStage.VALIDATION


def node_prerequisites(index: int, total: int, max_prereq: int) -> tuple[str, ...]:
    if index == 0:
        return ()

    stage = _stage_for_index(index, total)
    prereqs: list[str] = [f"N{index}"]
    if max_prereq >= 2 and index >= 3 and stage in {NodeStage.INTEGRATION, NodeStage.VALIDATION}:
        prereqs.append(f"N{index - 1}")
    if max_prereq >= 3 and index >= 5 and stage == NodeStage.VALIDATION:
        prereqs.append(f"N{index - 3}")

    deduped: list[str] = []
    seen: set[str] = set()
    for prereq in prereqs:
        if prereq in seen:
            continue
        seen.add(prereq)
        deduped.append(prereq)
    return tuple(deduped[:max_prereq])


def node_capability(title: str, stage: NodeStage) -> str:
    cleaned = re.sub(r"\s+", " ", title).strip().lower()
    if stage == NodeStage.FOUNDATION:
        return f"Define {cleaned} with precise concepts and assumptions."
    if stage == NodeStage.APPLICATION:
        return f"Implement {cleaned} in a runnable workflow."
    if stage == NodeStage.INTEGRATION:
        return f"Integrate {cleaned} with prior components."
    return f"Validate {cleaned} end-to-end with explicit quality criteria and evidence."


def node_core_ideas(title: str, stage: NodeStage) -> tuple[str, ...]:
    lower = title.lower()
    stage_idea = {
        NodeStage.FOUNDATION: "Vocabulary and conceptual boundaries for reliable reasoning.",
        NodeStage.APPLICATION: "Implementation mechanics and failure surface of the approach.",
        NodeStage.INTEGRATION: "Dependency interactions and coupling management across nodes.",
        NodeStage.VALIDATION: "Verification criteria, regression checks, and evidence traceability.",
    }[stage]
    return (
        f"Core mechanism of {lower}.",
        f"Assumptions and constraints behind {lower}.",
        stage_idea,
    )


def node_pitfalls(index: int, misconceptions: tuple[str, ...], stage: NodeStage) -> tuple[str, ...]:
    if misconceptions:
        current = misconceptions[index % len(misconceptions)]
        nxt = misconceptions[(index + 1) % len(misconceptions)]
        return (current, nxt)

    stage_pitfall = {
        NodeStage.FOUNDATION: "Skipping precise definitions and relying on vague intuition.",
        NodeStage.APPLICATION: "Implementing quickly without evaluating constraints and edge cases.",
        NodeStage.INTEGRATION: "Combining components without explicit interface contracts.",
        NodeStage.VALIDATION: "Declaring success without reproducible quality checks.",
    }[stage]
    return (
        stage_pitfall,
        "Confusing familiarity with demonstrated mastery.",
    )


def _outcome_hint(spec: GenerationSpec, index: int) -> str:
    context = spec.topic_spec.context_pack
    if context is None or not context.required_outcomes:
        return "produce a concrete artifact"
    outcome = context.required_outcomes[index % len(context.required_outcomes)]
    return f"produce `{outcome}`"


def node_mastery(
    node_id: str,
    title: str,
    stage: NodeStage,
    spec: GenerationSpec,
) -> MasteryCheck:
    outcome_hint = _outcome_hint(spec, int(node_id[1:]) - 1)
    local_hint = ""
    context = spec.topic_spec.context_pack
    if context is not None and context.local_paths:
        anchor = context.local_paths[(int(node_id[1:]) - 1) % len(context.local_paths)]
        local_hint = f" using `{anchor}` as a primary reference"

    if stage == NodeStage.FOUNDATION:
        task = (
            f"Write a concise technical note for {title}{local_hint} and {outcome_hint} "
            "that states assumptions and one counterexample."
        )
        criteria = (
            "Pass criteria: must include precise definitions, explicit assumptions, "
            "and one counterexample that demonstrates a real boundary condition."
        )
    elif stage == NodeStage.APPLICATION:
        task = (
            f"Implement a minimal working example for {title}{local_hint}, execute it, "
            "and document one failure mode with mitigation."
        )
        criteria = (
            "Pass criteria: implementation must run successfully, include interpretable "
            "output, and document mitigation for the stated failure mode."
        )
    elif stage == NodeStage.INTEGRATION:
        task = (
            f"Integrate {title} with outputs from prerequisite nodes{local_hint}, then "
            "write an interface decision record covering trade-offs."
        )
        criteria = (
            "Pass criteria: integration must be functional, dependencies must be explicit, "
            "and trade-offs must include concrete evidence."
        )
    else:
        task = (
            f"Run a verification pass for {title}{local_hint}: include tests, a quality "
            "checklist, and a short risk memo with next actions."
        )
        criteria = (
            "Pass criteria: include tests/checks, explicit acceptance criteria, and a risk memo. "
            "Failures must be explained and next actions prioritized."
        )

    return MasteryCheck(task=task, pass_criteria=criteria)


def build_node(
    index: int,
    spec: GenerationSpec,
    resolver: ResourceResolver,
    used_resource_urls: tuple[str, ...] = (),
) -> CurriculumNode:
    node_id = f"N{index + 1}"
    title = spec.titles[index]
    stage = _stage_for_index(index, spec.target_nodes)
    prerequisites = node_prerequisites(index, spec.target_nodes, spec.max_prerequisites_per_node)

    resource_dicts = resolver.resolve(
        ResourceRequest(
            topic_spec=spec.topic_spec,
            node_id=node_id,
            node_index=index,
            node_title=title,
            prerequisites=prerequisites,
            evidence_mode=spec.evidence_mode,
            used_resource_urls=used_resource_urls,
        )
    )
    resources = tuple(
        Resource(
            title=item["title"],
            url=item["url"],
            kind=item["kind"],
            role=item["role"],
            citation=item.get("citation"),
        )
        for item in resource_dicts
    )

    confidence = round(min(0.9, 0.6 + index * 0.025), 2) if spec.strict_mode else None

    return CurriculumNode(
        id=node_id,
        title=title,
        capability=node_capability(title, stage),
        prerequisites=prerequisites,
        core_ideas=node_core_ideas(title, stage),
        pitfalls=node_pitfalls(index, spec.misconceptions, stage),
        mastery_check=node_mastery(node_id, title, stage, spec),
        estimate_minutes=spec.minutes[index],
        resources=resources,
        estimate_confidence=confidence,
    )
