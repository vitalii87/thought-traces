from __future__ import annotations

import threading
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Callable, Mapping


class LineageDisposition(StrEnum):
    ACTIVE = "active"
    ATTRITED = "attrited"
    COMPLETE = "complete"


class StepStatus(StrEnum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class LineageStepResult:
    lineage_id: str
    epoch: int
    status: StepStatus
    output: Mapping[str, Any]
    error_type: str | None = None
    error_message: str | None = None


LineageStep = Callable[[str, int], Mapping[str, Any]]


class SequentialLineageCoordinator:
    """Run one lineage at a time and rotate order to reduce systematic host bias."""

    def __init__(self, lineage_ids: tuple[str, ...]) -> None:
        if not lineage_ids or len(set(lineage_ids)) != len(lineage_ids):
            raise ValueError("coordinator lineage IDs must be non-empty and unique")
        self.lineage_ids = lineage_ids
        self._dispositions = {
            lineage_id: LineageDisposition.ACTIVE for lineage_id in lineage_ids
        }
        self._run_lock = threading.Lock()

    @property
    def dispositions(self) -> Mapping[str, LineageDisposition]:
        return MappingProxyType(dict(self._dispositions))

    def order_for_epoch(self, epoch: int) -> tuple[str, ...]:
        if epoch <= 0:
            raise ValueError("epoch must be positive")
        offset = (epoch - 1) % len(self.lineage_ids)
        rotated = self.lineage_ids[offset:] + self.lineage_ids[:offset]
        return tuple(
            lineage_id
            for lineage_id in rotated
            if self._dispositions[lineage_id] is LineageDisposition.ACTIVE
        )

    def run_epoch(self, epoch: int, step: LineageStep) -> tuple[LineageStepResult, ...]:
        if not self._run_lock.acquire(blocking=False):
            raise RuntimeError("a lineage epoch is already running")
        try:
            results = []
            for lineage_id in self.order_for_epoch(epoch):
                try:
                    output = dict(step(lineage_id, epoch))
                    results.append(
                        LineageStepResult(
                            lineage_id,
                            epoch,
                            StepStatus.SUCCEEDED,
                            MappingProxyType(output),
                        )
                    )
                except Exception as error:
                    results.append(
                        LineageStepResult(
                            lineage_id,
                            epoch,
                            StepStatus.FAILED,
                            MappingProxyType({}),
                            type(error).__name__,
                            str(error),
                        )
                    )
            return tuple(results)
        finally:
            self._run_lock.release()

    def mark_attrited(self, lineage_id: str) -> None:
        self._set_terminal(lineage_id, LineageDisposition.ATTRITED)

    def mark_complete(self, lineage_id: str) -> None:
        self._set_terminal(lineage_id, LineageDisposition.COMPLETE)

    def _set_terminal(self, lineage_id: str, disposition: LineageDisposition) -> None:
        if lineage_id not in self._dispositions:
            raise KeyError(lineage_id)
        if self._dispositions[lineage_id] is not LineageDisposition.ACTIVE:
            raise ValueError(f"lineage is already terminal: {lineage_id}")
        self._dispositions[lineage_id] = disposition
