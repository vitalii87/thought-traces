import tempfile
import unittest
from pathlib import Path

from iah_arena.providers import ToolCall
from iah_arena.tools import WorkspaceToolExecutor


class WorkspaceToolExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name)
        (self.workspace / "solver.txt").write_text("old\n", encoding="utf-8")
        self.executor = WorkspaceToolExecutor(
            self.workspace,
            public_test_runner=lambda workspace: {
                "passed": (workspace / "solver.txt").read_text(encoding="utf-8") == "new\n"
            },
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def call(self, name: str, arguments: dict[str, object]):
        return self.executor.execute(ToolCall("call", name, arguments))

    def test_path_traversal_is_rejected(self) -> None:
        result = self.call("read_file", {"path": "../secret.txt"})
        self.assertTrue(result.is_error)

    def test_submission_requires_fresh_passing_tests(self) -> None:
        self.assertTrue(self.call("submit_candidate", {"summary": "premature"}).is_error)
        self.assertFalse(
            self.call("write_file", {"path": "solver.txt", "content": "new\n"}).is_error
        )
        self.assertFalse(self.call("run_public_tests", {}).is_error)
        self.assertFalse(self.call("submit_candidate", {"summary": "ready"}).is_error)
        self.assertTrue(self.executor.submitted)

    def test_change_invalidates_previous_public_test(self) -> None:
        self.call("write_file", {"path": "solver.txt", "content": "new\n"})
        self.call("run_public_tests", {})
        self.call("write_file", {"path": "notes.txt", "content": "changed"})

        result = self.call("submit_candidate", {"summary": "stale test"})
        self.assertTrue(result.is_error)


if __name__ == "__main__":
    unittest.main()
