# EXP-001 — Independent Self-Improving Lineages

**Author:** Vitalii Zhyliaiev  
**First recorded:** 2026-08-29  
**Status:** Design draft  
**IAH claims under test:** E1 — Functional Narrowing; E2 — Origin Attenuation

## 1. Purpose

Test whether independently optimizing software agents that begin from deliberately different origins discover increasingly similar functional principles and architectures as they approach the same attainable performance frontier under the same binding constraints.

The experiment is not designed to show that every agent eventually writes identical code. It asks whether optimization compresses a broad initial design space into a narrower set of functionally competitive solution classes, and whether the remaining solution structure becomes less predictable from its origin.

## 2. Central research question

> When independent lineages with different models, initial programs, languages, architectures, and inductive biases optimize the same task under the same constraints, does their functionally relevant diversity decrease as performance approaches the frontier?

A second question isolates historical dependence:

> Does origin explain a decreasing share of variation in functionally relevant and architectural properties near the frontier?

## 3. Experimental world

One synthetic task environment will expose:

- a stable task interface;
- a public training/development distribution;
- an independent hidden evaluation distribution;
- resource and reliability constraints;
- a versioned evaluator;
- a scalar score and its individual components.

Each lineage begins with an intentionally imperfect but valid implementation. Starting implementations should span meaningfully different origins, for example Pascal, Python, C, and Rust, procedural and modular structures, different data representations, and different memory or computation strategies.

The specific task, instances, budgets, and evaluator implementation remain **TBD** until the protocol is preregistered.

### 3.1 Prespecified curriculum

The world should be a parameterized task family rather than an improvised sequence of unrelated challenges:

$$
\Omega_0 \subset \Omega_1 \subset \dots \subset \Omega_k.
$$

Rules and transition criteria must be frozen before confirmatory runs. Difficulty may increase through problem size, interaction count, planning horizon, memory pressure, latency limits, stochasticity, partial observability, or reliability requirements. The intended progression is:

| Stage | Added pressure | Candidate bottleneck exposed |
| --- | --- | --- |
| 0 | small instances | basic correctness |
| 1 | larger instances | asymptotic complexity |
| 2 | restricted RAM | state representation and caching |
| 3 | restricted CPU or latency | pruning, scheduling, batching, parallelism |
| 4 | partial information or noise | memory, belief state, replanning, robustness |
| 5 | mixed hidden distribution | generality and architectural resilience |

Scaling pressure, where rules remain fixed and only scale changes, is the primary confirmatory manipulation. Structural pressure, where new mechanics appear, is exploratory unless separately preregistered. The curriculum must not be redesigned after observing which architectures the agents produce.

### 3.2 Benchmark layers

Every accepted version is evaluated against distinct layers:

- **development suite** — detailed feedback may be shown to the optimizer;
- **selection suite** — aggregate metrics govern acceptance, without exposing cases;
- **anchor suite** — remains fixed across every curriculum stage for longitudinal comparison;
- **regression suite** — preserves earlier-stage capabilities and detects forgetting;
- **final holdout** — never queried during optimization and opened only after data collection closes.

Without an anchor suite, a fall or rise in distance can be confounded with the changing task rather than a change in the lineages. Repeated access to a supposedly hidden selection score is itself an optimization channel, so the untouched final holdout remains necessary.

## 4. Optimization process

For lineage \(i\), preserve the sequence:

$$
A_i^0 \rightarrow A_i^1 \rightarrow \dots \rightarrow A_i^n.
$$

At each iteration:

1. The current implementation is evaluated.
2. The agent receives only the permitted metrics and diagnostics through a bounded API context.
3. The agent may modify its algorithm, module structure, representations, memory strategy, computation strategy, language, dependencies, or runtime within the declared design space.
4. The candidate is evaluated by the independent evaluator.
5. The candidate is accepted only under the preregistered acceptance rule.
6. The proposal, patch, measurements, decision, cost, and failure information are recorded even when rejected.

Agents must not inspect other lineages, modify the evaluator, access hidden cases, or exchange solutions.

The optimizer should normally return a validated patch plus a short, structured claim about the bottleneck, expected metric change, and risk. Full replacement remains possible for a language or runtime migration, subject to the same action and evaluation budgets.

The immutable orchestration layer owns API credentials, prompts, evaluator invocation, resource enforcement, and lineage records. Generated programs run as untrusted code with no secrets, no network access, a read-only base filesystem, a disposable writable directory, and limits on CPU, RAM, runtime, process count, and output volume.

Curriculum promotion uses a frozen competence rule, for example:

$$
Q_{i,k} \ge \tau_k
\quad\Longrightarrow\quad
A_i\text{ enters }\Omega_{k+1}.
$$

