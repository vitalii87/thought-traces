from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterator

from .domain import ArenaEvent


GENESIS_HASH = "0" * 64


class EventChainError(ValueError):
    """Raised when an event log is malformed or its hash chain is invalid."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _record_hash(previous_event_hash: str, event: dict[str, Any]) -> str:
    body = {"event": event, "previous_event_hash": previous_event_hash}
    return hashlib.sha256(_canonical_json(body)).hexdigest()


class JsonlEventStore:
    """Append-only JSONL event storage with per-file hash chaining."""

    def __init__(self, path: Path, *, durable: bool = True) -> None:
        self.path = Path(path)
        self.durable = durable

    def append(self, event: ArenaEvent) -> str:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        previous_hash = self.last_hash()
        event_data = event.as_dict()
        event_hash = _record_hash(previous_hash, event_data)
        record = {
            "event": event_data,
            "previous_event_hash": previous_hash,
            "event_hash": event_hash,
        }

        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(_canonical_json(record).decode("utf-8"))
            stream.write("\n")
            stream.flush()
            if self.durable:
                os.fsync(stream.fileno())
        return event_hash

    def records(self) -> Iterator[dict[str, Any]]:
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as error:
                    raise EventChainError(f"invalid JSON at line {line_number}") from error
                if not isinstance(value, dict):
                    raise EventChainError(f"record at line {line_number} is not an object")
                yield value

    def validate(self) -> int:
        expected_previous = GENESIS_HASH
        expected_lineage: str | None = None
        count = 0
        for count, record in enumerate(self.records(), start=1):
            try:
                previous_hash = record["previous_event_hash"]
                event = record["event"]
                stored_hash = record["event_hash"]
            except KeyError as error:
                raise EventChainError(f"missing field at line {count}: {error.args[0]}") from error

            if previous_hash != expected_previous:
                raise EventChainError(f"broken previous hash at line {count}")
            if not isinstance(event, dict):
                raise EventChainError(f"event at line {count} is not an object")
            lineage_id = event.get("lineage_id")
            if not isinstance(lineage_id, str) or not lineage_id:
                raise EventChainError(f"invalid lineage_id at line {count}")
            if expected_lineage is None:
                expected_lineage = lineage_id
            elif lineage_id != expected_lineage:
                raise EventChainError(f"mixed lineage_id at line {count}")
            computed_hash = _record_hash(previous_hash, event)
            if stored_hash != computed_hash:
                raise EventChainError(f"invalid event hash at line {count}")
            expected_previous = stored_hash
        return count

    def last_hash(self) -> str:
        last = GENESIS_HASH
        for record in self.records():
            last = record.get("event_hash", "")
        if last == GENESIS_HASH:
            return last
        self.validate()
        return last
