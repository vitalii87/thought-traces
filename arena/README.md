# IAH Arena

IAH Arena is the task-independent laboratory for running isolated, independently optimized software lineages. It is intentionally separate from both the immutable evaluator and the mutable candidate programs.

**Status:** foundation scaffold; no external provider or Docker execution is connected yet.

## Design boundary

The arena is trusted infrastructure. It will eventually own:

- provider-neutral decision sessions;
- prompt and tool schemas;
- transactional candidate workspaces;
- build and public-test execution;
- isolated judge execution;
- curriculum scheduling;
- budgets and stopping rules;
- immutable telemetry and artifact provenance;
- deterministic acceptance and rejection.

Candidate programs are untrusted and may modify only their assigned workspace. They must never receive provider credentials, evaluator source, hidden instances, neighboring lineage state, Docker control, or arena internals.

## Two clocks

The architecture distinguishes:

- **decision epochs**, in which an external model inspects evidence and proposes changes;
- **local compute phases**, in which builds, tests, profiling, and bounded searches run without model tokens.

This permits infrequent model calls while preserving autonomous local experimentation.

## Current foundation

The initial Python package provides:

- domain identifiers and event types;
- an append-only JSONL event store with a SHA-256 hash chain;
- hard API and local-compute budgets;
- a canonical provider adapter protocol;
- basic lineage initialization;
- a CLI for creating a lineage and verifying telemetry;
- dependency-free unit tests.

No task-specific score, preferred language, provider SDK, or container runtime is embedded in this layer.

## Planned architecture

```text
Trusted host
├── Arena controller
│   ├── provider adapters
│   ├── canonical tool loop
│   ├── budget ledger
│   ├── curriculum scheduler
│   └── event and artifact stores
├── Workshop A ── mutable candidate workspace
├── Workshop B ── mutable candidate workspace
├── Workshop C ── mutable candidate workspace
└── Judge ─────── fresh immutable evaluation container
```

The three workshops will share the same pinned polyglot image while using separate workspaces. Judge evaluations should run sequentially on the same host to reduce hardware contention.

## Event integrity

Each event record contains:

- a schema version;
- lineage, epoch, generation, and attempt identifiers;
- an event type and JSON payload;
- the hash of the previous event;
- a hash of the complete new record.

The chain detects accidental editing, truncation in the middle of a record, reordering, and cross-lineage mixing. It is provenance protection, not a substitute for external backups or cryptographic signatures.

## Development

The package currently uses only the Python standard library.

From `arena/`:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
python -m iah_arena init-lineage --state-dir state --lineage-id demo-001 --origin local-dry-run
python -m iah_arena verify-events --state-dir state --lineage-id demo-001
```

Generated state and artifacts are ignored by Git.

## Near-term milestones

1. Freeze canonical tool schemas and the upgrade-attempt state machine.
2. Add transactional workspace snapshots and rollback.
3. Add a fake provider for deterministic end-to-end tests.
4. Add a hardened local workshop runner.
5. Add fresh judge execution and resource collection.
6. Only then connect real provider adapters.
