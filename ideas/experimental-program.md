# Experimental Program for the Intelligence Attractor Hypothesis

**Author:** Vitalii Zhyliaiev

**Initial formulation:** 2026

**Revision:** v0.5 — 2026-08

**Status:** Proposed research methodology

[← Intelligence Attractor Hypothesis](intelligence-attractor-hypothesis.md)

---

## 1. Research Objective

The empirical program asks:

> **Under what task, objective, constraint, and design-space conditions does functional diversity among independently optimized systems decrease as their performance approaches an attainable frontier?**

A second question isolates historical origin:

> **Does the causal contribution of initialization and optimization history to prespecified functional properties decrease near that frontier?**

The program tests local consequences of IAH. It does not attempt to prove a universal or physical-limit attractor in one experiment.

## 2. Preregistered Experimental Domain

Every study should specify before observing results:

- task or task distribution;
- context \(\Omega_t\);
- objective \(Q\);
- admissible design space \(\mathcal X_n\);
- optimization process and budget;
- origin variables;
- common-inheritance controls;
- functional levels and observables;
- pseudometrics;
- equivalence tolerance;
- performance-frontier estimator;
- statistical model;
- null hypotheses;
- falsification criteria.

Terms such as “relevant,” “near-optimal,” “binding,” and “sufficiently specified” must be operational rather than retrospective.

## 3. Performance Frontier and Regret

For a fixed design space:

$$
Q_n^*(\Omega)
=
\sup_{X\in\mathcal X_n}
Q(X\mid\Omega).
$$

Define regret:

$$
r_n(X\mid\Omega)
=
Q_n^*(\Omega)-Q(X\mid\Omega).
$$

For problems with known or exhaustively enumerable optima, \(Q_n^*\) may be exact.

For unknown optima, studies should use one or more of:

- the best empirically observed frontier;
- theoretical upper and lower bounds;
- benchmark-specific regret bounds;
- optimization curves with uncertainty;
- normalized distance from a reproducible empirical frontier.

The estimate must be denoted separately:

$$
\widehat Q_n^*
\neq
Q_n^*
$$

unless equality is established.

## 4. Near-Optimal Sets

The theoretical \(\varepsilon\)-near-optimal set is:

$$
\mathcal N_{n,\varepsilon}(\Omega)
=
\left\{
X\in\mathcal X_n:
r_n(X\mid\Omega)
\le
\varepsilon
\right\}.
$$

In an empirical sample, only an estimate is observed:

$$
\widehat{\mathcal N}_{n,\varepsilon}
\subseteq
\mathcal N_{n,\varepsilon}.
$$

Claims must therefore report coverage limitations and uncertainty rather than treating the observed sample as the complete near-optimal region.

Because these cumulative sets are nested as \(\varepsilon\) decreases, their raw diameter is mechanically non-increasing. A decreasing cumulative-set diameter alone is therefore not a confirmatory test of IAH. Near-optimal sets remain useful for frontier topology, coverage, and exact-optimum analysis; the primary trend test uses matched regret bands.

## 5. Functional Observables and Pseudometrics

For each level \(\ell\), define a prespecified observable representation:

$$
\Psi_\ell(X,\Omega).
$$

Levels may include:

$$
\ell\in
\{
outcome,
behavior,
strategy,
representation,
algorithm,
architecture,
resource
\}.
$$

A functional pseudometric is:

$$
d_{F,\ell}(A,B)
=
d\left(
\Psi_\ell(A,\Omega),
\Psi_\ell(B,\Omega)
\right).
$$

Possible operational components include:

- divergence between behavior distributions;
- policy disagreement under interventions;
- differences in causal response profiles;
- representational similarity measures;
- algorithmic trace similarity;
- graph or module-level architecture features;
- energy, memory, latency, bandwidth, and reliability vectors.

No single metric is presumed universally correct. Metric selection is part of the scientific hypothesis and must precede observation of convergence.

## 6. Matched-Regret Functional Diversity

For a target regret \(r\) and preregistered band width \(\delta\), define:

