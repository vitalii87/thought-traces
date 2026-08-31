# IAH Arena

IAH Arena is the task-independent laboratory for running isolated, independently optimized software lineages. It is intentionally separate from both the immutable evaluator and the mutable candidate programs.

**Status:** the task-independent orchestration, acceptance, provenance, and container runtime layers are operational; no external model provider is connected yet.

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

The Python package now provides:

- domain identifiers and event types;
- an append-only JSONL event store with a SHA-256 hash chain;
- hard API and local-compute budgets;
- a canonical provider adapter protocol;
- an explicit upgrade-attempt lifecycle;
- copy-on-attempt workspaces with promotion and rollback-by-rejection;
- canonical, path-confined file/test/submit tools;
- a bounded provider tool loop and deterministic fake provider;
- end-to-end candidate submission and evaluator-controlled acceptance;
- a Docker runtime boundary for isolated workshop and read-only judge commands;
- a common polyglot image recipe that permits language migration;
- frozen task/curriculum contracts and explicit benchmark layers;
- component-preserving Pareto or weighted fitness acceptance;
- content-and-provenance-addressed accepted-candidate artifacts;
- a frozen experiment-run state machine with a one-shot final-holdout gate;
- validated cross-lineage event and long-form metric exports;
- strict TOML run configuration and CLI lifecycle control;
- deterministic information-budgeted prompts with structured improvement claims;
- a sequential rotating coordinator for independent lineage turns;
- a CLI for creating a lineage, verifying telemetry, and running a free local dry run;
- dependency-free unit tests.

No task-specific score, preferred language, or provider SDK is embedded in this layer.

The container recipe and operational notes are in [`docker/README.md`](docker/README.md). Docker image tags are rejected at runtime: the experiment must use a registry digest or local SHA-256 image ID.

The world-independent task boundary, curriculum rules, fitness policy, and artifact requirements are documented in [`TASK_PLUGINS.md`](TASK_PLUGINS.md).

Run freezing, holdout access control, and analysis exports are documented in [`EXPERIMENT_RUNS.md`](EXPERIMENT_RUNS.md).

Configuration, prompt fairness, crash recovery, and lineage scheduling are documented in [`OPTIMIZATION_CONTROL.md`](OPTIMIZATION_CONTROL.md).

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
python -m iah_arena dry-run --state-dir state --lineage-id dry-run-001
python -m iah_arena docker-check --image "sha256:<local-image-id>"
python -m iah_arena export-telemetry --state-dir state --output-dir exports/pilot --lineage-id lineage-a --lineage-id lineage-b
```

Generated state and artifacts are ignored by Git.

## Near-term milestones

1. Persist coordinator epoch/disposition state and connect it to curriculum transitions.
2. Add action-budget accounting for changed bytes and files.
3. Build and freeze the first polyglot image on the experiment host.
4. Select and implement a preregistered task plug-in, then run container smoke tests.
5. Only then connect real provider adapters.
