import unittest

from iah_arena.lifecycle import AttemptLifecycle, AttemptStatus, LifecycleError


class AttemptLifecycleTests(unittest.TestCase):
    def test_valid_submission_and_acceptance(self) -> None:
        lifecycle = AttemptLifecycle(epoch=2, attempt=3, parent_generation=4)
        submitted = lifecycle.transition(AttemptStatus.SUBMITTED)
        accepted = submitted.transition(AttemptStatus.ACCEPTED)

        self.assertEqual(accepted.status, AttemptStatus.ACCEPTED)
        self.assertEqual(lifecycle.status, AttemptStatus.OPEN)

    def test_terminal_transition_is_rejected(self) -> None:
        lifecycle = AttemptLifecycle(epoch=1, attempt=1, parent_generation=0)
        rejected = lifecycle.transition(AttemptStatus.REJECTED, reason="no gain")

        with self.assertRaises(LifecycleError):
            rejected.transition(AttemptStatus.SUBMITTED)


if __name__ == "__main__":
    unittest.main()
