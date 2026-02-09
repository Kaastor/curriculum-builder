# ADR-0003: Provider-Agnostic Structured LLM Client

- Status: Accepted
- Date: 2026-02-09

## Context

Generation should run in multiple environments:
- local codex CLI execution
- remote API-backed execution
- deterministic internal mode for tests

Without a common structured contract, provider switching causes behavior drift and parsing errors.

## Decision

Define a provider-agnostic `LLMClient` contract returning structured JSON, with strict schema enforcement at provider boundaries.

Implemented in:
- `learning_compiler/agent/llm_client.py`
- `learning_compiler/agent/model_policy.py`

## Consequences

Positive:
- common proposer/repair integration path
- controlled retries/timeouts across providers
- strong parse guarantees through strict schemas

Negative:
- schema maintenance overhead
- provider-specific failure handling complexity

## Alternatives Considered

- Provider-specific ad-hoc parsing in each stage:
  - rejected due to duplicated logic and reliability risk.
