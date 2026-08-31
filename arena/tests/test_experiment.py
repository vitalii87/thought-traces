import json
import tempfile
import unittest
from pathlib import Path

from iah_arena.experiment import (
    ExperimentPhase,
    ExperimentRunManager,
    HoldoutStatus,
    RunManifest,
)
from iah_arena.tasking import SuiteKind


def manifest() -> RunManifest:
    return RunManifest(
        experiment_id="run-001",
        protocol_version="v1",
        protocol_sha256="a" * 64,
        task_id="task",
        task_version="v1",
        evaluator_version="v1",
        curriculum_digest="b" * 64,
        environment_digest="sha256:" + "c" * 64,
        arena_commit="abc1234",
        configuration_sha256="f" * 64,
        lineage_ids=("lineage-a", "lineage-b"),
        optimizer_ids={"lineage-a": "provider/a", "lineage-b": "provider/b"},
        random_seeds={"lineage-a": 1, "lineage-b": 2},
        created_utc="2026-01-01T00:00:00+00:00",
    )


class ExperimentRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.manager = ExperimentRunManager(Path(self.temporary.name), "run-001")
        self.manager.create(manifest())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_final_holdout_is_closed_during_optimization(self) -> None:
        state = self.manager.start_optimization(expected_revision=0)
        self.manager.assert_suite_allowed(SuiteKind.SELECTION)
        with self.assertRaises(PermissionError):
            self.manager.assert_suite_allowed(SuiteKind.FINAL_HOLDOUT)
        self.assertEqual(state.phase, ExperimentPhase.OPTIMIZATION)

    def test_holdout_is_one_shot_and_completion_requires_every_lineage(self) -> None:
        self.manager.start_optimization(expected_revision=0)
        self.manager.close_optimization(expected_revision=1)
        self.manager.open_holdout(expected_revision=2)

        first = self.manager.reserve_holdout("lineage-a", "a" * 64, expected_revision=3)
        with self.assertRaises(PermissionError):
            self.manager.reserve_holdout("lineage-a", "a" * 64, expected_revision=4)
        state = self.manager.record_holdout_result(
            "lineage-a",
            first.reservation_token,
            "d" * 64,
            expected_revision=4,
        )
        self.assertEqual(state.phase, ExperimentPhase.HOLDOUT_OPEN)
        self.assertEqual(state.holdout_records["lineage-a"].status, HoldoutStatus.RECORDED)

        second = self.manager.reserve_holdout("lineage-b", "b" * 64, expected_revision=5)
        state = self.manager.record_holdout_result(
            "lineage-b",
            second.reservation_token,
            "e" * 64,
            expected_revision=6,
        )
        self.assertEqual(state.phase, ExperimentPhase.COMPLETE)
        with self.assertRaises(PermissionError):
            self.manager.assert_suite_allowed(SuiteKind.FINAL_HOLDOUT)
        self.assertGreaterEqual(self.manager.events.validate(), 8)

    def test_stale_revision_is_rejected(self) -> None:
        self.manager.start_optimization(expected_revision=0)
        with self.assertRaises(RuntimeError):
            self.manager.close_optimization(expected_revision=0)

    def test_state_tampering_is_detected(self) -> None:
        state = json.loads(self.manager.state_path.read_text(encoding="utf-8"))
        state["phase"] = "complete"
        self.manager.state_path.write_text(json.dumps(state), encoding="utf-8")
        with self.assertRaises(RuntimeError):
            self.manager.state()

        recovered = self.manager.recover_state()
        self.assertEqual(recovered.phase, ExperimentPhase.DRAFT)
        self.assertEqual(self.manager.state(), recovered)


if __name__ == "__main__":
    unittest.main()
