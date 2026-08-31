from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Protocol, Sequence


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ToolCall:
    call_id: str
    name: str
    arguments: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ToolResult:
    call_id: str
    output: Mapping[str, Any]
    is_error: bool = False


@dataclass(frozen=True, slots=True)
class DecisionContext:
    lineage_id: str
    epoch: int
    generation: int
    attempt: int
    objective: Mapping[str, Any]
    metrics: Mapping[str, Any]
    budget_remaining: Mapping[str, int]
    workspace_summary: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ProviderTurn:
    tool_calls: Sequence[ToolCall] = field(default_factory=tuple)
    final_text: str | None = None
    provider_response_id: str | None = None
    usage: Mapping[str, int] = field(default_factory=dict)


class ProviderAdapter(Protocol):
    """Provider-specific transport behind a canonical arena contract."""

    provider_name: str
    model_id: str

    def start(
        self,
        context: DecisionContext,
        tools: Sequence[ToolDefinition],
    ) -> ProviderTurn: ...

    def continue_with_results(
        self,
        provider_response_id: str,
        results: Sequence[ToolResult],
        tools: Sequence[ToolDefinition],
    ) -> ProviderTurn: ...


class ScriptedProvider:
    """Deterministic provider used to test orchestration without an external API."""

    provider_name = "scripted"
    model_id = "scripted-v1"

    def __init__(self, turns: Iterable[ProviderTurn]) -> None:
        self._turns = deque(turns)
        self.calls = 0

    def start(
        self,
        context: DecisionContext,
        tools: Sequence[ToolDefinition],
    ) -> ProviderTurn:
        return self._next()

    def continue_with_results(
        self,
        provider_response_id: str,
        results: Sequence[ToolResult],
        tools: Sequence[ToolDefinition],
    ) -> ProviderTurn:
        return self._next()

    def _next(self) -> ProviderTurn:
        if not self._turns:
            raise RuntimeError("scripted provider has no remaining turns")
        self.calls += 1
        turn = self._turns.popleft()
        if turn.provider_response_id is not None:
            return turn
        return ProviderTurn(
            tool_calls=turn.tool_calls,
            final_text=turn.final_text,
            provider_response_id=f"scripted-response-{self.calls}",
            usage=turn.usage,
        )
