"""
POLARIS -- Deterministic Realized Actuals Loader for Multi-Origin Campaign
===========================================================================
Authoritative Dataset: ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv
Governed SHA-256: 762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023

Provides a pure, deterministic loader to construct `actuals_by_origin_and_step`
for SingleShotPlanSlicingSimulatorAdapter and RecedingHorizonPlanSlicingSimulatorAdapter.

Temporal alignment contract:
  For an origin t0 (e.g. 2024-06-07T00:00:00Z), the 24 simulator steps represent
  transitions over consecutive 1-hour intervals [t0 + k, t0 + k + 1] for k in 0..23.
  Each transition step k consumes the realized environmental observation at t0 + k + 1
  (e.g. step 0 consumes 2024-06-07T01:00:00Z, step 23 consumes 2024-06-08T00:00:00Z).
  The simulator's DigitalTwinSimulator.step() advances state to next_step['timestamp'].

Strictly fails closed on:
  - Missing fixture file or SHA-256 digest mismatch
  - Empty origins sequence or empty fixture rows
  - Missing required columns ('timestamp', 'solar_SW_IN_W_m2', 'synthetic_load_W', 'wind_power_generic_W')
  - Non-UTC timestamps or malformed ISO 8601 strings
  - Non-monotonic timestamps, duplicates, or irregular intervals
  - Unaligned origins (non-hourly boundaries: minute != 0, second != 0)
  - Missing numerical values, NaN, inf, or invalid negative observations
  - Missing origins or incomplete step ranges
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence

CANONICAL_FIXTURE_RELATIVE_PATH = "ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv"
CANONICAL_FIXTURE_SHA256 = "762297aae21c0cb9d79fede0c9b2b266cf0d57e544ee147ffd4aff133e884023"
REQUIRED_FIXTURE_COLUMNS = (
    "timestamp",
    "solar_SW_IN_W_m2",
    "synthetic_load_W",
    "wind_power_generic_W",
)


class AuthoritativeActualsDict(dict):
    """
    Provenance-tagged dictionary carrying validated actuals from the authoritative fixture.
    """
    _is_authoritative_actuals: bool = True



def compute_file_sha256(file_path: Path | str) -> str:
    """Computes SHA-256 digest of a local file."""
    h = hashlib.sha256()
    path = Path(file_path)
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def load_authoritative_actuals_by_origin(
    fixture_path: Path | str = CANONICAL_FIXTURE_RELATIVE_PATH,
    origins: Sequence[str] = (),
    steps_per_origin: int = 24,
    verify_sha256: bool = True,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Loads deterministic actual environmental observations for each origin from the
    canonical H1.0 hybrid fixture.

    Parameters:
      fixture_path: Path to fixture.csv (defaults to ems/fixtures/POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv)
      origins: Sequence of origin identifiers (e.g. ['2024-06-01', ..., '2024-06-07'])
      steps_per_origin: Number of consecutive hourly transition steps per origin (default 24)
      verify_sha256: Fail-closed verification against CANONICAL_FIXTURE_SHA256

    Returns:
      Dict[str, List[Dict[str, Any]]] where each inner dict contains:
        - 'actual_SW_IN': float (solar irradiance W/m^2 >= 0.0)
        - 'actual_demand': float (electrical demand W >= 0.0)
        - 'actual_wind_generation': float (wind generation W >= 0.0)
        - 'timestamp': str (ISO 8601 UTC timestamp)
    """
    if not origins:
        raise ValueError("Fail-closed: origins sequence cannot be empty.")

    path = Path(fixture_path)
    if not path.is_file():
        raise FileNotFoundError(f"Fail-closed: Authoritative fixture not found at {path}")

    if verify_sha256:
        actual_hash = compute_file_sha256(path)
        if actual_hash != CANONICAL_FIXTURE_SHA256:
            raise ValueError(
                f"Fail-closed: Authoritative fixture SHA-256 mismatch!\n"
                f"  Expected: {CANONICAL_FIXTURE_SHA256}\n"
                f"  Actual:   {actual_hash}"
            )

    rows_by_ts: Dict[str, Dict[str, Any]] = {}
    prev_dt: datetime.datetime | None = None
    prev_ts: str | None = None

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("Fail-closed: Empty or unreadable CSV header in fixture.")

        missing_cols = [col for col in REQUIRED_FIXTURE_COLUMNS if col not in reader.fieldnames]
        if missing_cols:
            raise ValueError(
                f"Fail-closed: Missing required column(s) in fixture: {missing_cols}"
            )

        for line_num, row in enumerate(reader, start=2):
            ts = row.get("timestamp")
            if not ts:
                raise ValueError(f"Fail-closed: Missing timestamp at fixture line {line_num}")

            try:
                curr_dt = datetime.datetime.fromisoformat(ts)
            except ValueError as exc:
                raise ValueError(
                    f"Fail-closed: Malformed ISO 8601 timestamp '{ts}' at line {line_num}: {exc}"
                ) from exc

            # Enforce UTC timezone convention
            if curr_dt.tzinfo is None or curr_dt.utcoffset() != datetime.timedelta(0):
                raise ValueError(
                    f"Fail-closed: Non-UTC timestamp '{ts}' at fixture line {line_num} "
                    f"(tzinfo={curr_dt.tzinfo}, utcoffset={curr_dt.utcoffset()})"
                )

            # Strict monotonicity and regularity checks
            if prev_dt is not None:
                if curr_dt <= prev_dt:
                    raise ValueError(
                        f"Fail-closed: Non-monotonic or duplicate timestamp '{ts}' at line {line_num} "
                        f"(previous: '{prev_ts}')"
                    )
                delta = curr_dt - prev_dt
                if delta != datetime.timedelta(hours=1):
                    raise ValueError(
                        f"Fail-closed: Irregular time interval {delta} between '{prev_ts}' and '{ts}' "
                        f"at line {line_num} (expected 1 hour)"
                    )

            prev_dt = curr_dt
            prev_ts = ts

            try:
                sw_in = float(row["solar_SW_IN_W_m2"])
                demand = float(row["synthetic_load_W"])
                wind = float(row["wind_power_generic_W"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Fail-closed: Malformed numerical value in fixture row {ts} (line {line_num}): {exc}"
                ) from exc

            if math.isnan(sw_in) or math.isnan(demand) or math.isnan(wind):
                raise ValueError(f"Fail-closed: NaN observation in fixture row: {ts}")
            if math.isinf(sw_in) or math.isinf(demand) or math.isinf(wind):
                raise ValueError(f"Fail-closed: Infinite observation in fixture row: {ts}")

            # Physical non-negativity checks
            if sw_in < 0.0:
                raise ValueError(f"Fail-closed: Negative solar irradiance ({sw_in}) in row {ts}")
            if demand < 0.0:
                raise ValueError(f"Fail-closed: Negative electrical demand ({demand}) in row {ts}")
            if wind < 0.0:
                raise ValueError(f"Fail-closed: Negative wind generation ({wind}) in row {ts}")

            # Normalize timestamp to canonical 'Z' format
            norm_ts = curr_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

            rows_by_ts[norm_ts] = {
                "actual_SW_IN": sw_in,
                "actual_demand": demand,
                "actual_wind_generation": wind,
                "timestamp": norm_ts,
            }

    if not rows_by_ts:
        raise ValueError("Fail-closed: Authoritative fixture contains zero valid observation rows.")

    result: Dict[str, List[Dict[str, Any]]] = AuthoritativeActualsDict()
    for origin in origins:
        if not isinstance(origin, str) or not origin.strip():
            raise ValueError(f"Fail-closed: Invalid origin identifier '{origin!r}'")

        if "T" not in origin:
            origin_ts = f"{origin}T00:00:00Z"
        else:
            origin_ts = origin

        try:
            dt0 = datetime.datetime.fromisoformat(origin_ts)
        except ValueError as exc:
            raise ValueError(f"Fail-closed: Invalid ISO 8601 origin timestamp '{origin}': {exc}") from exc

        if dt0.tzinfo is None or dt0.utcoffset() != datetime.timedelta(0):
            raise ValueError(
                f"Fail-closed: Origin timestamp '{origin}' must be in UTC timezone "
                f"(tzinfo={dt0.tzinfo}, utcoffset={dt0.utcoffset()})"
            )

        # Exact hour-boundary alignment: must be minute=0, second=0, microsecond=0
        if dt0.minute != 0 or dt0.second != 0 or dt0.microsecond != 0:
            raise ValueError(
                f"Fail-closed: Origin timestamp '{origin}' is not aligned to an hourly boundary "
                f"(minute={dt0.minute}, second={dt0.second}, microsecond={dt0.microsecond})."
            )

        origin_steps: List[Dict[str, Any]] = []
        for h in range(steps_per_origin):
            # Transition step h advances state [t0 + h, t0 + h + 1], consuming observation at t0 + h + 1
            step_dt = dt0 + datetime.timedelta(hours=h + 1)
            step_ts = step_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            if step_ts not in rows_by_ts:
                raise KeyError(
                    f"Fail-closed: Missing actual observation for origin '{origin}' transition step {h} "
                    f"({step_ts}) in authoritative fixture."
                )
            origin_steps.append(rows_by_ts[step_ts])

        result[origin] = origin_steps

    return result
