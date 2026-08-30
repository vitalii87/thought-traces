# The Intelligence Attractor Hypothesis

## Functional Convergence Under the Constraints of Reality

**Author:** Vitalii Zhyliaiev

**Initial formulation:** 2026

**Revision:** v0.6 — 2026-08

**Status:** Developing research framework; not experimentally validated

---

## Abstract

The **Intelligence Attractor Hypothesis (IAH)** proposes that, for some classes of sufficiently specified problems, independently optimized intelligent systems may become functionally more similar as their performance approaches an attainable frontier.

The hypothesis is stronger than the general observation that constraints sometimes make solutions similar. Its central proposal is that optimization may progressively remove degrees of freedom that are historically arbitrary while increasing the proportion of functionally important properties determined by the task, objective, environment, available information, resource constraints, computation, causality, and physical reality.

This narrowing may occur at several levels: external outcomes, policies, representations, algorithms, cognitive architectures, and—where those variables are accessible to optimization—computational or physical implementation. Convergence does not imply literal identity. Systems may retain different syntax, encodings, geometries, or interchangeable components while sharing the functional properties required for near-frontier performance.

IAH contains an empirical core, architectural and recursive extensions, and stronger limiting conjectures. These levels are intentionally separated. A failure of a stronger claim does not rescue or falsify a weaker claim, and expanding the accessible design space does not revise a negative result obtained in a previously specified space.

The near-term scientific program is to measure whether functional diversity and dependence on arbitrary origin decrease among independently optimized systems as their regret approaches a task-specific performance frontier.

---

## 1. Central Thesis

IAH begins from an asymmetry in solution space:

> There may be far more ways to be inefficient than ways to remain functionally competitive near an attainable optimum.

Different intelligences need not converge because they copy one another. They may converge because independently discovering increasingly effective ways of interacting with the same environment eliminates some inefficient degrees of freedom.

The central origin-dependence thesis is:

> **Within a fixed context, objective, and prespecified design space, IAH predicts that as normalized regret decreases, variation in prespecified functional properties attributable to arbitrary origin variables tends to decline relative to variation explained by the task and binding constraints.**

This is a domain-conditional prediction, not a universal theorem. Exact symmetries, neutral directions, multiple optima, modularity, specialization, path dependence, and non-binding constraints may preserve or increase diversity.

## 2. Basic Objects and Scope

Let the task-relevant context at time \(t\) be:

$$
\Omega_t=(e_t,\mathcal T,\mathcal R_t,\mathcal I_t,H),
$$

where:

- \(e_t\) is the relevant state of the environment;
- \(\mathcal T\) is the transition dynamics or law governing possible future trajectories;
- \(\mathcal R_t\) is the available resource and physical-constraint set;
- \(\mathcal I_t\) is the information and observation interface available to the system;
- \(H\) is the evaluation or planning horizon.

If the environment is path-dependent, \(e_t\) must include the causally relevant history or a sufficient representation of it.

Three additional objects are specified separately:

$$
Q,\qquad S_i,\qquad \mathcal X_n.
$$

- \(Q\) is the objective or evaluation rule;
- \(S_i\) is the origin-dependent **Salt** of system \(i\);
- \(\mathcal X_n\) is a prespecified admissible design space.

Keeping these objects separate prevents historical origin, environmental uncertainty, and normative evaluation from being conflated.

For a candidate system \(X\in\mathcal X_n\), performance is evaluated as:

$$
Q(X\mid\Omega_t).
$$

The attainable frontier within \(\mathcal X_n\) is:

$$
Q_n^*(\Omega_t)
=
\sup_{X\in\mathcal X_n}Q(X\mid\Omega_t).
$$

The supremum is used because the best attainable value need not be realized by any finite candidate.

## 3. What “Attractor” Means

IAH uses **attractor** in a generalized optimization sense.

> Unless an explicit update dynamic and basin of attraction are defined, the term refers to concentration of functionally distinct near-optimal solutions rather than to an already established classical dynamical-systems attractor.

Two claims must remain distinct:

1. **Landscape concentration:** the functionally competitive region becomes narrow near the frontier.
2. **Dynamical attraction:** optimization processes starting from a broad range of initial conditions tend to enter that region.

