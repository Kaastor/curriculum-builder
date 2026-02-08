"""Reference selection helpers for generated curriculum nodes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from learning_compiler.domain import TopicSpec


@dataclass(slots=True, frozen=True)
class ResourceSpec:
    title: str
    url: str
    kind: str
    citation: str


@dataclass(slots=True, frozen=True)
class ResourceRequest:
    topic_spec: TopicSpec
    node_title: str
    evidence_mode: str


class ResourceResolver(Protocol):
    """Contract for resource selection implementations."""

    def resolve(self, request: ResourceRequest) -> list[dict[str, str]]:
        """Return normalized resources for one node."""


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
    ResourceSpec(
        title="Barren plateaus in quantum neural network training landscapes",
        url="https://www.nature.com/articles/s41467-018-07090-4",
        kind="paper",
        citation="Main result",
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
    ResourceSpec(
        title="Qiskit Machine Learning VQC",
        url="https://qiskit-community.github.io/qiskit-machine-learning/stubs/qiskit_machine_learning.algorithms.VQC.html",
        kind="doc",
        citation="API reference",
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


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _resource_pool(request: ResourceRequest) -> tuple[ResourceSpec, ...]:
    joined_scope = " ".join(request.topic_spec.scope_in)
    corpus = f"{request.topic_spec.goal} {joined_scope} {request.node_title}".lower()

    if _contains_any(corpus, ("quantum", "qubit", "qnn", "nisq")):
        return QUANTUM_RESOURCES
    if _contains_any(corpus, ("neural", "machine learning", "optimization", "model")):
        return ML_RESOURCES
    return GENERAL_RESOURCES


class DeterministicResourceResolver:
    """Deterministic in-repo resolver used as the default provider."""

    def resolve(self, request: ResourceRequest) -> list[dict[str, str]]:
        pool = _resource_pool(request)

        definition = pool[0]
        example = pool[1] if len(pool) > 1 else pool[0]

        resources: list[dict[str, str]] = [
            {
                "title": definition.title,
                "url": definition.url,
                "kind": definition.kind,
                "role": "definition",
            }
        ]

        if request.evidence_mode in {"standard", "strict"}:
            resources.append(
                {
                    "title": example.title,
                    "url": example.url,
                    "kind": example.kind,
                    "role": "example",
                }
            )

        if request.evidence_mode == "strict":
            for resource in resources:
                if resource["title"] == definition.title:
                    resource["citation"] = definition.citation
                else:
                    resource["citation"] = example.citation

        return resources


def build_resources(topic_spec: TopicSpec, node_title: str, evidence_mode: str) -> list[dict[str, str]]:
    """Backward-compatible convenience wrapper around default resolver."""
    resolver = DeterministicResourceResolver()
    return resolver.resolve(
        ResourceRequest(
            topic_spec=topic_spec,
            node_title=node_title,
            evidence_mode=evidence_mode,
        )
    )
