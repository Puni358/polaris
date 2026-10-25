"""
Isolated fetcher for Candidate F successor's 18Z LWP/IWP features.

Implements CANDIDATE_F_SUCCESSOR_18Z_FEATURE_CONTRACT_v1.md exactly:
  - Product: meps_det_pl (deterministic, pressure-level), MET Norway THREDDS archive
    meps25epsarchive, prior calendar day's 18Z run relative to the POLARIS origin.
  - Variables: mass_fraction_of_cloud_condensed_water_in_air_pl (LWP),
    mass_fraction_of_cloud_ice_in_air_pl (IWP).
  - Admissibility: forecast_reference_time of the selected run MUST equal origin - 6h
    exactly; lead hour for horizon h is 6 + h; h ranges 1..24.
  - Zero is a valid physical value (clear air); missing/failed is a distinct status,
    never silently filled with 0.0.
  - No fallback to a different run on failure. The origin fails closed.

This module performs NO network I/O at import time, and performs a live HTTP request
ONLY when `fetch_one_origin(..., config)` is called with a FetcherConfig whose
`network_opt_in` is True AND `dry_run` is False. Every code path in this file was
exercised in this task via mocked responses only (see tests/); no real network request
was made while writing or testing this module.
"""
from __future__ import annotations

import hashlib
import json
import math
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------- constants
PRODUCT = "meps_det_pl"
ARCHIVE_BASE = "https://thredds.met.no/thredds/dodsC/meps25epsarchive"
RUN_HOUR_UTC = 18                      # prior-day 18Z run, per the frozen contract
RUN_OFFSET_HOURS = 6                   # origin - 6h == run init time
HORIZONS = tuple(range(1, 25))         # h in 1..24
LWP_VAR = "mass_fraction_of_cloud_condensed_water_in_air_pl"
IWP_VAR = "mass_fraction_of_cloud_ice_in_air_pl"
EXPECTED_PRESSURE_LEVELS = 13
EXPECTED_TIME_STEPS_MIN = 31           # must cover lead hour 6+24=30 -> index 30, need >=31
NUOLJA_Y = 760
NUOLJA_X = 486
P700_IDX = 8                           # ~700 hPa level index, matches the existing pipeline's convention
VALID_SURFACE_PRESSURE_PA = (70000.0, 110000.0)
USER_AGENT = "POLARIS-CandidateF-Successor-18Z/1.0 (research, isolated fetcher)"


class FetchStatus:
    PENDING = "PENDING"
    CACHE_HIT = "CACHE_HIT"
    OK = "OK"
    FAILED_HTTP = "FAILED_HTTP"
    FAILED_PARSE = "FAILED_PARSE"
    FAILED_MISSING_VAR = "FAILED_MISSING_VAR"
    FAILED_DIM_MISMATCH = "FAILED_DIM_MISMATCH"
    FAILED_RUN_MISMATCH = "FAILED_RUN_MISMATCH"
    FAILED_DUPLICATE_TIME = "FAILED_DUPLICATE_TIME"
    FAILED_NONFINITE = "FAILED_NONFINITE"
    FAILED_HORIZON_OUT_OF_RANGE = "FAILED_HORIZON_OUT_OF_RANGE"
    FAILED_INVALID_SURFACE_PRESSURE = "FAILED_INVALID_SURFACE_PRESSURE"
    FAILED_BOUNDS_EXCEEDED = "FAILED_BOUNDS_EXCEEDED"
    FAILED_NETWORK_NOT_AUTHORIZED = "FAILED_NETWORK_NOT_AUTHORIZED"
    FAILED_BUDGET_EXHAUSTED = "FAILED_BUDGET_EXHAUSTED"


class FetcherError(RuntimeError):
    pass


