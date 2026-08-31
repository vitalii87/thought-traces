import unittest

from iah_arena.prompts import (
    ImprovementClaim,
    ImprovementPromptBuilder,
    InformationBudget,
    InformationBudgetExceeded,
)
from iah_arena.providers import DecisionContext
from iah_arena.tools import CANONICAL_TOOLS


class ImprovementPromptTests(unittest.TestCase):
    def context(self) -> DecisionContext:
        return DecisionContext(
            lineage_id="lineage-a",
            epoch=2,
            generation=1,
            attempt=3,
            objective={"quality": "maximize"},
            metrics={"quality": 0.7},
            budget_remaining={"model_calls": 2},
            workspace_summary={"files": ["solver.py"], "total_bytes": 100},
            stage={"stage_id": "small"},
        )

    def budget(self, **overrides) -> InformationBudget:
        values = {
            "max_prompt_chars": 20_000,
            "max_history_items": 3,
            "max_metric_items": 5,
            "max_workspace_files": 10,
            "max_workspace_bytes": 1_000,
        }
        values.update(overrides)
        return InformationBudget(**values)

    def test_prompt_is_deterministic_and_allows_language_migration(self) -> None:
        builder = ImprovementPromptBuilder(self.budget())
        history = ({"result": "rejected"},)
        first = builder.build(self.context(), CANONICAL_TOOLS, recent_history=history)
        second = builder.build(self.context(), CANONICAL_TOOLS, recent_history=history)

        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first.text, second.text)
        self.assertIn("Replace the programming language", first.text)
        self.assertNotIn("gemini", first.text.lower())

        attached = builder.attach(self.context(), CANONICAL_TOOLS)
        self.assertIsNotNone(attached.prompt_text)
        expected = builder.build(self.context(), CANONICAL_TOOLS)
        self.assertEqual(attached.prompt_sha256, expected.sha256)

    def test_information_budget_fails_closed(self) -> None:
        builder = ImprovementPromptBuilder(self.budget(max_workspace_bytes=99))
        with self.assertRaises(InformationBudgetExceeded):
            builder.build(self.context(), CANONICAL_TOOLS)

    def test_claim_schema_is_exact(self) -> None:
        claim = ImprovementClaim.from_mapping(
            {
                "bottleneck": "quadratic search",
                "hypothesis": "indexing removes repeated scans",
                "changes": ["add index"],
                "expected_effect": "lower runtime",
                "risks": ["memory growth"],
            }
        )
        self.assertEqual(claim.changes, ("add index",))


if __name__ == "__main__":
    unittest.main()
