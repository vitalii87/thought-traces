from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


class ArtifactError(RuntimeError):
    pass


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _freeze_metadata(value: Mapping[str, Any]) -> Mapping[str, Any]:
    encoded = _canonical_json(dict(value))
    decoded = json.loads(encoded)
    return _freeze_value(decoded)


def _freeze_value(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_value(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_value(item) for item in value)
    return value


def _thaw_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_value(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class ArtifactFile:
    path: str
    size_bytes: int
    sha256: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "size_bytes": self.size_bytes,
            "sha256": self.sha256,
        }


@dataclass(frozen=True, slots=True)
class ArtifactProvenance:
    lineage_id: str
    epoch: int
    generation: int
    attempt: int
    parent_generation: int
    task_id: str
    task_version: str
    evaluator_version: str
    curriculum_digest: str
    environment_digest: str
    arena_commit: str
    random_seed: int
    optimizer_id: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        text_fields = (
            self.lineage_id,
            self.task_id,
            self.task_version,
            self.evaluator_version,
            self.curriculum_digest,
            self.environment_digest,
            self.arena_commit,
            self.optimizer_id,
        )
        if not all(value.strip() for value in text_fields):
            raise ValueError("artifact provenance text fields must not be empty")
        if min(self.epoch, self.generation, self.attempt, self.parent_generation) < 0:
            raise ValueError("artifact provenance counters must be non-negative")
        if self.random_seed < 0:
            raise ValueError("artifact random_seed must be non-negative")
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))

    def as_dict(self) -> dict[str, Any]:
        return {
            "lineage_id": self.lineage_id,
            "epoch": self.epoch,
            "generation": self.generation,
            "attempt": self.attempt,
            "parent_generation": self.parent_generation,
            "task_id": self.task_id,
            "task_version": self.task_version,
            "evaluator_version": self.evaluator_version,
            "curriculum_digest": self.curriculum_digest,
            "environment_digest": self.environment_digest,
            "arena_commit": self.arena_commit,
            "random_seed": self.random_seed,
            "optimizer_id": self.optimizer_id,
            "metadata": _thaw_value(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class ArtifactManifest:
    artifact_id: str
    artifact_type: str
    tree_sha256: str
    files: tuple[ArtifactFile, ...]
    provenance: ArtifactProvenance
    created_utc: str
    schema_version: int = 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "tree_sha256": self.tree_sha256,
            "files": [entry.as_dict() for entry in self.files],
            "provenance": self.provenance.as_dict(),
            "created_utc": self.created_utc,
        }


class ArtifactStore:
    """Immutable content-and-provenance addressed directory snapshots."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()

    def capture_directory(
        self,
        source: Path,
        *,
        artifact_type: str,
        provenance: ArtifactProvenance,
    ) -> ArtifactManifest:
        source = Path(source).resolve()
        if not source.is_dir():
            raise FileNotFoundError(f"artifact source not found: {source}")
        if not artifact_type.strip():
            raise ValueError("artifact_type must not be empty")
        if self.root == source or self.root.is_relative_to(source):
            raise ArtifactError("artifact store must not be inside the captured directory")
        files = self._scan(source)
        tree_sha256 = hashlib.sha256(
            _canonical_json([entry.as_dict() for entry in files])
        ).hexdigest()
        identity = {
            "schema_version": 1,
            "artifact_type": artifact_type,
            "tree_sha256": tree_sha256,
            "files": [entry.as_dict() for entry in files],
            "provenance": provenance.as_dict(),
        }
        artifact_id = hashlib.sha256(_canonical_json(identity)).hexdigest()
        destination = self.path_for(artifact_id)
        if destination.exists():
            manifest = self.load(artifact_id)
            self.verify(artifact_id)
            return manifest

        manifest = ArtifactManifest(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            tree_sha256=tree_sha256,
            files=files,
            provenance=provenance,
            created_utc=datetime.now(timezone.utc).isoformat(timespec="microseconds"),
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix="artifact-", dir=destination.parent))
        try:
            shutil.copytree(source, staging / "files")
            (staging / "manifest.json").write_bytes(
                json.dumps(
                    manifest.as_dict(),
                    ensure_ascii=False,
                    allow_nan=False,
                    indent=2,
                    sort_keys=True,
                ).encode("utf-8")
                + b"\n"
            )
            os.replace(staging, destination)
        except Exception:
            shutil.rmtree(staging, ignore_errors=True)
            raise
        return manifest

    def path_for(self, artifact_id: str) -> Path:
        if len(artifact_id) != 64 or any(
            character not in "0123456789abcdef" for character in artifact_id
        ):
            raise ValueError("artifact_id must be a lowercase SHA-256 digest")
        return self.root / "sha256" / artifact_id[:2] / artifact_id

    def load(self, artifact_id: str) -> ArtifactManifest:
        value = json.loads((self.path_for(artifact_id) / "manifest.json").read_text("utf-8"))
        files = tuple(ArtifactFile(**entry) for entry in value["files"])
        provenance = ArtifactProvenance(**value["provenance"])
        return ArtifactManifest(
            artifact_id=value["artifact_id"],
            artifact_type=value["artifact_type"],
            tree_sha256=value["tree_sha256"],
            files=files,
            provenance=provenance,
            created_utc=value["created_utc"],
            schema_version=value["schema_version"],
        )

    def verify(self, artifact_id: str) -> int:
        manifest = self.load(artifact_id)
        if manifest.artifact_id != artifact_id:
            raise ArtifactError("manifest artifact ID mismatch")
        artifact_path = self.path_for(artifact_id)
        actual_files = self._scan(artifact_path / "files")
        if actual_files != manifest.files:
            raise ArtifactError("artifact file manifest mismatch")
        tree_sha256 = hashlib.sha256(
            _canonical_json([entry.as_dict() for entry in actual_files])
        ).hexdigest()
        if tree_sha256 != manifest.tree_sha256:
            raise ArtifactError("artifact tree hash mismatch")
        identity = {
            "schema_version": manifest.schema_version,
            "artifact_type": manifest.artifact_type,
            "tree_sha256": manifest.tree_sha256,
            "files": [entry.as_dict() for entry in manifest.files],
            "provenance": manifest.provenance.as_dict(),
        }
        if hashlib.sha256(_canonical_json(identity)).hexdigest() != artifact_id:
            raise ArtifactError("artifact provenance hash mismatch")
        return len(actual_files)

    @staticmethod
    def _scan(source: Path) -> tuple[ArtifactFile, ...]:
        entries = []
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ArtifactError("artifact directories must not contain symlinks")
            if not path.is_file():
                continue
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            entries.append(
                ArtifactFile(
                    path=path.relative_to(source).as_posix(),
                    size_bytes=path.stat().st_size,
                    sha256=digest.hexdigest(),
                )
            )
        return tuple(entries)
