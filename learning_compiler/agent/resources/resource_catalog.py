"""Deterministic reference catalogs and corpus-to-pool matching."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ResourceSpec:
    title: str
    url: str
    kind: str
    citation: str


QUANTUM_RESOURCES = (
    ResourceSpec(
        title="Quantum Computation and Quantum Information (Nielsen & Chuang)",
        url="https://doi.org/10.1017/CBO9780511976667",
        kind="book",
        citation="Chapter 2",
    ),
    ResourceSpec(
        title="Variational Quantum Algorithms",
        url="https://arxiv.org/abs/2012.09265",
        kind="paper",
        citation="Sections 2-3",
    ),
)

ML_RESOURCES = (
    ResourceSpec(
        title="Deep Learning (Goodfellow, Bengio, Courville)",
        url="https://www.deeplearningbook.org/",
        kind="book",
        citation="Chapters 6-8",
    ),
    ResourceSpec(
        title="PennyLane Demo: Variational classifier",
        url="https://pennylane.ai/qml/demos/tutorial_variational_classifier",
        kind="doc",
        citation="Demo implementation",
    ),
)

GENERAL_RESOURCES = (
    ResourceSpec(
        title="Stanford Encyclopedia of Philosophy",
        url="https://plato.stanford.edu/",
        kind="doc",
        citation="Relevant entry",
    ),
    ResourceSpec(
        title="Wikipedia",
        url="https://en.wikipedia.org/",
        kind="doc",
        citation="Relevant article",
    ),
)

AGENTIC_SYSTEM_RESOURCES = (
    ResourceSpec(
        title="Designing LLM Agentic Workflows",
        url="https://www.anthropic.com/engineering/building-effective-agents",
        kind="doc",
        citation="Workflow patterns section",
    ),
    ResourceSpec(
        title="OpenAI Cookbook: Structured Outputs",
        url="https://cookbook.openai.com/",
        kind="doc",
        citation="JSON schema generation examples",
    ),
    ResourceSpec(
        title="Google SRE Workbook",
        url="https://sre.google/workbook/table-of-contents/",
        kind="book",
        citation="SLO and incident response chapters",
    ),
)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def resource_pool_for_corpus(corpus: str) -> tuple[ResourceSpec, ...]:
    lowered = corpus.lower()
    if _contains_any(lowered, ("quantum", "qubit", "qnn", "nisq")):
        return QUANTUM_RESOURCES
    if _contains_any(lowered, ("neural", "machine learning", "optimization", "model")):
        return ML_RESOURCES
    if _contains_any(lowered, ("agent", "orchestration", "reliability", "validator", "dag")):
        return AGENTIC_SYSTEM_RESOURCES
    return GENERAL_RESOURCES

