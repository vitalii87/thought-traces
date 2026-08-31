import unittest

from iah_arena.tasking import (
    BenchmarkSuite,
    CurriculumScheduler,
    CurriculumSpec,
    CurriculumStage,
    CurriculumState,
    CurriculumStatus,
    PromotionRule,
    SuiteKind,
)


def suites() -> tuple[BenchmarkSuite, ...]:
    return tuple(
        BenchmarkSuite(
            kind.value,
            kind,
            "v1",
            "aggregate" if kind is not SuiteKind.DEVELOPMENT else "detailed",
        )
        for kind in SuiteKind
    )


class CurriculumTests(unittest.TestCase):
    def spec(self) -> CurriculumSpec:
        return CurriculumSpec(
            "task-family",
            "v1",
            (
                CurriculumStage(
                    "small",
                    0,
                    {"size": 8},
                    PromotionRule("quality", 0.8, minimum_evaluations=2),
                ),
                CurriculumStage("large", 1, {"size": 64}, PromotionRule("quality", 0.9)),
            ),
            suites(),
        )

    def test_digest_is_stable_for_same_frozen_specification(self) -> None:
        self.assertEqual(self.spec().digest, self.spec().digest)
        self.assertEqual(len(self.spec().digest), 64)

    def test_stage_parameters_are_deeply_frozen(self) -> None:
        stage = CurriculumStage(
            "frozen",
            0,
            {"limits": {"sizes": [1, 2]}},
            PromotionRule("quality", 1),
        )
        with self.assertRaises(TypeError):
            stage.parameters["limits"]["sizes"] = (3,)

    def test_promotion_requires_threshold_and_minimum_evaluations(self) -> None:
        scheduler = CurriculumScheduler(self.spec())
        first = scheduler.observe(CurriculumState(), {"quality": 0.9})
        second = scheduler.observe(first.state, {"quality": 0.9})

        self.assertFalse(first.promoted)
        self.assertTrue(second.promoted)
        self.assertEqual(second.state.stage_index, 1)
        self.assertEqual(second.state.evaluations_at_stage, 0)

    def test_last_stage_can_complete(self) -> None:
        scheduler = CurriculumScheduler(self.spec())
        state = CurriculumState(stage_index=1)
        decision = scheduler.observe(state, {"quality": 0.95})
        self.assertEqual(decision.state.status, CurriculumStatus.COMPLETED)

    def test_budget_exhaustion_records_attrition(self) -> None:
        decision = CurriculumScheduler(self.spec()).observe(
            CurriculumState(),
            {"quality": 1.0},
            budget_exhausted=True,
        )
        self.assertEqual(decision.state.status, CurriculumStatus.ATTRITED)

    def test_all_benchmark_layers_are_required(self) -> None:
        with self.assertRaises(ValueError):
            CurriculumSpec(
                "incomplete",
                "v1",
                (CurriculumStage("only", 0, {}, PromotionRule("quality", 1)),),
                suites()[:-1],
            )


if __name__ == "__main__":
    unittest.main()
