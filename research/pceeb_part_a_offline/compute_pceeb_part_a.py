#!/usr/bin/env python3
"""
PCEEB Part (a) -- Prefix Cumulative Energy Error Bound: offline statistics only.

STANDALONE, OFFLINE, RESEARCH-ONLY. Implements exactly and only UNC-01 Part (a)
as authorized by the project owner (docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.md/.json,
Section 14 item 7) and specified in docs/decision_registers/POLARIS_DEADLINE_MASTER_RESOLUTION.md
Section 4 ("PCEEB Research Specification and Offline Analysis Plan"):

    "for each forecast issue time, compute a running (prefix) sum of
    realized-minus-forecast solar energy error over the lookahead horizon,
    and derive an empirical quantile envelope of that prefix-sum trajectory
    (not a per-hour quantile) from the existing historical forecast-vs-realized
    record already used by FORECAST_UNCERTAINTY_AUDIT.md."

WHAT THIS SCRIPT DOES NOT DO (Part (b), explicitly out of scope, unperformed
and separately gated per the directive):
  - Does NOT compare the resulting bound's closed-loop-replay impact (diesel,
    curtailment, unmet-load) against any baseline.
  - Does NOT invoke, import, or reimplement system/evaluation/replay_harness.py.
  - Does NOT run any dispatch campaign, closed-loop simulation, or
    replay-equivalent comparison.
  - Does NOT touch gap19_highs_native.py, option_d.py, ecd.py, router.py,
    simulator.py, runner.py, or any other PROTECTED_FILES entry.
  - Does NOT fit, train, tune, recalibrate, or promote any model.
  - Does NOT change any production default, reserve policy, solar-credit
    behavior, or control flow.
  - Does NOT access the sealed 2025 blind partition. (The "BLIND_TEST_2023"
    split present in the primary input file is a 2023 in-sample holdout split
    used throughout prior, already-published audits in this repository --
    e.g. forecasting/reports/uncertainty/FORECAST_UNCERTAINTY_AUDIT.md, forecasting/reports/candidates/CANDIDATE_F_HISTORICAL_REPLAY_FORENSIC_AUDIT.md
    -- and is NOT the sealed 2025 blind-evaluation partition referenced
    elsewhere in the register. This script reads only files dated 2020-2024.)

INPUTS (both already used, non-sealed, read-only; paths relative to repo root):
  1. forecasting/candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv
     -- PRIMARY. 26,011 rows, 1,369 daily origins (2020-01-01 .. 2023-09-30),
     19 rows/origin (MEPS 18Z daytime-target-hour extraction; see
     forecasting/reports/uncertainty/FORECAST_UNCERTAINTY_AUDIT.md Section 1.1 and its own Gap Register
     GAP-ARCH-02/GAP-INDX-03). This is the dataset the audit calls "Dataset
     Artifact" #1, used for all of its primary descriptive statistics.
  2. forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv
     -- SECONDARY / corroboration only. 4,152 rows, 173 odd-day 2024 origins,
     24 rows/origin, complete horizon 1..24 (no GAP-INDX-03 indexing issue).
     Used by forecasting/reports/uncertainty/FORECAST_UNCERTAINTY_AUDIT.md as its second authoritative dataset.
     This script applies the IDENTICAL, parameter-free empirical-quantile
     procedure to this file independently -- it is NOT a train/test split, NOT
     a held-out evaluation of anything "fit" on dataset #1, and NOT a model
     validation. It is a second, independent descriptive computation, reported
     side-by-side for corroboration.

METHODOLOGICAL CHOICES MADE AND DOCUMENTED (per the directive's instruction
not to silently invent an unspecified choice -- each is stated explicitly
rather than left implicit):

  (M1) Sign convention: "realized-minus-forecast" per the PCEEB spec's own
       wording = actual - prediction. For the primary dataset this is
       EXACTLY the pre-existing `residual` column (independently verified
       this pass: residual == actual - prediction for every sampled non-zero
       row; `forecast_error` in the same file is the OPPOSITE sign,
       prediction - actual, matching forecasting/reports/uncertainty/FORECAST_UNCERTAINTY_AUDIT.md's own
       "Error = pred - actual" convention). This script uses `residual`
       for the primary dataset and computes `y_true - y_pred` for the
       secondary dataset (which has no precomputed residual column). Readers
       comparing this script's output to forecasting/reports/uncertainty/FORECAST_UNCERTAINTY_AUDIT.md's own
       error figures must flip the sign.

  (M2) Horizon indexing: the primary dataset has a REGISTER-DOCUMENTED,
       VERIFIED data gap (forecasting/reports/uncertainty/FORECAST_UNCERTAINTY_AUDIT.md Section 6,
       GAP-INDX-03): "1,321 origins are indexed h=1..19 (dispatch hours
       0..18), while 48 recovered origins are indexed h=6..24 (MEPS leads)."
       Independently re-confirmed this pass: all 1,369 origins are internally
       contiguous with exactly 19 rows each, but the *raw* `horizon_hour`
       range at which that 19-row block starts/ends varies by origin (min
       horizon_hour seen ranges 1-6 across origins; max ranges 19-24).
       Grouping by raw `horizon_hour` would therefore silently mix two
       different indexing conventions at the same nominal "horizon." This
       script instead indexes the prefix-sum envelope by LOOKAHEAD STEP RANK
       (the 1st, 2nd, ..., 19th row in each origin's own chronologically
       sorted sequence), which is well-defined and gap-free for every origin,
       and reports the per-step distribution of raw `horizon_hour` values
       alongside it for transparency. The secondary (2024) dataset has no such
       gap (complete 1..24 per origin) and step rank equals raw horizon
       exactly there.

  (M3) Units: source columns are hourly-mean solar irradiance (W/m^2, SW_IN).
       Treating each hourly reading as a 1-hour-average power and integrating
       over Delta-t = 1h gives a numerically identical Wh/m^2 energy value
       (W x 1h = Wh); this is a standard, dimensionally exact assumption given
       hourly sampling, not a fitted or invented conversion factor. All output
       values are therefore reported in Wh/m^2 with the same numeric magnitude
       as the source W/m^2 columns.

  (M4) Missing data: none found (0 NaN prediction/actual cells in either
       input file, independently re-verified this pass). No imputation logic
       was therefore needed or written. Had missing cells existed, this
       script's rule is: drop that origin's entire sequence from the
       per-step sample at every step from the first missing value onward
       (a prefix sum cannot be meaningfully continued past a missing term);
       this rule is implemented (see `_load_origin_sequences`) but is inert
       on both of this pass's input files.

  (M5) Quantile estimator: linear interpolation between order statistics
       (the common "Type 7" / NumPy-default definition), implemented here in
       pure Python (no third-party dependency) for exact, auditable
       reproducibility. Levels reported: 0.05, 0.10, 0.25, 0.50, 0.75, 0.90,
       0.95.

This script has NO third-party dependencies (stdlib only: csv, json,
hashlib, statistics, pathlib) so it runs identically regardless of the
repository's Python environment state.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent / "outputs"

PRIMARY_INPUT = REPO_ROOT / "forecasting/candidate_L_research" / "CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv"
SECONDARY_INPUT = REPO_ROOT / "forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv"

QUANTILE_LEVELS = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def empirical_quantile(sorted_values: Sequence[float], q: float) -> float:
    """Linear-interpolation ("Type 7") empirical quantile of an already-sorted sequence."""
    n = len(sorted_values)
    if n == 0:
        raise ValueError("empirical_quantile: empty sample")
    if n == 1:
        return float(sorted_values[0])
    pos = q * (n - 1)
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    frac = pos - lo
    return float(sorted_values[lo] * (1.0 - frac) + sorted_values[hi] * frac)


def _load_origin_sequences(
    path: Path,
    origin_col: str,
    horizon_col: str,
    pred_col: str,
    actual_col: str,
    residual_col: str | None,
) -> Tuple[Dict[str, List[Tuple[int, float]]], int]:
    """
    Returns {origin_id: [(horizon_value, residual_value_actual_minus_pred), ...]}
    sorted ascending by horizon_value per origin, plus a count of rows skipped
    for missing/non-numeric data (M4).
    """
    sequences: Dict[str, List[Tuple[int, float]]] = {}
    skipped = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                horizon = int(row[horizon_col])
                pred = float(row[pred_col])
                actual = float(row[actual_col])
                if residual_col is not None:
                    residual = float(row[residual_col])
                else:
                    residual = actual - pred
                # float() accepts the literal strings "nan"/"NaN" without
                # raising, so an explicit isnan check is required to honor
                # the M4 missing-data rule (skip rather than silently
                # propagate NaN into a cumulative sum).
                if math.isnan(pred) or math.isnan(actual) or math.isnan(residual):
                    raise ValueError("NaN value in required field")
            except (KeyError, ValueError, TypeError):
                skipped += 1
                continue
            sequences.setdefault(row[origin_col], []).append((horizon, residual))
    for origin in sequences:
        sequences[origin].sort(key=lambda t: t[0])
    return sequences, skipped


def _prefix_sums_by_step(
    sequences: Dict[str, List[Tuple[int, float]]]
) -> Tuple[Dict[int, List[float]], Dict[int, List[int]], Dict[str, List[float]]]:
    """
    For each origin, walk its horizon-sorted sequence and compute the running
    (prefix) cumulative sum of residual values. Returns:
      - step_to_prefix_values: {lookahead_step_rank (1-based): [prefix_sum per origin]}
      - step_to_raw_horizons:  {lookahead_step_rank: [raw horizon_hour value per origin]}
        (recorded for transparency per M2; NOT used as the grouping key)
      - per_origin_prefix:     {origin_id: [prefix_sum at step 1, 2, 3, ...]}
    """
    step_to_prefix_values: Dict[int, List[float]] = {}
    step_to_raw_horizons: Dict[int, List[int]] = {}
    per_origin_prefix: Dict[str, List[float]] = {}

    for origin, seq in sequences.items():
        running = 0.0
        prefixes: List[float] = []
        for step_rank, (raw_horizon, residual) in enumerate(seq, start=1):
            running += residual
            prefixes.append(running)
            step_to_prefix_values.setdefault(step_rank, []).append(running)
            step_to_raw_horizons.setdefault(step_rank, []).append(raw_horizon)
        per_origin_prefix[origin] = prefixes

    return step_to_prefix_values, step_to_raw_horizons, per_origin_prefix


def _build_envelope(
    step_to_prefix_values: Dict[int, List[float]],
    step_to_raw_horizons: Dict[int, List[int]],
) -> Dict[str, object]:
    envelope = {}
    for step_rank in sorted(step_to_prefix_values):
        values = sorted(step_to_prefix_values[step_rank])
        n = len(values)
        quantiles = {f"q{int(q*100):02d}": round(empirical_quantile(values, q), 6) for q in QUANTILE_LEVELS}
        raw_horizons = step_to_raw_horizons[step_rank]
        envelope[str(step_rank)] = {
            "lookahead_step_rank": step_rank,
            "n_origins": n,
            "mean_wh_m2": round(statistics.fmean(values), 6),
            "stdev_wh_m2": round(statistics.pstdev(values), 6) if n > 1 else 0.0,
            "min_wh_m2": round(min(values), 6),
            "max_wh_m2": round(max(values), 6),
            "quantiles_wh_m2": quantiles,
            "raw_horizon_hour_at_this_step": {
                "min": min(raw_horizons),
                "max": max(raw_horizons),
                "note": (
                    "Raw horizon_hour value(s) observed at this lookahead-step "
                    "rank, reported for transparency only (see methodological "
                    "note M2 / GAP-INDX-03); NOT the grouping key used for the "
                    "quantile envelope above."
                ),
            },
        }
    return envelope


def _write_per_origin_csv(path: Path, per_origin_prefix: Dict[str, List[float]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["origin_id", "lookahead_step_rank", "prefix_cumulative_residual_wh_m2"])
        for origin in sorted(per_origin_prefix):
            for step_rank, value in enumerate(per_origin_prefix[origin], start=1):
                writer.writerow([origin, step_rank, f"{value:.6f}"])


def run_dataset(
    label: str,
    path: Path,
    origin_col: str,
    horizon_col: str,
    pred_col: str,
    actual_col: str,
    residual_col: str | None,
) -> Dict[str, object]:
    sequences, skipped = _load_origin_sequences(
        path, origin_col, horizon_col, pred_col, actual_col, residual_col
    )
    step_to_prefix_values, step_to_raw_horizons, per_origin_prefix = _prefix_sums_by_step(sequences)
    envelope = _build_envelope(step_to_prefix_values, step_to_raw_horizons)

    csv_out = OUT_DIR / f"pceeb_per_origin_prefix_errors_{label}.csv"
    _write_per_origin_csv(csv_out, per_origin_prefix)

    result = {
        "dataset_label": label,
        "input_path": str(path.relative_to(REPO_ROOT)),
        "input_sha256": sha256_of_file(path),
        "n_origins": len(sequences),
        "n_rows_skipped_missing_or_nonnumeric": skipped,
        "sign_convention": "realized_minus_forecast (actual - prediction), per PCEEB spec wording (M1)",
        "units": "Wh/m^2 (numerically identical to source hourly W/m^2 under M3)",
        "horizon_indexing": "lookahead_step_rank, 1-based position within each origin's own chronologically sorted sequence (M2)",
        "quantile_estimator": "linear interpolation between order statistics (Type 7) (M5)",
        "envelope_by_lookahead_step": envelope,
        "per_origin_csv_output": str(csv_out.relative_to(REPO_ROOT)),
    }
    return result


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    primary = run_dataset(
        label="2020_2023_primary",
        path=PRIMARY_INPUT,
        origin_col="forecast_start",
        horizon_col="horizon_hour",
        pred_col="prediction",
        actual_col="actual",
        residual_col="residual",
    )
    secondary = run_dataset(
        label="2024_odd_fixture_corroboration",
        path=SECONDARY_INPUT,
        origin_col="origin_id",
        horizon_col="horizon",
        pred_col="y_pred",
        actual_col="y_true",
        residual_col=None,
    )

    primary_out = OUT_DIR / "pceeb_quantile_envelope_2020_2023.json"
    secondary_out = OUT_DIR / "pceeb_quantile_envelope_2024_odd_fixture.json"
    with open(primary_out, "w", encoding="utf-8") as f:
        json.dump(primary, f, indent=2)
    with open(secondary_out, "w", encoding="utf-8") as f:
        json.dump(secondary, f, indent=2)

    hashes_path = OUT_DIR / "HASHES.txt"
    with open(hashes_path, "w", encoding="utf-8") as f:
        f.write("PCEEB Part (a) -- input and output SHA-256 hashes\n")
        f.write("Generated by compute_pceeb_part_a.py. Offline, read-only, non-sealed inputs only.\n\n")
        f.write("INPUTS\n")
        f.write(f"{primary['input_sha256']}  {primary['input_path']}\n")
        f.write(f"{secondary['input_sha256']}  {secondary['input_path']}\n")
        f.write("\nOUTPUTS\n")
        for out_path in [
            primary_out,
            secondary_out,
            OUT_DIR / "pceeb_per_origin_prefix_errors_2020_2023_primary.csv",
            OUT_DIR / "pceeb_per_origin_prefix_errors_2024_odd_fixture_corroboration.csv",
        ]:
            f.write(f"{sha256_of_file(out_path)}  {out_path.relative_to(REPO_ROOT)}\n")

    print(f"Primary dataset:   {primary['n_origins']} origins, {len(primary['envelope_by_lookahead_step'])} lookahead steps")
    print(f"Secondary dataset: {secondary['n_origins']} origins, {len(secondary['envelope_by_lookahead_step'])} lookahead steps")
    print(f"Wrote: {primary_out}")
    print(f"Wrote: {secondary_out}")
    print(f"Wrote: {hashes_path}")


if __name__ == "__main__":
    main()
