import unittest

from iah_arena.coordinator import (
    LineageDisposition,
    SequentialLineageCoordinator,
    StepStatus,
)


class SequentialCoordinatorTests(unittest.TestCase):
    def test_order_rotates_between_epochs(self) -> None:
        coordinator = SequentialLineageCoordinator(("gpt", "gemini", "claude"))
        self.assertEqual(coordinator.order_for_epoch(1), ("gpt", "gemini", "claude"))
        self.assertEqual(coordinator.order_for_epoch(2), ("gemini", "claude", "gpt"))
        self.assertEqual(coordinator.order_for_epoch(3), ("claude", "gpt", "gemini"))

    def test_failure_is_isolated_and_does_not_stop_other_lineages(self) -> None:
        coordinator = SequentialLineageCoordinator(("a", "b", "c"))
        visited = []

        def step(lineage_id, epoch):
            visited.append(lineage_id)
            if lineage_id == "b":
                raise RuntimeError("provider failed")
            return {"epoch": epoch}

        results = coordinator.run_epoch(1, step)
        self.assertEqual(visited, ["a", "b", "c"])
        self.assertEqual(
            [result.status for result in results],
            [StepStatus.SUCCEEDED, StepStatus.FAILED, StepStatus.SUCCEEDED],
        )

    def test_terminal_lineage_is_excluded_from_future_epochs(self) -> None:
        coordinator = SequentialLineageCoordinator(("a", "b", "c"))
        coordinator.mark_attrited("b")
        self.assertEqual(coordinator.order_for_epoch(2), ("c", "a"))
        self.assertEqual(coordinator.dispositions["b"], LineageDisposition.ATTRITED)


if __name__ == "__main__":
    unittest.main()
