import csv
import json
import tempfile
import unittest
from pathlib import Path

from iah_arena.domain import ArenaEvent, EventType
from iah_arena.events import JsonlEventStore
from iah_arena.telemetry import TelemetryExporter


class TelemetryExporterTests(unittest.TestCase):
    def test_exports_validated_cross_lineage_tables(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state"
            for index, lineage_id in enumerate(("lineage-b", "lineage-a"), start=1):
                store = JsonlEventStore(state / "lineages" / lineage_id / "events.jsonl")
                store.append(ArenaEvent(lineage_id, EventType.LINEAGE_CREATED))
                store.append(
                    ArenaEvent(
                        lineage_id,
                        EventType.CANDIDATE_EVALUATED,
                        payload={
                            "accepted": True,
                            "fitness": {
                                "quality": 0.8 + index / 10,
                                "runtime_ms": 20 + index,
                                "operations": 9_007_199_254_740_993 + index,
                            },
                        },
                        epoch=1,
                        attempt=1,
                    )
                )

            exported = TelemetryExporter(state).export_bundle(
                ("lineage-b", "lineage-a"),
                root / "export",
            )

            self.assertEqual(exported.event_rows, 4)
            self.assertEqual(exported.metric_rows, 6)
            with (exported.path / "events.csv").open(encoding="utf-8", newline="") as stream:
                events = list(csv.DictReader(stream))
            with (exported.path / "metrics.csv").open(encoding="utf-8", newline="") as stream:
                metrics = list(csv.DictReader(stream))
            export_manifest = json.loads(
                (exported.path / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual({row["lineage_id"] for row in events}, {"lineage-a", "lineage-b"})
            self.assertEqual(
                {row["metric_path"] for row in metrics},
                {"fitness.operations", "fitness.quality", "fitness.runtime_ms"},
            )
            operation_values = {
                row["metric_value"]
                for row in metrics
                if row["metric_path"] == "fitness.operations"
            }
            self.assertEqual(
                operation_values,
                {"9007199254740994", "9007199254740995"},
            )
            self.assertEqual(export_manifest["export_id"], exported.export_id)

    def test_refuses_to_overwrite_an_export(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            state = root / "state"
            store = JsonlEventStore(state / "lineages" / "lineage-a" / "events.jsonl")
            store.append(ArenaEvent("lineage-a", EventType.LINEAGE_CREATED))
            output = root / "export"
            TelemetryExporter(state).export_bundle(("lineage-a",), output)
            with self.assertRaises(FileExistsError):
                TelemetryExporter(state).export_bundle(("lineage-a",), output)


if __name__ == "__main__":
    unittest.main()