A narrow optimum may be difficult to discover. A broad basin may lead to several functionally different optima. Experiments must state which claim they test.

Because \(\Omega_t\) changes, an attractor-like region may also move. The optimum at one contextual slice need not remain optimal later:

$$
\mathcal A(\mathcal X_n,\Omega_{t_1},Q)
\neq
\mathcal A(\mathcal X_n,\Omega_{t_2},Q).
$$

The relevant object for dynamic problems is generally a policy evaluated over future trajectories, not an isolated immediate action.

### Pursuit analogy

Imagine several snakes pursuing the same moving mouse. They begin at different positions and headings, so their early paths strongly reflect their origins. If the snakes share the same physical constraints and repeatedly correct their motion against the same target dynamics, the later portions of their paths may become increasingly similar: the target and the physics of pursuit explain more of the trajectory, while the starting position explains less.

The correspondence is:

- a snake is an independently optimized lineage;
- its initial position and body plan are origin and initial architecture;
- its physical limits are the admissible design space and resource constraints;
- course correction is iterative optimization;
- the moving mouse is a changing attainable frontier;
- the trail is the lineage's functional and architectural history.

The trails need not overlap in absolute coordinates. What may converge is the pursuit law: relative angle, curvature, prediction, response to target motion, and resource-efficient control. Likewise, software lineages need not produce textually identical code to discover the same functional principles.

The analogy is illustrative, not evidence for IAH. Ordinary optimization can also generate similar pursuit paths. The empirical content of IAH begins only when the experiment measures whether functionally relevant diversity and origin-attributable variation systematically contract near a shared frontier, and whether this contraction recurs after prespecified changes in the target or binding constraints.

## 4. Levels of Functional Convergence

### Outcome convergence

Different systems reach the same or nearly the same externally measured result.

This is the weakest level. Equal outcomes do not imply equal strategies, costs, or intelligence.

### Policy and strategy convergence

Independent systems discover similar action-selection rules, decompositions, planning strategies, or resource-allocation policies.

### Cognitive and algorithmic convergence

Independent systems converge in functionally important properties of representation, causal modeling, uncertainty handling, memory, compression, search, learning, or error correction.

### Architectural convergence

When architecture materially affects performance or cost and is itself an admissible optimization variable, independently optimized systems may converge in some functional architectural properties.

### Computational and physical convergence

If deeper implementation variables are causally accessible and affect the objective, optimization may act on topology, communication, memory hierarchy, computational substrate, energy use, latency, reliability, and organization of matter.

None of these levels predicts literal identity. Convergence is assessed modulo prespecified task-irrelevant symmetries and implementation differences.

## 5. Outcome Optimality and System Optimality

An optimizer is not merely an external observer of the solution. When its internal costs affect the objective, it becomes part of the object being optimized.

Suppose two agents complete the same task in the same measured time. At the outcome level they appear equivalent. But one may require:

- substantially more computation;
- greater energy;
- more memory;
- higher inference or communication cost;
- more training;
- less reliability or robustness.

They are outcome-equivalent but not equally system-optimal under an objective that includes those costs.

> **The optimizer itself becomes part of the optimization problem whenever the machinery used to discover and realize a solution has relevant consequences.**

This is the bridge from outcome convergence to architectural convergence.

## 6. Objective Consequences and Relational Evaluation

Reality determines what alternatives physically cause:

- energy consumption;
- latency;
- heat;
- error probability;
- reliability;
- memory and bandwidth use;
- learning cost;
- feasible future trajectories.

The objective determines how those consequences are evaluated.

> **Reality determines what alternatives cost and what consequences they produce; the objective determines which consequences count as better.**

IAH does not assume a universally correct objective or universal morality. An optimum may be well-defined relative to a specified subject, objective, context, and horizon without being best for every possible subject.

For policies \(\pi\), a conceptual evaluation is:

$$
Q(\pi\mid\Omega_t)
=
\mathbb E\!\left[
U(\tau)
\mid
\Omega_t,\pi
\right],
$$

where \(\tau\) is a future trajectory. Under deterministic dynamics the distribution may collapse to a single trajectory; under stochastic dynamics the policy is evaluated over the physically available distribution of consequences.

