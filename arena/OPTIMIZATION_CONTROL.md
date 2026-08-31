# Optimization control

## Run configuration

`run.example.toml` is the strict input format for a frozen run. Unknown fields are rejected so misspelled controls cannot silently fall back to defaults. The loader hashes both the raw TOML and the referenced protocol file, then embeds those hashes in the run manifest.

Before a real run, replace every placeholder task, curriculum, image, commit, and model snapshot value. A zero digest is syntactically valid for the example but is not a valid preregistration choice.

The CLI owns lifecycle mutations:

```powershell
python -m iah_arena create-run --state-dir state --config run.toml
python -m iah_arena run-status --state-dir state --experiment-id pilot-001
python -m iah_arena start-run --state-dir state --experiment-id pilot-001 --expected-revision 0
python -m iah_arena close-run-optimization --state-dir state --experiment-id pilot-001 --expected-revision 1
python -m iah_arena open-run-holdout --state-dir state --experiment-id pilot-001 --expected-revision 2
```

Mutations use a non-blocking OS file lock. If two controllers target the same run, one fails instead of interleaving state and event writes. After a crash or damaged state cache, `recover-run-state` reconstructs `state.json` from the latest validated hash-chain snapshot.

## Information budget and prompts

The improvement prompt is canonical JSON under a fixed contract. It contains only the current lineage identity, objective, stage, metrics, declared remaining budgets, workspace summary, bounded local history, and canonical tools. It explicitly permits architecture and language replacement while prohibiting access to other lineages and hidden evaluator state.

Information budgets are provider-neutral counts: prompt characters, history items, metric items, workspace file count, and workspace bytes. Exceeding one fails closed instead of silently truncating different evidence for different providers. Native provider tokens and cost remain separately recorded budgets.

Every submission must include a structured claim:

- observed bottleneck;
- causal hypothesis;
- concrete changes;
- expected metric effect;
- risks.

The claim is telemetry, not evidence of success. Public tests and the independent evaluator still determine acceptance.

## Sequential lineage coordination

The coordinator executes only one lineage callback at a time. Epoch order rotates deterministically:

```text
epoch 1: A → B → C
epoch 2: B → C → A
epoch 3: C → A → B
```

This reduces systematic thermal or background-load advantage from always evaluating one provider first. A failure is isolated to its lineage and does not prevent the remaining lineages from receiving their turn. Attrited and completed lineages are excluded explicitly rather than disappearing as missing data.
