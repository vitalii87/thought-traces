from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping
from uuid import uuid4

from .domain import ArenaEvent, EventType
from .events import JsonlEventStore
from .locking import FileLock
from .tasking import SuiteKind


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ENVIRONMENT_DIGEST = re.compile(r"^(?:.+@sha256:|sha256:)[0-9a-f]{64}$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        + b"\n"
    )
    os.replace(temporary, path)


class ExperimentPhase(StrEnum):
    DRAFT = "draft"
    OPTIMIZATION = "optimization"
    OPTIMIZATION_CLOSED = "optimization_closed"
    HOLDOUT_OPEN = "holdout_open"
    COMPLETE = "complete"


class HoldoutStatus(StrEnum):
    RESERVED = "reserved"
    RECORDED = "recorded"


@dataclass(frozen=True, slots=True)
class RunManifest:
    experiment_id: str
    protocol_version: str
    protocol_sha256: str
    task_id: str
    task_version: str
    evaluator_version: str
    curriculum_digest: str
    environment_digest: str
    arena_commit: str
    configuration_sha256: str
    lineage_ids: tuple[str, ...]
    optimizer_ids: Mapping[str, str]
    random_seeds: Mapping[str, int]
    created_utc: str = field(default_factory=_now)
    schema_version: int = 1

    def __post_init__(self) -> None:
        text = (
            self.experiment_id,
            self.protocol_version,
            self.protocol_sha256,
            self.task_id,
            self.task_version,
            self.evaluator_version,
            self.curriculum_digest,
            self.environment_digest,
            self.arena_commit,
            self.configuration_sha256,
            self.created_utc,
        )
        if not all(value.strip() for value in text):
            raise ValueError("run manifest identity fields must not be empty")
        if not _SAFE_ID.fullmatch(self.experiment_id):
            raise ValueError("run manifest experiment_id is invalid")
        if not _SHA256.fullmatch(self.protocol_sha256):
            raise ValueError("protocol_sha256 must be a lowercase SHA-256 digest")
        if not _SHA256.fullmatch(self.curriculum_digest):
            raise ValueError("curriculum_digest must be a lowercase SHA-256 digest")
        if not _ENVIRONMENT_DIGEST.fullmatch(self.environment_digest):
            raise ValueError("environment_digest must be an immutable SHA-256 reference")
        if not _SHA256.fullmatch(self.configuration_sha256):
            raise ValueError("configuration_sha256 must be a lowercase SHA-256 digest")
        if not self.lineage_ids or len(set(self.lineage_ids)) != len(self.lineage_ids):
            raise ValueError("run manifest lineage IDs must be non-empty and unique")
        if any(not _SAFE_ID.fullmatch(lineage_id) for lineage_id in self.lineage_ids):
            raise ValueError("run manifest contains an invalid lineage ID")
        expected = set(self.lineage_ids)
        if set(self.optimizer_ids) != expected or set(self.random_seeds) != expected:
            raise ValueError("optimizer and seed maps must exactly match lineage IDs")
        if any(not value.strip() for value in self.optimizer_ids.values()):
            raise ValueError("optimizer IDs must not be empty")
        if any(seed < 0 for seed in self.random_seeds.values()):
            raise ValueError("random seeds must be non-negative")
        object.__setattr__(self, "optimizer_ids", MappingProxyType(dict(self.optimizer_ids)))
        object.__setattr__(self, "random_seeds", MappingProxyType(dict(self.random_seeds)))

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "experiment_id": self.experiment_id,
            "protocol_version": self.protocol_version,
            "protocol_sha256": self.protocol_sha256,
            "task_id": self.task_id,
            "task_version": self.task_version,
            "evaluator_version": self.evaluator_version,
            "curriculum_digest": self.curriculum_digest,
            "environment_digest": self.environment_digest,
            "arena_commit": self.arena_commit,
            "configuration_sha256": self.configuration_sha256,
            "lineage_ids": list(self.lineage_ids),
            "optimizer_ids": dict(self.optimizer_ids),
            "random_seeds": dict(self.random_seeds),
            "created_utc": self.created_utc,
        }

    @property
    def digest(self) -> str:
        return hashlib.sha256(_canonical_json(self.as_dict())).hexdigest()

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RunManifest":
        return cls(
            experiment_id=str(value["experiment_id"]),
            protocol_version=str(value["protocol_version"]),
            protocol_sha256=str(value["protocol_sha256"]),
            task_id=str(value["task_id"]),
            task_version=str(value["task_version"]),
            evaluator_version=str(value["evaluator_version"]),
            curriculum_digest=str(value["curriculum_digest"]),
            environment_digest=str(value["environment_digest"]),
            arena_commit=str(value["arena_commit"]),
            configuration_sha256=str(value["configuration_sha256"]),
            lineage_ids=tuple(str(item) for item in value["lineage_ids"]),
            optimizer_ids={str(key): str(item) for key, item in value["optimizer_ids"].items()},
            random_seeds={str(key): int(item) for key, item in value["random_seeds"].items()},
            created_utc=str(value["created_utc"]),
            schema_version=int(value["schema_version"]),
        )


