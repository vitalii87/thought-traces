import tempfile
import unittest
from pathlib import Path

from iah_arena.budgets import BudgetLedger, BudgetLimits
from iah_arena.runtime import (
    JsonRuntimeEvaluator,
    Mount,
    RuntimeLimits,
    RuntimePublicTestRunner,
    RuntimeRequest,
    RuntimeResult,
    RuntimeRole,
    ScriptedRuntime,
)


class RuntimeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.limits = RuntimeLimits(cpus=1, memory_mb=256, pids=32, timeout_seconds=5)

    def test_judge_must_use_read_only_workspace(self) -> None:
        with self.assertRaises(ValueError):
            RuntimeRequest(("judge",), RuntimeRole.JUDGE, workspace_read_only=False)

    def test_judge_rejects_writable_extra_mount(self) -> None:
        with self.assertRaises(ValueError):
            RuntimeRequest(
                ("judge",),
                RuntimeRole.JUDGE,
                workspace_read_only=True,
                extra_mounts=(Mount(Path("fixtures"), "/fixtures", read_only=False),),
            )

    def test_public_test_runner_reports_and_charges_runtime(self) -> None:
        runtime = ScriptedRuntime((RuntimeResult(0, False, 1_001, stdout="ok"),))
        budget = BudgetLedger(BudgetLimits(1, 1, 1, 1, 5))
        runner = RuntimePublicTestRunner(
            runtime=runtime,
            request=RuntimeRequest(("test",), RuntimeRole.WORKSHOP, False),
            limits=self.limits,
            budget=budget,
        )

        result = runner(Path("workspace"))

        self.assertTrue(result["passed"])
        self.assertEqual(budget.usage.local_cpu_seconds, 2)

    def test_json_evaluator_reads_final_stdout_line(self) -> None:
        runtime = ScriptedRuntime(
            (RuntimeResult(0, False, 10, stdout='diagnostic\n{"accepted": true, "fitness": 4}\n'),)
        )
        evaluator = JsonRuntimeEvaluator(
            runtime=runtime,
            request=RuntimeRequest(("judge",), RuntimeRole.JUDGE, True),
            limits=self.limits,
        )

        result = evaluator(Path("workspace"))

        self.assertTrue(result["accepted"])
        self.assertEqual(result["fitness"], 4)

    def test_failed_judge_is_a_rejection(self) -> None:
        runtime = ScriptedRuntime((RuntimeResult(2, False, 10, stderr="failed"),))
        evaluator = JsonRuntimeEvaluator(
            runtime=runtime,
            request=RuntimeRequest(("judge",), RuntimeRole.JUDGE, True),
            limits=self.limits,
        )

        result = evaluator(Path("workspace"))

        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "judge execution failed")


if __name__ == "__main__":
    unittest.main()
