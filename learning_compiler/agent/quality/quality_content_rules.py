"""Content-oriented quality rules for deterministic curriculum scoring."""

from __future__ import annotations

from statistics import median
import re
from typing import Any

from learning_compiler.agent.quality.pedagogy_critic import PedagogyCritique
from learning_compiler.agent.quality.quality_types import QualityDiagnostic
from learning_compiler.domain import TopicSpec
from learning_compiler.validator.helpers import is_number

ACTION_VERBS = (
    "analyze",
    "build",
    "compare",
    "define",
    "design",
    "document",
    "explain",
    "implement",
    "integrate",
    "measure",
    "run",
    "simulate",
    "test",
    "validate",
    "write",
)

MEASURABLE_SIGNALS = (
    "must ",
    "at least",
    "include",
    "pass",
    "threshold",
    "criteria",
)


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{4,}", text.lower()))


def score_resource_relevance(
    nodes: list[dict[str, Any]],
    topic_spec: TopicSpec,
    diagnostics: list[QualityDiagnostic],
) -> int:
    score = 100
    corpus = " ".join((topic_spec.goal, *topic_spec.scope_in)).lower()
    if topic_spec.context_pack is not None:
        corpus += " " + " ".join(topic_spec.context_pack.focus_terms).lower()
    corpus_tokens = _tokens(corpus)
    seen_urls: set[str] = set()
    duplicate_urls = 0
    for node in nodes:
        node_id = str(node.get("id", ""))
        resources = node.get("resources", [])
        if not isinstance(resources, list) or not resources:
            score -= 18
            diagnostics.append(
                QualityDiagnostic(
                    rule_id="resource.missing",
                    severity="high",
                    node_id=node_id,
                    message="Node has no resources.",
                    hard_fail=True,
                )
            )
            continue
        material = " ".join(
            f"{item.get('title', '')} {item.get('url', '')}" for item in resources if isinstance(item, dict)
        ).lower()
        if corpus_tokens and not _tokens(material).intersection(corpus_tokens):
            score -= 8
            diagnostics.append(
                QualityDiagnostic(
                    rule_id="resource.weak_relevance",
                    severity="medium",
                    node_id=node_id,
                    message="Weak overlap between resources and topic context.",
                )
            )
        for resource in resources:
            url = resource.get("url") if isinstance(resource, dict) else None
            if not isinstance(url, str):
                continue
            if url in seen_urls:
                duplicate_urls += 1
            seen_urls.add(url)
    if duplicate_urls > max(2, len(nodes) // 2):
        diagnostics.append(
            QualityDiagnostic(
                rule_id="resource.repetitive_anchor",
                severity="medium",
                message="Resource anchors are highly repetitive across nodes.",
            )
        )
        score -= 10
    return max(0, score)


def score_mastery_actionability(nodes: list[dict[str, Any]], diagnostics: list[QualityDiagnostic]) -> int:
    score = 100
    for node in nodes:
        node_id = str(node.get("id", ""))
        mastery = node.get("mastery_check", {})
        task = str(mastery.get("task", "")).strip().lower() if isinstance(mastery, dict) else ""
        criteria = (
            str(mastery.get("pass_criteria", "")).strip().lower()
            if isinstance(mastery, dict)
            else ""
        )
        if len(task) < 20 or not any(f"{verb} " in task for verb in ACTION_VERBS):
            score -= 12
            diagnostics.append(
                QualityDiagnostic(
                    rule_id="mastery.non_actionable_task",
                    severity="high",
                    node_id=node_id,
                    message="Mastery task is not specific enough for implementation.",
                    hard_fail=True,
                )
            )
        if len(criteria) < 20 or not any(token in criteria for token in MEASURABLE_SIGNALS):
            score -= 12
            diagnostics.append(
                QualityDiagnostic(
                    rule_id="mastery.non_measurable_criteria",
                    severity="high",
                    node_id=node_id,
                    message="Pass criteria lacks measurable acceptance signals.",
                    hard_fail=True,
                )
            )
    return max(0, score)


def score_effort_coherence(nodes: list[dict[str, Any]], diagnostics: list[QualityDiagnostic]) -> int:
    score = 100
    estimates = [float(node.get("estimate_minutes")) for node in nodes if is_number(node.get("estimate_minutes"))]
    if not estimates:
        return 0
    unique = set(estimates)
    if len(estimates) >= 6 and len(unique) <= 2:
        score -= 25
        diagnostics.append(
            QualityDiagnostic(
                rule_id="effort.flat_distribution",
                severity="medium",
                message="Estimate distribution is too flat for curriculum size.",
            )
        )
    med = median(estimates)
    if med > 0:
        outliers = [item for item in estimates if item > med * 3.0]
        if outliers:
            score -= 10
            diagnostics.append(
                QualityDiagnostic(
                    rule_id="effort.outlier",
                    severity="low",
                    message="Detected very large estimate outliers.",
                )
            )
    return max(0, score)


def score_redundancy(nodes: list[dict[str, Any]], diagnostics: list[QualityDiagnostic]) -> int:
    score = 100
    title_prefixes = {
        " ".join(re.findall(r"[a-z0-9]+", str(node.get("title", "")).lower())[:5]) for node in nodes
    }
    if len(nodes) >= 6 and len(title_prefixes) <= max(2, len(nodes) // 3):
        score -= 25
        diagnostics.append(
            QualityDiagnostic(
                rule_id="redundancy.title_repetition",
                severity="medium",
                message="Node titles are overly repetitive.",
            )
        )
    return max(0, score)


def score_learner_coherence(
    pedagogy: PedagogyCritique,
    diagnostics: list[QualityDiagnostic],
) -> int:
    score = 100
    for item in pedagogy.diagnostics:
        if item.rule_id == "learner.hidden_prerequisite":
            diagnostics.append(
                QualityDiagnostic(
                    rule_id=item.rule_id,
                    severity=item.severity,
                    node_id=item.node_id,
                    message=item.message,
                    hard_fail=True,
                )
            )
            score -= 25
        elif item.severity in {"high", "critical"}:
            score -= 15
        elif item.severity == "medium":
            score -= 8
        else:
            score -= 3
    return max(0, score)