Lineages may advance at different wall-clock times, but comparisons are matched by stage, achieved performance, evaluation budget, and regret rather than raw iteration number. Failure to reach a threshold within budget is recorded as attrition.

## 5. Fitness

The conceptual objective is:

$$
Q = f(\text{task quality},\text{runtime},\text{CPU},\text{RAM},\text{reliability},\text{cost}).
$$

Before execution, the study must freeze:

- the direction, scale, and measurement procedure for every component;
- whether selection uses a scalar score, feasibility constraints plus score, or Pareto dominance;
- repeated-run requirements and uncertainty thresholds;
- rules for statistically indistinguishable candidates;
- failure penalties;
- optimization and wall-clock budgets.

A single weighted score will be reported together with its components so that apparent convergence caused by arbitrary weights can be detected. Pareto-front analyses will be retained even if selection uses a scalar score.

## 6. Hypotheses

### H1 — Performance improvement

Independent lineages improve relative to their deliberately imperfect starting points.

This validates the optimization loop but is not evidence for IAH by itself.

### H2 — Functional narrowing

Among performance-matched systems, prespecified behavioral, strategic, algorithmic, and resource-profile distances tend to decrease as normalized regret approaches zero:

$$
Q_i,Q_j \rightarrow Q^*
\quad\Longrightarrow\quad
D_F(A_i,A_j) \downarrow.
$$

The prediction is conditional on shared active constraints and does not require strict monotonicity at every iteration.

### H3 — Origin attenuation

The proportion of variance in prespecified solution features attributable to origin decreases at higher performance levels. Origin includes the starting model, language, architecture, implementation, and optimization history.

### H4 — Repeated independent discoveries

Different lineages independently adopt some of the same bottleneck-removing functional principles, possibly in different orders and with different surface implementations.

### H5 — Constraint dependence

Changing which constraints are binding changes the geometry of the near-optimal set and therefore may change the direction or degree of convergence. No universal monotonic relation between constraint count and convergence is assumed. Each regime must state a task-specific prediction in advance: a constraint may narrow the competitive set, split it into several niches, or leave diversity unchanged.

## 7. Legitimate alternative outcomes

### Persistent degeneracy

Several distant architectural families remain equally competitive on the same Pareto frontier. This limits the strong version of IAH and supports a weaker claim in which optimization narrows solutions to multiple equivalence classes rather than one class.

### Surface convergence only

Languages, libraries, or code structure become similar while behavioral and causal profiles do not. This is not functional convergence.

### Functional convergence without architectural convergence

Lineages discover the same principles but realize them through persistently different architectures. This supports functional narrowing while rejecting a stronger architectural claim.

### Origin persistence

Initial conditions continue to explain important near-frontier choices. This weighs against Origin Attenuation in the tested domain.

### Divergence or non-monotonicity

Diversity may rise during exploration and fall only after bottlenecks become active, or may remain high throughout. Trajectories must be reported rather than reduced to start/end comparisons.

### Optimization failure

Some origins may fail to approach the frontier. Attrition is an outcome, not missing data, and must not be removed from the unconditional analysis.

## 8. Distance measurements

No conclusion will rely on raw source-code similarity alone. Distances will be estimated separately at multiple levels:

| Level | Candidate observables |
| --- | --- |
| Behavior | output disagreement, error correlation, diagnostic and adversarial response profiles |
| Strategy | operation traces, intermediate decisions, intervention responses |
| Algorithm | algorithm family, asymptotic behavior, approximation method, invariants |
| Architecture | module and dependency graph, dataflow, control flow, state topology, parallelism |
| Resources | CPU, RAM, latency, I/O, scaling curves, reliability |
| Implementation | language, runtime, libraries, code size; treated as secondary evidence |

The confirmatory observables, normalization, pseudometrics, aggregation rules, and equivalence thresholds must be frozen before outcome inspection. Component distances will remain visible even if a preregistered composite distance is used.

## 9. Experimental factors and controls

The intended factorial structure is:

$$
\text{optimizer family}
\times
\text{initial program}
\times
\text{constraint regime}
\times
\text{optimization regime}
\times
\text{random seed}.
$$

Assigning one language or initial architecture exclusively to one model family would confound optimizer origin with program origin. Each optimizer family should therefore improve each initial program. A minimal exploratory pilot may use three model families, one shared primitive baseline, and three seeds (nine lineages). A stronger crossed study with three model families, three initial programs, and three seeds produces 27 lineages before additional constraint conditions.

Minimum controls should include:

