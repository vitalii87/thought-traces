# Experiment-run lifecycle

The run manager freezes experiment identity and prevents optimization from querying the final holdout.

## Frozen manifest

Before execution, a run manifest records:

- protocol version and content hash;
- task, evaluator, and curriculum versions;
- immutable container image digest;
- arena commit;
- complete lineage set;
- optimizer identity and random seed for every lineage.

The manifest has its own deterministic digest. Optimizer and seed maps must match the declared lineage set exactly.

## State machine

```text
draft
  → optimization
  → optimization_closed
  → holdout_open
  → complete
```

Development, selection, anchor, and regression suites are available only during `optimization`. The final holdout is available only during `holdout_open`. No suite is available after completion through this gate.

Every mutation requires the caller's expected state revision. This detects stale controllers. A non-blocking OS file lock prevents simultaneous controllers from interleaving writes. Each resulting state snapshot is hashed into the append-only run event chain, so accidental edits to `state.json` are detected and the cache can be recovered after a crash.

## One-shot final holdout

After optimization closes, each lineage reserves one final accepted artifact before its holdout evaluation. The manager issues a random reservation token and refuses a second reservation. The result is recorded by SHA-256 using that token.

The run becomes complete only when every preregistered lineage has one recorded result. A crashed evaluator can record the result of an existing reservation, but it cannot reserve another artifact silently.

The gate must wrap the trusted suite launcher. Merely labeling a directory “holdout” is not access control, and task or candidate code must never receive its host path.

## Telemetry export

The exporter first validates every lineage hash chain, then creates an atomic bundle:

- `events.csv` — all events and hashes with canonical JSON payloads;
- `metrics.csv` — long-form numeric leaves from candidate evaluations;
- `manifest.json` — source lineage heads, row counts, file hashes, and export ID.

Long-form metrics preserve components across changing evaluators and avoid forcing a premature fixed set of CSV columns. Integer values remain integers rather than passing through floating-point conversion.

```powershell
python -m iah_arena export-telemetry `
  --state-dir state `
  --output-dir exports/pilot-001 `
  --lineage-id gpt-lineage `
  --lineage-id gemini-lineage `
  --lineage-id claude-lineage
```

Exports never overwrite an existing directory.
