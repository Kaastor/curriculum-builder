"""Node construction helpers for curriculum generation."""

from __future__ import annotations

import re

from learning_compiler.agent.research import ResourceRequest, ResourceResolver
from learning_compiler.agent.spec import GenerationSpec
from learning_compiler.domain import CurriculumNode, MasteryCheck, Resource


def node_prerequisites(index: int, max_prereq: int) -> tuple[str, ...]:
    if index == 0:
        return ()

    prereqs = [f"N{index}"]
    if max_prereq >= 2 and index > 1 and index % 3 == 0:
        prereqs.append(f"N{index - 1}")
    if max_prereq >= 3 and index > 4 and index % 5 == 0:
        prereqs.append(f"N{index - 3}")
    return tuple(prereqs[:max_prereq])


def node_capability(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", title).strip().lower()
    return f"Explain and apply {cleaned} toward the topic goal with explicit trade-off reasoning."


def node_core_ideas(title: str) -> tuple[str, ...]:
    lower = title.lower()
    return (
        f"Core mechanism of {lower}.",
        f"Assumptions and constraints behind {lower}.",
        f"How {lower} contributes to the end-goal capability.",
    )


def node_pitfalls(index: int, misconceptions: tuple[str, ...]) -> tuple[str, ...]:
    if misconceptions:
        current = misconceptions[index % len(misconceptions)]
        nxt = misconceptions[(index + 1) % len(misconceptions)]
        return (current, nxt)

    return (
        "Using intuition without validating assumptions.",
        "Confusing familiarity with demonstrated mastery.",
    )


def build_node(
    index: int,
    spec: GenerationSpec,
    resolver: ResourceResolver,
) -> CurriculumNode:
    node_id = f"N{index + 1}"
    title = spec.titles[index]

    resource_dicts = resolver.resolve(
        ResourceRequest(
            topic_spec=spec.topic_spec,
            node_title=title,
            evidence_mode=spec.evidence_mode,
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
        capability=node_capability(title),
        prerequisites=node_prerequisites(index, spec.max_prerequisites_per_node),
        core_ideas=node_core_ideas(title),
        pitfalls=node_pitfalls(index, spec.misconceptions),
        mastery_check=MasteryCheck(
            task=f"Teach back {title} with one worked example and one failure-mode analysis.",
            pass_criteria="Explanation is correct, trade-offs are explicit, and reasoning is evidence-backed.",
        ),
        estimate_minutes=spec.minutes[index],
        resources=resources,
        estimate_confidence=confidence,
    )
