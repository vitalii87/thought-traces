from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from .domain import EventType
from .events import JsonlEventStore


_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _numeric_leaves(value: Any, prefix: str = "") -> Iterable[tuple[str, int | float]]:
    if isinstance(value, Mapping):
        for key in sorted(value):
            child = f"{prefix}.{key}" if prefix else str(key)
            yield from _numeric_leaves(value[key], child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"{prefix}[{index}]"
            yield from _numeric_leaves(item, child)
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        yield prefix, value


@dataclass(frozen=True, slots=True)
class TelemetryExport:
    path: Path
    export_id: str
    event_rows: int
    metric_rows: int


class TelemetryExporter:
    """Create a deterministic, analysis-ready snapshot across independent lineages."""

    EVENT_COLUMNS = (
        "timestamp_utc",
        "lineage_id",
        "epoch",
        "generation",
        "attempt",
        "event_type",
        "event_id",
        "previous_event_hash",
        "event_hash",
        "payload_json",
    )
    METRIC_COLUMNS = (
        "timestamp_utc",
        "lineage_id",
        "epoch",
        "generation",
        "attempt",
        "event_id",
        "metric_path",
        "metric_value",
    )

    def __init__(self, state_dir: Path) -> None:
        self.state_dir = Path(state_dir)

    def export_bundle(self, lineage_ids: Iterable[str], output_dir: Path) -> TelemetryExport:
        requested_lineage_ids = tuple(lineage_ids)
        if not requested_lineage_ids or len(set(requested_lineage_ids)) != len(
            requested_lineage_ids
        ):
            raise ValueError("lineage IDs must be non-empty and unique")
        lineage_ids = tuple(sorted(requested_lineage_ids))
        if any(not _SAFE_ID.fullmatch(lineage_id) for lineage_id in lineage_ids):
            raise ValueError("lineage ID contains unsupported characters")
        output_dir = Path(output_dir).resolve()
        if output_dir.exists():
            raise FileExistsError(f"telemetry output already exists: {output_dir}")

        records = []
        source_hashes = {}
        source_counts = {}
        for lineage_id in lineage_ids:
            store = JsonlEventStore(
                self.state_dir / "lineages" / lineage_id / "events.jsonl"
            )
            if not store.path.is_file():
                raise FileNotFoundError(f"lineage telemetry not found: {lineage_id}")
            source_counts[lineage_id] = store.validate()
            source_hashes[lineage_id] = store.last_hash()
            for record in store.records():
                records.append(record)
        records.sort(
            key=lambda record: (
                record["event"]["timestamp_utc"],
                record["event"]["lineage_id"],
                record["event"]["event_id"],
            )
        )

        output_dir.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(
            tempfile.mkdtemp(prefix="telemetry-", dir=output_dir.parent)
        )
        try:
            event_rows = self._write_events(staging / "events.csv", records)
            metric_rows = self._write_metrics(staging / "metrics.csv", records)
            identity = {
                "schema_version": 1,
                "lineage_ids": list(lineage_ids),
                "source_event_hashes": source_hashes,
                "source_event_counts": source_counts,
                "event_rows": event_rows,
                "metric_rows": metric_rows,
                "events_csv_sha256": _sha256_file(staging / "events.csv"),
                "metrics_csv_sha256": _sha256_file(staging / "metrics.csv"),
            }
            export_id = hashlib.sha256(
                json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            manifest = {
                **identity,
                "export_id": export_id,
                "created_utc": datetime.now(timezone.utc).isoformat(timespec="microseconds"),
            }
            (staging / "manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            os.replace(staging, output_dir)
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise
        return TelemetryExport(output_dir, export_id, event_rows, metric_rows)

    def _write_events(self, path: Path, records: list[dict[str, Any]]) -> int:
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=self.EVENT_COLUMNS, lineterminator="\n")
            writer.writeheader()
            for record in records:
                event = record["event"]
                writer.writerow(
                    {
                        "timestamp_utc": event["timestamp_utc"],
                        "lineage_id": event["lineage_id"],
                        "epoch": event["epoch"],
                        "generation": event["generation"],
                        "attempt": event["attempt"],
                        "event_type": event["event_type"],
                        "event_id": event["event_id"],
                        "previous_event_hash": record["previous_event_hash"],
                        "event_hash": record["event_hash"],
                        "payload_json": json.dumps(
                            event["payload"],
                            ensure_ascii=False,
                            allow_nan=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                    }
                )
        return len(records)

    def _write_metrics(self, path: Path, records: list[dict[str, Any]]) -> int:
        rows = 0
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=self.METRIC_COLUMNS, lineterminator="\n")
            writer.writeheader()
            for record in records:
                event = record["event"]
                if event["event_type"] != EventType.CANDIDATE_EVALUATED.value:
                    continue
                for metric_path, metric_value in _numeric_leaves(event["payload"]):
                    writer.writerow(
                        {
                            "timestamp_utc": event["timestamp_utc"],
                            "lineage_id": event["lineage_id"],
                            "epoch": event["epoch"],
                            "generation": event["generation"],
                            "attempt": event["attempt"],
                            "event_id": event["event_id"],
                            "metric_path": metric_path,
                            "metric_value": str(metric_value)
                            if isinstance(metric_value, int)
                            else format(metric_value, ".17g"),
                        }
                    )
                    rows += 1
        return rows
