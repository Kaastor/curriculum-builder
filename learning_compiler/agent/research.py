"""Reference selection helpers for generated curriculum nodes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
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
    node_id: str
    node_index: int
    node_title: str
    prerequisites: tuple[str, ...]
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


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _required_resource_count(evidence_mode: str) -> int:
    return 2 if evidence_mode in {"standard", "strict"} else 1


def _infer_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".rst", ".txt", ".json", ".yaml", ".yml"}:
        return "doc"
    if suffix in {".py", ".sh", ".toml"}:
        return "spec"
    return "other"


def _tokenize(text: str) -> set[str]:
    parts = re.findall(r"[a-z0-9]{3,}", text.lower())
    return set(parts)


def _resource_pool(request: ResourceRequest) -> tuple[ResourceSpec, ...]:
    joined_scope = " ".join(request.topic_spec.scope_in)
    context_focus = " ".join(request.topic_spec.context_pack.focus_terms) if request.topic_spec.context_pack else ""
    corpus = f"{request.topic_spec.goal} {joined_scope} {context_focus} {request.node_title}".lower()

    if _contains_any(corpus, ("quantum", "qubit", "qnn", "nisq")):
        return QUANTUM_RESOURCES
    if _contains_any(corpus, ("neural", "machine learning", "optimization", "model")):
        return ML_RESOURCES
    return GENERAL_RESOURCES


class DeterministicResourceResolver:
    """Deterministic in-repo resolver used as the default provider."""

    def resolve(self, request: ResourceRequest) -> list[dict[str, str]]:
        pool = _resource_pool(request)
        resources: list[dict[str, str]] = []
        for index in range(_required_resource_count(request.evidence_mode)):
            selected = pool[min(index, len(pool) - 1)]
            resource: dict[str, str] = {
                "title": selected.title,
                "url": selected.url,
                "kind": selected.kind,
                "role": "definition" if index == 0 else "example",
            }
            if request.evidence_mode == "strict":
                resource["citation"] = selected.citation
            resources.append(resource)
        return resources


class RepoLocalResolver:
    """Resolve local repository materials when context_pack.local_paths is provided."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root.resolve()

    def _candidate_paths(self, request: ResourceRequest) -> list[Path]:
        context = request.topic_spec.context_pack
        if context is None:
            return []

        candidates: set[Path] = set()
        for raw in context.local_paths:
            candidate = Path(raw)
            full_path = (self._repo_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
            if full_path != self._repo_root and self._repo_root not in full_path.parents:
                continue
            if full_path.exists() and full_path.is_file():
                candidates.add(full_path)
        return sorted(candidates, key=lambda item: item.as_posix())

    def _score_path(self, path: Path, request: ResourceRequest) -> int:
        context = request.topic_spec.context_pack
        focus = " ".join(context.focus_terms) if context is not None else ""
        scope = " ".join(request.topic_spec.scope_in)
        outcomes = " ".join(context.required_outcomes) if context is not None else ""
        corpus_tokens = _tokenize(f"{request.topic_spec.goal} {scope} {focus} {outcomes} {request.node_title}")
        path_tokens = _tokenize(path.as_posix())
        return len(corpus_tokens.intersection(path_tokens))

    def resolve(self, request: ResourceRequest) -> list[dict[str, str]]:
        candidates = self._candidate_paths(request)
        if not candidates:
            return []

        ranked = sorted(
            ((self._score_path(path, request), path) for path in candidates),
            key=lambda item: (-item[0], item[1].as_posix()),
        )
        selected = [path for _, path in ranked[: _required_resource_count(request.evidence_mode)]]

        resources: list[dict[str, str]] = []
        for index, path in enumerate(selected):
            relative = path.relative_to(self._repo_root).as_posix()
            resource: dict[str, str] = {
                "title": f"Local reference: {relative}",
                "url": f"local://{relative}",
                "kind": _infer_kind(path),
                "role": "definition" if index == 0 else "example",
            }
            if request.evidence_mode == "strict":
                resource["citation"] = relative
            resources.append(resource)
        return resources


class CompositeResourceResolver:
    """Compose primary + fallback resolver while preserving deterministic order."""

    def __init__(self, primary: ResourceResolver, fallback: ResourceResolver) -> None:
        self._primary = primary
        self._fallback = fallback

    def resolve(self, request: ResourceRequest) -> list[dict[str, str]]:
        required = _required_resource_count(request.evidence_mode)
        merged: list[dict[str, str]] = []
        seen_urls: set[str] = set()

        for source in (self._primary.resolve(request), self._fallback.resolve(request)):
            for resource in source:
                url = resource.get("url")
                if not isinstance(url, str) or url in seen_urls:
                    continue
                seen_urls.add(url)
                merged.append(dict(resource))
                if len(merged) >= required:
                    break
            if len(merged) >= required:
                break

        if merged and required > 1:
            merged[0]["role"] = "definition"
            if len(merged) > 1:
                merged[1]["role"] = "example"

        if request.evidence_mode == "strict":
            for resource in merged:
                resource.setdefault("citation", "deterministic-reference")

        return merged


def default_resource_resolver(topic_spec: TopicSpec, repo_root: Path | None = None) -> ResourceResolver:
    fallback = DeterministicResourceResolver()
    context = topic_spec.context_pack
    if context is None or not context.local_paths:
        return fallback

    root = (repo_root or Path.cwd()).resolve()
    return CompositeResourceResolver(
        primary=RepoLocalResolver(root),
        fallback=fallback,
    )


def build_resources(topic_spec: TopicSpec, node_title: str, evidence_mode: str) -> list[dict[str, str]]:
    """Backward-compatible convenience wrapper around default resolver."""
    resolver = default_resource_resolver(topic_spec)
    return resolver.resolve(
        ResourceRequest(
            topic_spec=topic_spec,
            node_id="N1",
            node_index=0,
            node_title=node_title,
            prerequisites=(),
            evidence_mode=evidence_mode,
        )
    )