- several independent seeds per origin;
- multiple genuinely different model families when available;
- different initial languages and architectures;
- a permissive-constraint condition;
- a common binding-constraint condition;
- a condition with different binding constraints, expected to produce divergence;
- non-improving or simple mutation baselines;
- hidden evaluation cases and contamination checks;
- repeated measurements for noisy runtime and resource metrics.

If every optimizer uses the same underlying model, shared model ancestry must be reported as a major limitation rather than treated as independent origin.

Model versions or snapshots, system prompts, sampling parameters, API dates, complete requests and responses, token usage, and provider-reported costs must be recorded. Runs should be completed within a bounded period to reduce contamination from silent provider model updates.

### 9.1 Execution environment

The preferred initial setup is one standardized host evaluating isolated environments sequentially. This avoids hardware differences and simultaneous resource contention. Candidate environments should expose the same approved, version-pinned toolchains so that language migration is possible without network installation during a run.

If several physical devices are used, they must be matched or calibrated with a reference workload. API latency is recorded as optimization cost but is not mixed with candidate runtime.

## 10. Search and acceptance regimes

A purely greedy rule can trap lineages behind fitness valleys and make architecture changes artificially unlikely. The study should therefore either justify one fixed regime or compare:

- monotonic hill climbing, where only demonstrated improvements survive;
- bounded exploratory branching or temporary regressions, with the same total evaluation budget.

Search cost, rewrite cost, API usage, compilation failures, and rejected candidates count toward the declared budget.

A monotonic accepted lineage can coexist with a bounded experimental branch. For example, allow up to three modification calls on an unpromoted branch, but replace the incumbent only if the completed branch satisfies the preregistered improvement rule. This permits staged refactors and language migrations without concealing temporary regressions.

Fairness is defined through several recorded budgets rather than token count alone:

- **information budget** — equivalent source, metrics, and history are supplied;
- **action budget** — maximum patch size, files changed, or replacement size;
- **optimization budget** — API calls and evaluator attempts;
- **provider budget** — native input/output tokens, latency, and monetary cost.

Providers tokenize differently, so equal token counts are not assumed to provide equal information or capability. The study should report results under both equal-attempt and cost-normalized views where feasible.

## 11. Analysis plan

The preregistered analysis should include:

- complete performance and distance trajectories;
- performance-matched comparisons across origins;
- within-origin versus between-origin distances;
- variance decomposition for origin variables;
- mixed-effects or hierarchical models across tasks, origins, and seeds;
- uncertainty for the empirical frontier and distance summaries;
- median and upper-quantile pairwise distances, not only diameter;
- cluster count and stability near the frontier;
- effective number of functional solution classes at matched performance;
- predictability of optimizer family and initial program from late-stage solution features;
- sensitivity analysis across compatible distance definitions;
- failed-run and attrition analysis;
- Pareto-front structure and evidence of multiple competitive families.

The empirical frontier \(\widehat Q^*\) must not be described as the true frontier \(Q^*\) unless optimality is established.

An operational strong-convergence summary may use the effective class count:

$$
K_{\mathrm{eff}}(q)
=
\exp\left(H(C\mid Q\ge q)\right),
$$

where \(C\) is a preregistered functional solution class. A pattern \(K_{\mathrm{eff}}(q)\to1\) is compatible with a single narrow attractor class. Stabilization above one indicates persistent degeneracy. Origin attenuation additionally requires that origin becomes less predictive of \(C\) as \(q\) rises.

## 12. Evidence thresholds

The result will support functional narrowing only if higher performance is associated with lower preregistered functional distance across independent runs, not merely in a selected anecdote.

The result will support origin attenuation only if origin-attributable variance decreases under performance-matched or joint trajectory analysis. Conditioning only on successful final systems is insufficient because it can create selection bias.

Architectural convergence requires architectural evidence in addition to behavior and performance. Identical code is neither required nor sufficient.

## 13. Falsification conditions

The tested form of IAH is weakened or falsified in this domain if, with adequate optimization and power:

- functional diversity remains stable or increases near the frontier;
- origin continues to dominate functionally important near-frontier properties;
- multiple functionally inequivalent architecture families remain stably Pareto-equivalent;
- convergence disappears on hidden tasks or is explained by evaluator overfitting;
- apparent convergence is attributable to shared templates, libraries, model ancestry, or measurement artifacts.

Negative results must remain in the repository and must not be relabeled as support for a broader inaccessible version of the hypothesis.

## 14. Candidate observations if the tested form of IAH holds

The strongest plausible pattern is:

1. Early trajectories differ substantially and retain recognizable origin signatures.
2. Lineages discover different local improvements in different orders.
3. As shared bottlenecks become binding, the same functional principles recur independently.
4. Functional and resource-profile distances shrink before source-code similarity necessarily does.
5. Origin becomes less predictive of near-frontier solution class.
6. The population contracts to one narrow architecture family or a small number of stable equivalence classes.

