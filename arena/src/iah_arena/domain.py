from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping
from uuid import uuid4


class EventType(StrEnum):
    LINEAGE_CREATED = "lineage_created"
    WORKSPACE_INITIALIZED = "workspace_initialized"
    CURRICULUM_STAGE_ENTERED = "curriculum_stage_entered"
    CURRICULUM_PROMOTED = "curriculum_promoted"
    CURRICULUM_ATTRITED = "curriculum_attrited"
    EPOCH_STARTED = "epoch_started"
    ATTEMPT_STARTED = "attempt_started"
    PROVIDER_CALL_STARTED = "provider_call_started"
    PROVIDER_CALL_COMPLETED = "provider_call_completed"
    TOOL_CALLED = "tool_called"
    TOOL_COMPLETED = "tool_completed"
    BUILD_COMPLETED = "build_completed"
    PUBLIC_TEST_COMPLETED = "public_test_completed"
    LOCAL_JOB_STARTED = "local_job_started"
    LOCAL_JOB_COMPLETED = "local_job_completed"
    CANDIDATE_SUBMITTED = "candidate_submitted"
    CANDIDATE_EVALUATED = "candidate_evaluated"
    CANDIDATE_ACCEPTED = "candidate_accepted"
    CANDIDATE_REJECTED = "candidate_rejected"
    ATTEMPT_ABORTED = "attempt_aborted"
    ARTIFACT_CAPTURED = "artifact_captured"
    BUDGET_CHARGED = "budget_charged"
    HUMAN_INTERVENTION = "human_intervention"
    ARENA_FAILURE = "arena_failure"


@dataclass(frozen=True, slots=True)
class ArenaEvent:
    lineage_id: str
    event_type: EventType
    payload: Mapping[str, Any] = field(default_factory=dict)
    epoch: int = 0
    generation: int = 0
    attempt: int = 0
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="microseconds")
    )
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        if not self.lineage_id.strip():
            raise ValueError("lineage_id must not be empty")
        if min(self.epoch, self.generation, self.attempt) < 0:
            raise ValueError("epoch, generation, and attempt must be non-negative")
        return {
            "schema_version": self.schema_version,
            "event_id": self.event_id,
            "timestamp_utc": self.timestamp_utc,
            "lineage_id": self.lineage_id,
            "epoch": self.epoch,
            "generation": self.generation,
            "attempt": self.attempt,
            "event_type": self.event_type.value,
            "payload": dict(self.payload),
        }
