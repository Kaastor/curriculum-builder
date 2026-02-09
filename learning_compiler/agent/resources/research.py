"""Backward-compatible facade for resource resolver contracts."""

from learning_compiler.agent.resource_catalog import ResourceSpec
from learning_compiler.agent.resource_resolvers import (
    CompositeResourceResolver,
    DeterministicResourceResolver,
    RepoLocalResolver,
    ResourceRequest,
    ResourceResolver,
    build_resources,
    default_resource_resolver,
)

__all__ = [
    "CompositeResourceResolver",
    "DeterministicResourceResolver",
    "RepoLocalResolver",
    "ResourceRequest",
    "ResourceResolver",
    "ResourceSpec",
    "build_resources",
    "default_resource_resolver",
]