IAH does **not** derive objectives from causal facts alone. Any claim that objective structures themselves converge requires an independently specified meta-objective, dominance relation, or admissibility principle. Without such an additional criterion, “a better objective” is undefined rather than merely unknown.

## 7. Empirical Core

The empirical core has two related but logically distinct hypotheses.

### E1 — Functional Narrowing

For specified classes of tasks, the functional diameter of independently obtained near-optimal systems is predicted to decrease as their regret relative to the attainable performance frontier decreases, after controlling for common inheritance and measurement uncertainty.

### E2 — Origin Attenuation

Under fixed \(\Omega_t\), \(Q\), and \(\mathcal X_n\), the causal influence of controlled origin perturbations on prespecified functional properties is predicted to decrease as independently optimized systems approach the frontier.

E1 and E2 do not imply each other. A narrow region may retain origin-dependent variation, while origin dependence may be weak even when several functionally distinct near-optimal regions exist.

Detailed operational definitions and experiments are provided in [Experimental Program for the Intelligence Attractor Hypothesis](experimental-program.md). Origin variables and confounds are treated in [Salt Sensitivity](empirical-evidence-salt-sensitivity.md).

## 8. Architectural Extension

### D1 — Internal Convergence

> **When representations, algorithms, or architectures are themselves admissible optimization variables and materially affect performance or cost, near-frontier systems may converge in some prespecified functional properties of those internal levels, modulo task-irrelevant symmetries and implementation details.**

This is stronger than outcome convergence and must be tested separately. A task can admit one best output while supporting many equally efficient internal implementations.

Cognitive and architectural optimization may interact:

$$
(C_t,A_t)
\rightarrow
performance
\rightarrow
measurement
\rightarrow
modification
\rightarrow
(C_{t+1},A_{t+1}).
$$

This loop expands what can be optimized but does not guarantee improvement, escape from local optima, or convergence to a unique architecture.

## 9. Recursive Extension Across Design Spaces

Let:

$$
\mathcal X_0
\subset
\mathcal X_1
\subset
\mathcal X_2
\subset\cdots
$$

be preregistered design spaces defined by increasingly rich allowed interventions—for example:

- fixed policy;
- trainable policy;
- trainable representation;
- trainable algorithm;
- modifiable architecture;
- modifiable optimization mechanism.

### R1 — Cross-Space Recurrence

IAH proposes that functional narrowing may recur separately in increasingly expressive design spaces when newly accessible variables materially affect the objective.

Each \(\mathcal X_n\) defines an independent empirical domain:

$$
\mathcal A_n
=
\mathcal A(\mathcal X_n,\Omega_t,Q).
$$

> Expanding the design space generates a new hypothesis and does not revise a negative result obtained in a previously specified space.

This prevents an appeal to an unknown “deeper attractor” from immunizing a failed claim.

The detailed architectural argument is developed in [Recursive Architectural Attractor and Open-Ended Optimization Depth](recursive-architectural-attractor.md).

## 10. Relational Narrowing and Functional Uniqueness

Apparent ties may disappear when additional causally relevant consequences are included. This motivates **Relational Narrowing**:

> As functionally different alternatives are embedded in an increasingly complete but prespecified causally relevant context, the set of contexts in which they remain accidentally tied may shrink.

This does not imply that every tie disappears. Exact symmetry, genuine indifference, plateaus, and multiple global optima remain legitimate possibilities.

Two stronger claims are separated from the empirical core:

### U1 — Generic Functional Concentration

For some non-degenerate task and context classes, the functional diameter of the near-optimal set may approach zero as regret approaches zero.

### U2 — Strong-Limit Functional Uniqueness

For a stated limiting accessible design space, context, objective, horizon, and functional pseudometric, all limiting optimal realizations may belong to one functional equivalence class.

U2 is not a theorem of arbitrary optimization. It is a strong limiting conjecture. Persistent functionally inequivalent global optima under the specified conditions count against it without necessarily falsifying E1, E2, or D1.

Definitions and counterexamples are developed in [Relational Narrowing and Strong Functional Uniqueness](relational-narrowing-and-strong-functional-uniqueness.md).

## 11. Causal and Predictive Knowledge

IAH does not assume that an ideal intelligence can calculate everything.

Prediction may be limited by:

