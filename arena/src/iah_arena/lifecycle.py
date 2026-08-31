from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class LifecycleError(RuntimeError):
    pass


class AttemptStatus(StrEnum):
    OPEN = "open"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    ABORTED = "aborted"


_ALLOWED_TRANSITIONS = {
    AttemptStatus.OPEN: {
        AttemptStatus.SUBMITTED,
        AttemptStatus.REJECTED,
        AttemptStatus.ABORTED,
    },
    AttemptStatus.SUBMITTED: {
        AttemptStatus.ACCEPTED,
        AttemptStatus.REJECTED,
    },
    AttemptStatus.ACCEPTED: set(),
    AttemptStatus.REJECTED: set(),
    AttemptStatus.ABORTED: set(),
}


@dataclass(frozen=True, slots=True)
class AttemptLifecycle:
    epoch: int
    attempt: int
    parent_generation: int
    status: AttemptStatus = AttemptStatus.OPEN
    reason: str | None = None

    def __post_init__(self) -> None:
        if min(self.epoch, self.attempt, self.parent_generation) < 0:
            raise ValueError("lifecycle identifiers must be non-negative")

    def transition(self, target: AttemptStatus, *, reason: str | None = None) -> "AttemptLifecycle":
        if target not in _ALLOWED_TRANSITIONS[self.status]:
            raise LifecycleError(f"invalid attempt transition: {self.status} -> {target}")
        return replace(self, status=target, reason=reason)

    def as_dict(self) -> dict[str, object]:
        return {
            "epoch": self.epoch,
            "attempt": self.attempt,
            "parent_generation": self.parent_generation,
            "status": self.status.value,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, value: dict[str, object]) -> "AttemptLifecycle":
        return cls(
            epoch=int(value["epoch"]),
            attempt=int(value["attempt"]),
            parent_generation=int(value["parent_generation"]),
            status=AttemptStatus(str(value["status"])),
            reason=None if value.get("reason") is None else str(value["reason"]),
        )
