from __future__ import annotations

import json
import math
from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable, Mapping, Protocol, Sequence

from .budgets import BudgetDelta, BudgetLedger
from .domain import EventType


class RuntimeRole(StrEnum):
    WORKSHOP = "workshop"
    JUDGE = "judge"


@dataclass(frozen=True, slots=True)
class RuntimeLimits:
    cpus: float
    memory_mb: int
    pids: int
    timeout_seconds: float
    tmpfs_mb: int = 128
    max_output_bytes: int = 256_000

    def __post_init__(self) -> None:
        if self.cpus <= 0 or self.timeout_seconds <= 0:
            raise ValueError("cpus and timeout_seconds must be positive")
        if min(self.memory_mb, self.pids, self.tmpfs_mb, self.max_output_bytes) <= 0:
            raise ValueError("runtime limits must be positive")


@dataclass(frozen=True, slots=True)
class Mount:
    host_path: Path
    container_path: str
    read_only: bool = True

    def __post_init__(self) -> None:
        target = PurePosixPath(self.container_path)
        if not target.is_absolute() or ".." in target.parts:
            raise ValueError("container mount path must be absolute and normalized")


@dataclass(frozen=True, slots=True)
class RuntimeRequest:
    argv: tuple[str, ...]
    role: RuntimeRole
    workspace_read_only: bool
    working_directory: str = "/workspace"
    extra_mounts: tuple[Mount, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.argv or any(not argument for argument in self.argv):
            raise ValueError("runtime argv must contain non-empty arguments")
        directory = PurePosixPath(self.working_directory)
        if not directory.is_absolute() or ".." in directory.parts:
            raise ValueError("working_directory must be absolute and normalized")
        if self.role is RuntimeRole.JUDGE and not self.workspace_read_only:
            raise ValueError("judge workspace must be read-only")
        if self.role is RuntimeRole.JUDGE and any(
            not mount.read_only for mount in self.extra_mounts
        ):
            raise ValueError("judge extra mounts must be read-only")


@dataclass(frozen=True, slots=True)
class RuntimeResult:
    exit_code: int | None
    timed_out: bool
    duration_ms: int
    stdout: str = ""
    stderr: str = ""
    output_truncated: bool = False
    runtime_metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def succeeded(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def as_dict(self) -> dict[str, Any]:
        return {
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "duration_ms": self.duration_ms,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "output_truncated": self.output_truncated,
            "runtime_metadata": dict(self.runtime_metadata),
        }


class CandidateRuntime(Protocol):
    def run(
        self,
        workspace: Path,
        request: RuntimeRequest,
        limits: RuntimeLimits,
    ) -> RuntimeResult: ...


class ScriptedRuntime:
    """Deterministic runtime for orchestration tests without Docker."""

    def __init__(self, results: Iterable[RuntimeResult]) -> None:
        self._results = deque(results)
        self.requests: list[tuple[Path, RuntimeRequest, RuntimeLimits]] = []

    def run(
        self,
        workspace: Path,
        request: RuntimeRequest,
        limits: RuntimeLimits,
    ) -> RuntimeResult:
        self.requests.append((Path(workspace), request, limits))
        if not self._results:
            raise RuntimeError("scripted runtime has no remaining results")
        return self._results.popleft()


RuntimeEventSink = Callable[[EventType, Mapping[str, Any]], None]


class RuntimePublicTestRunner:
    def __init__(
        self,
        *,
        runtime: CandidateRuntime,
        request: RuntimeRequest,
        limits: RuntimeLimits,
        budget: BudgetLedger | None = None,
        event_sink: RuntimeEventSink | None = None,
    ) -> None:
        if request.role is not RuntimeRole.WORKSHOP:
            raise ValueError("public tests must use the workshop role")
        self.runtime = runtime
        self.request = request
        self.limits = limits
        self.budget = budget
        self.event_sink = event_sink

    def __call__(self, workspace: Path) -> Mapping[str, Any]:
        result = self.runtime.run(workspace, self.request, self.limits)
        self._charge(result)
        payload = {"passed": result.succeeded, **result.as_dict()}
        if self.event_sink is not None:
            self.event_sink(EventType.PUBLIC_TEST_COMPLETED, payload)
        return payload

    def _charge(self, result: RuntimeResult) -> None:
        if self.budget is None:
            return
        seconds = max(1, math.ceil(result.duration_ms / 1000 * self.limits.cpus))
        self.budget.charge(BudgetDelta(local_cpu_seconds=seconds))


class JsonRuntimeEvaluator:
    """Run a read-only judge command whose final stdout line is a JSON object."""

    def __init__(
        self,
        *,
        runtime: CandidateRuntime,
        request: RuntimeRequest,
        limits: RuntimeLimits,
        budget: BudgetLedger | None = None,
    ) -> None:
        if request.role is not RuntimeRole.JUDGE or not request.workspace_read_only:
            raise ValueError("evaluator requires a read-only judge request")
        self.runtime = runtime
        self.request = request
        self.limits = limits
        self.budget = budget

    def __call__(self, workspace: Path) -> Mapping[str, Any]:
        result = self.runtime.run(workspace, self.request, self.limits)
        if self.budget is not None:
            seconds = max(1, math.ceil(result.duration_ms / 1000 * self.limits.cpus))
            self.budget.charge(BudgetDelta(local_cpu_seconds=seconds))
        if not result.succeeded:
            return {
                "accepted": False,
                "reason": "judge execution failed",
                "runtime": result.as_dict(),
            }
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        if not lines:
            raise ValueError("judge emitted no JSON result")
        value = json.loads(lines[-1])
        if not isinstance(value, dict) or not isinstance(value.get("accepted"), bool):
            raise ValueError("judge result must be a JSON object with boolean accepted")
        return {**value, "runtime": result.as_dict()}
