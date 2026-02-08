"""Agent-owned curriculum generation from topic spec."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from learning_compiler.agent.research import build_resources


def _as_int(value: Any, default: int) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def _as_float(value: Any, default: float) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return default


def _derive_topic_label(topic_spec: dict[str, Any]) -> str:
    goal = str(topic_spec.get("goal", "Learning Topic")).strip()
    if len(goal) <= 72:
        return goal
    return goal[:69].rstrip() + "..."


def _seed_titles(topic_spec: dict[str, Any], target_nodes: int) -> list[str]:
    scope_in = topic_spec.get("scope_in", [])
    seeds: list[str] = [
        "Goal framing and capability criteria",
        "Prerequisite bridge and terminology",
    ]
    seeds.extend(str(item).strip() for item in scope_in if isinstance(item, str) and item.strip())
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

    return deduped[:target_nodes]


def _distribute_minutes(total_minutes: int, count: int) -> list[int]:
    if count <= 0:
        return []

    base = max(30, total_minutes // count)
    minutes = [base for _ in range(count)]
    remainder = total_minutes - (base * count)

    index = 0
    while remainder > 0:
        minutes[index % count] += 1
        remainder -= 1
        index += 1

    return minutes


def _node_prerequisites(index: int, max_prereq: int) -> list[str]:
    if index == 0:
        return []

    prereqs = [f"N{index}"]
    if max_prereq >= 2 and index > 1 and index % 3 == 0:
        prereqs.append(f"N{index - 1}")
    if max_prereq >= 3 and index > 4 and index % 5 == 0:
        prereqs.append(f"N{index - 3}")
    return prereqs[:max_prereq]


def _node_core_ideas(title: str) -> list[str]:
    lower = title.lower()
    return [
        f"Core mechanism of {lower}.",
        f"Assumptions and constraints behind {lower}.",
        f"How {lower} contributes to the end-goal capability.",
    ]


def _node_pitfalls(index: int, misconceptions: list[str]) -> list[str]:
    if misconceptions:
        current = misconceptions[index % len(misconceptions)]
        nxt = misconceptions[(index + 1) % len(misconceptions)]
        return [current, nxt]

    return [
        "Using intuition without validating assumptions.",
        "Confusing familiarity with demonstrated mastery.",
    ]


def _normalize_evidence_mode(value: Any) -> str:
    mode = str(value or "minimal").strip().lower()
    if mode in {"minimal", "standard", "strict"}:
        return mode
    return "minimal"


def _target_nodes(topic_spec: dict[str, Any]) -> int:
    constraints = topic_spec.get("constraints", {})
    min_nodes = _as_int(constraints.get("node_count_min"), 8)
    max_nodes = _as_int(constraints.get("node_count_max"), max(min_nodes, 16))
    if max_nodes < min_nodes:
        max_nodes = min_nodes

    scope_in = topic_spec.get("scope_in", [])
    scope_size = len(scope_in) if isinstance(scope_in, list) else 0
    return max(min_nodes, min(max_nodes, max(6, scope_size + 3)))


def _target_minutes(topic_spec: dict[str, Any], node_count: int) -> list[int]:
    constraints = topic_spec.get("constraints", {})
    min_hours = _as_float(constraints.get("total_hours_min"), 8.0)
    max_hours = _as_float(constraints.get("total_hours_max"), 40.0)
    if max_hours < min_hours:
        max_hours = min_hours

    total_minutes = int(round(((min_hours + max_hours) / 2.0) * 60.0))
    return _distribute_minutes(total_minutes, node_count)


def _extract_misconceptions(topic_spec: dict[str, Any]) -> list[str]:
    misconceptions = topic_spec.get("misconceptions")
    if not isinstance(misconceptions, list):
        return []

    return [
        item.strip()
        for item in misconceptions
        if isinstance(item, str) and item.strip()
    ]


def _node_capability(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", title).strip().lower()
    return f"Explain and apply {cleaned} toward the topic goal with explicit trade-off reasoning."


def generate_curriculum(topic_spec: dict[str, Any]) -> dict[str, Any]:
    target_nodes = _target_nodes(topic_spec)
    minutes = _target_minutes(topic_spec, target_nodes)

    constraints = topic_spec.get("constraints", {})
    max_prereq = max(1, _as_int(constraints.get("max_prerequisites_per_node"), 3))
    evidence_mode = _normalize_evidence_mode(topic_spec.get("evidence_mode"))
    strict_mode = evidence_mode == "strict"

    titles = _seed_titles(topic_spec, target_nodes)
    misconceptions = _extract_misconceptions(topic_spec)

    nodes: list[dict[str, Any]] = []
    for idx, title in enumerate(titles):
        node_id = f"N{idx + 1}"
        node: dict[str, Any] = {
            "id": node_id,
            "title": title,
            "capability": _node_capability(title),
            "prerequisites": _node_prerequisites(idx, max_prereq),
            "core_ideas": _node_core_ideas(title),
            "pitfalls": _node_pitfalls(idx, misconceptions),
            "mastery_check": {
                "task": f"Teach back {title} with one worked example and one failure-mode analysis.",
                "pass_criteria": "Explanation is correct, trade-offs are explicit, and reasoning is evidence-backed.",
            },
            "estimate_minutes": minutes[idx],
            "resources": build_resources(topic_spec, title, evidence_mode),
        }

        if strict_mode:
            node["estimate_confidence"] = round(min(0.9, 0.6 + idx * 0.025), 2)

        nodes.append(node)

    curriculum: dict[str, Any] = {
        "topic": _derive_topic_label(topic_spec),
        "nodes": nodes,
    }

    if strict_mode:
        tail = [f"N{max(1, target_nodes - 1)}", f"N{target_nodes}"]
        curriculum["open_questions"] = [
            {
                "question": "Which claims remain weakly evidenced or contradictory for this topic under current references?",
                "related_nodes": tail,
                "status": "open",
            }
        ]

    return curriculum


def generate_curriculum_file(topic_spec_path: Path, curriculum_path: Path) -> dict[str, Any]:
    topic_spec = json.loads(topic_spec_path.read_text(encoding="utf-8"))
    if not isinstance(topic_spec, dict):
        raise SystemExit(f"topic_spec must be an object: {topic_spec_path}")

    curriculum = generate_curriculum(topic_spec)
    curriculum_path.parent.mkdir(parents=True, exist_ok=True)
    curriculum_path.write_text(json.dumps(curriculum, indent=2) + "\n", encoding="utf-8")
    return curriculum
