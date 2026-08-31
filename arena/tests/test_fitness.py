import unittest
from pathlib import Path

from iah_arena.fitness import (
    AcceptanceMode,
    FitnessPolicy,
    FitnessVector,
    MetricDirection,
    MetricSpec,
    ParetoArchive,
    ParetoPoint,
    ParetoRelation,
    PolicyEvaluator,
)


class FitnessPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metrics = (
            MetricSpec("quality", MetricDirection.MAXIMIZE, epsilon=0.01, weight=2),
            MetricSpec(
                "runtime_ms",
                MetricDirection.MINIMIZE,
                feasibility_max=100,
                weight=0.1,
            ),
        )

    def test_pareto_dominance_respects_direction_and_epsilon(self) -> None:
        policy = FitnessPolicy(self.metrics)
        incumbent = FitnessVector({"quality": 0.8, "runtime_ms": 80})
        candidate = FitnessVector({"quality": 0.82, "runtime_ms": 70})

        decision = policy.decide(candidate, incumbent)

        self.assertTrue(decision.accepted)
        self.assertEqual(decision.relation, ParetoRelation.DOMINATES)

    def test_tradeoff_is_retained_but_not_greedily_accepted(self) -> None:
        policy = FitnessPolicy(self.metrics)
        incumbent = FitnessVector({"quality": 0.8, "runtime_ms": 80})
        candidate = FitnessVector({"quality": 0.9, "runtime_ms": 90})

        decision = policy.decide(candidate, incumbent)

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.relation, ParetoRelation.TRADEOFF)

    def test_infeasible_candidate_is_rejected(self) -> None:
        policy = FitnessPolicy(self.metrics)
        decision = policy.decide(
            FitnessVector({"quality": 1, "runtime_ms": 101}),
            FitnessVector({"quality": 0.5, "runtime_ms": 80}),
        )
        self.assertFalse(decision.accepted)
        self.assertIn("infeasible", decision.reason)

    def test_weighted_policy_preserves_component_relation(self) -> None:
        policy = FitnessPolicy(
            self.metrics,
            mode=AcceptanceMode.WEIGHTED,
            minimum_scalar_improvement=0.1,
        )
        decision = policy.decide(
            FitnessVector({"quality": 0.9, "runtime_ms": 80}),
            FitnessVector({"quality": 0.8, "runtime_ms": 80}),
        )
        self.assertTrue(decision.accepted)
        self.assertIsNotNone(decision.candidate_score)

    def test_archive_keeps_equivalent_and_tradeoff_families(self) -> None:
        archive = ParetoArchive(FitnessPolicy(self.metrics))
        self.assertTrue(
            archive.add(ParetoPoint("fast", FitnessVector({"quality": 0.8, "runtime_ms": 60})))
        )
        self.assertTrue(
            archive.add(ParetoPoint("accurate", FitnessVector({"quality": 0.9, "runtime_ms": 80})))
        )
        self.assertTrue(
            archive.add(
                ParetoPoint(
                    "equivalent",
                    FitnessVector({"quality": 0.9, "runtime_ms": 80}),
                )
            )
        )
        self.assertEqual(len(archive.points), 3)

    def test_policy_evaluator_overrides_task_acceptance_flag(self) -> None:
        evaluator = PolicyEvaluator(
            evaluator=lambda workspace: {
                "accepted": True,
                "fitness": {"quality": 0.7, "runtime_ms": 90},
            },
            policy=FitnessPolicy(self.metrics),
            incumbent=FitnessVector({"quality": 0.8, "runtime_ms": 80}),
        )

        result = evaluator(Path("unused"))

        self.assertFalse(result["accepted"])
        self.assertEqual(result["acceptance"]["pareto_relation"], "dominated")


if __name__ == "__main__":
    unittest.main()
