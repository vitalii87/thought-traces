from __future__ import annotations

from dataclasses import dataclass


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class BudgetLimits:
    model_calls: int
    input_tokens: int
    output_tokens: int
    cost_microusd: int
    local_cpu_seconds: int

    def __post_init__(self) -> None:
        if min(
            self.model_calls,
            self.input_tokens,
            self.output_tokens,
            self.cost_microusd,
            self.local_cpu_seconds,
        ) < 0:
            raise ValueError("budget limits must be non-negative")


@dataclass(frozen=True, slots=True)
class BudgetDelta:
    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_microusd: int = 0
    local_cpu_seconds: int = 0

    def __post_init__(self) -> None:
        if min(
            self.model_calls,
            self.input_tokens,
            self.output_tokens,
            self.cost_microusd,
            self.local_cpu_seconds,
        ) < 0:
            raise ValueError("budget deltas must be non-negative")


@dataclass(frozen=True, slots=True)
class BudgetUsage:
    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_microusd: int = 0
    local_cpu_seconds: int = 0

    def plus(self, delta: BudgetDelta) -> "BudgetUsage":
        return BudgetUsage(
            model_calls=self.model_calls + delta.model_calls,
            input_tokens=self.input_tokens + delta.input_tokens,
            output_tokens=self.output_tokens + delta.output_tokens,
            cost_microusd=self.cost_microusd + delta.cost_microusd,
            local_cpu_seconds=self.local_cpu_seconds + delta.local_cpu_seconds,
        )


class BudgetLedger:
    def __init__(self, limits: BudgetLimits) -> None:
        self.limits = limits
        self.usage = BudgetUsage()

    def violations(self, delta: BudgetDelta) -> tuple[str, ...]:
        projected = self.usage.plus(delta)
        violations = []
        for name in BudgetLimits.__dataclass_fields__:
            if getattr(projected, name) > getattr(self.limits, name):
                violations.append(name)
        return tuple(violations)

    def can_charge(self, delta: BudgetDelta) -> bool:
        return not self.violations(delta)

    def charge(self, delta: BudgetDelta) -> BudgetUsage:
        violations = self.violations(delta)
        if violations:
            raise BudgetExceeded("budget exceeded: " + ", ".join(violations))
        self.usage = self.usage.plus(delta)
        return self.usage

    def remaining(self) -> BudgetUsage:
        return BudgetUsage(
            model_calls=self.limits.model_calls - self.usage.model_calls,
            input_tokens=self.limits.input_tokens - self.usage.input_tokens,
            output_tokens=self.limits.output_tokens - self.usage.output_tokens,
            cost_microusd=self.limits.cost_microusd - self.usage.cost_microusd,
            local_cpu_seconds=self.limits.local_cpu_seconds - self.usage.local_cpu_seconds,
        )
