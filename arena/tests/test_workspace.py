import tempfile
import unittest
from pathlib import Path

from iah_arena.workspace import LineageWorkspaceManager


class WorkspaceManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.seed = root / "seed"
        self.seed.mkdir()
        (self.seed / "solver.txt").write_text("seed\n", encoding="utf-8")
        self.manager = LineageWorkspaceManager(root / "state", "lineage-a")
        self.manager.initialize(self.seed)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_rejected_attempt_does_not_modify_accepted_generation(self) -> None:
        attempt = self.manager.begin_attempt(epoch=1, attempt=1)
        (attempt.files_path / "solver.txt").write_text("rejected\n", encoding="utf-8")
        archived = self.manager.reject(attempt, reason="fitness decreased")

        self.assertEqual(
            (self.manager.current_files() / "solver.txt").read_text(encoding="utf-8"),
            "seed\n",
        )
        self.assertTrue(archived.path.is_dir())
        self.assertEqual(archived.lifecycle.reason, "fitness decreased")

    def test_accepted_attempt_becomes_next_immutable_generation(self) -> None:
        attempt = self.manager.begin_attempt(epoch=1, attempt=1)
        (attempt.files_path / "solver.txt").write_text("better\n", encoding="utf-8")
        submitted = self.manager.submit(attempt)
        promoted = self.manager.accept(submitted)

        self.assertEqual(self.manager.current_generation(), 1)
        self.assertEqual(
            (self.manager.current_files() / "solver.txt").read_text(encoding="utf-8"),
            "better\n",
        )
        self.assertEqual(promoted.path.name, "gen-0001")


if __name__ == "__main__":
    unittest.main()
