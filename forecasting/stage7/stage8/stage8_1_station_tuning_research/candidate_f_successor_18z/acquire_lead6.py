"""
v2-authorized acquisition: source lead 6 only, for the 711 planned origins.

Implements CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v2.md's base-horizon-1 fix:
lead = 5 + h, so for h=1, lead=6, valid_time = run_init + 6h = origin (since
run_init = origin - 6h). This is a SINGLE lead index, not the [0:1:30] range v1 used --
deliberately narrow, per this task's "no broad reacquisition" instruction.

Reuses fetcher.py's URL/run-identity helpers, validation philosophy (fail closed, no
silent substitution), atomic cache writes, and batch_runner's bounded/rate-limited/
circuit-breaker execution -- no parallel fetch implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, "/home/punith-bs/01polaris (Copy)")
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_f_successor_18z import fetcher as F
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_f_successor_18z.acquire_full import full_inventory, _parse_origin
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_f_successor_18z.batch_runner import run_batch, BatchResult
from forecasting.stage7.stage8.stage8_1_station_tuning_research.candidate_f_successor_18z.fetcher import FetcherConfig, FetchStatus, ProvenanceRecord

LEAD6 = 6  # v2 Sec.2: lead = 5+h, h=1 -> lead=6


def build_lead6_url(run_init: datetime) -> str:
    base = F.build_url(run_init)
    parts = [
        f"{F.LWP_VAR}[{LEAD6}:1:{LEAD6}][{F.P700_IDX}:1:{F.P700_IDX}][{F.NUOLJA_Y}:1:{F.NUOLJA_Y}][{F.NUOLJA_X}:1:{F.NUOLJA_X}]",
        f"{F.IWP_VAR}[{LEAD6}:1:{LEAD6}][{F.P700_IDX}:1:{F.P700_IDX}][{F.NUOLJA_Y}:1:{F.NUOLJA_Y}][{F.NUOLJA_X}:1:{F.NUOLJA_X}]",
        f"pressure[{F.P700_IDX}:1:{F.P700_IDX}]",
        "forecast_reference_time",
        f"time[{LEAD6}:1:{LEAD6}]",
    ]
    query = ",".join(parts)
    encoded = urllib.parse.quote(query, safe="=:,")
    return f"{base}?{encoded}"


def validate_lead6(ascii_text: str, forecast_start: datetime, run_init: datetime):
    if not ascii_text or not ascii_text.strip():
        return FetchStatus.FAILED_PARSE, None, "empty response"
    frt = F.parse_ascii_series(ascii_text, "forecast_reference_time", 1)
    if frt is None:
        return FetchStatus.FAILED_MISSING_VAR, None, "forecast_reference_time not found"
    frt_dt = datetime.fromtimestamp(float(frt[0]), tz=timezone.utc)
    if frt_dt != run_init:
        return FetchStatus.FAILED_RUN_MISMATCH, None, f"frt {frt_dt.isoformat()} != required {run_init.isoformat()}"
    time_arr = F.parse_ascii_series(ascii_text, "time", 1)
    if time_arr is None:
        return FetchStatus.FAILED_DIM_MISMATCH, None, "time value not found"
    expected_valid = run_init + timedelta(hours=LEAD6)
    actual_valid = datetime.fromtimestamp(float(time_arr[0]), tz=timezone.utc)
    if actual_valid != expected_valid:
        return FetchStatus.FAILED_DIM_MISMATCH, None, f"time {actual_valid.isoformat()} != expected {expected_valid.isoformat()}"
    pressure = F.parse_ascii_series(ascii_text, "pressure", 1)
    if pressure is None:
        return FetchStatus.FAILED_MISSING_VAR, None, "pressure not found"
    lwp = F.parse_ascii_series(ascii_text, F.LWP_VAR, 1)
    iwp = F.parse_ascii_series(ascii_text, F.IWP_VAR, 1)
    if lwp is None:
        return FetchStatus.FAILED_MISSING_VAR, None, f"{F.LWP_VAR} not found"
    if iwp is None:
        return FetchStatus.FAILED_MISSING_VAR, None, f"{F.IWP_VAR} not found"
    lwp_v, iwp_v = float(lwp[0]), float(iwp[0])
    if not (lwp_v == lwp_v) or not (iwp_v == iwp_v):  # NaN check
        return FetchStatus.FAILED_NONFINITE, None, "non-finite LWP/IWP"
    # base horizon_hour=1 target per v2 Sec.1: valid at origin+(1-1)=origin
    expected_origin_valid = forecast_start
    if actual_valid != expected_origin_valid:
        return FetchStatus.FAILED_DIM_MISMATCH, None, (
            f"v2 target mismatch: lead-6 valid_time {actual_valid.isoformat()} != origin {expected_origin_valid.isoformat()}"
        )
    payload = {
        "forecast_reference_time_utc": frt_dt.isoformat(),
        "pressure_hpa": float(pressure[0]),
        "per_horizon": [{
            "horizon_hour": 1, "lead_hour": LEAD6, "valid_time_utc": actual_valid.isoformat(),
            "lwp_mass_fraction": lwp_v, "iwp_mass_fraction": iwp_v,
        }],
    }
    return FetchStatus.OK, payload, "validated (v2 lead-6)"


def fetch_lead6_one(forecast_start: datetime, config: FetcherConfig, *, budget=None) -> ProvenanceRecord:
    run_init = F.run_init_time_for_origin(forecast_start)
    url = build_lead6_url(run_init)

    cached = F.read_cache(config, forecast_start)
    if cached is not None and cached.get("retrieval_status") == FetchStatus.OK:
        payload = cached.get("payload") or {}
        h0 = (payload.get("per_horizon") or [{}])[0]
        return ProvenanceRecord(
            forecast_start=forecast_start.isoformat(), run_init_time_utc=run_init.isoformat(),
            product=F.PRODUCT, url=url, variables=[F.LWP_VAR, F.IWP_VAR],
            pressure_hpa=payload.get("pressure_hpa"), valid_times_utc=[h0.get("valid_time_utc", "")],
            lead_hours=[h0.get("lead_hour", LEAD6)], retrieval_status=FetchStatus.OK,
            cache_status=FetchStatus.CACHE_HIT, units={"lwp": "kg/kg", "iwp": "kg/kg"},
            validation_outcome="validated (from cache)", content_sha256=cached.get("content_sha256"),
        )

    bgt = budget if budget is not None else F.AttemptBudget(config.max_retries)
    if bgt.remaining <= 0:
        return ProvenanceRecord(
            forecast_start=forecast_start.isoformat(), run_init_time_utc=run_init.isoformat(),
            product=F.PRODUCT, url=url, variables=[F.LWP_VAR, F.IWP_VAR], pressure_hpa=None,
            valid_times_utc=[], lead_hours=[], retrieval_status=FetchStatus.FAILED_BUDGET_EXHAUSTED,
            cache_status=FetchStatus.PENDING, units={}, validation_outcome="budget exhausted",
        )

    ascii_text, http_status = F._fetch_with_retry(url, config, F._default_urlopen, bgt)
    if ascii_text is None:
        status = FetchStatus.FAILED_BUDGET_EXHAUSTED if http_status == "BUDGET_EXHAUSTED" else f"{FetchStatus.FAILED_HTTP}_{http_status}"
        return ProvenanceRecord(
            forecast_start=forecast_start.isoformat(), run_init_time_utc=run_init.isoformat(),
            product=F.PRODUCT, url=url, variables=[F.LWP_VAR, F.IWP_VAR], pressure_hpa=None,
            valid_times_utc=[], lead_hours=[], retrieval_status=status, cache_status=FetchStatus.PENDING,
            units={}, validation_outcome="fetch failed", detail=f"status={http_status}",
        )

    content_hash = hashlib.sha256(ascii_text.encode("utf-8")).hexdigest()
    status, payload, detail = validate_lead6(ascii_text, forecast_start, run_init)
    F.write_cache_atomic(config, forecast_start, {
        "forecast_start": forecast_start.isoformat(), "retrieval_status": status,
        "payload": payload, "content_sha256": content_hash, "detail": detail,
    })
    h0 = (payload or {}).get("per_horizon", [{}])[0] if payload else {}
    return ProvenanceRecord(
        forecast_start=forecast_start.isoformat(), run_init_time_utc=run_init.isoformat(),
        product=F.PRODUCT, url=url, variables=[F.LWP_VAR, F.IWP_VAR],
        pressure_hpa=(payload or {}).get("pressure_hpa"),
        valid_times_utc=[h0.get("valid_time_utc", "")] if h0 else [],
        lead_hours=[h0.get("lead_hour", LEAD6)] if h0 else [],
        retrieval_status=status, cache_status=FetchStatus.OK if status == FetchStatus.OK else FetchStatus.PENDING,
        units={"lwp": "kg/kg", "iwp": "kg/kg"} if status == FetchStatus.OK else {},
        validation_outcome=detail, content_sha256=content_hash, detail=detail,
    )


def log(msg, fp=None):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line, flush=True)
    if fp:
        fp.write(line + "\n")
        fp.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--max-requests", type=int, default=1500)
    ap.add_argument("--max-runtime-s", type=float, default=7200.0)
    ap.add_argument("--rate-limit-per-s", type=float, default=0.5)
    ap.add_argument("--timeout-s", type=float, default=15.0)
    ap.add_argument("--max-retries", type=int, default=3)
    ap.add_argument("--max-consecutive-failures", type=int, default=15)
    ap.add_argument("--log-file", type=str, default=None)
    args = ap.parse_args()

    fp = open(args.log_file, "a", encoding="utf-8") if args.log_file else None
    cache_dir = Path(args.cache_dir)
    cfg = FetcherConfig(
        dry_run=False, network_opt_in=True, max_origins=10_000,
        max_requests=args.max_requests, concurrency=1, timeout_s=args.timeout_s,
        max_retries=args.max_retries, rate_limit_per_s=args.rate_limit_per_s,
        max_runtime_s=args.max_runtime_s, cache_dir=cache_dir,
    )
    origins = full_inventory()
    log(f"Planned unique origins: {len(origins)} (lead-6 only acquisition, v2)", fp)

    def _logged(o, c, budget=None):
        rec = fetch_lead6_one(o, c, budget=budget)
        log(f"origin={rec.forecast_start} status={rec.retrieval_status} cache={rec.cache_status}", fp)
        return rec

    result = run_batch(origins, cfg, fetch_fn=_logged, max_consecutive_failures=args.max_consecutive_failures)
    ok_count = sum(1 for r in result.attempted if r.retrieval_status == FetchStatus.OK)
    manifest = {
        "contract_version": "v2", "lead": LEAD6,
        "planned_unique_origins": len(origins), "attempted": len(result.attempted),
        "ok": ok_count, "failed": len(result.attempted) - ok_count,
        "skipped_over_bounds": len(result.skipped_over_bounds),
        "total_outbound_attempts_used": result.total_outbound_attempts_used,
        "max_outbound_attempts": result.max_outbound_attempts,
        "stopped_early_reason": result.stopped_early_reason,
        "all_711_complete": ok_count == len(origins),
        "elapsed_s": None, "by_status": {},
    }
    for r in result.attempted:
        manifest["by_status"][r.retrieval_status] = manifest["by_status"].get(r.retrieval_status, 0) + 1
    (cache_dir / "LEAD6_ACQUISITION_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    log("Manifest: " + json.dumps(manifest, indent=2, sort_keys=True), fp)
    if fp:
        fp.close()
    return 0 if manifest["all_711_complete"] else 1


if __name__ == "__main__":
    sys.exit(main())
