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
    seeds: list[str] = ["Capability framing and success criteria"]

    if topic_spec.prerequisites:
        seeds.append("Prerequisite bridge and terminology alignment")

    seeds.extend(
        f"Implement {item.strip()}"
        for item in topic_spec.scope_in
        if item.strip()
    )

    if topic_spec.context_pack is not None:
        seeds.extend(
            f"Deliverable: {outcome.strip()}"
            for outcome in topic_spec.context_pack.required_outcomes
            if outcome.strip()
        )

    seeds.extend(
        [
            "Interface integration strategy",
            "Verification checklist design",
        ]
    )

    deduped: list[str] = []
    seen: set[str] = set()
    for title in seeds:
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(title)

    while len(deduped) < target_nodes:
        deduped.append(f"Applied implementation cycle {len(deduped) + 1}")

    return tuple(deduped[:target_nodes])


def _title_weight(index: int, count: int, title: str) -> float:
    ratio = index / max(1, count - 1)
    weight = 1.0 + (0.4 * ratio)

    keyword_boosts = {
        "integration": 0.25,
        "verification": 0.25,
        "reliability": 0.2,
        "trade-off": 0.15,
        "deliverable": 0.1,
        "architecture": 0.2,
        "orchestration": 0.2,
        "testing": 0.2,
    }
    lowered = title.lower()
    for token, boost in keyword_boosts.items():
        if token in lowered:
            weight += boost

    if index == count - 1:
        weight += 0.15

    return weight


def distribute_minutes(total_minutes: int, titles: tuple[str, ...]) -> tuple[int, ...]:
    count = len(titles)
    if count <= 0:
        return ()

    minimum = min(20, total_minutes // count) if total_minutes >= count else 0

    base_total = minimum * count
    remainder = max(0, total_minutes - base_total)
    weights = [_title_weight(index, count, title) for index, title in enumerate(titles)]
    weight_sum = sum(weights) or 1.0

    increments = [int(remainder * (weight / weight_sum)) for weight in weights]
    distributed = sum(increments)
    if distributed < remainder:
        order = sorted(
            range(count),
            key=lambda idx: (
                -((remainder * (weights[idx] / weight_sum)) - increments[idx]),
                idx,
            ),
        )
        for idx in order[: remainder - distributed]:
            increments[idx] += 1

    minutes = [minimum + extra for extra in increments]

    return tuple(minutes)


def target_nodes(topic_spec: TopicSpec) -> int:
    min_nodes = topic_spec.constraints.node_count_min or 8
    max_nodes = topic_spec.constraints.node_count_max or max(min_nodes, 16)
    if max_nodes < min_nodes:
        max_nodes = min_nodes

    scope_size = len(topic_spec.scope_in)
    return max(min_nodes, min(max_nodes, max(6, scope_size + 3)))


def target_minutes(topic_spec: TopicSpec, titles: tuple[str, ...]) -> tuple[int, ...]:
    node_count = len(titles)
    min_hours = topic_spec.constraints.total_hours_min
    max_hours = topic_spec.constraints.total_hours_max
    if max_hours < min_hours:
        max_hours = min_hours

    total_minutes = int(round(((min_hours + max_hours) / 2.0) * 60.0))
    return distribute_minutes(total_minutes, titles)


def build_generation_spec(raw_topic_spec: dict[str, Any]) -> GenerationSpec:
    topic_spec = TopicSpec.from_mapping(raw_topic_spec)
    count = target_nodes(topic_spec)
    evidence_mode = normalize_evidence_mode(topic_spec.evidence_mode)
    titles = seed_titles(topic_spec, count)

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
        titles=titles,
        minutes=target_minutes(topic_spec, titles),
        misconceptions=topic_spec.misconceptions,
    )
