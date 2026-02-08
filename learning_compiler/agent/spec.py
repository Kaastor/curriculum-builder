"""Topic spec normalization for curriculum generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from learning_compiler.domain import TopicSpec


@dataclass(slots=True, frozen=True)
class GenerationSpec:
    topic_spec: TopicSpec
    topic_label: str
    evidence_mode: str
    strict_mode: bool
    target_nodes: int
    max_prerequisites_per_node: int
    titles: tuple[str, ...]
    minutes: tuple[int, ...]
    misconceptions: tuple[str, ...]


def as_int(value: Any, default: int) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def as_float(value: Any, default: float) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return default


def normalize_evidence_mode(value: Any) -> str:
    mode = str(value or "minimal").strip().lower()
    if mode in {"minimal", "standard", "strict"}:
        return mode
    return "minimal"


def derive_topic_label(topic_spec: TopicSpec) -> str:
    goal = topic_spec.goal
    if len(goal) <= 72:
        return goal
    return goal[:69].rstrip() + "..."


def seed_titles(topic_spec: TopicSpec, target_nodes: int) -> tuple[str, ...]:
    seeds: list[str] = [
        "Goal framing and capability criteria",
        "Prerequisite bridge and terminology",
    ]
    seeds.extend(item.strip() for item in topic_spec.scope_in if item.strip())
    seeds.append("Integrated synthesis and production risk review")

    deduped: list[str] = []
    seen: set[str] = set()
    for title in seeds:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(title)

    while len(deduped) < target_nodes:
        deduped.append(f"Applied synthesis {len(deduped) + 1}")

    return tuple(deduped[:target_nodes])


def distribute_minutes(total_minutes: int, count: int) -> tuple[int, ...]:
    if count <= 0:
        return ()

    base = max(30, total_minutes // count)
    minutes = [base for _ in range(count)]
    remainder = total_minutes - (base * count)

    index = 0
    while remainder > 0:
        minutes[index % count] += 1
        remainder -= 1
        index += 1

    return tuple(minutes)


def target_nodes(topic_spec: TopicSpec) -> int:
    min_nodes = topic_spec.constraints.node_count_min or 8
    max_nodes = topic_spec.constraints.node_count_max or max(min_nodes, 16)
    if max_nodes < min_nodes:
        max_nodes = min_nodes

    scope_size = len(topic_spec.scope_in)
    return max(min_nodes, min(max_nodes, max(6, scope_size + 3)))


def target_minutes(topic_spec: TopicSpec, node_count: int) -> tuple[int, ...]:
    min_hours = topic_spec.constraints.total_hours_min
    max_hours = topic_spec.constraints.total_hours_max
    if max_hours < min_hours:
        max_hours = min_hours

    total_minutes = int(round(((min_hours + max_hours) / 2.0) * 60.0))
    return distribute_minutes(total_minutes, node_count)


def build_generation_spec(raw_topic_spec: dict[str, Any]) -> GenerationSpec:
    topic_spec = TopicSpec.from_mapping(raw_topic_spec)
    count = target_nodes(topic_spec)
    evidence_mode = normalize_evidence_mode(topic_spec.evidence_mode)

    return GenerationSpec(
        topic_spec=topic_spec,
        topic_label=derive_topic_label(topic_spec),
        evidence_mode=evidence_mode,
        strict_mode=evidence_mode == "strict",
        target_nodes=count,
        max_prerequisites_per_node=max(
            1,
            topic_spec.constraints.max_prerequisites_per_node or 3,
        ),
        titles=seed_titles(topic_spec, count),
        minutes=target_minutes(topic_spec, count),
        misconceptions=topic_spec.misconceptions,
    )
