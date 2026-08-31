import tempfile
import unittest
from pathlib import Path

from iah_arena.locking import FileLock, LockUnavailable


class FileLockTests(unittest.TestCase):
    def test_second_controller_cannot_acquire_same_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "run.lock"
            with FileLock(path):
                with self.assertRaises(LockUnavailable):
                    with FileLock(path):
                        pass
            with FileLock(path):
                pass


if __name__ == "__main__":
    unittest.main()