- chaos and sensitivity to initial conditions;
- computational irreducibility;
- quantum or other physical uncertainty;
- inaccessible information;
- finite energy, memory, and time;
- undecidability and self-reference.

Near-optimal behavior also does not universally require a complete causal model. A model-free policy or a compressed sufficient statistic may be enough.

A defensible conditional extension is:

> For task distributions in which counterfactual prediction, intervention selection, and generalization are performance-limiting, near-optimal systems should approach the minimum causal or predictive sufficiency required to attain the frontier.

In stochastic environments this means approaching the best physically attainable predictive distribution for relevant consequences, not magically knowing one predetermined future.

## 12. Claim Structure

IAH is not a single linear ladder. Its empirical claims and limiting conjectures form related branches:

| Claim | Question | Status |
| --- | --- | --- |
| E1 — Functional Narrowing | Does near-optimal functional diversity decrease? | Empirical hypothesis |
| E2 — Origin Attenuation | Does arbitrary origin matter less near the frontier? | Empirical hypothesis |
| D1 — Internal Convergence | Does narrowing extend to mutable internal properties? | Strong empirical extension |
| R1 — Cross-Space Recurrence | Does narrowing recur across richer intervention spaces? | Recursive theoretical/empirical extension |
| U1 — Generic Functional Concentration | Do some non-degenerate domains approach one functional class? | Strong domain-conditional hypothesis |
| U2 — Strong-Limit Functional Uniqueness | Does a specified limiting domain admit one optimal functional class? | Strong limiting conjecture |
| O1 — Objective-Level Convergence | Can objective structures converge? | Underdefined without a meta-objective |

Failure of a stronger or separate branch does not automatically falsify weaker claims. A weak claim cannot be rescued by appealing to a stronger inaccessible level.

## 13. Falsifiability Boundaries

Evidence against E1 includes repeated preregistered cases in which regret decreases without any systematic reduction in functional diameter.

Evidence against E2 includes persistent causal dependence of near-frontier functional properties on controlled Salt perturbations.

Evidence against D1 includes highly optimized systems that remain functionally unrelated at prespecified mutable internal levels under matched conditions.

Evidence against R1 includes design spaces in which newly accessible variables provide measurable advantages but repeatedly fail to become targets of optimization or exhibit the predicted narrowing.

Evidence against U2 includes two genuinely functionally inequivalent exact global optima that persist under the stated finite context, objective, equivalence relation, and design space.

Terms such as “sufficiently specified,” “functionally relevant,” “near the frontier,” and “binding constraint” must be operationalized before results are observed. They cannot be redefined afterward to protect the theory.

## 14. Far-Limit Interpretation

A speculative limiting interpretation of IAH asks what would happen if intelligence and self-optimization could exploit nearly every causally accessible degree of freedom relevant to an objective.

In that regime, arbitrary historical properties might contribute progressively less to functionally important structure, while information, computation, resources, the objective, and physical constraints contribute more.

This does not imply infinite intelligence, complete prediction, a universal value system, or literal identity of all optimized systems. It also does not imply that the limiting regime is physically reachable.

The strongest possible implication is a regime in which remaining improvement is constrained primarily by irreducible limits of accessible reality rather than correctable deficiencies of the intelligent system. This far-limit interpretation is not required for near-term empirical validation of E1 or E2.

## 15. Research Direction

The immediate research question is:

> **Under what task, objective, constraint, and design-space conditions does functional diversity among independently optimized systems decrease as normalized regret approaches zero?**

A corresponding origin question is:

> **Does the causal contribution of initialization and historical path dependence to functionally important properties decrease near independently measured performance frontiers?**

The next step is not to assume universal convergence, but to identify:

- where narrowing occurs;
- where it fails;
- which constraints produce it;
- which symmetries preserve diversity;
- how deeply it penetrates into cognition and architecture;
- whether the observed effects exceed ordinary common inheritance and shared engineering convention.

See:

- [Salt Sensitivity](empirical-evidence-salt-sensitivity.md)
- [Relational Narrowing and Strong Functional Uniqueness](relational-narrowing-and-strong-functional-uniqueness.md)
- [Recursive Architectural Attractor](recursive-architectural-attractor.md)
- [Experimental Program](experimental-program.md)
- [Related Work Map](related-work.md)
