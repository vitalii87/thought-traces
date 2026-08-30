from __future__ import annotations

import argparse
from pathlib import Path

from .controller import ArenaController


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
    return parser


def main() -> int:
    args = _parser().parse_args()
    controller = ArenaController(args.state_dir)

    if args.command == "init-lineage":
        event_hash = controller.initialize_lineage(args.lineage_id, origin=args.origin)
        print(f"created {args.lineage_id} event_hash={event_hash}")
        return 0

    if args.command == "verify-events":
        count = controller.verify_lineage(args.lineage_id)
        print(f"verified {args.lineage_id} events={count}")
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
