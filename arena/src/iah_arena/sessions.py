from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

from .budgets import BudgetDelta, BudgetLedger
from .domain import EventType
from .providers import DecisionContext, ProviderAdapter, ProviderTurn, ToolResult
from .tools import CANONICAL_TOOLS, WorkspaceToolExecutor


EventSink = Callable[[EventType, Mapping[str, Any]], None]


class SessionError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class SessionLimits:
    max_provider_turns: int = 8
    max_tool_calls: int = 20

    def __post_init__(self) -> None:
        if self.max_provider_turns <= 0 or self.max_tool_calls <= 0:
            raise ValueError("session limits must be positive")


@dataclass(frozen=True, slots=True)
class SessionOutcome:
    submitted: bool
    aborted: bool
    provider_turns: int
    tool_calls: int
    reason: str | None
    claim: Mapping[str, Any] | None = None


class DecisionSessionRunner:
    def __init__(
        self,
        *,
        provider: ProviderAdapter,
        executor: WorkspaceToolExecutor,
        budget: BudgetLedger,
        event_sink: EventSink,
        limits: SessionLimits = SessionLimits(),
    ) -> None:
        self.provider = provider
        self.executor = executor
        self.budget = budget
        self.event_sink = event_sink
        self.limits = limits

    def run(self, context: DecisionContext) -> SessionOutcome:
        if context.prompt_text is not None:
            actual_hash = hashlib.sha256(context.prompt_text.encode("utf-8")).hexdigest()
            if context.prompt_sha256 != actual_hash:
                raise SessionError("decision prompt hash mismatch")
        provider_turns = 0
        tool_calls = 0
        previous_response_id: str | None = None
        results: Sequence[ToolResult] = ()

        while True:
            if provider_turns >= self.limits.max_provider_turns:
                raise SessionError("provider turn limit reached")
            if not self.budget.can_charge(BudgetDelta(model_calls=1)):
                raise SessionError("model call budget reached")

            self.event_sink(
                EventType.PROVIDER_CALL_STARTED,
                {
                    "provider": self.provider.provider_name,
                    "model_id": self.provider.model_id,
                    "prompt_sha256": context.prompt_sha256,
                    "information_counts": dict(context.information_counts),
                },
            )
            if previous_response_id is None:
                turn = self.provider.start(context, CANONICAL_TOOLS)
            else:
                turn = self.provider.continue_with_results(
                    previous_response_id,
                    results,
                    CANONICAL_TOOLS,
                )
            provider_turns += 1
            previous_response_id = turn.provider_response_id
            self._charge_turn(turn)
            self.event_sink(
                EventType.PROVIDER_CALL_COMPLETED,
                {
                    "provider": self.provider.provider_name,
                    "model_id": self.provider.model_id,
                    "provider_response_id": previous_response_id,
                    "usage": dict(turn.usage),
                    "tool_call_count": len(turn.tool_calls),
                },
            )

            if not turn.tool_calls:
                return SessionOutcome(
                    submitted=self.executor.submitted,
                    aborted=self.executor.aborted,
                    provider_turns=provider_turns,
                    tool_calls=tool_calls,
                    reason=self.executor.terminal_reason or turn.final_text,
                    claim=None
                    if self.executor.submission_claim is None
                    else self.executor.submission_claim.as_dict(),
                )

            if tool_calls + len(turn.tool_calls) > self.limits.max_tool_calls:
                raise SessionError("tool call limit reached")

            current_results = []
            for call in turn.tool_calls:
                tool_calls += 1
                self.event_sink(
                    EventType.TOOL_CALLED,
                    {
                        "call_id": call.call_id,
                        "name": call.name,
                        "arguments": dict(call.arguments),
                    },
                )
                result = self.executor.execute(call)
                current_results.append(result)
                self.event_sink(
                    EventType.TOOL_COMPLETED,
                    {
                        "call_id": call.call_id,
                        "name": call.name,
                        "is_error": result.is_error,
                        "output": dict(result.output),
                    },
                )
                if self.executor.submitted or self.executor.aborted:
                    return SessionOutcome(
                        submitted=self.executor.submitted,
                        aborted=self.executor.aborted,
                        provider_turns=provider_turns,
                        tool_calls=tool_calls,
                        reason=self.executor.terminal_reason,
                        claim=None
                        if self.executor.submission_claim is None
                        else self.executor.submission_claim.as_dict(),
                    )
            results = tuple(current_results)

    def _charge_turn(self, turn: ProviderTurn) -> None:
        delta = BudgetDelta(
            model_calls=1,
            input_tokens=int(turn.usage.get("input_tokens", 0)),
            output_tokens=int(turn.usage.get("output_tokens", 0)),
            cost_microusd=int(turn.usage.get("cost_microusd", 0)),
        )
        usage = self.budget.charge(delta)
        self.event_sink(
            EventType.BUDGET_CHARGED,
            {
                "delta": {
                    "model_calls": delta.model_calls,
                    "input_tokens": delta.input_tokens,
                    "output_tokens": delta.output_tokens,
                    "cost_microusd": delta.cost_microusd,
                },
                "usage": {
                    "model_calls": usage.model_calls,
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "cost_microusd": usage.cost_microusd,
                },
            },
        )
