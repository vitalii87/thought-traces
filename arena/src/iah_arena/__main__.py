from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory

from .budgets import BudgetLedger, BudgetLimits
from .controller import ArenaController
from .docker_runtime import DockerRuntime
from .providers import DecisionContext, ProviderTurn, ScriptedProvider, ToolCall
from .runtime import RuntimeLimits, RuntimeRequest, RuntimeRole
from .sessions import SessionLimits


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="iah-arena")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init-lineage", help="create an empty lineage event chain")
    init.add_argument("--state-dir", type=Path, required=True)
    init.add_argument("--lineage-id", required=True)
    init.add_argument("--origin", required=True)

    verify = subparsers.add_parser("verify-events", help="verify a lineage event hash chain")
    verify.add_argument("--state-dir", type=Path, required=True)
    verify.add_argument("--lineage-id", required=True)

    dry_run = subparsers.add_parser(
        "dry-run",
        help="exercise one complete upgrade attempt with a deterministic fake provider",
    )
    dry_run.add_argument("--state-dir", type=Path, required=True)
    dry_run.add_argument("--lineage-id", default="dry-run-001")

    docker_check = subparsers.add_parser(
        "docker-check",
        help="run the toolchain report inside a pinned polyglot image",
    )
    docker_check.add_argument("--image", required=True)
    docker_check.add_argument("--docker-binary", default="docker")
    docker_check.add_argument("--container-user", default="1000:1000")
    return parser


def _dry_run(controller: ArenaController, lineage_id: str) -> int:
    with TemporaryDirectory(prefix="iah-seed-") as temporary:
        seed = Path(temporary)
        (seed / "solver.txt").write_text("primitive\n", encoding="utf-8")
        controller.initialize_lineage(lineage_id, origin="scripted-dry-run")
        controller.initialize_workspace(lineage_id, seed)

    provider = ScriptedProvider(
        (
            ProviderTurn(tool_calls=(ToolCall("1", "read_file", {"path": "solver.txt"}),)),
            ProviderTurn(
                tool_calls=(
                    ToolCall(
                        "2",
                        "write_file",
                        {"path": "solver.txt", "content": "improved\n"},
                    ),
                )
            ),
            ProviderTurn(tool_calls=(ToolCall("3", "run_public_tests", {}),)),
            ProviderTurn(
                tool_calls=(
                    ToolCall("4", "submit_candidate", {"summary": "dry-run upgrade"}),
                )
            ),
        )
    )
    limits = BudgetLimits(8, 10_000, 10_000, 100_000, 60)
    budget = BudgetLedger(limits)
    context = DecisionContext(
        lineage_id=lineage_id,
        epoch=1,
        generation=0,
        attempt=1,
        objective={"goal": "replace the primitive marker"},
        metrics={"public_passed": False},
        budget_remaining=asdict(budget.remaining()),
        workspace_summary={"known_files": ["solver.txt"]},
    )

    def public_tests(workspace: Path) -> dict[str, object]:
        passed = (workspace / "solver.txt").read_text(encoding="utf-8") == "improved\n"
        return {"passed": passed, "checks": 1}

    def evaluator(workspace: Path) -> dict[str, object]:
        accepted = (workspace / "solver.txt").read_text(encoding="utf-8") == "improved\n"
        return {"accepted": accepted, "fitness": 1.0 if accepted else 0.0}

    result = controller.run_attempt(
        lineage_id=lineage_id,
        epoch=1,
        attempt=1,
        provider=provider,
        context=context,
        budget=budget,
        public_test_runner=public_tests,
        evaluator=evaluator,
        limits=SessionLimits(max_provider_turns=6, max_tool_calls=10),
    )
    event_count = controller.verify_lineage(lineage_id)
    print(
        f"dry-run accepted={result.accepted} generation={result.generation} "
        f"provider_turns={result.session.provider_turns} events={event_count}"
    )
    return 0 if result.accepted else 1


def _docker_check(image: str, docker_binary: str, container_user: str) -> int:
    runtime = DockerRuntime(
        image,
        docker_binary=docker_binary,
        container_user=container_user,
    )
    limits = RuntimeLimits(
        cpus=1,
        memory_mb=512,
        pids=32,
        timeout_seconds=30,
        tmpfs_mb=64,
        max_output_bytes=64_000,
    )
    request = RuntimeRequest(
        ("iah-toolchain-report",),
        RuntimeRole.JUDGE,
        workspace_read_only=True,
    )
    with TemporaryDirectory(prefix="iah-docker-check-") as temporary:
        result = runtime.run(Path(temporary), request, limits)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip())
    print(
        f"docker-check succeeded={result.succeeded} timed_out={result.timed_out} "
        f"duration_ms={result.duration_ms}"
    )
    return 0 if result.succeeded else 1


def main() -> int:
    args = _parser().parse_args()
    if args.command == "docker-check":
        return _docker_check(args.image, args.docker_binary, args.container_user)

    controller = ArenaController(args.state_dir)

    if args.command == "init-lineage":
        event_hash = controller.initialize_lineage(args.lineage_id, origin=args.origin)
        print(f"created {args.lineage_id} event_hash={event_hash}")
        return 0

    if args.command == "verify-events":
        count = controller.verify_lineage(args.lineage_id)
        print(f"verified {args.lineage_id} events={count}")
        return 0

    if args.command == "dry-run":
        return _dry_run(controller, args.lineage_id)

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
