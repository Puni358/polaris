#!/usr/bin/env python3
"""
EVID-03 -- Numeric basis (units/horizon/margin) evidence for the reserve-shortfall
ceiling and solar-credit cap: offline, empirical, research-only.

STANDALONE, OFFLINE, RESEARCH-ONLY. Implements exactly and only the EVID-03
analysis the project owner explicitly commissioned this pass ("I commission
the bounded, offline, research-only EVID-03 analysis described in the
register"), scoped per `docs/decision_registers/POLARIS_MASTER_DECISION_REGISTER.json`'s own EVID-03
entry and `forecasting/n6/remediation_reports/SAFETY_ENFORCEMENT_AUDIT_AND_PROPOSAL.md`
Section 4 ("Reserve-limit evidence (Policy C)"):

    "Units/horizon/margins that WOULD need to be specified by the project
    owner before a ceiling could be authorized: Wh vs. kWh (the guard
    enforces Wh); per-step vs. cumulative-over-horizon vs.
    cumulative-over-campaign; whether the ceiling scales with the EBR
    target (a percentage) or is a fixed absolute Wh figure; whether it
    differs for the 6-hour EBR window vs. the 24h terminal target."

WHAT THIS SCRIPT DOES: re-expresses the ALREADY-COMPUTED, already-authorized
PCEEB Part (a) prefix-cumulative solar-forecast-error quantile envelope
(`research/pceeb_part_a_offline/outputs/`) in the SPECIFIC units and horizon
bases GAP19's own reserve-policy code actually uses (6-hour rolling EBR
window; full-lookahead/terminal-target window), expressed both in absolute
Wh and as a percentage of the EBR_BASE_WH=15,000 Wh constant ALREADY
hard-coded in this repository (`n6_solar.py`, `polaris_inference_runner.py`)
-- it does not invent that constant, only uses it as an existing reference
scale. It additionally computes one new, bounded, purely descriptive
statistic directly from the same two permitted historical CSVs: the
empirical rate and magnitude of "forecast-overestimate" events (instances
where cumulative realized irradiance fell below cumulative predicted
irradiance) at the same two horizon bases -- the direct empirical analogue
of "how often, and by how much, would a policy that credits the point
forecast to the reserve have been wrong," which is the question a
solar-credit cap exists to bound.

WHAT THIS SCRIPT DOES NOT DO (explicitly out of scope, per the directive):
  - Does NOT select, propose, recommend, or adopt any specific numeric
    reserve-shortfall ceiling or solar-credit cap fraction. Every quantile
    and rate below is reported as a descriptive statistic of historical
    data, not as a recommended or approved threshold.
  - Does NOT invoke, import, bypass, or reimplement
    system/evaluation/replay_harness.py. Does NOT run any dispatch
    campaign, closed-loop simulation, or replay-equivalent comparison.
    (The actual GAP19 "reserve_shortfall" output depends jointly on solar,
    wind, demand, battery SOC trajectory and the optimizer's own
    lexicographic objective -- this script characterizes only the
    solar-forecast-error INPUT to that joint system, in isolation, as a
    bounded proxy. It is NOT a replay-validated measurement of actual
    GAP19 reserve-shortfall outcomes; see LIMITATIONS below.)
  - Does NOT edit, touch, or re-derive gap19_highs_native.py, option_d.py,
    ecd.py, router.py, simulator.py, runner.py, or any other PROTECTED_FILES
    entry. All GAP19-side facts below (EBR 6h window, terminal-target
    horizon, reserve_shortfall_total_wh = sum over 24 steps) are cited from
    a READ-ONLY inspection of gap19_highs_native.py and
    system/safety/reserve_policy_guard.py performed this pass, reproduced
    verbatim in the companion report, not re-run or re-executed.
  - Does NOT fit, train, tune, recalibrate, or promote any model.
  - Does NOT change any production default, reserve policy, solar-credit
    behavior, or control flow.
  - Does NOT access the sealed 2025 blind partition. Inputs are identical
    to, and re-verified against the same SHA-256 hashes as, PCEEB Part (a)'s
    own inputs (2020-2024 data only).

INPUTS (identical to PCEEB Part (a); both already used, non-sealed, read-only):
  1. forecasting/candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv
     -- PRIMARY. 1,369 daily origins, 19 lookahead-step ranks/origin.
  2. forecasting/reports/stage8/POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv
     -- SECONDARY / corroboration. 173 origins, 24 lookahead-step ranks/origin.
  3. research/pceeb_part_a_offline/outputs/pceeb_quantile_envelope_2020_2023.json
     and .../pceeb_quantile_envelope_2024_odd_fixture.json -- the PRIOR,
     already-authorized (UNC-01 Part (a)) prefix-cumulative-error quantile
     envelopes computed from inputs 1-2. Read, not recomputed, to avoid a
     second, possibly-drifting implementation of the same statistic; this
     script's own SHA-256 check (below) confirms these files are
     byte-identical to the versions generated and hashed in that prior pass.

METHODOLOGICAL CHOICES MADE AND DOCUMENTED (not silently invented):

  (E1) GAP19's two reserve-target horizon bases, cited read-only from
       system/optimization/implementations/gap19_highs_native.py (a
       PROTECTED_FILES entry; read but not edited in this or any pass):
         - E_EBR_target[t]: a 6-hour ROLLING lookahead sum of critical-load
           energy (gap19_highs_native.py lines ~111-131, docstring "Governed
           EBR 6-Hour Lookahead Target Trajectory").
         - E_term_target: a single value applied only at the FINAL step of
           the 24-step horizon (t=23), i.e. a full-horizon/terminal basis
           (gap19_highs_native.py lines ~133-151).
         - E_stage2_target[t] = max(E_EBR_target[t], terminal-at-t=23) --
           the "Pointwise Maximum Reserve Envelope."
       This script therefore reports the PCEEB envelope at lookahead-step
       rank 6 (6h-window analogue) and at the FINAL available step rank for
       each dataset (19 for primary, 24 for secondary; full-horizon/terminal
       analogue) -- the two bases EVID-03 itself asks to be distinguished.

  (E2) GAP19's own "reserve_shortfall_total_wh", cited read-only from
       system/safety/reserve_policy_guard.py lines 308-311 (NOT a
       PROTECTED_FILES entry; this is the existing, non-protected guard
       module, read but not edited): `sum(plan["reserve_shortfall"])` across
       the plan's 24 per-step slack values -- i.e. the guard's CURRENT,
       ad-hoc choice is already "cumulative-over-horizon within one 24h
       dispatch decision," NOT "per-step" and NOT "cumulative-over-campaign."
       EVID-03 flags that this choice itself has never been owner-validated
       as the correct basis for a ceiling. This script does not change or
       endorse it; it is reported here as existing fact, for the owner's
       own comparison against the empirical quantiles below.

  (E3) Units conversion, solar-forecast-error (irradiance, Wh/m^2) ->
       generation-energy-equivalent (Wh): this script multiplies the PCEEB
       envelope's Wh/m^2 quantiles by K_PV = 51.0 W/(W/m^2) -- the EXISTING
       plant-conversion constant already hard-coded identically in
       `system/forecasting/implementations/n6_solar.py` (line ~62) and
       `forecasting/stage7/.../artifacts/polaris_inference_runner.py` (line ~34) -- to
       obtain a generation-power-equivalent in W, numerically identical to
       Wh under 1-hour sampling (same dimensional-identity assumption PCEEB
       Part (a) already documented and used for its own W/m^2 -> Wh/m^2
       step). This is a LINEAR scaling; it does NOT apply the inverter
       ceiling clip (P_INV_MAX_W = 60,000 W) that the real plant model
       applies via `min(P_INV_MAX_W, ghi * K_PV)`. See LIMITATIONS.

  (E4) Reference scale for expressing results as a percentage: this script
       divides the Wh quantiles above by EBR_BASE_WH = 15,000 Wh -- the
       EXISTING constant already hard-coded identically in both
       `n6_solar.py` and `polaris_inference_runner.py` as the EBR's own
       minimum floor. Using it as a denominator is a reporting convenience
       (it is the only EBR-related absolute-Wh constant already present in
       the repository), NOT an endorsement that this is the correct scaling
       basis for a FUTURE ceiling, and NOT a claim that this constant is
       itself owner-authorized (SAF-07's own disposition -- "unverified, no
       provenance found" -- is unchanged and explicitly reiterated here).

  (E5) "Forecast-overestimate event" (solar-credit risk proxy): at each
       lookahead-step rank, this script re-derives (from the same two raw
       CSVs used by PCEEB Part (a), with IDENTICAL loading/sign-convention
       logic -- M1/M2/M4/M5 below, restated from that script) the fraction
       of origins whose prefix-cumulative residual (actual - prediction) is
       STRICTLY NEGATIVE at that step, i.e. realized irradiance fell short
       of predicted irradiance cumulatively up to that step. This is the
       direct empirical analogue of "how often would a policy that credits
       the point forecast's generation to the reserve have been wrong." The
       magnitude quantiles (Wh-equivalent, via E3) are reported for the
       negative-event subset only. No credit fraction is computed, selected,
       or proposed from this -- only the historical rate and magnitude of
       the error direction a credit policy would need to tolerate.

  (M1) Sign convention: identical to PCEEB Part (a) -- "residual" column
       (primary) / y_true - y_pred (secondary) = actual - prediction.
  (M2) Horizon indexing: identical to PCEEB Part (a) -- lookahead-step rank
       (1-based position in each origin's own chronological sequence), NOT
       raw horizon_hour, per the register-documented GAP-INDX-03 gap.
  (M4) Missing data: identical skip-on-NaN rule as PCEEB Part (a); re-verified
       inert (0 skipped rows) on both inputs this pass.
  (M5) Quantile estimator: identical linear-interpolation ("Type 7")
       estimator as PCEEB Part (a), re-implemented here (stdlib-only, no
       import of the PCEEB module, to keep this directory fully standalone
       per the existing research/pceeb_part_a_offline/ pattern).

LIMITATIONS (documented per the directive's explicit instruction: "if the
dataset or specification cannot support a conclusion, document the
limitation rather than extrapolating"):
  (L1) This analysis characterizes only the SOLAR-FORECAST-ERROR component
       of what would actually drive a GAP19 reserve shortfall. Real
       reserve_shortfall (s_J2) also depends on wind generation, demand,
       battery state-of-charge trajectory, the optimizer's joint
       lexicographic objective (J1 > J2 > J3 > J4), and the terminal/EBR
       envelope's own interaction with the hard SOC floor (min_e_wh) --
       none of which this script models. It is a one-dimensional,
       solar-only proxy/bound, not a replay-validated measurement of actual
       dispatch outcomes. A full measurement would require Part (b)-style
       closed-loop replay, which remains gated behind
       `CampaignExecutionNotAuthorizedError` and is explicitly NOT performed
       here or in any pass to date.
  (L2) The K_PV linear scaling (E3) ignores the inverter ceiling
       nonlinearity (P_INV_MAX_W clip) and ignores clearsky/terrain
       shading adjustments the real plant model applies. For the error
       magnitudes observed in this dataset (step-6 and final-step quantiles
       reported below), this is a reasonable order-of-magnitude
       approximation, not an exact physical replay.
  (L3) Neither input CSV carries per-origin ensemble/uncertainty spread
       (e.g. the N6 model's own `ensemble_std`), so this script cannot
       reproduce the N6 conformal lower-bound (Q_HAT_NORM=1.8590) coverage
       computation directly. `forecasting/reports/uncertainty/FORECAST_UNCERTAINTY_AUDIT.md`'s own,
       already-published finding on that exact question (static q10:
       88.53% pooled one-sided coverage, but "operationally excessive" in
       closed-loop replay: +38.18% diesel, +92.87% curtailment) is CITED
       here as existing evidence, not recomputed -- that figure came from a
       replay this script does not and must not re-run.
  (L4) Neither dataset is Nuolja-station-specific critical-load data;
       EVID-02's "REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED" finding is
       unchanged and applies to any demand-side interpretation of these
       figures.
  (L5) This script's own "forecast-overestimate event" statistic (E5) is a
       NEW computation (not previously published in any prior report), but
       it uses only the two already-permitted, already-hashed datasets and
       the same methodology PCEEB Part (a) already established and the
       owner already authorized (UNC-01) -- no new dataset, no live access,
       no sealed data.

This script has NO third-party dependencies (stdlib only: csv, json,
hashlib, math, statistics, pathlib) so it runs identically regardless of
the repository's Python environment state.
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
PCEEB_OUT_DIR = REPO_ROOT / "research" / "pceeb_part_a_offline" / "outputs"
PCEEB_PRIMARY_ENVELOPE = PCEEB_OUT_DIR / "pceeb_quantile_envelope_2020_2023.json"
PCEEB_SECONDARY_ENVELOPE = PCEEB_OUT_DIR / "pceeb_quantile_envelope_2024_odd_fixture.json"

QUANTILE_LEVELS = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)

# Existing, already-hard-coded repository constants (NOT invented here).
# Cited verbatim from system/forecasting/implementations/n6_solar.py and
# forecasting/stage7/.../artifacts/polaris_inference_runner.py (both files re-read this
# pass; both independently define identical values).
K_PV_W_PER_WM2: float = 51.0          # Power conversion factor [W / (W/m^2)]
P_INV_MAX_W: float = 60000.0          # Inverter saturation ceiling [W] (NOT applied -- see L2)
ETA_DIS: float = 0.95                 # Battery discharge efficiency (cited for context; not applied below)
EBR_BASE_WH: float = 15000.0          # Existing EBR floor constant, used ONLY as a reference denominator (E4)

# Existing GAP19 hard-floor constant, cited read-only from
# system/config/battery.yaml + gap19_highs_native.py (default values).
DEFAULT_BATTERY_CAPACITY_WH: float = 200000.0
DEFAULT_MIN_SOC_PCT: float = 20.0
DEFAULT_MIN_E_WH: float = DEFAULT_BATTERY_CAPACITY_WH * (DEFAULT_MIN_SOC_PCT / 100.0)  # 40,000 Wh

# The two GAP19 reserve-target horizon bases (E1): 6h rolling EBR window,
# and the full/terminal horizon (final lookahead-step rank per dataset).
EBR_WINDOW_STEP_RANK: int = 6


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def empirical_quantile(sorted_values: Sequence[float], q: float) -> float:
    """Linear-interpolation ("Type 7") empirical quantile of an already-sorted sequence.
    Identical estimator to PCEEB Part (a)'s own (M5), reimplemented here to
    keep this directory standalone."""
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
    """Identical loading/sign-convention logic to PCEEB Part (a) (M1/M2/M4),
    reimplemented here (not imported) to keep this directory standalone."""
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
) -> Dict[int, List[float]]:
    """Running (prefix) cumulative sum of residuals per origin, grouped by
    lookahead-step rank. Identical methodology to PCEEB Part (a)."""
    step_to_prefix_values: Dict[int, List[float]] = {}
    for origin, seq in sequences.items():
        running = 0.0
        for step_rank, (_raw_horizon, residual) in enumerate(seq, start=1):
            running += residual
            step_to_prefix_values.setdefault(step_rank, []).append(running)
    return step_to_prefix_values


def overestimate_event_stats(values: Sequence[float]) -> Dict[str, object]:
    """(E5) Given the prefix-cumulative residuals (actual - prediction) at one
    lookahead-step rank across all origins, computes the empirical rate and
    magnitude of 'forecast-overestimate' events: prefix-cumulative residual
    STRICTLY NEGATIVE (realized < predicted cumulatively). No threshold is
    selected; this reports historical rate/magnitude only."""
    n = len(values)
    negative = sorted(v for v in values if v < 0.0)
    n_negative = len(negative)
    rate = n_negative / n if n > 0 else None
    result: Dict[str, object] = {
        "n_origins": n,
        "n_overestimate_events": n_negative,
        "overestimate_event_rate": round(rate, 6) if rate is not None else None,
    }
    if n_negative > 0:
        magnitudes = [abs(v) for v in negative]  # magnitude of the overestimate, Wh/m^2
        result["overestimate_magnitude_wh_m2_quantiles"] = {
            f"q{int(q * 100):02d}": round(empirical_quantile(magnitudes, q), 6)
            for q in QUANTILE_LEVELS
        }
        result["overestimate_magnitude_wh_m2_mean"] = round(statistics.fmean(magnitudes), 6)
        result["overestimate_magnitude_wh_m2_max"] = round(max(magnitudes), 6)
    else:
        result["overestimate_magnitude_wh_m2_quantiles"] = None
        result["overestimate_magnitude_wh_m2_mean"] = None
        result["overestimate_magnitude_wh_m2_max"] = None
    return result


def wh_m2_quantiles_to_generation_wh(quantiles_wh_m2: Dict[str, float]) -> Dict[str, float]:
    """(E3) Linear K_PV scaling of irradiance-error quantiles (Wh/m^2) into
    generation-energy-equivalent quantiles (Wh). Does NOT apply the inverter
    ceiling clip -- see LIMITATIONS (L2)."""
    return {k: round(v * K_PV_W_PER_WM2, 4) for k, v in quantiles_wh_m2.items()}


def wh_as_pct_of_ebr_base(wh_quantiles: Dict[str, float]) -> Dict[str, float]:
    """(E4) Expresses Wh quantiles as a percentage of the EXISTING EBR_BASE_WH
    constant (15,000 Wh), purely as a reporting convenience / reference
    scale -- not an endorsement of this basis for a future ceiling."""
    return {k: round(100.0 * v / EBR_BASE_WH, 4) for k, v in wh_quantiles.items()}


def analyze_dataset(
    label: str,
    raw_path: Path,
    pceeb_envelope_path: Path,
    origin_col: str,
    horizon_col: str,
    pred_col: str,
    actual_col: str,
    residual_col: str | None,
    final_step_rank: int,
) -> Dict[str, object]:
    # --- Re-verify PCEEB Part (a)'s own input/output hashes are unchanged ---
    with open(pceeb_envelope_path, "r", encoding="utf-8") as f:
        pceeb_envelope = json.load(f)
    pceeb_input_sha256_recorded = pceeb_envelope["input_sha256"]
    pceeb_input_sha256_recomputed = sha256_of_file(raw_path)
    envelope_by_step = pceeb_envelope["envelope_by_lookahead_step"]

    # --- (E1/E3/E4) Re-express the 6h-EBR-window and final/terminal steps ---
    def basis_summary(step_rank: int, basis_name: str) -> Dict[str, object]:
        step_entry = envelope_by_step[str(step_rank)]
        quantiles_wh_m2 = step_entry["quantiles_wh_m2"]
        quantiles_gen_wh = wh_m2_quantiles_to_generation_wh(quantiles_wh_m2)
        quantiles_pct_of_ebr_base = wh_as_pct_of_ebr_base(quantiles_gen_wh)
        return {
            "basis": basis_name,
            "lookahead_step_rank": step_rank,
            "n_origins": step_entry["n_origins"],
            "source": "PCEEB Part (a) envelope (research/pceeb_part_a_offline/outputs/), read-only",
            "irradiance_error_quantiles_wh_m2": quantiles_wh_m2,
            "generation_energy_equivalent_quantiles_wh": quantiles_gen_wh,
            "as_pct_of_existing_ebr_base_wh_15000": quantiles_pct_of_ebr_base,
            "as_pct_of_default_hard_soc_floor_min_e_wh_40000": {
                k: round(100.0 * v / DEFAULT_MIN_E_WH, 4) for k, v in quantiles_gen_wh.items()
            },
        }

    ebr_window_basis = basis_summary(EBR_WINDOW_STEP_RANK, "6h_rolling_ebr_window (E1)")
    terminal_basis = basis_summary(final_step_rank, "full_horizon_terminal_target (E1)")

    # --- (E5) New overestimate-event-rate/magnitude statistic, both bases ---
    sequences, skipped = _load_origin_sequences(
        raw_path, origin_col, horizon_col, pred_col, actual_col, residual_col
    )
    step_to_prefix_values = _prefix_sums_by_step(sequences)

    def event_basis_summary(step_rank: int, basis_name: str) -> Dict[str, object]:
        stats = overestimate_event_stats(step_to_prefix_values[step_rank])
        if stats["overestimate_magnitude_wh_m2_quantiles"] is not None:
            gen_wh_quantiles = wh_m2_quantiles_to_generation_wh(
                stats["overestimate_magnitude_wh_m2_quantiles"]
            )
            stats["overestimate_magnitude_generation_wh_quantiles"] = gen_wh_quantiles
            stats["overestimate_magnitude_pct_of_ebr_base_wh_15000"] = wh_as_pct_of_ebr_base(
                gen_wh_quantiles
            )
        else:
            stats["overestimate_magnitude_generation_wh_quantiles"] = None
            stats["overestimate_magnitude_pct_of_ebr_base_wh_15000"] = None
        return {"basis": basis_name, "lookahead_step_rank": step_rank, **stats}

    ebr_window_events = event_basis_summary(EBR_WINDOW_STEP_RANK, "6h_rolling_ebr_window (E1)")
    terminal_events = event_basis_summary(final_step_rank, "full_horizon_terminal_target (E1)")

    return {
        "dataset_label": label,
        "raw_input_path": str(raw_path.relative_to(REPO_ROOT)),
        "raw_input_sha256": pceeb_input_sha256_recomputed,
        "pceeb_recorded_input_sha256_matches": pceeb_input_sha256_recomputed == pceeb_input_sha256_recorded,
        "pceeb_envelope_source_path": str(pceeb_envelope_path.relative_to(REPO_ROOT)),
        "n_rows_skipped_missing_or_nonnumeric_this_pass": skipped,
        "reserve_shortfall_basis_evidence": {
            "6h_rolling_ebr_window": ebr_window_basis,
            "full_horizon_terminal_target": terminal_basis,
        },
        "solar_credit_risk_evidence_overestimate_events": {
            "6h_rolling_ebr_window": ebr_window_events,
            "full_horizon_terminal_target": terminal_events,
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    primary = analyze_dataset(
        label="2020_2023_primary",
        raw_path=PRIMARY_INPUT,
        pceeb_envelope_path=PCEEB_PRIMARY_ENVELOPE,
        origin_col="forecast_start",
        horizon_col="horizon_hour",
        pred_col="prediction",
        actual_col="actual",
        residual_col="residual",
        final_step_rank=19,
    )
    secondary = analyze_dataset(
        label="2024_odd_fixture_corroboration",
        raw_path=SECONDARY_INPUT,
        pceeb_envelope_path=PCEEB_SECONDARY_ENVELOPE,
        origin_col="origin_id",
        horizon_col="horizon",
        pred_col="y_pred",
        actual_col="y_true",
        residual_col=None,
        final_step_rank=24,
    )

    result = {
        "analysis": "EVID-03 reserve-shortfall/solar-credit units/horizon/margin evidence",
        "commissioned_by": "project owner, this pass (2026-10-17), per directive item 1",
        "scope": "offline, non-campaign, non-replay, non-sealed-data, descriptive-statistics-only",
        "boundary_statement": (
            "This analysis supplies EMPIRICAL EVIDENCE ONLY. It does not select, propose, "
            "recommend, or adopt any numeric reserve-shortfall ceiling or solar-credit cap. "
            "Any adoption of a specific number from this evidence into SAF-03, SAF-04, or "
            "SAF-05 requires a SEPARATE, explicit owner risk-tolerance decision, not implied "
            "by this report's existence."
        ),
        "existing_constants_cited_not_invented": {
            "K_PV_W_PER_WM2": K_PV_W_PER_WM2,
            "P_INV_MAX_W": P_INV_MAX_W,
            "ETA_DIS": ETA_DIS,
            "EBR_BASE_WH": EBR_BASE_WH,
            "default_battery_capacity_wh": DEFAULT_BATTERY_CAPACITY_WH,
            "default_min_soc_pct": DEFAULT_MIN_SOC_PCT,
            "default_min_e_wh_hard_floor": DEFAULT_MIN_E_WH,
            "source_citation": (
                "n6_solar.py and polaris_inference_runner.py (K_PV/P_INV_MAX_W/ETA_DIS/EBR_BASE_WH); "
                "system/config/battery.yaml + gap19_highs_native.py defaults (capacity_wh/min_soc_pct)"
            ),
        },
        "datasets": {"primary": primary, "secondary_corroboration": secondary},
    }

    out_path = OUT_DIR / "evid03_reserve_margin_evidence.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    hashes_path = OUT_DIR / "HASHES.txt"
    with open(hashes_path, "w", encoding="utf-8") as f:
        f.write("EVID-03 reserve-margin analysis -- input and output SHA-256 hashes\n")
        f.write("Generated by compute_evid03_reserve_margin_analysis.py.\n")
        f.write("Offline, read-only, non-sealed inputs only. No ceiling/cap proposed or adopted.\n\n")
        f.write("INPUTS\n")
        f.write(f"{primary['raw_input_sha256']}  {primary['raw_input_path']}\n")
        f.write(f"{secondary['raw_input_sha256']}  {secondary['raw_input_path']}\n")
        f.write(f"(PCEEB envelope, read-only) {primary['pceeb_envelope_source_path']}\n")
        f.write(f"(PCEEB envelope, read-only) {secondary['pceeb_envelope_source_path']}\n")
        f.write("\nOUTPUTS\n")
        f.write(f"{sha256_of_file(out_path)}  {out_path.relative_to(REPO_ROOT)}\n")

    print(f"Primary dataset:   6h-window step={EBR_WINDOW_STEP_RANK}, terminal step=19")
    print(f"Secondary dataset: 6h-window step={EBR_WINDOW_STEP_RANK}, terminal step=24")
    print(f"PCEEB input hash match (primary):   {primary['pceeb_recorded_input_sha256_matches']}")
    print(f"PCEEB input hash match (secondary): {secondary['pceeb_recorded_input_sha256_matches']}")
    print(f"Wrote: {out_path}")
    print(f"Wrote: {hashes_path}")


if __name__ == "__main__":
    main()
