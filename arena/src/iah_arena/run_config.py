from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .experiment import RunManifest


def _exact_keys(
    value: Mapping[str, Any],
    *,
    required: set[str],
    optional: set[str] = frozenset(),
    scope: str,
) -> None:
    actual = set(value)
    missing = required - actual
    unknown = actual - required - optional
    if missing or unknown:
        raise ValueError(
            f"invalid {scope} keys; missing={sorted(missing)}, unknown={sorted(unknown)}"
        )


@dataclass(frozen=True, slots=True)
class LoadedRunConfig:
    source_path: Path
    configuration_sha256: str
    protocol_path: Path
    manifest: RunManifest


class RunConfigLoader:
    """Strict TOML loader: unknown fields are errors, not silently ignored typos."""

    def load(self, path: Path) -> LoadedRunConfig:
        path = Path(path).resolve()
        encoded = path.read_bytes()
        value = tomllib.loads(encoded.decode("utf-8"))
        _exact_keys(
            value,
            required={"schema_version", "run", "lineages"},
            scope="top-level run config",
        )
        if isinstance(value["schema_version"], bool) or value["schema_version"] != 1:
            raise ValueError("unsupported run config schema_version")
        run = value["run"]
        if not isinstance(run, dict):
            raise ValueError("run config section must be a table")
        _exact_keys(
            run,
            required={
                "experiment_id",
                "protocol_version",
                "protocol_path",
                "task_id",
                "task_version",
                "evaluator_version",
                "curriculum_digest",
                "environment_digest",
                "arena_commit",
            },
            optional={"created_utc"},
            scope="run table",
        )
        for key in (
            "experiment_id",
            "protocol_version",
            "protocol_path",
            "task_id",
            "task_version",
            "evaluator_version",
            "curriculum_digest",
            "environment_digest",
            "arena_commit",
        ):
            if not isinstance(run[key], str):
                raise ValueError(f"run.{key} must be a string")
        if "created_utc" in run and not isinstance(run["created_utc"], str):
            raise ValueError("run.created_utc must be a string")
        lineages = value["lineages"]
        if not isinstance(lineages, list) or not lineages:
            raise ValueError("lineages must be a non-empty array of tables")
        lineage_ids = []
        optimizer_ids = {}
        random_seeds = {}
        for index, lineage in enumerate(lineages):
            if not isinstance(lineage, dict):
                raise ValueError(f"lineages[{index}] must be a table")
            _exact_keys(
                lineage,
                required={"lineage_id", "optimizer_id", "random_seed"},
                scope=f"lineages[{index}]",
            )
            if not isinstance(lineage["lineage_id"], str) or not isinstance(
                lineage["optimizer_id"], str
            ):
                raise ValueError(f"lineages[{index}] IDs must be strings")
            if isinstance(lineage["random_seed"], bool) or not isinstance(
                lineage["random_seed"], int
            ):
                raise ValueError(f"lineages[{index}].random_seed must be an integer")
            lineage_id = lineage["lineage_id"]
            lineage_ids.append(lineage_id)
            optimizer_ids[lineage_id] = lineage["optimizer_id"]
            random_seeds[lineage_id] = lineage["random_seed"]

        protocol_path = Path(str(run["protocol_path"]))
        if not protocol_path.is_absolute():
            protocol_path = (path.parent / protocol_path).resolve()
        if not protocol_path.is_file():
            raise FileNotFoundError(f"protocol file not found: {protocol_path}")
        protocol_sha256 = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
        configuration_sha256 = hashlib.sha256(encoded).hexdigest()
        manifest_args = {
            "experiment_id": str(run["experiment_id"]),
            "protocol_version": str(run["protocol_version"]),
            "protocol_sha256": protocol_sha256,
            "task_id": str(run["task_id"]),
            "task_version": str(run["task_version"]),
            "evaluator_version": str(run["evaluator_version"]),
            "curriculum_digest": str(run["curriculum_digest"]),
            "environment_digest": str(run["environment_digest"]),
            "arena_commit": str(run["arena_commit"]),
            "configuration_sha256": configuration_sha256,
            "lineage_ids": tuple(lineage_ids),
            "optimizer_ids": optimizer_ids,
            "random_seeds": random_seeds,
        }
        if "created_utc" in run:
            manifest_args["created_utc"] = str(run["created_utc"])
        return LoadedRunConfig(
            source_path=path,
            configuration_sha256=configuration_sha256,
            protocol_path=protocol_path,
            manifest=RunManifest(**manifest_args),
        )
