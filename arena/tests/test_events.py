import json
import tempfile
import unittest
from pathlib import Path

from iah_arena.controller import ArenaController
from iah_arena.domain import ArenaEvent, EventType
from iah_arena.events import EventChainError, JsonlEventStore


class EventStoreTests(unittest.TestCase):
    def test_round_trip_and_hash_chain(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            store = JsonlEventStore(path, durable=False)
            first_hash = store.append(
                ArenaEvent(
                    lineage_id="lineage-1",
                    event_type=EventType.LINEAGE_CREATED,
                    payload={"origin": "test"},
                )
            )
            second_hash = store.append(
                ArenaEvent(
                    lineage_id="lineage-1",
                    event_type=EventType.EPOCH_STARTED,
                    epoch=1,
                )
            )

            records = list(store.records())
            self.assertEqual(store.validate(), 2)
            self.assertEqual(records[1]["previous_event_hash"], first_hash)
            self.assertEqual(records[1]["event_hash"], second_hash)

    def test_detects_payload_tampering(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            store = JsonlEventStore(path, durable=False)
            store.append(
                ArenaEvent(
                    lineage_id="lineage-1",
                    event_type=EventType.LINEAGE_CREATED,
                    payload={"origin": "original"},
                )
            )
            record = json.loads(path.read_text(encoding="utf-8"))
            record["event"]["payload"]["origin"] = "changed"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")

            with self.assertRaises(EventChainError):
                store.validate()

    def test_detects_mixed_lineages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            store = JsonlEventStore(path, durable=False)
            store.append(
                ArenaEvent(
                    lineage_id="lineage-1",
                    event_type=EventType.LINEAGE_CREATED,
                )
            )
            store.append(
                ArenaEvent(
                    lineage_id="lineage-2",
                    event_type=EventType.EPOCH_STARTED,
                )
            )

            with self.assertRaises(EventChainError):
                store.validate()

    def test_controller_refuses_duplicate_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            controller = ArenaController(Path(directory))
            controller.initialize_lineage("lineage-1", origin="test")
            with self.assertRaises(FileExistsError):
                controller.initialize_lineage("lineage-1", origin="test")


if __name__ == "__main__":
    unittest.main()