$$
\mathcal B_n(r,\delta)
=
\left\{
X\in\mathcal X_n:
\left|r_n(X\mid\Omega)-r\right|
\le
\delta
\right\}.
$$

The canonical diversity quantity is the expected pairwise functional distance between independently obtained systems in the same band:

$$
D_{n,\ell}(r;\delta)
=
\mathbb E
\left[
d_{F,\ell}(X_i,X_j)
\mid
i\neq j,\;
X_i,X_j\in\mathcal B_n(r,\delta)
\right].
$$

The band definition, overlap rule, and any schedule for \(\delta\) must be frozen before outcome inspection. Because empirical pairwise summaries are sensitive to dependence, outliers, and sample size, studies should report:

- median pairwise distance;
- mean pairwise distance where justified;
- upper distance quantiles;
- cumulative near-optimal-set diameter as a secondary descriptive statistic;
- cluster count under a preregistered threshold;
- effective dimensionality;
- variance components;
- topology of the sampled near-optimal region.

### E1 — Functional Narrowing

For prespecified task classes:

$$
D_{n,\ell}(r;\delta)
\text{ tends to decrease over a prespecified near-frontier regime as }
r\downarrow.
$$

The hypothesis does not require pointwise monotonic decrease for every iteration, task, or level. The confirmatory statistical trend and comparison bands must be specified for each experiment.

## 7. Origin Dependence

Let \(O\) denote controlled origin variables and let:

$$
X_b(O\mid\Omega,Q,\mathcal X_n)
$$

be the system produced under optimization budget \(b\).

A provisional matched-regret Origin Sensitivity quantity is:

$$
OS_{n,\ell}(r)
=
\operatorname{Effect}_{O}
\left(
\Psi_\ell
\mid
r_n(X_b)\approx r
\right).
$$

Here \(\operatorname{Effect}_{O}\) is not one universal estimator. Studies should define it through factorial interventions, causal variance components, or another preregistered model while accounting for optimization budget and selection.

### E2 — Origin Attenuation

The preregistered test asks whether origin-attributable functional variation decreases as achieved regret decreases.

Performance matching and conditioning require care: selecting only successful runs can create selection bias. Analyses should therefore report:

- unconditional optimization trajectories;
- performance-matched comparisons;
- joint models of regret and functional distance;
- attrition and failed-run rates.

## 8. Null Hypotheses

Possible null hypotheses include:

### Null for functional narrowing

$$
H_{0,E1}:
d_{F,\ell}
\perp
r_n
$$

after accounting for sample size and task instance.

### Null for origin attenuation

$$
H_{0,E2}:
\operatorname{Var}_{O}
(\Psi_\ell)
\text{ does not decrease with regret}.
$$

### Null for architectural convergence

Near-frontier architectural distance is no smaller than expected under performance-matched random or inherited baselines.

Exact statistical forms should be chosen for each experiment rather than treated as universal.

## 9. Synthetic-World Experiment

Novel synthetic environments can reduce contamination from known solutions.

Agents receive only:

- an environment interface;
- rules or observations;
- an objective;
- resource limits;
- feedback.

They do not receive a known optimal implementation.

Vary independently:

- model family;
- initialization;
- training history;
- memory;
- tools;
- priors;
- architecture;
- optimization algorithm.

Measure:

- score and regret;
- behavior and strategy distance;
- resource profile;
- internal and architectural observables where available;
- origin-attributable variance.

Include tasks with:

- a unique known optimum;
- several exact optima;
- symmetry-protected optima;
- broad plateaus;
- rugged local optima;
- deliberately neutral implementation dimensions.

These controls test whether the method can detect both narrowing and genuine persistent diversity.

## 10. Outcome-to-System Optimality Experiment

Use a controlled game or simulator.

### Stage 1: outcome objective

Optimize completion time or external score and identify systems with equal or near-equal outcome performance.

### Stage 2: system objective

Progressively include preregistered internal costs:

- operation count;
- memory;
- inference cost;
- latency;
- training cost;
- energy proxy;
- robustness;
- reliability.

Measure whether the functionally competitive region changes or narrows.

This tests the distinction:

$$
Outcome\ Optimality
\rightarrow
System\ Optimality.
$$

