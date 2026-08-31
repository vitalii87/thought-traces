from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping


class MetricDirection(StrEnum):
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


class AcceptanceMode(StrEnum):
    PARETO = "pareto"
    WEIGHTED = "weighted"


class ParetoRelation(StrEnum):
    DOMINATES = "dominates"
    DOMINATED = "dominated"
    EQUIVALENT = "equivalent"
    TRADEOFF = "tradeoff"


@dataclass(frozen=True, slots=True)
class MetricSpec:
    name: str
    direction: MetricDirection
    epsilon: float = 0.0
    feasibility_min: float | None = None
    feasibility_max: float | None = None
    weight: float = 0.0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("metric name must not be empty")
        if self.epsilon < 0 or not math.isfinite(self.epsilon):
            raise ValueError("metric epsilon must be finite and non-negative")
        for bound in (self.feasibility_min, self.feasibility_max):
            if bound is not None and not math.isfinite(bound):
                raise ValueError("feasibility bounds must be finite")
        if (
            self.feasibility_min is not None
            and self.feasibility_max is not None
            and self.feasibility_min > self.feasibility_max
        ):
            raise ValueError("feasibility_min must not exceed feasibility_max")
        if not math.isfinite(self.weight) or self.weight < 0:
            raise ValueError("metric weight must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class FitnessVector:
    values: Mapping[str, float]

    def __post_init__(self) -> None:
        if not self.values or any(
            not isinstance(name, str) or not name.strip() for name in self.values
        ):
            raise ValueError("fitness vector must contain named metrics")
        normalized = {name: float(value) for name, value in self.values.items()}
        if any(not math.isfinite(value) for value in normalized.values()):
            raise ValueError("fitness values must be finite")
        object.__setattr__(self, "values", MappingProxyType(normalized))


@dataclass(frozen=True, slots=True)
class AcceptanceDecision:
    accepted: bool
    reason: str
    relation: ParetoRelation | None
    incumbent_score: float | None = None
    candidate_score: float | None = None


class FitnessPolicy:
    def __init__(
        self,
        metrics: Iterable[MetricSpec],
        *,
        mode: AcceptanceMode = AcceptanceMode.PARETO,
        minimum_scalar_improvement: float = 0.0,
    ) -> None:
        self.metrics = tuple(metrics)
        names = [metric.name for metric in self.metrics]
        if not names or len(names) != len(set(names)):
            raise ValueError("fitness metric names must be non-empty and unique")
        if minimum_scalar_improvement < 0 or not math.isfinite(minimum_scalar_improvement):
            raise ValueError("minimum scalar improvement must be finite and non-negative")
        if mode is AcceptanceMode.WEIGHTED and not any(
            metric.weight > 0 for metric in self.metrics
        ):
            raise ValueError("weighted mode requires at least one positive metric weight")
        self.mode = mode
        self.minimum_scalar_improvement = minimum_scalar_improvement

    def validate(self, vector: FitnessVector) -> tuple[str, ...]:
        expected = {metric.name for metric in self.metrics}
        actual = set(vector.values)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            raise ValueError(f"fitness metric mismatch; missing={missing}, extra={extra}")
        violations = []
        for metric in self.metrics:
            value = vector.values[metric.name]
            if metric.feasibility_min is not None and value < metric.feasibility_min:
                violations.append(f"{metric.name}<minimum")
            if metric.feasibility_max is not None and value > metric.feasibility_max:
                violations.append(f"{metric.name}>maximum")
        return tuple(violations)

    def compare(self, candidate: FitnessVector, incumbent: FitnessVector) -> ParetoRelation:
        self.validate(candidate)
        self.validate(incumbent)
        candidate_better = False
        incumbent_better = False
        for metric in self.metrics:
            candidate_value = candidate.values[metric.name]
            incumbent_value = incumbent.values[metric.name]
            delta = candidate_value - incumbent_value
            if metric.direction is MetricDirection.MINIMIZE:
                delta = -delta
            if delta > metric.epsilon:
                candidate_better = True
            elif delta < -metric.epsilon:
                incumbent_better = True
        if candidate_better and not incumbent_better:
            return ParetoRelation.DOMINATES
        if incumbent_better and not candidate_better:
            return ParetoRelation.DOMINATED
        if not candidate_better and not incumbent_better:
            return ParetoRelation.EQUIVALENT
        return ParetoRelation.TRADEOFF

    def scalar_score(self, vector: FitnessVector) -> float:
        self.validate(vector)
        score = 0.0
        for metric in self.metrics:
            sign = 1.0 if metric.direction is MetricDirection.MAXIMIZE else -1.0
            score += sign * metric.weight * vector.values[metric.name]
        return score

    def decide(self, candidate: FitnessVector, incumbent: FitnessVector) -> AcceptanceDecision:
        violations = self.validate(candidate)
        incumbent_violations = self.validate(incumbent)
        if violations:
            return AcceptanceDecision(False, "infeasible: " + ", ".join(violations), None)
        if incumbent_violations:
            return AcceptanceDecision(True, "candidate restores feasibility", None)
        relation = self.compare(candidate, incumbent)
        if self.mode is AcceptanceMode.PARETO:
            accepted = relation is ParetoRelation.DOMINATES
            return AcceptanceDecision(accepted, f"pareto relation: {relation.value}", relation)

        incumbent_score = self.scalar_score(incumbent)
        candidate_score = self.scalar_score(candidate)
        improvement = candidate_score - incumbent_score
        accepted = improvement > self.minimum_scalar_improvement
        return AcceptanceDecision(
            accepted,
            f"scalar improvement: {improvement}",
            relation,
            incumbent_score,
            candidate_score,
        )


@dataclass(frozen=True, slots=True)
class ParetoPoint:
    identifier: str
    fitness: FitnessVector


class ParetoArchive:
    """Retain all currently non-dominated points, including equivalent families."""

    def __init__(self, policy: FitnessPolicy) -> None:
        self.policy = policy
        self._points: list[ParetoPoint] = []

    @property
    def points(self) -> tuple[ParetoPoint, ...]:
        return tuple(self._points)

    def add(self, point: ParetoPoint) -> bool:
        violations = self.policy.validate(point.fitness)
        if violations:
            raise ValueError("cannot archive infeasible point: " + ", ".join(violations))
        if any(existing.identifier == point.identifier for existing in self._points):
            raise ValueError(f"duplicate Pareto point identifier: {point.identifier}")
        if any(
            self.policy.compare(existing.fitness, point.fitness) is ParetoRelation.DOMINATES
            for existing in self._points
        ):
            return False
        self._points = [
            existing
            for existing in self._points
            if self.policy.compare(point.fitness, existing.fitness)
            is not ParetoRelation.DOMINATES
        ]
        self._points.append(point)
        return True


RawFitnessEvaluator = Callable[[Path], Mapping[str, Any]]


class PolicyEvaluator:
    """Derive acceptance from frozen arena policy instead of trusting task code."""

    def __init__(
        self,
        *,
        evaluator: RawFitnessEvaluator,
        policy: FitnessPolicy,
        incumbent: FitnessVector,
        fitness_field: str = "fitness",
    ) -> None:
        if not fitness_field.strip():
            raise ValueError("fitness_field must not be empty")
        policy.validate(incumbent)
        self.evaluator = evaluator
        self.policy = policy
        self.incumbent = incumbent
        self.fitness_field = fitness_field

    def __call__(self, workspace: Path) -> Mapping[str, Any]:
        raw = dict(self.evaluator(workspace))
        values = raw.get(self.fitness_field)
        if not isinstance(values, Mapping):
            raise ValueError(f"evaluator result must contain mapping '{self.fitness_field}'")
        candidate = FitnessVector(values)
        decision = self.policy.decide(candidate, self.incumbent)
        raw.pop("accepted", None)
        raw["accepted"] = decision.accepted
        raw["fitness"] = dict(candidate.values)
        raw["acceptance"] = {
            "mode": self.policy.mode.value,
            "reason": decision.reason,
            "pareto_relation": None
            if decision.relation is None
            else decision.relation.value,
            "incumbent_score": decision.incumbent_score,
            "candidate_score": decision.candidate_score,
        }
        return raw
