from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from typing import Any, Iterable, Mapping, Sequence

from .providers import DecisionContext, ToolDefinition


class InformationBudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class InformationBudget:
    max_prompt_chars: int
    max_history_items: int
    max_metric_items: int
    max_workspace_files: int
    max_workspace_bytes: int

    def __post_init__(self) -> None:
        if min(
            self.max_prompt_chars,
            self.max_history_items,
            self.max_metric_items,
            self.max_workspace_files,
            self.max_workspace_bytes,
        ) < 0:
            raise ValueError("information budget limits must be non-negative")


@dataclass(frozen=True, slots=True)
class ImprovementClaim:
    bottleneck: str
    hypothesis: str
    changes: tuple[str, ...]
    expected_effect: str
    risks: tuple[str, ...]

    def __post_init__(self) -> None:
        if not all(
            value.strip() for value in (self.bottleneck, self.hypothesis, self.expected_effect)
        ):
            raise ValueError("improvement claim fields must not be empty")
        if not self.changes or any(not item.strip() for item in self.changes):
            raise ValueError("improvement claim must list concrete changes")
        if any(not item.strip() for item in self.risks):
            raise ValueError("improvement claim risks must not contain empty items")

    def as_dict(self) -> dict[str, Any]:
        return {
            "bottleneck": self.bottleneck,
            "hypothesis": self.hypothesis,
            "changes": list(self.changes),
            "expected_effect": self.expected_effect,
            "risks": list(self.risks),
        }

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ImprovementClaim":
        expected = {"bottleneck", "hypothesis", "changes", "expected_effect", "risks"}
        if set(value) != expected:
            raise ValueError("improvement claim fields do not match the frozen schema")
        changes = value["changes"]
        risks = value["risks"]
        if not isinstance(changes, list) or not isinstance(risks, list):
            raise ValueError("improvement claim changes and risks must be arrays")
        scalar_fields = ("bottleneck", "hypothesis", "expected_effect")
        if any(not isinstance(value[field], str) for field in scalar_fields):
            raise ValueError("improvement claim scalar fields must be strings")
        if any(not isinstance(item, str) for item in changes + risks):
            raise ValueError("improvement claim array items must be strings")
        return cls(
            bottleneck=value["bottleneck"],
            hypothesis=value["hypothesis"],
            changes=tuple(changes),
            expected_effect=value["expected_effect"],
            risks=tuple(risks),
        )


@dataclass(frozen=True, slots=True)
class PromptEnvelope:
    text: str
    sha256: str
    character_count: int
    information_counts: Mapping[str, int]


class ImprovementPromptBuilder:
    CONTRACT_VERSION = "iah-improvement-v1"

    def __init__(self, budget: InformationBudget) -> None:
        self.budget = budget

    def build(
        self,
        context: DecisionContext,
        tools: Sequence[ToolDefinition],
        *,
        recent_history: Iterable[Mapping[str, Any]] = (),
    ) -> PromptEnvelope:
        history = tuple(dict(item) for item in recent_history)
        metrics = dict(context.metrics)
        workspace = dict(context.workspace_summary)
        files = workspace.get("files", workspace.get("known_files", ()))
        if not isinstance(files, (list, tuple)):
            raise ValueError("workspace summary files must be an array")
        total_bytes = int(workspace.get("total_bytes", 0))
        counts = {
            "history_items": len(history),
            "metric_items": len(metrics),
            "workspace_files": len(files),
            "workspace_bytes": total_bytes,
        }
        violations = []
        for key, maximum in (
            ("history_items", self.budget.max_history_items),
            ("metric_items", self.budget.max_metric_items),
            ("workspace_files", self.budget.max_workspace_files),
            ("workspace_bytes", self.budget.max_workspace_bytes),
        ):
            if counts[key] > maximum:
                violations.append(f"{key}={counts[key]}>{maximum}")
        if violations:
            raise InformationBudgetExceeded(
                "information budget exceeded: " + ", ".join(violations)
            )

        payload = {
            "contract_version": self.CONTRACT_VERSION,
            "instructions": {
                "objective": "Improve only this lineage under the declared constraints.",
                "freedoms": [
                    "Change algorithms, architecture, modules, representations, or build system.",
                    "Replace the programming language when evidence supports the migration cost.",
                    "Use bounded local tests and computation through the provided tools.",
                ],
                "prohibitions": [
                    "Do not infer or request other lineage implementations.",
                    (
                        "Do not access hidden evaluator cases, credentials, network, "
                        "or arena internals."
                    ),
                    "Do not claim success without fresh public tests and submit_candidate.",
                ],
                "decision_rule": (
                    "Diagnose the current bottleneck from supplied evidence, make the smallest "
                    "useful validated change or a justified staged rewrite, then submit or abort."
                ),
            },
            "context": {
                "lineage_id": context.lineage_id,
                "epoch": context.epoch,
                "generation": context.generation,
                "attempt": context.attempt,
                "stage": dict(context.stage),
                "objective": dict(context.objective),
                "metrics": metrics,
                "budget_remaining": dict(context.budget_remaining),
                "workspace_summary": workspace,
                "recent_history": list(history),
            },
            "required_submission_claim": {
                "bottleneck": "string",
                "hypothesis": "string",
                "changes": ["string"],
                "expected_effect": "string",
                "risks": ["string"],
            },
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
                for tool in tools
            ],
        }
        body = json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        text = "IAH ARENA DECISION CONTRACT\n" + body
        if len(text) > self.budget.max_prompt_chars:
            raise InformationBudgetExceeded(
                f"prompt characters={len(text)}>{self.budget.max_prompt_chars}"
            )
        return PromptEnvelope(
            text=text,
            sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
            character_count=len(text),
            information_counts=counts,
        )

    def attach(
        self,
        context: DecisionContext,
        tools: Sequence[ToolDefinition],
        *,
        recent_history: Iterable[Mapping[str, Any]] = (),
    ) -> DecisionContext:
        envelope = self.build(context, tools, recent_history=recent_history)
        return replace(
            context,
            prompt_text=envelope.text,
            prompt_sha256=envelope.sha256,
            information_counts=envelope.information_counts,
        )