class AttemptBudget:
    """A hard, shared, thread-safe cap on TOTAL outbound HTTP attempts (including every
    retry of every origin) across an entire batch. This is the mechanism that makes
    `max_requests` an actual cap on outbound attempts rather than merely a cap on how
    many origins are *started*. Once exhausted, no further attempt is made by anyone
    holding a reference to this object, for the rest of that batch -- the budget is
    never replenished mid-run."""

    def __init__(self, max_attempts: int):
        if max_attempts < 1:
            raise FetcherError("max_attempts must be >= 1")
        self.max_attempts = max_attempts
        self._used = 0
        self._lock = threading.Lock()

    def try_consume(self) -> bool:
        with self._lock:
            if self._used >= self.max_attempts:
                return False
            self._used += 1
            return True

    @property
    def used(self) -> int:
        with self._lock:
            return self._used

    @property
    def remaining(self) -> int:
        with self._lock:
            return self.max_attempts - self._used


# ---------------------------------------------------------------------------- config
@dataclass
class FetcherConfig:
    """Bounded execution controls. Defaults are maximally conservative: no network call
    can happen unless both dry_run=False and network_opt_in=True are set explicitly by
    the caller. This task never sets either."""
    dry_run: bool = True
    network_opt_in: bool = False
    max_requests: int = 10
    max_origins: int = 5
    concurrency: int = 1
    timeout_s: float = 12.0
    max_retries: int = 3
    backoff_base_s: float = 1.5
    rate_limit_per_s: float = 1.0
    max_runtime_s: float = 60.0
    cache_dir: Path = field(default_factory=lambda: Path(__file__).parent / "cache")

    def __post_init__(self):
        if self.concurrency < 1:
            raise FetcherError("concurrency must be >= 1")
        if self.max_requests < 1 or self.max_origins < 1:
            raise FetcherError("max_requests and max_origins must be >= 1")
        self.cache_dir = Path(self.cache_dir)


# ---------------------------------------------------------------------------- provenance
@dataclass
class ProvenanceRecord:
    forecast_start: str
    run_init_time_utc: str
    product: str
    url: str
    variables: List[str]
    pressure_hpa: Optional[float]
    valid_times_utc: List[str]
    lead_hours: List[int]
    retrieval_status: str
    cache_status: str
    units: Dict[str, str]
    validation_outcome: str
    content_sha256: Optional[str] = None
    detail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------- URL/time helpers
def run_init_time_for_origin(forecast_start: datetime) -> datetime:
    """The admissible 18Z run's init time: origin - 6h, per the frozen contract."""
    if forecast_start.tzinfo is None:
        forecast_start = forecast_start.replace(tzinfo=timezone.utc)
    run_init = forecast_start - timedelta(hours=RUN_OFFSET_HOURS)
    if run_init.hour != RUN_HOUR_UTC:
        raise FetcherError(
            f"origin {forecast_start.isoformat()} does not map to an {RUN_HOUR_UTC}Z run "
            f"6h prior (got run hour {run_init.hour}); refusing to construct a URL for a "
            f"non-admissible run"
        )
    return run_init


def build_url(run_init: datetime) -> str:
    y, m, d = run_init.strftime("%Y"), run_init.strftime("%m"), run_init.strftime("%d")
    tag = run_init.strftime("%Y%m%dT%HZ")
    return f"{ARCHIVE_BASE}/{y}/{m}/{d}/{PRODUCT}_{tag}.ncml.ascii"


MAX_REQUIRED_TIME_INDEX = RUN_OFFSET_HOURS + max(HORIZONS)  # = 30: the last index ever read


def build_query(variables: Tuple[str, ...] = (LWP_VAR, IWP_VAR)) -> str:
    """Pressure-level variables indexed at the single ~700 hPa level and the Nuolja grid
    point, over ONLY the time indices actually needed (0..30, covering lead hours
    0..30, i.e. every horizon 1..24 at offset 6).

    BUGFIX (found during the live 711-origin acquisition, 2026-10-12): an earlier
    revision requested the full [0:1:66] time range on the (confirmed-for-only-two-
    sample-dates) assumption that every 18Z run's time dimension has exactly 67 steps.
    A real run (2024-02-01T18Z) was confirmed, via the server's own error message
    during this acquisition, to have only 40 steps ("Bad Projection Request: stop >=
    size: 66:39"), causing every origin from that date onward to fail with HTTP 400 --
    not a server outage or throttling, a query-construction bug. Since the fetcher
    never reads past index 30 (lead hour 6+24), requesting only [0:1:30] is both
    sufficient and robust to any run whose time dimension is as short as 31 steps."""
    parts = [f"{v}[0:1:{MAX_REQUIRED_TIME_INDEX}][{P700_IDX}:1:{P700_IDX}][{NUOLJA_Y}:1:{NUOLJA_Y}][{NUOLJA_X}:1:{NUOLJA_X}]" for v in variables]
    parts.append(f"pressure[{P700_IDX}:1:{P700_IDX}]")
    parts.append("forecast_reference_time")
    parts.append(f"time[0:1:{MAX_REQUIRED_TIME_INDEX}]")
    return ",".join(parts)


