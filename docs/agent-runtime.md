# Agent Runtime

This document describes generation runtime behavior, provider modes, and troubleshooting.

## 1. Runtime Components

- `learning_compiler/agent/generator.py`
  - entrypoint for curriculum generation and trace persistence.
- `learning_compiler/agent/planning/spec.py`
  - normalization from raw topic spec to `GenerationSpec`.
- `learning_compiler/agent/optimizer.py`
  - loop controller for iterative optimization.
- `learning_compiler/agent/planning/proposer.py`
  - initial draft proposal stage.
- `learning_compiler/agent/quality/pedagogy_critic.py`
  - deterministic learner-path critique.
- `learning_compiler/agent/quality/model.py`
  - deterministic multi-dimension score model.
- `learning_compiler/agent/quality/planner.py`
  - diagnostics to repair actions.
- `learning_compiler/agent/quality/executor.py`
  - deterministic patches + provider-mediated repair pass.
- `learning_compiler/agent/llm/client.py`
  - public facade and provider factory.
- `learning_compiler/agent/llm/remote.py`
  - remote Responses API provider implementation.
- `learning_compiler/agent/llm/codex.py`
  - `codex exec` provider implementation.
- `learning_compiler/agent/llm/schema.py` and `learning_compiler/agent/llm/prompt.py`
  - strict schema and prompt/parse helpers reused by provider adapters.

## 2. End-to-End Runtime Flow

```mermaid
flowchart TD
    A[topic_spec.json] --> B[build_generation_spec]
    B --> C[initialize model policy]
    C --> D[build provider client]
    D --> E[optimize loop]
    E --> F[best curriculum]
    E --> G[optimization trace]
    F --> H[write curriculum.json]
    G --> I[write optimization_trace.json]
```

## 3. Optimization Loop

```mermaid
sequenceDiagram
    participant Proposer
    participant Critic
    participant Judge
    participant Planner
    participant Repair

    Proposer->>Proposer: build draft curriculum
    loop iteration 1..N
        Critic->>Critic: learner-path diagnostics
        Judge->>Judge: deterministic quality scoring
        Planner->>Planner: choose repair actions
        alt accepted
            Judge-->>Proposer: stop with best draft
        else no actions
            Planner-->>Proposer: stop at plateau
        else actions selected
            Repair->>Repair: mutate draft and request structured repair JSON
        end
    end
```

Acceptance condition:
- no hard-fail diagnostics
- score >= `AGENT_TARGET_SCORE`
- pedagogy minimum quality satisfied

## 4. Provider Selection Flow

```mermaid
flowchart TD
    A[model policy] --> B{AGENT_PROVIDER}
    B -->|codex_exec| C[CodexExecLLMClient]
    B -->|remote_llm| D[RemoteLLMClient]
    B -->|internal| E[InternalLLMClient]
```

## 5. Provider Modes and Flows

### `codex_exec` (default)

- uses CLI subprocess: `CODING_AGENT_CMD exec - ...`
- enforces strict output schema via `--output-schema`
- reads final message from `--output-last-message`
- retries according to retry budget

```mermaid
flowchart TD
    A[LLMRequest] --> B[build prompt + schema]
    B --> C[attempt loop]
    C --> D[run codex exec subprocess]
    D --> E{timeout?}
    E -- yes --> C
    E -- no --> F{return code 0?}
    F -- no --> C
    F -- yes --> G{output file exists}
    G -- no --> C
    G -- yes --> H{valid JSON object}
    H -- no --> C
    H -- yes --> I[return payload]
    C -->|attempts exhausted| J[typed error]
```

Typical use:

```bash
AGENT_PROVIDER=codex_exec \
CODING_AGENT_CMD=codex \
python3.11 scripts/orchestration.py run <run_id>
```

### `remote_llm`

- uses HTTP `POST <OPENAI_BASE_URL>/responses`
- sends strict JSON schema format request
- extracts structured payload from response blocks
- retries retryable network/HTTP failures

```mermaid
flowchart TD
    A[LLMRequest] --> B[resolve API key + validate base URL]
    B --> C[build Responses payload]
    C --> D[attempt loop]
    D --> E[HTTP POST /responses]
    E --> F{HTTP/network error}
    F -- retryable and attempts left --> D
    F -- fatal or exhausted --> G[typed error]
    F -- no --> H{response JSON object}
    H -- no --> G
    H -- yes --> I[extract structured JSON]
    I --> J{valid payload object}
    J -- no --> G
    J -- yes --> K[return payload]
```

Typical use:

```bash
AGENT_PROVIDER=remote_llm \
AGENT_MODEL=gpt-4.1-mini \
OPENAI_API_KEY=<key> \
python3.11 scripts/orchestration.py run <run_id>
```

### `internal`

- deterministic internal client
- no remote API and no CLI model call
- useful for deterministic tests and fast local checks

```mermaid
flowchart TD
    A[LLMRequest] --> B[InternalLLMClient.run_json]
    B --> C[deterministic placeholder payload]
    C --> D[return payload]
```

## 6. Runtime Policy and Config Flow

Policy source:
- `learning_compiler/agent/model_policy.py`

Key env vars:
- `AGENT_PROVIDER` (`codex_exec|remote_llm|internal`)
- `AGENT_MODEL`
- `CODING_AGENT_CMD`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `AGENT_MAX_ITERATIONS`
- `AGENT_MAX_ACTIONS_PER_ITERATION`
- `AGENT_TARGET_SCORE`
- `AGENT_TIMEOUT_SECONDS`
- `AGENT_RETRY_BUDGET`
- `AGENT_SCOPE_TEXT_MAX_CHARS`

Defaults:
- provider: `codex_exec`
- timeout: `300s` for `codex_exec`, `30s` for others
- retry budget default: `1`

```mermaid
flowchart TD
    A[load config + env] --> B[parse provider]
    B --> C[resolve model_id default]
    C --> D[resolve timeout default by provider]
    D --> E[resolve retry/iteration/target params]
    E --> F[ModelPolicy snapshot]
```

## 7. Structured Output Contract Flow

Provider calls are schema-constrained:
- proposer schema: `proposer_curriculum_v1`
- repair schema: `repair_curriculum_v1`

Schema requires:
- top-level object with `curriculum`
- node list with required typed fields
- resource and mastery object shapes
- no additional properties

```mermaid
flowchart TD
    A[stage payload] --> B[select schema by stage]
    B --> C[provider enforces strict schema]
    C --> D[raw model output]
    D --> E[json parse]
    E --> F{root is object}
    F -- no --> G[typed internal error]
    F -- yes --> H[stage consumes structured payload]
```

## 8. Prompt/Payload Strategy Flow

Agent runtime uses compact payloads for LLM stages:
- compact topic spec subset
- compact curriculum projection (`id`, `title`, `prerequisites`, `estimate_minutes`)
- optional scope document payload with truncation guard

```mermaid
flowchart TD
    A[raw topic_spec + curriculum + scope text] --> B[compact topic_spec projection]
    A --> C[compact curriculum projection]
    A --> D[scope truncation guard]
    B --> E[LLM stage payload]
    C --> E
    D --> E
    E --> F[prompt JSON]
```

## 9. Reliability and Troubleshooting Flow

```mermaid
flowchart TD
    A[generation failure] --> B{provider}
    B -->|codex_exec| C[check AGENT_MODEL and timeout]
    B -->|remote_llm| D[check OPENAI_API_KEY and OPENAI_BASE_URL]
    B -->|internal| E[check schema parse/consumer expectations]
    C --> F[rerun with adjusted config]
    D --> F
    E --> F
    F --> G{success}
    G -- no --> H[capture typed error + escalate]
    G -- yes --> I[continue pipeline]
```

### Error: `codex_exec mode failed to return valid structured JSON`

Likely causes:
- model timeout
- malformed model output not matching schema
- incompatible model override in chat-authenticated codex mode

Checks:
1. unset `AGENT_MODEL` for `codex_exec` if using account default routing
2. increase `AGENT_TIMEOUT_SECONDS`
3. confirm `CODING_AGENT_CMD` points to working `codex` binary

### Error: invalid `OPENAI_BASE_URL`

- ensure `OPENAI_BASE_URL` includes valid `http://` or `https://` scheme
- verify hostname is present

### Error: `OPENAI_API_KEY is required`

- only applies to `AGENT_PROVIDER=remote_llm`
- set `OPENAI_API_KEY` or switch provider to `codex_exec`/`internal`

## 10. Extension Guide Flow

To add a new provider:
1. extend `ModelProvider` enum and parsing.
2. implement `LLMClient.run_json` behavior.
3. wire client construction in `build_llm_client`.
4. add tests for retries, timeout, malformed output, and config errors.
5. document env vars and defaults.

```mermaid
flowchart TD
    A[new provider idea] --> B[extend provider enum + parse]
    B --> C[implement client adapter]
    C --> D[wire build_llm_client]
    D --> E[add reliability/error tests]
    E --> F[update docs and examples]
    F --> G[run make gate]
```