The result may be narrowing, restructuring, fragmentation, or expansion. Only prespecified predictions count as confirmatory evidence.

## 11. Architectural and Self-Modification Experiments

Start from deliberately different initial systems and allow controlled modification of:

- memory;
- modules;
- communication;
- scheduling;
- topology;
- architecture;
- optimization procedure.

Use nested intervention spaces:

$$
\mathcal X_0
\subset
\mathcal X_1
\subset\cdots.
$$

For each \(\mathcal X_n\):

1. estimate its frontier;
2. measure level-specific functional distance;
3. test E1 and E2 independently;
4. record redesign and search costs;
5. preserve negative results.

A failure in \(\mathcal X_n\) cannot be reclassified as success because a later experiment uses \(\mathcal X_{n+1}\).

## 12. Constraint Regimes

IAH does not assume:

$$
more\ constraints
\Rightarrow
more\ convergence.
$$

Binding constraints may:

- narrow the competitive region;
- create specialized niches;
- increase sensitivity;
- alter the topology of the near-optimal set;
- produce multiple optima;
- eliminate previously competitive classes.

Experiments should vary:

- energy budget;
- memory;
- latency;
- bandwidth;
- reliability;
- compute;
- task distribution.

The research objective is to identify task/constraint classes in which systematic narrowing occurs and classes in which it does not.

## 13. Common-Inheritance Controls

Convergence can be caused by shared origin rather than independent optimization.

Controls should compare:

- shared corpus and shared solution history;
- shared observations but independent learning;
- different corpora and priors;
- different model families;
- independent environment exploration;
- novel tasks created after training;
- restricted access to libraries and reference implementations.

Audit for:

- benchmark leakage;
- copied code patterns;
- shared frameworks;
- evaluator-induced conventions;
- common prompts;
- common optimization libraries;
- hidden human standardization.

Environmental observations are not automatically contamination. The key distinction is inherited solution structure versus independent inference from constraints.

## 14. Statistical and Measurement Requirements

Studies should report:

- number of independent runs;
- optimization budget;
- randomization procedure;
- model and task sampling;
- confidence intervals;
- measurement reliability;
- sensitivity to metric choice;
- multiple-comparison correction where required;
- preregistered confirmatory and exploratory analyses;
- complete failed-run accounting.

Where possible, use:

- mixed-effects models across tasks and model families;
- variance decomposition;
- causal factorial designs for origin variables;
- bootstrap uncertainty for frontier and distance estimates;
- robustness checks across compatible pseudometrics.

One visually compelling convergence example is insufficient.

## 15. Falsifiers

### Against E1

Performance approaches the frontier while prespecified functional diversity remains stable or increases across the target task class.

### Against E2

Origin variables continue to dominate functionally important choices near matched frontiers.

### Against architectural convergence

Highly optimized architectures remain functionally unrelated under matched objectives, contexts, and mutable architecture spaces.

### Against Relational Narrowing

Adding preregistered causally relevant consequences systematically fails to reduce accidental degeneracy in the target domain.

### Against Strong Functional Uniqueness

Two functionally inequivalent exact global optima persist in a finite, fully evaluated design space under the prespecified equivalence relation.

### Against a recursive domain claim

Newly mutable internal variables provide measurable advantages but show no predicted relationship between functional distance and regret.

Negative results target the claim and domain that generated them. They should not be generalized automatically to every IAH level.

## 16. Initial Feasible PhD Scope

A feasible initial program should prioritize:

1. finite or bounded synthetic environments;
2. independently optimized agents with controlled origin perturbations;
3. behavior, strategy, and resource-level pseudometrics;
4. known or bounded frontiers;
5. one controlled extension in which architecture becomes mutable;
6. comparison across symmetry, plateau, and binding-constraint regimes.

The primary contribution would be a method for measuring functional narrowing and origin attenuation—not a claim to have demonstrated a universal intelligence attractor.

For the theoretical motivation, see [The Intelligence Attractor Hypothesis](intelligence-attractor-hypothesis.md). For the origin-specific prediction, see [Origin Dependence and Attenuation](origin-dependence-and-attenuation.md).