def full_request_url(forecast_start: datetime) -> Tuple[str, datetime]:
    """BUGFIX (found during the live pilot, see DESIGN notes / audit trail): the DODS
    constraint syntax uses `[`, `]`, `:`, `,` -- unescaped `[`/`]` in a query string are
    not valid per RFC 3986 and were rejected by the THREDDS server with HTTP 400 in a
    live test. The existing project's own convention
    (acquire_extract_meps_2020_2023.py: `urllib.parse.quote(query, safe='=:')`)
    percent-encodes everything except '=' and ':'; replicated here with ',' also kept
    literal (confirmed, by a live, read-only diagnostic request during this
    investigation, to be accepted by the server in exactly this form)."""
    run_init = run_init_time_for_origin(forecast_start)
    base = build_url(run_init)
    query = build_query()
    encoded_query = urllib.parse.quote(query, safe="=:,")
    url = f"{base}?{encoded_query}"
    return url, run_init


def cache_key(forecast_start: datetime) -> str:
    """Cache identity includes every parameter that affects response identity: the
    product, the exact run tag, the variable set, the pressure index, and the grid
    point -- not merely the origin date, so a changed query never silently reuses a
    stale, incompatible cache entry."""
    run_init = run_init_time_for_origin(forecast_start)
    identity = "|".join([
        PRODUCT, run_init.strftime("%Y%m%dT%HZ"), LWP_VAR, IWP_VAR,
        str(P700_IDX), str(NUOLJA_Y), str(NUOLJA_X),
    ])
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]


