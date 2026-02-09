# Incident Runbook

This runbook covers common operational failures and recovery actions.

## 1. First Triage Flow

```mermaid
flowchart TD
    A[incident detected] --> B[status <run_id>]
    B --> C[validate <run_id>]
    C --> D{validation passes}
    D -- yes --> E[plan <run_id>]
    E --> F[iterate <run_id>]
    F --> G[resolved]
    D -- no --> H[inspect validation_report.md]
    H --> I[apply fix]
    I --> C
```

## 2. Failure Classification Flow

```mermaid
flowchart TD
    A[command failed] --> B{error signature}
    B -->|stage_conflict| C[topic spec not ready path]
    B -->|validation failures| D[quality/schema/dag path]
    B -->|codex structured JSON error| E[codex_exec reliability path]
    B -->|OPENAI_API_KEY missing| F[remote_llm auth path]
    B -->|invalid OPENAI_BASE_URL| G[remote_llm config path]
    B -->|invalid run metadata| H[fresh-run recovery path]
```

## 3. Common Failures and Recovery Flows

### A. `stage_conflict` on `run`

Signature:
- topic spec not ready

Cause:
- run is still `initialized` and no `--scope-file` provided

Recovery:
- fill `inputs/topic_spec.json`, or
- rerun with `--scope-file`

```mermaid
flowchart TD
    A[stage_conflict] --> B{scope file available}
    B -- yes --> C[run with --scope-file]
    B -- no --> D[complete topic_spec contract]
    C --> E[rerun run command]
    D --> E
```

### B. Validation failure

Signature:
- `validate` or `run` exits non-zero with report failures

Cause:
- schema, DAG integrity, evidence mode, or quality rules failed

Recovery:
1. inspect `outputs/reviews/validation_report.md`
2. fix generator inputs/config or regenerate
3. rerun `validate` then `plan/iterate`

```mermaid
flowchart TD
    A[validation failed] --> B[open validation_report.md]
    B --> C[classify failures]
    C --> D[fix spec/generator/config]
    D --> E[rerun validate]
    E --> F{passes}
    F -- yes --> G[run plan + iterate]
    F -- no --> C
```

### C. `codex_exec mode failed to return valid structured JSON`

Possible causes:
- timeout
- malformed structured output
- incompatible `AGENT_MODEL` override

Recovery:
1. unset `AGENT_MODEL` (for chat-account codex default model routing)
2. increase `AGENT_TIMEOUT_SECONDS`
3. verify `CODING_AGENT_CMD` and `codex` CLI availability
4. rerun orchestration

```mermaid
flowchart TD
    A[codex_exec structured output error] --> B[unset AGENT_MODEL]
    B --> C[increase AGENT_TIMEOUT_SECONDS]
    C --> D[verify CODING_AGENT_CMD/codex binary]
    D --> E[rerun]
    E --> F{success}
    F -- no --> G[escalate with logs and settings]
    F -- yes --> H[resolved]
```

### D. `OPENAI_API_KEY is required` (remote_llm)

Cause:
- `AGENT_PROVIDER=remote_llm` without API key

Recovery:
- set `OPENAI_API_KEY`, or
- switch provider to `codex_exec`/`internal`

```mermaid
flowchart TD
    A[OPENAI_API_KEY required] --> B{use remote_llm?}
    B -- yes --> C[set OPENAI_API_KEY]
    B -- no --> D[switch to codex_exec/internal]
    C --> E[rerun]
    D --> E
```

### E. Invalid `OPENAI_BASE_URL`

Cause:
- malformed URL or missing scheme/host

Recovery:
- set valid `http(s)://...` base URL
- rerun

```mermaid
flowchart TD
    A[invalid OPENAI_BASE_URL] --> B[set valid HTTPS base URL]
    B --> C[rerun remote_llm request]
```

### F. Invalid run metadata

Signature:
- error indicates incompatible or invalid `run.json`

Cause:
- schema evolution or manual metadata corruption

Recovery:
1. archive run: `python3.11 scripts/orchestration.py archive <run_id>`
2. initialize fresh run
3. regenerate artifacts

```mermaid
flowchart TD
    A[invalid run metadata] --> B[archive run]
    B --> C[init new run]
    C --> D[reapply inputs]
    D --> E[run pipeline]
```

## 4. Stale Artifact Resolution Flow

Symptoms:
- stage appears behind expected command history
- `plan`/`diff` not reflecting latest curriculum edits

Resolution:
- stage auto-sync handles most cases
- rerun `validate`, `plan`, `iterate` in sequence

```mermaid
flowchart TD
    A[stale artifact symptoms] --> B[status]
    B --> C[validate]
    C --> D[plan]
    D --> E[iterate]
    E --> F[stage and outputs current]
```

## 5. Escalation Flow

Escalate when:
- repeated structured-output failures across retries/providers
- deterministic validator failures after known-good baseline changes
- parsing failures in core contracts (`topic_spec`, `curriculum`, `run.json`)

Include in escalation report:
- command run
- run ID
- provider mode/env vars
- exact typed error message
- relevant artifact paths and timestamps

```mermaid
flowchart TD
    A[unresolved after retries] --> B[collect evidence bundle]
    B --> C[command + run_id + env + error + artifact paths]
    C --> D[file escalation report]
```

## 6. Post-Incident Flow

- add regression test if code bug found
- update docs if behavior/ops procedure changed
- run `make gate`
- summarize root cause and prevention action in PR notes

```mermaid
flowchart TD
    A[incident resolved] --> B{code defect identified}
    B -- yes --> C[add regression test]
    B -- no --> D[record operational root cause]
    C --> E[update docs]
    D --> E
    E --> F[run make gate]
    F --> G[publish incident summary]
```
