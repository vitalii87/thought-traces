# Salt Sensitivity

## A Testable Prediction of the Intelligence Attractor Hypothesis

**Author:** Vitalii Zhyliaiev

**Initial formulation:** 2026-08-19

**Revision:** v0.5 — 2026-08

**Status:** Testable hypothesis; no empirical validation claimed

[← Intelligence Attractor Hypothesis](intelligence-attractor-hypothesis.md)

---

## 1. Purpose

Present-day AI systems differ for many reasons that are not intrinsic to the task they are asked to solve. The **Salt Sensitivity** hypothesis asks whether the functional influence of those origin-dependent differences decreases as independently optimized systems approach a shared performance frontier.

The hypothesis is not that all agents will produce identical text, code, or architecture. It concerns prespecified functionally important properties after controlling for common inheritance, evaluator bias, and measurement uncertainty.

## 2. Salt as Origin Dependence

**Salt** is shorthand for historically contingent and origin-dependent properties of an agent or optimization run.

It is a heterogeneous vector rather than a natural scalar:

$$
S_i=
(
S_{initialization},
S_{seed},
S_{ordering},
S_{history},
S_{ancestry},
S_{implementation},
S_{development},
\ldots
).
$$

Depending on the experiment, Salt may include:

- parameter initialization;
- training seed;
- data ordering;
- training and optimization history;
- architecture ancestry;
- implementation history;
- stochastic developmental path;
- inherited conventions not required by the task.

The experiment must state in advance which components are varied and which are held constant.

## 3. What Salt Does Not Include

Salt should not absorb every source of uncertainty.

In particular, it must remain separate from:

- the current environment state;
- the objective;
- resource and physical constraints;
- transition dynamics;
- uncertainty about future trajectories;
- measurement noise.

Conceptually:

$$
S_i
\neq
P(\tau\mid\Omega_t,a).
$$

Salt describes the origin and contingent path of the system. The trajectory distribution describes how the environment may evolve under an action or policy.

The central question is whether, under matched external conditions, changing \(S_i\) continues to change functionally important properties near the frontier.

## 4. Central Prediction

Let an optimization process with competence or budget \(c\) produce:

$$
X_c(S_i\mid\Omega_t,Q,\mathcal X_n).
$$

IAH predicts:

> **Within a fixed context, objective, and prespecified design space, variation in prespecified functional properties attributable to arbitrary origin variables tends to decline as independently optimized systems approach the attainable performance frontier.**

This does not assert that origin dependence always vanishes. Salt may remain influential when:

- the objective has several distinct optima;
- symmetries preserve alternative solutions;
- optimization remains trapped in different local regions;
- constraints are weak or non-binding;
- several niches are equally competitive;
- the chosen functional description ignores relevant differences.

## 5. Operational Salt Sensitivity

The earlier expression:

$$
\frac{\partial Solution}{\partial Salt}
$$

is not generally well-defined because Salt contains discrete, continuous, categorical, and historically structured variables.

An operational alternative is to compare systems produced under controlled Salt perturbations.

For a prespecified functional pseudometric \(d_{F,\ell}\), a provisional sensitivity at optimization level \(c\) is:

$$
SS_{n,\ell}(c)
=
\mathbb E
\left[
d_{F,\ell}
\left(
X_c(S),X_c(S')
\right)
\right],
$$

where:

- \(S\) and \(S'\) are controlled origin perturbations;
- \(n\) identifies the design space;
- \(\ell\) identifies the functional level being compared;
- external context and objective are matched.

Pairwise distance is only one possible estimator. A stronger statistical design may estimate the proportion of variance in predefined functional features causally attributable to Salt while controlling for performance, task instance, model family, and measurement error.

No universal Salt metric is assumed.

## 6. Functional Distance

Literal source-code or text similarity is not the target.

Experiments may measure distinct distances:

$$
D_{outcome},
\quad
D_{behavior},
\quad
D_{strategy},
\quad
D_{representation},
\quad
D_{algorithm},
\quad
D_{architecture},
\quad
D_{resource}.
$$

For each level, researchers must preregister:

- observable features;
- invariances and symmetries;
- the distance or pseudometric;
- the evaluation distribution;
- the tolerance for approximate equivalence.

Choosing after the experiment whichever property happened to converge would not constitute strong evidence.

## 7. Shared Data: Contamination or Constraint Information?

Shared data is not automatically evidence against IAH.

### Historical contamination

Agents may converge because they inherited the same ready-made solution, implementation, convention, or highly specific human pattern.

For example:

$$
shared\ corpus
\rightarrow
copied\ implementation
\rightarrow
same\ solution.
$$

This is weak and heavily confounded evidence.

### Constraint information

An environment may independently generate observations from which different systems infer similar effective principles:

$$
environment
\rightarrow
observations
\rightarrow
independent\ learning
\rightarrow
convergent\ solution.
$$

Here data is the channel through which environmental constraints enter cognition.

The scientific problem is to distinguish inheritance of a solution from independent reconstruction under common constraints.

## 8. Evidence-Strength Ladder

Increasingly informative designs include:

1. **Same corpus → same answer.** Very weak; common inheritance dominates.
2. **Same observations → same strategy.** Weak; shared representation and training conventions may remain.
3. **Different priors and histories + same environment → same functional strategy.** Stronger.
4. **Different model families + independent exploration → same functional principles.** Stronger still.
5. **Different self-modifying architectures → convergence in prespecified architectural or resource properties.** Strong evidence for the architectural extension of IAH.

No single experiment establishes the full theory.

## 9. Architectural Salt

Initial architecture can itself be part of Salt.

If architecture is fixed, an experiment can only test convergence within that inherited architectural family. If architecture is modifiable, a stronger question becomes available:

> Does dependence of functionally important architecture on initial architecture decrease as systems approach the frontier?

Conceptually:

$$
origin\ dependence\downarrow,
\qquad
constraint\ dependence\uparrow,
\qquad
functional\ architectural\ convergence\uparrow.
$$

This remains conditional. Expanded architectural freedom may also create new niches or symmetries and increase diversity.

## 10. Minimal Experimental Design

A useful initial experiment should:

1. define a task and evaluation context;
2. specify the objective and resource accounting;
3. define the admissible design space;
4. select controlled Salt variables;
5. run independent optimization trajectories;
6. estimate the attainable frontier or bounds;
7. preregister functional features and distances;
8. measure performance and functional distance jointly;
9. control common data, shared implementations, and evaluator leakage;
10. report uncertainty and negative results.

Tasks with exhaustively enumerable or provably bounded optima are especially valuable for early tests.

## 11. Falsification and Limitations

Evidence against the Salt Sensitivity hypothesis includes:

- origin variables continuing to explain stable functional differences at matched near-frontier performance;
- no reduction in Salt-attributable variance as regret decreases;
- convergence disappearing after common-inheritance controls;
- task constraints explaining less variation than historical origin near the frontier.

A negative result applies to the preregistered task, metric, design space, and Salt intervention. It cannot be dismissed by redefining functional relevance or moving to a deeper design space after seeing the result.

Salt Sensitivity is a proposed empirical signature of IAH, not yet empirical evidence for it.

For the wider methodology, see [Experimental Program for the Intelligence Attractor Hypothesis](experimental-program.md).