# ---------------------------------------------------------------------------- ASCII parsing
def parse_ascii_series(ascii_text: str, var_name: str, expected_count: int) -> Optional[np.ndarray]:
    """Adapted from the existing project convention in acquire_extract_meps_2020_2023.py
    (candidate_L_research), reused here rather than reinvented, per the task's
    instruction to reuse existing parsing conventions.

    BUGFIX (found during the live re-pilot, 2026-10-12): a true DODS *scalar* variable
    (e.g. `forecast_reference_time`) is rendered inline as `"var_name, value"` on a
    single line -- NOT as a `"var_name[...]"` / `"var_name.var_name"` header line
    followed by separate value lines, which is how *array/grid* variables (pressure,
    time, the Grid data arrays) are rendered. This was confirmed directly against a
    real response during this investigation:
        "forecast_reference_time, 1.7056872E9"
    The header-based scan below (unchanged, and still correct for array/grid
    variables) never matched that line, so `forecast_reference_time` parsed as None,
    which made every real response fail validation with FAILED_MISSING_VAR even
    though the fetch itself succeeded (HTTP 200). This inline-scalar case is checked
    first, as a narrow, additive fix, before falling back to the original scan."""
    if not ascii_text or var_name not in ascii_text:
        return None
    if expected_count == 1:
        for raw_line in ascii_text.splitlines():
            line_str = raw_line.strip()
            if line_str.startswith(var_name + ",") or line_str.startswith(var_name + " ,"):
                remainder = line_str[len(var_name):].lstrip()
                if remainder.startswith(","):
                    remainder = remainder[1:].strip()
                try:
                    return np.array([float(remainder)], dtype=float)
                except ValueError:
                    pass  # fall through to the header-based scan below
    try:
        lines = ascii_text.splitlines()
        values: List[float] = []
        in_var = False
        for line in lines:
            line_str = line.strip()
            if line_str.startswith(var_name + "[") or line_str.startswith(var_name + "."):
                in_var = True
                continue
            if in_var:
                if line_str.startswith("Dataset") or (line_str and line_str[0].isalpha() and "[" in line_str):
                    in_var = False
                    continue
                for p in line_str.split(","):
                    p_clean = p.strip()
                    if not p_clean:
                        continue
                    if "[" in p_clean:
                        p_clean = p_clean.split("]")[-1].strip()
                    try:
                        values.append(float(p_clean))
                    except ValueError:
                        pass
        if len(values) >= expected_count:
            return np.array(values[:expected_count], dtype=float)
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------- validation
def validate_response(
    *, ascii_text: str, forecast_start: datetime, run_init: datetime,
) -> Tuple[str, Optional[Dict[str, Any]], str]:
    """Returns (status, parsed_payload_or_None, detail). Never raises; every failure
    mode is a returned status string, per the contract's 'fail closed, explicit
    failures' requirement."""
    if not ascii_text or not ascii_text.strip():
        return FetchStatus.FAILED_PARSE, None, "empty response body"

    frt = parse_ascii_series(ascii_text, "forecast_reference_time", 1)
    if frt is None:
        return FetchStatus.FAILED_MISSING_VAR, None, "forecast_reference_time not found"
    frt_dt = datetime.fromtimestamp(float(frt[0]), tz=timezone.utc)
    if frt_dt != run_init:
        return (
            FetchStatus.FAILED_RUN_MISMATCH, None,
            f"forecast_reference_time {frt_dt.isoformat()} != required run init {run_init.isoformat()}",
        )

    time_arr = parse_ascii_series(ascii_text, "time", EXPECTED_TIME_STEPS_MIN)
    if time_arr is None:
        return FetchStatus.FAILED_DIM_MISMATCH, None, f"time array shorter than required {EXPECTED_TIME_STEPS_MIN} steps"
    if len(set(time_arr.tolist())) != len(time_arr):
        return FetchStatus.FAILED_DUPLICATE_TIME, None, "duplicate timestamps in time array"
    if not np.all(np.diff(time_arr) > 0):
        return FetchStatus.FAILED_DIM_MISMATCH, None, "time array is not strictly increasing"

    pressure = parse_ascii_series(ascii_text, "pressure", 1)
    if pressure is None:
        return FetchStatus.FAILED_MISSING_VAR, None, "pressure variable not found"

    lwp_raw = parse_ascii_series(ascii_text, LWP_VAR, EXPECTED_TIME_STEPS_MIN)
    iwp_raw = parse_ascii_series(ascii_text, IWP_VAR, EXPECTED_TIME_STEPS_MIN)
    if lwp_raw is None:
        return FetchStatus.FAILED_MISSING_VAR, None, f"{LWP_VAR} not found or too short"
    if iwp_raw is None:
        return FetchStatus.FAILED_MISSING_VAR, None, f"{IWP_VAR} not found or too short"

    for h in HORIZONS:
        lead = RUN_OFFSET_HOURS + h
        if lead >= len(time_arr) or lead >= len(lwp_raw) or lead >= len(iwp_raw):
            return FetchStatus.FAILED_HORIZON_OUT_OF_RANGE, None, f"horizon {h} (lead {lead}) exceeds returned array length"

    values_to_check = np.concatenate([lwp_raw[: max(HORIZONS) + RUN_OFFSET_HOURS + 1],
                                       iwp_raw[: max(HORIZONS) + RUN_OFFSET_HOURS + 1]])
    if not np.all(np.isfinite(values_to_check)):
        return FetchStatus.FAILED_NONFINITE, None, "non-finite value in LWP/IWP series within the required horizon range"

    per_horizon = []
    for h in HORIZONS:
        lead = RUN_OFFSET_HOURS + h
        valid_time = run_init + timedelta(hours=lead)
        expected_valid_time = forecast_start + timedelta(hours=h)
        if valid_time != expected_valid_time:
            return (
                FetchStatus.FAILED_DIM_MISMATCH, None,
                f"horizon {h}: computed valid_time {valid_time.isoformat()} != expected {expected_valid_time.isoformat()}",
            )
        per_horizon.append({
            "horizon_hour": h,
            "lead_hour": lead,
            "valid_time_utc": valid_time.isoformat(),
            "lwp_mass_fraction": float(lwp_raw[lead]),
            "iwp_mass_fraction": float(iwp_raw[lead]),
        })

    payload = {
        "forecast_reference_time_utc": frt_dt.isoformat(),
        "pressure_hpa": float(pressure[0]),
        "per_horizon": per_horizon,
    }
    return FetchStatus.OK, payload, "validated"