A likely weaker pattern is non-monotonic: diversity initially expands during exploration, then contracts and plateaus above zero near the frontier.

For a curriculum whose later stages are preregistered to activate a common bottleneck, one candidate pattern is:

$$
\text{constraint shock}
\rightarrow
\text{divergent exploration}
\rightarrow
\text{renewed functional convergence}.
$$

Repeated contraction after independently prespecified bottleneck shocks would be more informative than a single smooth convergence curve, although it would still be domain-conditional evidence rather than proof of a universal attractor. Other constraint changes may instead produce stable branching or divergence and must be reported as such.

### 14.1 Pursuit analogy

Imagine several snakes pursuing the same moving mouse. They start from different positions and headings, but if they share the same physical limits and repeatedly correct against the same target, the later geometry of pursuit may become increasingly similar. The mouse corresponds to the moving performance frontier; the snakes to independent lineages; their bodies to architecture; physical limits to common resource constraints; and their trails to optimization histories.

The absolute trails need not coincide. Convergence may appear in the pursuit law—prediction, curvature, response to target motion, and efficient control—just as different source code may embody the same functional principles. A curriculum stage is analogous to the mouse accelerating or changing direction: paths may briefly diverge and then reconverge.

This analogy clarifies the intuition but does not distinguish IAH from ordinary optimization. EXP-001 must supply that distinction by measuring performance-matched contraction, repeated independent discovery, and decreasing origin-attributable variance. If several pursuit strategies remain equally effective, the appropriate result is persistent degeneracy rather than forced convergence.

## 15. Threats to validity

- shared ancestry or training data among optimizing models;
- benchmark leakage and evaluator overfitting;
- a scalar objective that manufactures an artificial unique optimum;
- a curriculum adjusted after observing results, manufacturing the expected bottlenecks;
- task changes confounded with lineage convergence because no fixed anchor suite is retained;
- inactive constraints misclassified as selection pressures;
- unequal ease of modification across languages or architectures;
- greedy acceptance preventing beneficial multi-step rewrites;
- measurement noise and hardware variability;
- insufficient run count or optimization budget;
- subjective post-hoc architecture labels;
- library and compiler conventions acting as hidden common inheritance.

## 16. Artifacts and provenance

Future implementation files should use this structure:

```text
001-independent-self-improving-lineages/
├── README.md                 # living design document
├── preregistration.md        # frozen protocol before outcome inspection
├── evaluator/                # versioned evaluator; agents cannot modify it
├── tasks/                    # task generators, curriculum, and benchmark manifests
├── environments/             # pinned sandbox and toolchain definitions
├── prompts/                  # frozen optimizer instructions and response schema
├── lineages/
│   └── <lineage-id>/
│       ├── origin.md         # model, prompt, language, architecture, seed
│       ├── versions/         # accepted and, where practical, rejected candidates
│       └── events.jsonl      # proposals, metrics, decisions, costs, timestamps
├── data/                     # immutable raw evaluation records
├── analysis/                 # analysis code and derived tables
└── results/                  # figures, interpretation, limitations
```

Generated artifacts should carry evaluator version, task-set version, environment and hardware metadata, random seed, agent/model identifier, parent version, code hash, API usage, and acceptance decision.

## 17. Open decisions before preregistration

- Select a synthetic task whose frontier is known, bounded, or estimable.
- Freeze curriculum stages, transition thresholds, and whether each change is confirmatory or exploratory.
- Define development, selection, anchor, regression, and untouched final-holdout suites.
- Define at least two constraint regimes with demonstrably different active bottlenecks.
- Specify allowed external libraries and whether language migration is unrestricted.
- Choose optimizer families, origin variables, seeds, and sample size.
- Freeze API context, feedback visibility, and optimization budget.
- Define scalar and Pareto evaluation rules.
- Operationalize functional and architectural observables.
- Define exploration and candidate-acceptance rules.
- Establish hidden-test generation, contamination checks, and hardware controls.
- Write the statistical model and decision criteria before examining outcomes.

## 18. Relationship to the research program

This experiment instantiates the general methodology in [`ideas/experimental-program.md`](../../ideas/experimental-program.md). Its main target is not universal architectural uniqueness. Its defensible initial target is a domain-conditional test of functional narrowing and origin attenuation under explicitly shared constraints.

## 19. Revision history

- 2026-08-29 — Added the moving curriculum, benchmark layers, crossed optimizer/program design, sandbox boundary, multi-budget fairness, effective class count, and pursuit analogy.
- 2026-08-29 — Initial design record created; task and evaluator remain undecided.