@dataclass(frozen=True, slots=True)
class HoldoutRecord:
    lineage_id: str
    artifact_id: str
    reservation_token: str
    status: HoldoutStatus
    reserved_utc: str
    result_sha256: str | None = None
    recorded_utc: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "artifact_id": self.artifact_id,
            "reservation_token": self.reservation_token,
            "status": self.status.value,
            "reserved_utc": self.reserved_utc,
            "result_sha256": self.result_sha256,
            "recorded_utc": self.recorded_utc,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "HoldoutRecord":
        return cls(
            lineage_id=str(value["lineage_id"]),
            artifact_id=str(value["artifact_id"]),
            reservation_token=str(value["reservation_token"]),
            status=HoldoutStatus(str(value["status"])),
            reserved_utc=str(value["reserved_utc"]),
            result_sha256=None
            if value.get("result_sha256") is None
            else str(value["result_sha256"]),
            recorded_utc=None
            if value.get("recorded_utc") is None
            else str(value["recorded_utc"]),
        )


@dataclass(frozen=True, slots=True)
class RunState:
    phase: ExperimentPhase = ExperimentPhase.DRAFT
    revision: int = 0
    holdout_records: Mapping[str, HoldoutRecord] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.revision < 0:
            raise ValueError("run state revision must be non-negative")
        object.__setattr__(
            self,
            "holdout_records",
            MappingProxyType(dict(self.holdout_records)),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase.value,
            "revision": self.revision,
            "holdout_records": {
                lineage_id: record.as_dict()
                for lineage_id, record in sorted(self.holdout_records.items())
            },
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RunState":
        return cls(
            phase=ExperimentPhase(str(value["phase"])),
            revision=int(value["revision"]),
            holdout_records={
                str(key): HoldoutRecord.from_dict(item)
                for key, item in value.get("holdout_records", {}).items()
            },
        )


class ExperimentRunManager:
    def __init__(self, state_dir: Path, experiment_id: str) -> None:
        if not _SAFE_ID.fullmatch(experiment_id):
            raise ValueError("experiment_id is invalid")
        self.experiment_id = experiment_id
        self.root = Path(state_dir) / "runs" / experiment_id
        self.manifest_path = self.root / "manifest.json"
        self.state_path = self.root / "state.json"
        self.lock_path = self.root / "run.lock"
        self.events = JsonlEventStore(self.root / "events.jsonl")

    def create(self, manifest: RunManifest) -> RunState:
        if manifest.experiment_id != self.experiment_id:
            raise ValueError("manifest experiment_id mismatch")
        with FileLock(self.lock_path):
            if self.manifest_path.exists() or self.state_path.exists():
                raise FileExistsError(f"experiment run already exists: {self.experiment_id}")
            state = RunState()
            _write_json_atomic(self.manifest_path, manifest.as_dict())
            self._emit(EventType.EXPERIMENT_CREATED, {"manifest_digest": manifest.digest})
            self._commit_state(state)
        return state

    def manifest(self) -> RunManifest:
        return RunManifest.from_dict(json.loads(self.manifest_path.read_text("utf-8")))

    def state(self) -> RunState:
        with FileLock(self.lock_path):
            return self._state_unlocked()

    def _state_unlocked(self) -> RunState:
        value = json.loads(self.state_path.read_text("utf-8"))
        state = RunState.from_dict(value)
        records = list(self.events.records())
        self.events.validate()
        if not records:
            raise RuntimeError("run event chain is empty")
        commit = records[-1]["event"]
        expected_digest = hashlib.sha256(_canonical_json(state.as_dict())).hexdigest()
        if (
            commit["event_type"] != EventType.RUN_STATE_COMMITTED.value
            or commit["payload"].get("revision") != state.revision
            or commit["payload"].get("state_sha256") != expected_digest
        ):
            raise RuntimeError("run state does not match its committed event")
        return state

    def recover_state(self) -> RunState:
        with FileLock(self.lock_path):
            self.events.validate()
            records = list(self.events.records())
            if not records:
                raise RuntimeError("run event chain is empty")
            commit = records[-1]["event"]
            if commit["event_type"] != EventType.RUN_STATE_COMMITTED.value:
                raise RuntimeError("run event chain does not end in a committed state")
            value = commit["payload"].get("state")
            if not isinstance(value, dict):
                raise RuntimeError("committed run state snapshot is missing")
            digest = hashlib.sha256(_canonical_json(value)).hexdigest()
            if commit["payload"].get("state_sha256") != digest:
                raise RuntimeError("committed run state snapshot is invalid")
            recovered = RunState.from_dict(value)
            self._emit(
                EventType.RUN_STATE_RECOVERED,
                {"revision": recovered.revision},
            )
            self._commit_state(recovered)
            return recovered

    def start_optimization(self, *, expected_revision: int) -> RunState:
        return self._transition(
            ExperimentPhase.DRAFT,
            ExperimentPhase.OPTIMIZATION,
            expected_revision,
        )

    def close_optimization(self, *, expected_revision: int) -> RunState:
        return self._transition(
            ExperimentPhase.OPTIMIZATION,
            ExperimentPhase.OPTIMIZATION_CLOSED,
            expected_revision,
        )

    def open_holdout(self, *, expected_revision: int) -> RunState:
        return self._transition(
            ExperimentPhase.OPTIMIZATION_CLOSED,
            ExperimentPhase.HOLDOUT_OPEN,
            expected_revision,
        )

    def assert_suite_allowed(self, suite_kind: SuiteKind) -> None:
        phase = self.state().phase
        if phase is ExperimentPhase.OPTIMIZATION and suite_kind is not SuiteKind.FINAL_HOLDOUT:
            return
        if phase is ExperimentPhase.HOLDOUT_OPEN and suite_kind is SuiteKind.FINAL_HOLDOUT:
            return
        raise PermissionError(f"suite {suite_kind.value} is unavailable during phase {phase.value}")

    def reserve_holdout(
        self,
        lineage_id: str,
        artifact_id: str,
        *,
        expected_revision: int,
    ) -> HoldoutRecord:
        with FileLock(self.lock_path):
            manifest = self.manifest()
            state = self._checked_state(expected_revision)
            self._assert_suite_allowed(state.phase, SuiteKind.FINAL_HOLDOUT)
            if lineage_id not in manifest.lineage_ids:
                raise ValueError(f"lineage is not part of this run: {lineage_id}")
            if lineage_id in state.holdout_records:
                raise PermissionError(f"final holdout already reserved for lineage: {lineage_id}")
            if not _SHA256.fullmatch(artifact_id):
                raise ValueError("artifact_id must be a lowercase SHA-256 digest")
            record = HoldoutRecord(
                lineage_id=lineage_id,
                artifact_id=artifact_id,
                reservation_token=uuid4().hex,
                status=HoldoutStatus.RESERVED,
                reserved_utc=_now(),
            )
            records = dict(state.holdout_records)
            records[lineage_id] = record
            next_state = RunState(state.phase, state.revision + 1, records)
            self._emit(
                EventType.HOLDOUT_RESERVED,
                {"lineage_id": lineage_id, "artifact_id": artifact_id},
            )
            self._commit_state(next_state)
        return record

    def record_holdout_result(
        self,
        lineage_id: str,
        reservation_token: str,
        result_sha256: str,
        *,
        expected_revision: int,
    ) -> RunState:
        with FileLock(self.lock_path):
            state = self._checked_state(expected_revision)
            if state.phase is not ExperimentPhase.HOLDOUT_OPEN:
                raise PermissionError(
                    "final holdout results can only be recorded while holdout is open"
                )
            record = state.holdout_records.get(lineage_id)
            if record is None or record.reservation_token != reservation_token:
                raise PermissionError("invalid final-holdout reservation")
            if record.status is not HoldoutStatus.RESERVED:
                raise PermissionError("final-holdout result is already recorded")
            if not _SHA256.fullmatch(result_sha256):
                raise ValueError("result_sha256 must be a lowercase SHA-256 digest")
            records = dict(state.holdout_records)
            records[lineage_id] = HoldoutRecord(
                lineage_id=record.lineage_id,
                artifact_id=record.artifact_id,
                reservation_token=record.reservation_token,
                status=HoldoutStatus.RECORDED,
                reserved_utc=record.reserved_utc,
                result_sha256=result_sha256,
                recorded_utc=_now(),
            )
            complete = set(records) == set(self.manifest().lineage_ids) and all(
                item.status is HoldoutStatus.RECORDED for item in records.values()
            )
            phase = ExperimentPhase.COMPLETE if complete else state.phase
            next_state = RunState(phase, state.revision + 1, records)
            self._emit(
                EventType.HOLDOUT_RECORDED,
                {"lineage_id": lineage_id, "result_sha256": result_sha256},
            )
            if complete:
                self._emit(
                    EventType.EXPERIMENT_PHASE_CHANGED,
                    {"from": state.phase.value, "to": phase.value},
                )
            self._commit_state(next_state)
        return next_state

    def _transition(
        self,
        source: ExperimentPhase,
        target: ExperimentPhase,
        expected_revision: int,
    ) -> RunState:
        with FileLock(self.lock_path):
            state = self._checked_state(expected_revision)
            if state.phase is not source:
                raise ValueError(
                    f"invalid experiment transition: {state.phase.value} -> {target.value}"
                )
            next_state = RunState(target, state.revision + 1, state.holdout_records)
            self._emit(
                EventType.EXPERIMENT_PHASE_CHANGED,
                {"from": source.value, "to": target.value},
            )
            self._commit_state(next_state)
        return next_state

    def _checked_state(self, expected_revision: int) -> RunState:
        state = self._state_unlocked()
        if state.revision != expected_revision:
            raise RuntimeError(
                f"stale run revision: expected {expected_revision}, actual {state.revision}"
            )
        return state

    def _emit(self, event_type: EventType, payload: Mapping[str, Any]) -> None:
        self.events.append(
            ArenaEvent(
                lineage_id=f"experiment:{self.experiment_id}",
                event_type=event_type,
                payload=payload,
            )
        )

    def _commit_state(self, state: RunState) -> None:
        value = state.as_dict()
        self._emit(
            EventType.RUN_STATE_COMMITTED,
            {
                "revision": state.revision,
                "state_sha256": hashlib.sha256(_canonical_json(value)).hexdigest(),
                "state": value,
            },
        )
        _write_json_atomic(self.state_path, value)

    @staticmethod
    def _assert_suite_allowed(phase: ExperimentPhase, suite_kind: SuiteKind) -> None:
        if phase is ExperimentPhase.OPTIMIZATION and suite_kind is not SuiteKind.FINAL_HOLDOUT:
            return
        if phase is ExperimentPhase.HOLDOUT_OPEN and suite_kind is SuiteKind.FINAL_HOLDOUT:
            return
        raise PermissionError(f"suite {suite_kind.value} is unavailable during phase {phase.value}")
