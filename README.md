# Intelligence Attractor Hypothesis

**Vitalii Zhyliaiev**

This repository develops and tests the **Intelligence Attractor Hypothesis (IAH)**: the proposal that, for some task classes, independently optimized intelligent systems become less functionally diverse and less dependent on arbitrary historical origin as they approach an attainable performance frontier.

The work is in development. No experimental validation, peer review, institutional affiliation, or academic acceptance is claimed.

## Start Here

For a research or PhD review, use this order:

1. **[Research Overview](RESEARCH_OVERVIEW.md)** — the thesis, contribution, current evidence status, and scope.
2. **[Core IAH Theory](ideas/intelligence-attractor-hypothesis.md)** — definitions and claim structure.
3. **[Experimental Program](ideas/experimental-program.md)** — operationalization, metrics, null hypotheses, and falsifiers.
4. **[EXP-001: Independent Self-Improving Lineages](experiments/001-independent-self-improving-lineages/README.md)** — the first concrete study.
5. **[IAH Arena](arena/README.md)** — the experimental infrastructure and current implementation status.

## Current Status

| Component | Status | Next decisive step |
| --- | --- | --- |
| Theory | v0.6 research framework | Resolve scope and complete related-work positioning |
| Experimental methodology | Drafted | Freeze study-specific metrics and statistical models |
| EXP-001 | Design draft | Select task and evaluator, then preregister |
| IAH Arena | Core infrastructure operational | Add task plug-in and provider adapters |
| Evidence | None claimed | Run controlled pilot experiments |

## Repository Map

- **RESEARCH_OVERVIEW.md** — professor-facing summary.
- **ideas/** — core theory, theoretical extensions, and speculative limits.
- **experiments/** — preregistered protocols, data, and results.
- **arena/** — experimental orchestration and isolation code.
- **notes/** — exploratory material.
- **templates/** — reusable idea and experiment templates.

The [ideas index](ideas/README.md) separates the empirical core, strong extensions, and speculative limits. The [experiment registry](experiments/README.md) tracks study status. The [arena documentation](arena/README.md) distinguishes implemented infrastructure from planned work.

## Central Empirical Question

> Under what task, objective, constraint, and design-space conditions does functional diversity among independently optimized systems decrease as normalized regret approaches an attainable performance frontier?

## Author and Attribution

This repository preserves the development history of the hypothesis and its experiments. When discussing or reusing the work, please attribute **Vitalii Zhyliaiev** and link to the relevant version or document.
