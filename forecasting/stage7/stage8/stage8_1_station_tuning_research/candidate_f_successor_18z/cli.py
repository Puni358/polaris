"""
Command-line entry points for the Candidate F successor 18Z fetcher.

Subcommands:
  plan                 -- network-free. Reads local matrices, reports counts/estimates.
  show-fetch-command    -- network-free. Prints (does not run) the command that a future,
                           separately authorized network pilot would use.
  fetch                 -- the ONLY subcommand that can ever make a network request, and
                           only if the caller passes BOTH --network-opt-in and
                           --i-understand-this-makes-real-network-requests.

Running this file with no arguments, or with `plan`, performs no network I/O.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import planner as P
from .fetcher import FetcherConfig
from .batch_runner import run_batch
from .planner import _load_local_origins, _parse_origin, MATRIX_2024, MATRIX_2025


def _cmd_plan(args: argparse.Namespace) -> int:
    result = P.plan()
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0


def _cmd_show_fetch_command(args: argparse.Namespace) -> int:
    """Prints, for review only, the command a future authorized pilot run would use.
    Does not execute it."""
    cmd = (
        "python -m stage7.stage8.stage8_1_station_tuning_research."
        "candidate_f_successor_18z.cli fetch "
        "--max-origins 5 --max-requests 5 --concurrency 1 --rate-limit-per-s 0.5 "
        "--timeout-s 15 --max-retries 3 --max-runtime-s 120 "
        "--network-opt-in --i-understand-this-makes-real-network-requests "
        "--origin-start 2024-01-20 --origin-count 5"
    )
    print("PROPOSED FUTURE COMMAND (not executed by this CLI call):")
    print(cmd)
    print("\nThis is a small, explicitly bounded pilot (5 origins, 5 requests max) "
          "intended for review and separate authorization before any larger run.")
    return 0


def select_pilot_origins(origin_start: str, origin_count: int) -> list:
    """Selects `origin_count` DISTINCT forecast origins from the actual local origin
    inventory (the existing, already-public CORRECTED feature matrices), at or after
    `origin_start`. Never assumes N consecutive calendar days equal N available
    origins -- an origin is only selected if it genuinely appears in the local
    inventory. Raises ValueError if fewer than origin_count such origins exist."""
    inventory = sorted(set(_load_local_origins(MATRIX_2024)) | set(_load_local_origins(MATRIX_2025)))
    start_dt = _parse_origin(origin_start if "T" in origin_start or len(origin_start) > 10
                              else origin_start + "T00:00:00+00:00")
    candidates = [ts for ts in inventory if _parse_origin(ts) >= start_dt]
    if len(candidates) < origin_count:
        raise ValueError(
            f"only {len(candidates)} local inventory origins at/after {origin_start}, "
            f"need {origin_count} distinct origins"
        )
    selected = candidates[:origin_count]
    if len(set(selected)) != len(selected):
        raise ValueError("internal error: selected origin list contains duplicates")
    return [_parse_origin(ts) for ts in selected]


def _cmd_fetch(args: argparse.Namespace) -> int:
    if not (args.network_opt_in and args.i_understand_this_makes_real_network_requests):
        print("Refusing: both --network-opt-in and "
              "--i-understand-this-makes-real-network-requests are required.", file=sys.stderr)
        return 2
    cfg = FetcherConfig(
        dry_run=False, network_opt_in=True,
        max_requests=args.max_requests, max_origins=args.max_origins,
        concurrency=args.concurrency, timeout_s=args.timeout_s,
        max_retries=args.max_retries, rate_limit_per_s=args.rate_limit_per_s,
        max_runtime_s=args.max_runtime_s,
        cache_dir=Path(args.cache_dir) if args.cache_dir else FetcherConfig().cache_dir,
    )
    origins = select_pilot_origins(args.origin_start, args.origin_count)
    print("Selected distinct pilot origins (from local inventory, no network used to select them):")
    for o in origins:
        print(f"  {o.isoformat()}")
    result = run_batch(origins, cfg)
    print(json.dumps(result.summary(), indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="candidate_f_successor_18z")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("plan", help="network-free: report local acquisition plan").set_defaults(func=_cmd_plan)
    sub.add_parser("show-fetch-command", help="network-free: print the proposed future pilot command").set_defaults(
        func=_cmd_show_fetch_command
    )

    fetch_p = sub.add_parser("fetch", help="REQUIRES explicit opt-in; makes real network requests")
    fetch_p.add_argument("--max-origins", type=int, default=5)
    fetch_p.add_argument("--max-requests", type=int, default=5)
    fetch_p.add_argument("--concurrency", type=int, default=1)
    fetch_p.add_argument("--timeout-s", type=float, default=12.0)
    fetch_p.add_argument("--max-retries", type=int, default=3)
    fetch_p.add_argument("--rate-limit-per-s", type=float, default=1.0)
    fetch_p.add_argument("--max-runtime-s", type=float, default=60.0)
    fetch_p.add_argument("--origin-start", type=str, default="2024-01-20")
    fetch_p.add_argument("--origin-count", type=int, default=1)
    fetch_p.add_argument("--network-opt-in", action="store_true")
    fetch_p.add_argument("--i-understand-this-makes-real-network-requests", action="store_true")
    fetch_p.add_argument("--cache-dir", type=str, default=None,
                          help="Dedicated output/cache directory for this run. Defaults to the "
                               "package's own cache/ dir if omitted.")
    fetch_p.set_defaults(func=_cmd_fetch)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
