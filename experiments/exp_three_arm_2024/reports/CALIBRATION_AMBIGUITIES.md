# Arm C calibration: open ambiguities

Status: **A1–A6, and A8 (added after M7), each have a RECOMMENDED resolution awaiting project-lead approval** (2026-10-11). The full decision records are in `reports/DECISION_RESOLUTION_2026-10-11.md` §5 and, with evidence, leakage analysis and tests per choice, `reports/DECISION_RESOLUTION_M7_2026-10-11.md` §4, and the summary is at the end of this file. The original text below is kept as written, with two corrections marked. Nothing here was run on real data.

`scripts/calibrate_arm_c.py` implements Arm C (PROTOCOL.md §4) only where the protocol is unambiguous. Each point below is a place where the protocol allows more than one reasonable implementation, and the choice could change the calibrated reserve. Each one is a `null` field in `config/EXPERIMENT_CONFIG.json`. The code raises when it meets a `null` or unknown value, and preflight refuses calibration while any field is `null` or any value is not `APPROVED`. No default was chosen.

The values that the protocol does state are carried in the config as `PROPOSED`, not `APPROVED`, because D5 is still pending:
- γ grid 0.10–1.00, step 0.01;
- objective: daylight MAE, with daylight meaning elevation > 0 and clear-sky GHI > 0;
- α = 0.10;
- elevation edges 0/5/15/30/90°;
- cloud edges 0/0.2/0.8/1.0;
- a minimum of 20 origin-days per bin.

## A1. Quantile estimator (`quantile_method`)

The protocol says "split-conformal residual quantiles" at α = 0.10, but it gives no estimator. The candidates differ:
- **`split_conformal_lower`:** the order statistic r₍k₎ with k = ⌊α(n + 1)⌋. This is the usual finite-sample conformal rule. It is undefined for n < 9 at α = 0.10.
- **Any numpy `method=`**, for example `linear` (the default) or `inverted_cdf`.

With bins of about 20 origin-days, the estimators can differ by tens of W/m².

## A2. Bin boundary closure (`bin_boundary_rule`)

The protocol gives the bins as "0–5, 5–15, 15–30, > 30°" and "< 0.2, 0.2–0.8, > 0.8". These are not consistent about which side of each edge is closed. For example, a cloud fraction of exactly 0.2 is "0.2–0.8" in one reading and could be the first bin in another.

The weather file stores cloud cover as integer percent, so values of exactly 20 % and 80 % do occur. The choice is therefore not academic. Implemented options: `left_closed` [lo, hi) or `right_closed` (lo, hi]. In both, the outer edges are inclusive.

## A3. Merge direction (`insufficient_bin_policy`)

The protocol says to merge a sparse bin "with the neighbouring elevation bin". It does not say which neighbour: an interior bin has two. Implemented options:
- `fail`: refuse;
- `merge_lower_elevation`;
- `merge_higher_elevation`.

Merges are recorded in the artifact. A bin is never filled with evaluation-window data or with a global quantile.

## A4. Definition of "origin-days" in a bin

Implemented as the number of distinct calibration `forecast_start` values that contribute at least one daylight hour to the bin. Another reading counts distinct calendar days of the target hours. A target hour of horizon h belongs to forecast_start + h − 1 h, so the two counts differ near midnight. At 68° N in summer, daylight can span midnight.

This rule is in code, not config, and **needs explicit confirmation under D5**. If it is not confirmed, the code must be changed and re-reviewed before calibration.

> **Correction (2026-10-11, decision pass):** the sentence above about the counts differing near midnight is wrong for this data. Every origin starts at 00:00, and its targets are 00:00–23:00 of the same calendar day, so the two counts are identical. Calibration now refuses origins that do not start at 00:00.

## A5. Residual space (`residual_space`)

The protocol says the lower bound ŝ is "used for the EBR reserve". The EBR adapter consumes PV power in W. Residuals can be taken either:
- in GHI (W/m²), then converted to W through the frozen PV map; or
- in PV power (W), after the map.

The PV map is clipped at 60 kW, so the two give different bounds on bright hours. Options: `ghi_w_m2`, `pv_w`.

## A6. γ tie rule (`gamma_tie_rule`)

The protocol says to minimize daylight MAE on the grid but does not say how to break an exact tie. Ties are unlikely with real data. The code raises if one happens and no rule is approved. Options: `smallest_gamma`, `largest_gamma`.

