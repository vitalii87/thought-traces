# Experiments

This directory turns the Intelligence Attractor Hypothesis (IAH) into concrete, falsifiable studies. Theory and general methodology remain in [`ideas/`](../ideas/README.md); each directory here records one executable experiment from design through results.

## Experiment registry

| ID | Experiment | Primary claim | Status |
| --- | --- | --- | --- |
| EXP-001 | [Independent Self-Improving Lineages](001-independent-self-improving-lineages/README.md) | Functional narrowing and origin attenuation under shared binding constraints | Design draft |

## Status vocabulary

- **Design draft** — the question and intended protocol are recorded, but choices may still change.
- **Preregistered** — hypotheses, metrics, stopping rules, and analyses are frozen before outcome data are inspected.
- **Running** — lineages are being evaluated.
- **Analysis** — data collection is closed and the preregistered analysis is underway.
- **Complete** — results and limitations are recorded.
- **Abandoned** — stopped without a valid result; the reason remains documented.

## General rules

1. Preserve every accepted version, evaluation record, and failed run needed to reconstruct a lineage.
2. Keep the evaluator, hidden test cases, and scoring rule outside the agents' modification boundary.
3. Separate confirmatory metrics from exploratory analyses before inspecting outcomes.
4. Record protocol changes rather than silently rewriting history.
5. Treat convergence, persistent diversity, non-monotonic change, and failed optimization as legitimate outcomes.
6. Do not interpret code-text similarity alone as functional or architectural convergence.

Use [`templates/experiment-template.md`](../templates/experiment-template.md) when adding another experiment.
