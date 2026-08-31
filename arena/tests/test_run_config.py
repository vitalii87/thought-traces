import hashlib
import tempfile
import unittest
from pathlib import Path

from iah_arena.run_config import RunConfigLoader


class RunConfigLoaderTests(unittest.TestCase):
    def test_loads_protocol_hash_and_lineage_maps(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = root / "protocol.md"
            protocol.write_text("frozen protocol\n", encoding="utf-8")
            config = root / "run.toml"
            config.write_text(
                self.config_text(),
                encoding="utf-8",
            )

            loaded = RunConfigLoader().load(config)

            self.assertEqual(
                loaded.manifest.protocol_sha256,
                hashlib.sha256(protocol.read_bytes()).hexdigest(),
            )
            self.assertEqual(loaded.manifest.lineage_ids, ("gpt", "gemini", "claude"))
            self.assertEqual(loaded.manifest.random_seeds["claude"], 3)

    def test_unknown_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "protocol.md").write_text("protocol", encoding="utf-8")
            config = root / "run.toml"
            config.write_text(self.config_text() + "\nunknown = true\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                RunConfigLoader().load(config)

    @staticmethod
    def config_text() -> str:
        return """schema_version = 1

[run]
experiment_id = "pilot-001"
protocol_version = "v1"
protocol_path = "protocol.md"
task_id = "placeholder-task"
task_version = "v1"
evaluator_version = "v1"
curriculum_digest = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
environment_digest = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
arena_commit = "abc1234"
created_utc = "2026-01-01T00:00:00+00:00"

[[lineages]]
lineage_id = "gpt"
optimizer_id = "openai/model"
random_seed = 1

[[lineages]]
lineage_id = "gemini"
optimizer_id = "google/model"
random_seed = 2

[[lineages]]
lineage_id = "claude"
optimizer_id = "anthropic/model"
random_seed = 3
"""


if __name__ == "__main__":
    unittest.main()