> **Evidence added after M7 (geometry only, no observations):** the maximum clear-sky GHI is 624 W/m² in the calibration window and 724 W/m² in the evaluation window, both below the PV-map clip at 1,176.5 W/m². The point forecast and lower bound therefore never clip, and the two spaces differ only for calibration hours with actual GHI above 1,176.5 W/m². The calibration artifact now records that count (`residual_space_diagnostic`).

## A8. Definition of "daylight" (added after M7)

The protocol's γ objective is "daylight MAE", and the residuals are taken on daylight hours, but PROTOCOL.md does not define daylight. The code uses elevation > 0° (corrected geometry) and clear-sky GHI > 0, and `lower_bound` uses the same rule at run time, so night hours get ŝ = 0. This was CC's operationalization, not a protocol value. It is now RECOMMENDED and awaits approval under D5.

## A7. Time-centring of the target (noted, not resolved)

At label HH:00, the hourly SW_IN target is the mean of the ten-minute values HH:00…HH:50. The SITES values are period-ending, so this covers roughly (HH−1):50 to HH:50. The forecaster's clear-sky value is instantaneous at the corrected label instant.

That leaves a centring offset of about 20 minutes. It is a pre-existing convention of every POLARIS forecast–actual comparison and of PROTOCOL.md. It is recorded here, not changed.

## Related gate ambiguities (not calibration, also unresolved)

These are listed in DESIGN_AND_GATES.md:
- **G-a, S4-strict interval (D6):** one-sided or two-sided 95 % upper bound.
- **G-b, S4-strict bootstrap seed (D6):** no seed is recorded.
- ~~**G-c, SoC-parity factor f (D4):** needed only if the adjusted fuel metric becomes primary. f is defined in no repository document.~~ **Correction:** PROTOCOL.md §7 defines f ∈ {0.30, 0.75} L/kWh (from `diesel.yaml`). D4 now fixes the primary metric as unadjusted. The only open secondary choice is per-origin vs aggregate application.
- **G-d, E1 Holm family (D10):** which arms are tested together.

## Resolution summary (2026-10-11): RECOMMENDED, awaiting project-lead approval

| ID | Recommended value (config `arm_c_method`) | Basis |
|---|---|---|
| A1 | `quantile_method: split_conformal_lower` (r₍⌊α(n+1)⌋₎; raise if k < 1) | Protocol says "split-conformal"; finite-sample rule; never above `inverted_cdf` |
| A2 | `bin_boundary_rule: {"elevation": "right_closed", "cloud": "closed_middle"}`: (0,5], (5,15], (15,30], (30,90]; [0,0.2), [0.2,0.8], (0.8,1] | Literal reading of ">30°", "<0.2" and ">0.8" |
| A3 | `insufficient_bin_policy: merge_single_neighbour_else_lower` | Edge bins have only one neighbour. >30° occurs on only 19 of 222 calibration days, so it must merge down. The interior direction is a convention |
| A4 | `origin_day_definition`: distinct 00:00 `forecast_start` origins with ≥ 1 daylight hour in the bin | Protocol term; identical to calendar days for 00:00 origins (enforced) |
| A5 | `residual_space: ghi_w_m2` | The PV map is linear below 1,176.5 W/m²; maximum clear-sky GHI is 624 (calibration) and 724 W/m² (evaluation); the protocol works in GHI; the artifact records any calibration hour where the spaces differ |
| A6 | `gamma_tie_rule: largest_gamma` | Lowest point forecast if tied; deterministic |
| A8 | `gamma_objective.daylight_rule: elevation>0 and clearsky_ghi>0` (status of `gamma_objective` stays PROPOSED; A8 flagged in `daylight_rule_note`) | PROTOCOL does not define daylight; same rule in calibration and at run time |

Each entry has status `RECOMMENDED — AWAITING PROJECT-LEAD APPROVAL`. Preflight refuses calibration until each is `APPROVED`.

## Citation status (added after M8)

PROTOCOL §4 states the 20 origin-day minimum and the daylight-MAE objective, citing `CLOUD_TO_GHI_EXPERIMENT_PROTOCOL.md:27` and `:19-21`. That file is in a 2025 campaign folder and was not opened. No non-2025 governance or source file in the staged repository copy states either requirement. Both citations are **UNVERIFIED**, recorded as `citation_status` in the config. Details: `reports/DECISION_FOLLOWUP_M8_2026-10-11.md` §5.
