from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol


def _freeze_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("curriculum parameter object keys must be strings")
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise ValueError("curriculum parameters must contain finite JSON values")


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


class SuiteKind(StrEnum):
    DEVELOPMENT = "development"
    SELECTION = "selection"
    ANCHOR = "anchor"
    REGRESSION = "regression"
    FINAL_HOLDOUT = "final_holdout"


class PromotionDirection(StrEnum):
    AT_LEAST = "at_least"
    AT_MOST = "at_most"


@dataclass(frozen=True, slots=True)
class BenchmarkSuite:
    suite_id: str
    kind: SuiteKind
    version: str
    feedback_detail: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.suite_id, self.version, self.feedback_detail)):
            raise ValueError("benchmark suite fields must not be empty")


@dataclass(frozen=True, slots=True)
class PromotionRule:
    metric: str
    threshold: float
    direction: PromotionDirection = PromotionDirection.AT_LEAST
    minimum_evaluations: int = 1

    def __post_init__(self) -> None:
        if not self.metric.strip() or not math.isfinite(self.threshold):
            raise ValueError("promotion metric and threshold must be valid")
        if self.minimum_evaluations <= 0:
            raise ValueError("minimum_evaluations must be positive")

    def satisfied(self, metrics: Mapping[str, float], evaluations: int) -> bool:
        if evaluations < self.minimum_evaluations or self.metric not in metrics:
            return False
        value = float(metrics[self.metric])
        if not math.isfinite(value):
            return False
        if self.direction is PromotionDirection.AT_LEAST:
            return value >= self.threshold
        return value <= self.threshold


@dataclass(frozen=True, slots=True)
class CurriculumStage:
    stage_id: str
    ordinal: int
    parameters: Mapping[str, Any]
    promotion_rule: PromotionRule | None
    confirmatory: bool = True

    def __post_init__(self) -> None:
        if not self.stage_id.strip() or self.ordinal < 0:
            raise ValueError("curriculum stage identity is invalid")
        object.__setattr__(self, "parameters", _freeze_json(self.parameters))


@dataclass(frozen=True, slots=True)
class CurriculumSpec:
    curriculum_id: str
    version: str
    stages: tuple[CurriculumStage, ...]
    suites: tuple[BenchmarkSuite, ...]

    def __post_init__(self) -> None:
        if not self.curriculum_id.strip() or not self.version.strip() or not self.stages:
            raise ValueError("curriculum identity and stages are required")
        ordinals = [stage.ordinal for stage in self.stages]
        if ordinals != list(range(len(self.stages))):
            raise ValueError("curriculum ordinals must be contiguous and ordered from zero")
        if len({stage.stage_id for stage in self.stages}) != len(self.stages):
            raise ValueError("curriculum stage IDs must be unique")
        suite_kinds = [suite.kind for suite in self.suites]
        required = set(SuiteKind)
        if not required.issubset(suite_kinds):
            missing = sorted(kind.value for kind in required - set(suite_kinds))
            raise ValueError(f"benchmark suite kinds are missing: {missing}")
        if len({suite.suite_id for suite in self.suites}) != len(self.suites):
            raise ValueError("benchmark suite IDs must be unique")

    @property
    def digest(self) -> str:
        payload = {
            "curriculum_id": self.curriculum_id,
            "version": self.version,
            "stages": [
                {
                    "stage_id": stage.stage_id,
                    "ordinal": stage.ordinal,
                    "parameters": _thaw_json(stage.parameters),
                    "promotion_rule": None
                    if stage.promotion_rule is None
                    else {
                        "metric": stage.promotion_rule.metric,
                        "threshold": stage.promotion_rule.threshold,
                        "direction": stage.promotion_rule.direction.value,
                        "minimum_evaluations": stage.promotion_rule.minimum_evaluations,
                    },
                    "confirmatory": stage.confirmatory,
                }
                for stage in self.stages
            ],
            "suites": [
                {
                    "suite_id": suite.suite_id,
                    "kind": suite.kind.value,
                    "version": suite.version,
                    "feedback_detail": suite.feedback_detail,
                }
                for suite in self.suites
            ],
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


class CurriculumStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ATTRITED = "attrited"


@dataclass(frozen=True, slots=True)
class CurriculumState:
    stage_index: int = 0
    evaluations_at_stage: int = 0
    status: CurriculumStatus = CurriculumStatus.ACTIVE


@dataclass(frozen=True, slots=True)
class CurriculumDecision:
    state: CurriculumState
    promoted: bool
    reason: str


class CurriculumScheduler:
    def __init__(self, spec: CurriculumSpec) -> None:
        self.spec = spec

    def observe(
        self,
        state: CurriculumState,
        metrics: Mapping[str, float],
        *,
        budget_exhausted: bool = False,
    ) -> CurriculumDecision:
        if state.status is not CurriculumStatus.ACTIVE:
            raise ValueError("cannot update a terminal curriculum state")
        if not 0 <= state.stage_index < len(self.spec.stages):
            raise ValueError("curriculum state points outside the specification")
        evaluations = state.evaluations_at_stage + 1
        if budget_exhausted:
            return CurriculumDecision(
                CurriculumState(state.stage_index, evaluations, CurriculumStatus.ATTRITED),
                False,
                "budget exhausted before promotion",
            )
        stage = self.spec.stages[state.stage_index]
        rule = stage.promotion_rule
        if rule is None or not rule.satisfied(metrics, evaluations):
            return CurriculumDecision(
                CurriculumState(state.stage_index, evaluations),
                False,
                "promotion threshold not reached",
            )
        if state.stage_index == len(self.spec.stages) - 1:
            return CurriculumDecision(
                CurriculumState(state.stage_index, evaluations, CurriculumStatus.COMPLETED),
                True,
                "final stage completed",
            )
        return CurriculumDecision(
            CurriculumState(state.stage_index + 1, 0),
            True,
            "promotion threshold reached",
        )


PublicTestFactory = Callable[[CurriculumStage], Callable[[Path], Mapping[str, Any]]]
EvaluatorFactory = Callable[[CurriculumStage], Callable[[Path], Mapping[str, Any]]]


class TaskPlugin(Protocol):
    task_id: str
    task_version: str
    evaluator_version: str
    curriculum: CurriculumSpec

    def objective(self, stage: CurriculumStage) -> Mapping[str, Any]: ...

    def make_public_test_runner(
        self,
        stage: CurriculumStage,
    ) -> Callable[[Path], Mapping[str, Any]]: ...

    def make_evaluator(
        self,
        stage: CurriculumStage,
    ) -> Callable[[Path], Mapping[str, Any]]: ...
