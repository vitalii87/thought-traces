from __future__ import annotations

import os
from pathlib import Path
from types import TracebackType


class LockUnavailable(RuntimeError):
    pass


class FileLock:
    """Non-blocking advisory single-process lock for the arena control plane."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._stream = None

    def __enter__(self) -> "FileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        stream = self.path.open("a+b")
        stream.seek(0, os.SEEK_END)
        if stream.tell() == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        try:
            self._lock(stream)
        except OSError as error:
            stream.close()
            raise LockUnavailable(f"arena lock is already held: {self.path}") from error
        self._stream = stream
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._stream is None:
            return
        try:
            self._unlock(self._stream)
        finally:
            self._stream.close()
            self._stream = None

    @staticmethod
    def _lock(stream) -> None:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            return
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    @staticmethod
    def _unlock(stream) -> None:
        stream.seek(0)
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            return
        import fcntl

        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
