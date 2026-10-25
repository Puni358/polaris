"""
Full 711-origin acquisition orchestration for the Candidate F successor 18Z fetcher.

Reuses the existing planner (for the origin inventory), fetcher (for identity/caching/
validation), and batch_runner (for bounded, resumable, rate-limited execution) --
no parallel fetch implementation. This script only: (1) loads the real local origin
inventory, (2) imports and re-validates the 5 already-fetched, already-validated pilot
run 3 records into a NEW, dedicated cache directory (never touching run1/run2/run3's
own directories), and (3) drives batch_runner.run_batch over the remaining origins with
explicit, bounded operational limits plus a consecutive-failure circuit breaker.

Resumable by construction: rerunning this script against the same --cache-dir causes
every already-OK origin to be served from cache (zero budget consumed), so an
interrupted run can simply be restarted with the same arguments.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import planner as P
from .fetcher import FetcherConfig, FetchStatus, ProvenanceRecord, cache_key, write_cache_atomic, fetch_one_origin
from .batch_runner import run_batch

HORIZON_RANGE = tuple(range(1, 25))
EXPECTED_PRESSURE_HPA = 700.0


def _parse_origin(ts: str) -> datetime:
    ts = ts.replace("Z", "+00:00") if ts.endswith("Z") else ts
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def full_inventory() -> list:
    origins_str = sorted(set(P._load_local_origins(P.MATRIX_2024)) | set(P._load_local_origins(P.MATRIX_2025)))
    return [_parse_origin(ts) for ts in origins_str]


def _structurally_valid(payload: dict, origin: datetime) -> bool:
    """Re-validates a stored payload's STRUCTURE (not a fresh network fetch): correct
    run offset, exactly horizons 1-24 present once each, correct pressure level, every
    valid_time matching origin+horizon. This is what 'verification before reuse' means
    here -- we do not re-fetch, but we do not blindly trust the file either."""
    try:
        frt = datetime.fromisoformat(payload["forecast_reference_time_utc"])
        if frt != origin.astimezone(timezone.utc).replace(tzinfo=timezone.utc) - __import__("datetime").timedelta(hours=6):
            return False
        if abs(payload.get("pressure_hpa", -1) - EXPECTED_PRESSURE_HPA) > 1e-6:
            return False
        horizons = [h["horizon_hour"] for h in payload["per_horizon"]]
        if sorted(horizons) != list(HORIZON_RANGE):
            return False
        for h in payload["per_horizon"]:
            expected_valid = origin + __import__("datetime").timedelta(hours=h["horizon_hour"])
            if datetime.fromisoformat(h["valid_time_utc"]) != expected_valid:
                return False
            if not (h["lwp_mass_fraction"] == h["lwp_mass_fraction"]):  # NaN check without numpy
                return False
            if not (h["iwp_mass_fraction"] == h["iwp_mass_fraction"]):
                return False
        return True
    except (KeyError, ValueError, TypeError):
        return False


def import_pilot_records(pilot_dir: Path, target_cfg: FetcherConfig, log) -> int:
    """Copies ONLY structurally-revalidated, retrieval_status==OK records from a prior
    pilot cache directory into the target cache directory, keyed by the SAME identity
    scheme (cache_key depends only on run/product/variable/grid identity, not on which
    directory holds the file, so a matching origin's record is a valid reuse). Returns
    the count actually imported. Never touches the source pilot directory."""
    imported = 0
    if not pilot_dir.exists():
        return 0
    for f in sorted(pilot_dir.glob("*.json")):
        try:
            record = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if record.get("retrieval_status") != FetchStatus.OK:
            continue
        try:
            origin = _parse_origin(record["forecast_start"])
        except (KeyError, ValueError):
            continue
        expected_key = cache_key(origin)
        if record.get("cache_key") != expected_key:
            log(f"  SKIP import {f.name}: cache_key mismatch for recomputed identity (stale/incompatible)")
            continue
        if not _structurally_valid(record.get("payload") or {}, origin):
            log(f"  SKIP import {f.name}: failed structural re-validation")
            continue
        write_cache_atomic(target_cfg, origin, {
            "forecast_start": record["forecast_start"], "retrieval_status": FetchStatus.OK,
            "payload": record["payload"], "content_sha256": record.get("content_sha256"),
            "detail": f"imported and re-validated from {pilot_dir.name}",
        })
        imported += 1
        log(f"  imported {record['forecast_start']} from {pilot_dir.name} (re-validated OK)")
    return imported


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--import-pilot-dir", action="append", default=[])
    ap.add_argument("--max-requests", type=int, default=1500)
    ap.add_argument("--max-runtime-s", type=float, default=7200.0)
    ap.add_argument("--rate-limit-per-s", type=float, default=0.5)
    ap.add_argument("--timeout-s", type=float, default=15.0)
    ap.add_argument("--max-retries", type=int, default=3)
    ap.add_argument("--max-consecutive-failures", type=int, default=15)
    ap.add_argument("--log-file", type=str, default=None)
    args = ap.parse_args()

    log_fp = open(args.log_file, "a", encoding="utf-8") if args.log_file else None

    def log(msg: str) -> None:
        line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
        print(line, flush=True)
        if log_fp:
            log_fp.write(line + "\n")
            log_fp.flush()

    cache_dir = Path(args.cache_dir)
    cfg = FetcherConfig(
        dry_run=False, network_opt_in=True,
        max_origins=10_000,  # the real bound here is the inventory length, not this cap
        max_requests=args.max_requests, concurrency=1,
        timeout_s=args.timeout_s, max_retries=args.max_retries,
        rate_limit_per_s=args.rate_limit_per_s, max_runtime_s=args.max_runtime_s,
        cache_dir=cache_dir,
    )

    origins = full_inventory()
    log(f"Planned unique origins: {len(origins)}")

    for pilot_dir in args.import_pilot_dir:
        n = import_pilot_records(Path(pilot_dir), cfg, log)
        log(f"Imported {n} re-validated OK record(s) from {pilot_dir}")

    def _logged_fetch(o, c, budget=None):
        rec = fetch_one_origin(o, c, budget=budget)
        log(f"origin={rec.forecast_start} status={rec.retrieval_status} cache={rec.cache_status}")
        return rec

    t0 = time.monotonic()
    result = run_batch(origins, cfg, fetch_fn=_logged_fetch, max_consecutive_failures=args.max_consecutive_failures)
    elapsed = time.monotonic() - t0

    ok_count = sum(1 for r in result.attempted if r.retrieval_status == FetchStatus.OK)
    manifest = {
        "planned_unique_origins": len(origins),
        "attempted": len(result.attempted),
        "ok": ok_count,
        "failed": len(result.attempted) - ok_count,
        "skipped_over_bounds": len(result.skipped_over_bounds),
        "total_outbound_attempts_used": result.total_outbound_attempts_used,
        "max_outbound_attempts": result.max_outbound_attempts,
        "stopped_early_reason": result.stopped_early_reason,
        "pilot_complete_all_711": ok_count == len(origins),
        "elapsed_s": round(elapsed, 2),
        "by_status": {},
    }
    for r in result.attempted:
        manifest["by_status"][r.retrieval_status] = manifest["by_status"].get(r.retrieval_status, 0) + 1

    manifest_path = cache_dir / "ACQUISITION_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    log(f"Manifest written to {manifest_path}")
    log(json.dumps(manifest, indent=2, sort_keys=True))

    if log_fp:
        log_fp.close()
    return 0 if manifest["pilot_complete_all_711"] else 1


if __name__ == "__main__":
    sys.exit(main())
