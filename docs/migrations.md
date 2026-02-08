# Artifact Migration Rules

## Run Metadata Schema

Current run metadata schema version: `2`.

Migration entrypoint:
- `learning_compiler.orchestration.migrations.migrate_run_meta`

## Backward Compatibility Rules

1. Stage alias migration:
- legacy `map_generated` is migrated to `generated`.

2. History entry migration:
- legacy `{at_utc, stage, reason}` is migrated to
  `{at_utc, event_type, stage, message, metadata}`.
- `event_type` is standardized to `stage_transition`.

3. Missing fields:
- missing `schema_version` is set to current version.
- missing/invalid `history` is reconstructed with a bootstrap event.
- missing `created_at_utc` is defaulted to `1970-01-01T00:00:00Z`.

## Persistence Rule

- Migration is applied lazily on run load.
- If migration changes metadata, updated `run.json` is written immediately.