# ---------------------------------------------------------------------------- cache
def _cache_path(config: FetcherConfig, key: str) -> Path:
    config.cache_dir.mkdir(parents=True, exist_ok=True)
    return config.cache_dir / f"{key}.json"


def read_cache(config: FetcherConfig, forecast_start: datetime) -> Optional[Dict[str, Any]]:
    key = cache_key(forecast_start)
    path = _cache_path(config, key)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as fp:
            record = json.load(fp)
    except (json.JSONDecodeError, OSError):
        return None
    if record.get("cache_key") != key:
        return None
    return record


def write_cache_atomic(config: FetcherConfig, forecast_start: datetime, record: Dict[str, Any]) -> None:
    """Atomic write: write to a temp file in the same directory, then os.replace. Never
    leaves a partially-written cache file visible under the final name."""
    key = cache_key(forecast_start)
    path = _cache_path(config, key)
    record = dict(record)
    record["cache_key"] = key
    tmp_path = path.with_suffix(".json.tmp")
    with open(tmp_path, "w", encoding="utf-8") as fp:
        json.dump(record, fp, indent=2, sort_keys=True)
    tmp_path.replace(path)  # atomic on POSIX


# ---------------------------------------------------------------------------- single-origin fetch
def fetch_one_origin(
    forecast_start: datetime, config: FetcherConfig,
    *, _urlopen=None, budget: Optional[AttemptBudget] = None,
) -> ProvenanceRecord:
    """Fetches (or reuses a cached, identity-matching result for) one origin's LWP/IWP
    18Z features. `_urlopen` is an injection point for tests only; production code
    never passes it and falls back to urllib.request.urlopen.

    `budget`, if given, is a *shared* AttemptBudget enforced across an entire batch
    (see batch_runner.run_batch) -- every retry of every origin consumes from the same
    budget, so `max_requests` is a true cap on total outbound attempts, not merely on
    how many origins are started. If omitted (single-origin direct calls, e.g. in
    tests), a fresh budget sized to config.max_retries is created so a lone call keeps
    its existing retry behavior unchanged."""
    url, run_init = full_request_url(forecast_start)

    cached = read_cache(config, forecast_start)
    if cached is not None and cached.get("retrieval_status") == FetchStatus.OK:
        rec = ProvenanceRecord(
            forecast_start=forecast_start.isoformat(), run_init_time_utc=run_init.isoformat(),
            product=PRODUCT, url=url, variables=[LWP_VAR, IWP_VAR],
            pressure_hpa=cached.get("payload", {}).get("pressure_hpa"),
            valid_times_utc=[h["valid_time_utc"] for h in cached.get("payload", {}).get("per_horizon", [])],
            lead_hours=[h["lead_hour"] for h in cached.get("payload", {}).get("per_horizon", [])],
            retrieval_status=FetchStatus.OK, cache_status=FetchStatus.CACHE_HIT,
            units={"lwp": "kg/kg (raw mass fraction)", "iwp": "kg/kg (raw mass fraction)"},
            validation_outcome="validated (from cache)",
            content_sha256=cached.get("content_sha256"),
        )
        return rec

    if not config.network_opt_in or config.dry_run:
        return ProvenanceRecord(
            forecast_start=forecast_start.isoformat(), run_init_time_utc=run_init.isoformat(),
            product=PRODUCT, url=url, variables=[LWP_VAR, IWP_VAR], pressure_hpa=None,
            valid_times_utc=[], lead_hours=[], retrieval_status=FetchStatus.FAILED_NETWORK_NOT_AUTHORIZED,
            cache_status=FetchStatus.PENDING, units={}, validation_outcome="not attempted (dry-run or no network opt-in)",
            detail="network_opt_in and dry_run=False are both required to make a request; neither path executed a request",
        )

    local_budget = budget if budget is not None else AttemptBudget(config.max_retries)
    if local_budget.remaining <= 0:
        return ProvenanceRecord(
            forecast_start=forecast_start.isoformat(), run_init_time_utc=run_init.isoformat(),
            product=PRODUCT, url=url, variables=[LWP_VAR, IWP_VAR], pressure_hpa=None,
            valid_times_utc=[], lead_hours=[], retrieval_status=FetchStatus.FAILED_BUDGET_EXHAUSTED,
            cache_status=FetchStatus.PENDING, units={}, validation_outcome="not attempted (global attempt budget already exhausted)",
            detail=f"global outbound-attempt budget ({local_budget.max_attempts}) exhausted before this origin was reached",
        )

    opener = _urlopen or _default_urlopen
    ascii_text, http_status = _fetch_with_retry(url, config, opener, local_budget)
    if ascii_text is None:
        status = FetchStatus.FAILED_BUDGET_EXHAUSTED if http_status == "BUDGET_EXHAUSTED" else f"{FetchStatus.FAILED_HTTP}_{http_status}"
        return ProvenanceRecord(
            forecast_start=forecast_start.isoformat(), run_init_time_utc=run_init.isoformat(),
            product=PRODUCT, url=url, variables=[LWP_VAR, IWP_VAR], pressure_hpa=None,
            valid_times_utc=[], lead_hours=[], retrieval_status=status,
            cache_status=FetchStatus.PENDING, units={}, validation_outcome="not validated (fetch failed)",
            detail=f"HTTP/network failure or budget exhaustion, status={http_status}",
        )

    content_hash = hashlib.sha256(ascii_text.encode("utf-8")).hexdigest()
    status, payload, detail = validate_response(ascii_text=ascii_text, forecast_start=forecast_start, run_init=run_init)

    write_cache_atomic(config, forecast_start, {
        "forecast_start": forecast_start.isoformat(), "retrieval_status": status,
        "payload": payload, "content_sha256": content_hash, "detail": detail,
    })

    valid_times = [h["valid_time_utc"] for h in payload["per_horizon"]] if payload else []
    lead_hours = [h["lead_hour"] for h in payload["per_horizon"]] if payload else []
    return ProvenanceRecord(
        forecast_start=forecast_start.isoformat(), run_init_time_utc=run_init.isoformat(),
        product=PRODUCT, url=url, variables=[LWP_VAR, IWP_VAR],
        pressure_hpa=(payload["pressure_hpa"] if payload else None),
        valid_times_utc=valid_times, lead_hours=lead_hours,
        retrieval_status=status, cache_status=FetchStatus.OK if status == FetchStatus.OK else FetchStatus.PENDING,
        units={"lwp": "kg/kg (raw mass fraction)", "iwp": "kg/kg (raw mass fraction)"} if status == FetchStatus.OK else {},
        validation_outcome=detail, content_sha256=content_hash, detail=detail,
    )


