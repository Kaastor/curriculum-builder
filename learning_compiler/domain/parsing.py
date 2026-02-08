"""Parsing helpers converting mappings into typed domain documents."""

from __future__ import annotations

from typing import Any

from learning_compiler.domain.models import (
    Curriculum,
    CurriculumNode,
    MasteryCheck,
    OpenQuestion,
    Resource,
    TopicSpec,
)


def _string_tuple(values: Any) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()
    return tuple(str(item).strip() for item in values if isinstance(item, str) and item.strip())


def parse_topic_spec(payload: dict[str, Any]) -> TopicSpec:
    return TopicSpec.from_mapping(payload)


def parse_curriculum(payload: dict[str, Any]) -> Curriculum:
    nodes_raw = payload.get("nodes", [])
    open_questions_raw = payload.get("open_questions", [])

    nodes: list[CurriculumNode] = []
    if isinstance(nodes_raw, list):
        for node in nodes_raw:
            if not isinstance(node, dict):
                continue
            mastery_raw = node.get("mastery_check", {})
            mastery = MasteryCheck(
                task=str(mastery_raw.get("task", "")).strip()
                if isinstance(mastery_raw, dict)
                else "",
                pass_criteria=str(mastery_raw.get("pass_criteria", "")).strip()
                if isinstance(mastery_raw, dict)
                else "",
            )
            resources_raw = node.get("resources", [])
            resources: list[Resource] = []
            if isinstance(resources_raw, list):
                for resource in resources_raw:
                    if not isinstance(resource, dict):
                        continue
                    resources.append(
                        Resource(
                            title=str(resource.get("title", "")).strip(),
                            url=str(resource.get("url", "")).strip(),
                            kind=str(resource.get("kind", "")).strip(),
                            role=str(resource.get("role", "")).strip(),
                            citation=(
                                str(resource["citation"]).strip()
                                if isinstance(resource.get("citation"), str)
                                and str(resource.get("citation", "")).strip()
                                else None
                            ),
                        )
                    )
            estimate_raw = node.get("estimate_minutes", 0)
            if isinstance(estimate_raw, bool):
                estimate_minutes = 0.0
            elif isinstance(estimate_raw, (int, float)):
                estimate_minutes = float(estimate_raw)
            else:
                estimate_minutes = 0.0

            confidence_raw = node.get("estimate_confidence")
            confidence = (
                float(confidence_raw)
                if isinstance(confidence_raw, (int, float)) and not isinstance(confidence_raw, bool)
                else None
            )
            nodes.append(
                CurriculumNode(
                    id=str(node.get("id", "")).strip(),
                    title=str(node.get("title", "")).strip(),
                    capability=str(node.get("capability", "")).strip(),
                    prerequisites=_string_tuple(node.get("prerequisites")),
                    core_ideas=_string_tuple(node.get("core_ideas")),
                    pitfalls=_string_tuple(node.get("pitfalls")),
                    mastery_check=mastery,
                    estimate_minutes=estimate_minutes,
                    resources=tuple(resources),
                    estimate_confidence=confidence,
                )
            )

    open_questions: list[OpenQuestion] = []
    if isinstance(open_questions_raw, list):
        for item in open_questions_raw:
            if not isinstance(item, dict):
                continue
            open_questions.append(
                OpenQuestion(
                    question=str(item.get("question", "")).strip(),
                    related_nodes=_string_tuple(item.get("related_nodes")),
                    status=str(item.get("status", "")).strip(),
                )
            )

    return Curriculum(
        topic=str(payload.get("topic", "")).strip(),
        nodes=tuple(nodes),
        open_questions=tuple(open_questions),
    )
