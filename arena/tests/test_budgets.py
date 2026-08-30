import unittest

from iah_arena.budgets import BudgetDelta, BudgetExceeded, BudgetLedger, BudgetLimits


class BudgetLedgerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.ledger = BudgetLedger(
            BudgetLimits(
                model_calls=2,
                input_tokens=100,
                output_tokens=50,
                cost_microusd=1_000,
                local_cpu_seconds=60,
            )
        )

    def test_charge_and_remaining(self) -> None:
        usage = self.ledger.charge(
            BudgetDelta(
                model_calls=1,
                input_tokens=40,
                output_tokens=10,
                cost_microusd=250,
                local_cpu_seconds=12,
            )
        )
        self.assertEqual(usage.model_calls, 1)
        self.assertEqual(self.ledger.remaining().input_tokens, 60)
        self.assertEqual(self.ledger.remaining().cost_microusd, 750)

    def test_rejects_charge_atomically(self) -> None:
        with self.assertRaises(BudgetExceeded):
            self.ledger.charge(BudgetDelta(input_tokens=101))
        self.assertEqual(self.ledger.usage.input_tokens, 0)

    def test_reports_all_violations(self) -> None:
        violations = self.ledger.violations(
            BudgetDelta(model_calls=3, output_tokens=51, local_cpu_seconds=61)
        )
        self.assertEqual(
            violations,
            ("model_calls", "output_tokens", "local_cpu_seconds"),
        )


if __name__ == "__main__":
    unittest.main()