def _default_urlopen(req, timeout):  # pragma: no cover - never exercised by tests, no network in this task
    return urllib.request.urlopen(req, timeout=timeout)


def _fetch_with_retry(url: str, config: FetcherConfig, opener, budget: AttemptBudget) -> Tuple[Optional[str], Any]:
    """Every single outbound attempt -- including every retry -- must first consume
    one unit from `budget`. If the budget is exhausted (by this origin's own earlier
    retries, or by other origins in the same batch), this function makes NO further
    HTTP call and returns immediately with status 'BUDGET_EXHAUSTED'. This is what
    makes max_requests a true global cap on outbound attempts: a retry can never push
    total attempts past the configured budget, and exhausting the budget mid-origin
    stops that origin's own retries too, not just later origins."""
    last_status: Any = None
    for attempt in range(config.max_retries):
        if not budget.try_consume():
            return None, "BUDGET_EXHAUSTED"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with opener(req, timeout=config.timeout_s) as resp:
                status = getattr(resp, "status", 200)
                if status == 200:
                    return resp.read().decode("utf-8", errors="ignore"), 200
                last_status = status
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, 404
            last_status = e.code
        except Exception as e:  # noqa: BLE001
            last_status = str(e)
        if attempt < config.max_retries - 1 and budget.remaining > 0:
            time.sleep(config.backoff_base_s * (attempt + 1))
    return None, last_status
