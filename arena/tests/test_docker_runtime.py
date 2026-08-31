import subprocess
import tempfile
import unittest
from pathlib import Path

from iah_arena.docker_runtime import DockerRuntime, ProcessResult
from iah_arena.runtime import Mount, RuntimeLimits, RuntimeRequest, RuntimeRole


IMAGE = "example.invalid/iah-polyglot@sha256:" + "a" * 64


class DockerRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name) / "workspace"
        self.workspace.mkdir()
        self.limits = RuntimeLimits(
            cpus=1.5,
            memory_mb=512,
            pids=64,
            timeout_seconds=7,
            tmpfs_mb=32,
            max_output_bytes=10,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_requires_digest_pinned_image(self) -> None:
        with self.assertRaises(ValueError):
            DockerRuntime("ubuntu:latest")
        self.assertEqual(DockerRuntime("sha256:" + "b" * 64).image[:7], "sha256:")

    def test_judge_command_contains_isolation_and_read_only_mounts(self) -> None:
        fixtures = Path(self.temporary.name) / "fixtures"
        fixtures.mkdir()
        runtime = DockerRuntime(IMAGE)
        request = RuntimeRequest(
            ("/opt/iah/judge", "--case", "1"),
            RuntimeRole.JUDGE,
            True,
            extra_mounts=(Mount(fixtures, "/fixtures", True),),
        )

        command = runtime.build_command(
            self.workspace,
            request,
            self.limits,
            container_name="iah-test",
        )

        self.assertIn("none", command)
        self.assertIn("ALL", command)
        self.assertIn("no-new-privileges", command)
        self.assertIn("1000:1000", command)
        self.assertIn("/run/iah:rw,exec,nosuid,nodev,size=32m", command)
        mounts = [
            command[index + 1]
            for index, value in enumerate(command[:-1])
            if value == "--mount"
        ]
        self.assertEqual(len(mounts), 2)
        self.assertTrue(all(value.endswith(",readonly") for value in mounts))
        image_index = command.index(IMAGE)
        self.assertEqual(command[image_index:], [IMAGE, "/opt/iah/judge", "--case", "1"])

    def test_run_bounds_combined_output(self) -> None:
        def process(argv, timeout):
            return ProcessResult(0, "abcdefghij", "klmnopqrst")

        runtime = DockerRuntime(IMAGE, process_runner=process)
        result = runtime.run(
            self.workspace,
            RuntimeRequest(("true",), RuntimeRole.WORKSHOP, False),
            self.limits,
        )

        self.assertTrue(result.succeeded)
        self.assertTrue(result.output_truncated)
        self.assertLessEqual(len(result.stdout.encode()) + len(result.stderr.encode()), 10)

    def test_timeout_forces_container_removal(self) -> None:
        calls = []

        def process(argv, timeout):
            calls.append(list(argv))
            if len(calls) == 1:
                raise subprocess.TimeoutExpired(argv, timeout, output=b"partial")
            return ProcessResult(0, "", "")

        runtime = DockerRuntime(IMAGE, process_runner=process)
        result = runtime.run(
            self.workspace,
            RuntimeRequest(("slow",), RuntimeRole.WORKSHOP, False),
            self.limits,
        )

        self.assertTrue(result.timed_out)
        self.assertEqual(calls[1][1:3], ["rm", "--force"])


if __name__ == "__main__":
    unittest.main()
