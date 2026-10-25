"""
Deterministic, network-free acquisition planner for the Candidate F successor's 18Z
LWP/IWP fetcher.

Reads the EXISTING, already-public origin inventory from the already-existing corrected
feature matrices (read-only; this planner never writes to those files) and reports
counts, request/response-size estimates, and a conservative runtime projection. Makes
NO network request, mutates NO cache, creates NO feature matrix, and alters NO
experiment state. Every number below is either a direct local count or a clearly
labeled estimate/assumption -- never presented as a verified historical fact.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .fetcher import FetcherConfig, cache_key, run_init_time_for_origin

REPO_ROOT = Path("/home/punith-bs/01polaris (Copy)")
MATRIX_2024 = REPO_ROOT / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2024_CORRECTED.csv"
MATRIX_2025 = REPO_ROOT / "forecasting/stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv"

# Labeled estimate, not a measurement: observed DODS .ascii response sizes for this
# product/variable/grid-point combination were not directly measured in this task
# (no network request was made). This figure is a rough order-of-magnitude placeholder
# based on the query shape (2 variables x 67 time steps x 1 pressure level x 1 grid
# point, plus small ancillary variables, in verbose ASCII-DODS text format) and MUST be
# treated as an unverified assumption until a real response is inspected under an
# authorized network pilot.
ESTIMATED_RESPONSE_BYTES_PER_REQUEST = 15_000  # ASSUMPTION, not measured


def _load_local_origins(matrix_path: Path) -> List[str]:
    """Reads only the 'forecast_start' column, locally, read-only. Returns the sorted
    unique list of origin timestamps as strings, exactly as stored in the existing
    matrix -- no new file is written by this function."""
    if not matrix_path.exists():
        return []
    import csv

    seen = set()
    with open(matrix_path, "r", encoding="utf-8", newline="") as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            seen.add(row["forecast_start"])
    return sorted(seen)


def _parse_origin(ts: str) -> datetime:
    ts = ts.replace("Z", "+00:00") if ts.endswith("Z") else ts
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@dataclass
class AcquisitionPlan:
    origins_2024: int
    origins_2025: int
    origins_total: int
    requests_per_origin: int
    total_requests: int
    cache_hits: int
    cache_misses: int
    estimated_response_bytes_per_request: int
    estimated_total_bytes: int
    estimated_disk_mb: float
    runtime_seconds_at_conservative_rate: float
    runtime_minutes_at_conservative_rate: float
    conservative_rate_limit_per_s: float
    worst_case_retry_multiplier: int
    worst_case_requests_bound: int
    worst_case_runtime_minutes: float
    origins_outside_verifiable_coverage: List[str]
    output_cache_dir: str
    proposed_manifest: Dict[str, int]

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        return d


def plan(config: Optional[FetcherConfig] = None) -> AcquisitionPlan:
    """The ONLY function this module exposes for producing a plan. Performs local file
    reads and local cache-directory inspection only. No network call anywhere in this
    function or anything it calls."""
    config = config or FetcherConfig()  # defaults: dry_run=True, network_opt_in=False

    origins_2024_str = _load_local_origins(MATRIX_2024)
    origins_2025_str = _load_local_origins(MATRIX_2025)
    origins_total_str = origins_2024_str + origins_2025_str

    requests_per_origin = 1  # one DODS query retrieves both variables, full time axis, one origin's run
    total_requests = len(origins_total_str) * requests_per_origin

    cache_hits = 0
    cache_misses = 0
    outside_coverage: List[str] = []
    for ts in origins_total_str:
        try:
            origin_dt = _parse_origin(ts)
            run_init_time_for_origin(origin_dt)  # raises if not a clean 18Z-6h mapping
        except Exception:
            outside_coverage.append(ts)
            continue
        key = cache_key(origin_dt)
        cache_path = config.cache_dir / f"{key}.json"
        if cache_path.exists():
            cache_hits += 1
        else:
            cache_misses += 1

    est_total_bytes = total_requests * ESTIMATED_RESPONSE_BYTES_PER_REQUEST
    conservative_rate = 1.0  # 1 request/second, deliberately conservative
    runtime_s = cache_misses / conservative_rate if conservative_rate > 0 else float("inf")

    worst_case_retry_multiplier = config.max_retries  # every request could exhaust retries once
    worst_case_requests_bound = cache_misses * worst_case_retry_multiplier
    worst_case_runtime_min = (worst_case_requests_bound / conservative_rate) / 60.0 if conservative_rate > 0 else float("inf")

    return AcquisitionPlan(
        origins_2024=len(origins_2024_str),
        origins_2025=len(origins_2025_str),
        origins_total=len(origins_total_str),
        requests_per_origin=requests_per_origin,
        total_requests=total_requests,
        cache_hits=cache_hits,
        cache_misses=cache_misses,
        estimated_response_bytes_per_request=ESTIMATED_RESPONSE_BYTES_PER_REQUEST,
        estimated_total_bytes=est_total_bytes,
        estimated_disk_mb=round(est_total_bytes / (1024 * 1024), 3),
        runtime_seconds_at_conservative_rate=round(runtime_s, 1),
        runtime_minutes_at_conservative_rate=round(runtime_s / 60.0, 2),
        conservative_rate_limit_per_s=conservative_rate,
        worst_case_retry_multiplier=worst_case_retry_multiplier,
        worst_case_requests_bound=worst_case_requests_bound,
        worst_case_runtime_minutes=round(worst_case_runtime_min, 2),
        origins_outside_verifiable_coverage=outside_coverage,
        output_cache_dir=str(config.cache_dir),
        proposed_manifest={"origins_2024": len(origins_2024_str), "origins_2025": len(origins_2025_str)},
    )


def main() -> None:  # CLI entry point for the plan-only command
    result = plan()
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
