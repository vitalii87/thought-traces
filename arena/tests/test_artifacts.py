import json
import tempfile
import unittest
from pathlib import Path

from iah_arena.artifacts import ArtifactError, ArtifactProvenance, ArtifactStore


def provenance(**metadata) -> ArtifactProvenance:
    return ArtifactProvenance(
        lineage_id="lineage-a",
        epoch=1,
        generation=1,
        attempt=1,
        parent_generation=0,
        task_id="task",
        task_version="v1",
        evaluator_version="judge-v1",
        curriculum_digest="c" * 64,
        environment_digest="sha256:" + "d" * 64,
        arena_commit="abc123",
        random_seed=42,
        optimizer_id="provider/model",
        metadata=metadata,
    )


class ArtifactStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.source = root / "source"
        self.source.mkdir()
        (self.source / "solver.txt").write_text("solution\n", encoding="utf-8")
        self.store = ArtifactStore(root / "artifacts")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_capture_is_content_and_provenance_addressed(self) -> None:
        first = self.store.capture_directory(
            self.source,
            artifact_type="accepted_candidate",
            provenance=provenance(run="one"),
        )
        repeated = self.store.capture_directory(
            self.source,
            artifact_type="accepted_candidate",
            provenance=provenance(run="one"),
        )
        different = self.store.capture_directory(
            self.source,
            artifact_type="accepted_candidate",
            provenance=provenance(run="two"),
        )

        self.assertEqual(first.artifact_id, repeated.artifact_id)
        self.assertNotEqual(first.artifact_id, different.artifact_id)
        self.assertEqual(self.store.verify(first.artifact_id), 1)

    def test_tampering_is_detected(self) -> None:
        manifest = self.store.capture_directory(
            self.source,
            artifact_type="accepted_candidate",
            provenance=provenance(),
        )
        captured = self.store.path_for(manifest.artifact_id) / "files" / "solver.txt"
        captured.write_text("tampered\n", encoding="utf-8")

        with self.assertRaises(ArtifactError):
            self.store.verify(manifest.artifact_id)

    def test_manifest_contains_required_provenance(self) -> None:
        manifest = self.store.capture_directory(
            self.source,
            artifact_type="accepted_candidate",
            provenance=provenance(),
        )
        value = json.loads(
            (self.store.path_for(manifest.artifact_id) / "manifest.json").read_text("utf-8")
        )
        self.assertEqual(value["provenance"]["evaluator_version"], "judge-v1")
        self.assertEqual(value["files"][0]["path"], "solver.txt")


if __name__ == "__main__":
    unittest.main()
