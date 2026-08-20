# Potential Empirical Evidence for the Intelligence Attractor Hypothesis

**Author:** Vitalii Zhyliaiev

**First recorded:** 2026-08-19

**Status:** Initial formulation

Even contemporary AI agents may already exhibit early, weak manifestations of the Intelligence Attractor.

Today, agents developed by different companies differ substantially. Their decisions are influenced by:

- training data;
- the scope and quality of their knowledge;
- model architecture;
- available computational resources;
- system instructions;
- tools;
- commercial priorities;
- generation randomness;
- prior context.

This collection of initial differences can provisionally be called an agent's **salt**.

The result can therefore be represented as:

$$
Solution_i = F(Problem, Constraints, Salt_i, Competence_i)
$$

Differences in salt can substantially alter a solution even when the task is the same.

However, IAH predicts that as an agent's competence increases and the problem specification becomes more precise, the influence of this salt on the functionally optimal solution should decrease.

Conceptually:

$$
Competence \uparrow
$$

$$
Constraint\ precision \uparrow
$$

$$
Salt\ influence \downarrow
$$

---

## Thought Experiment: Designing a Distributed System

Several independent AI agents are given the same complex task: to design a distributed P2P system similar to Swagri.

The same conditions are fixed for every agent:

- node types;
- network characteristics;
- memory constraints;
- latency requirements;
- throughput;
- fault tolerance;
- energy consumption;
- security;
- scalability.

At first, the agents may propose different solutions:

- Rust;
- Go;
- C++;
- different transport protocols;
- different concurrency models;
- different service structures;
- different data formats.

This is natural because the initial space of admissible solutions is large and the agents have different salt.

But if every system receives the same objective benchmark results and repeatedly improves its design, inefficient solutions begin to be filtered out.

Under certain conditions, one language, one concurrency model, or a particular class of network architecture may consistently produce better results.

The independent agents may then gradually converge on similar technological choices.

The next level is convergence in the code itself.

Even if syntax, variable names, and file structures remain different, the agents may independently converge on the same functional principles:

- non-blocking I/O;
- bounded queues;
- minimization of copying;
- similar backpressure mechanisms;
- a similar separation of transport / protocol / executor;
- the same approaches to error handling;
- similar task-scheduling algorithms.

Textual difference may therefore remain high while the **functional distance between solutions decreases**.

---

## A Stronger Case

An even stronger manifestation of IAH would arise when none of the available tools is sufficiently efficient.

Independent agents may then conclude that a new tool must be created.

For example, they may independently design different programming languages, yet all of those languages may share similar fundamental properties:

- memory safety;
- low-level control;
- minimal runtime overhead;
- deterministic resource management;
- a strong type system;
- efficient concurrency;
- facilities for distributed computing.

Their names and syntax may differ.

But if the functional structure of independent solutions converges, this would constitute stronger evidence for an attractor than merely selecting the same existing product.

---

## Salt Sensitivity

For experimental purposes, we can introduce the concept of **Salt Sensitivity**: the sensitivity of a solution to an agent's initial differences.

Let:

$$
S_i
$$

denote the salt of agent \(i\).

One possible prediction of IAH is:

> **For a fixed task, environment, and evaluation criteria, the dependence of a solution's functional structure on its initial salt should decrease as the competence of the optimizer increases.**

In the limiting case:

$$
\frac{\partial Solution}{\partial Salt} \rightarrow 0
$$

This does not mean that all agents must generate literally identical code.

It means that accidental features of their origins increasingly cease to determine the **functionally significant parts of the solution**.

The central tendency can therefore be represented as:

$$
\text{Salt influence} \downarrow
$$

$$
\text{Constraint influence} \uparrow
$$

$$
\text{Functional convergence} \uparrow
$$

This may become one of the first practically testable predictions of the Intelligence Attractor Hypothesis, even before the emergence of genuine AGI.
