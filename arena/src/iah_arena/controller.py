from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .domain import ArenaEvent, EventType
from .events import JsonlEventStore


class ArenaController:
    """Minimal trusted controller foundation.

    Provider sessions, workspace mutation, Docker, and evaluation are deliberately
    left for later milestones. This class currently establishes lineage identity
    and durable provenance only.
    """

    def __init__(self, state_dir: Path) -> None:
        self.state_dir = Path(state_dir)

    def event_store(self, lineage_id: str) -> JsonlEventStore:
        return JsonlEventStore(self.state_dir / "lineages" / lineage_id / "events.jsonl")

    def initialize_lineage(
        self,
        lineage_id: str,
        *,
        origin: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        store = self.event_store(lineage_id)
        if store.path.exists() and store.validate() > 0:
            raise FileExistsError(f"lineage already exists: {lineage_id}")
        payload = {"origin": origin, "metadata": dict(metadata or {})}
        return store.append(
            ArenaEvent(
                lineage_id=lineage_id,
                event_type=EventType.LINEAGE_CREATED,
                payload=payload,
            )
        )

    def verify_lineage(self, lineage_id: str) -> int:
        return self.event_store(lineage_id).validate()
