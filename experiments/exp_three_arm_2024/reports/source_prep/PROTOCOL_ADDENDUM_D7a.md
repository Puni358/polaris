# Protocol Addendum D7a: Arm A-Fix (solar-position timestamp correction)

**Status:** prepared for project-lead approval. **Not executed.** This addendum implements Puni's conditional D7a decision (2026-10-11, "As-is + fix sub-arm"). It authorizes no simulation, training or experiment run.

## 1. Arms after D7a

| Arm | Solar forecaster geometry | Result label |
|---|---|---|
| PC-Control | legacy, unchanged (denominator) | — |
| A | legacy (labels read as UTC: the known 1 h error) | `LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT` |
| **A-Fix** | corrected: labels read as UTC+1 | `DIAGNOSTIC — NOT PROMOTION-ELIGIBLE` |
| B | not used (perfect solar) | DIAGNOSTIC, non-deployable |
| C | corrected (see §4) | DIAGNOSTIC |

A-Fix is a diagnostic comparison. It does not become the winner if it does better. Changing the official winner needs a separate governance decision (D7a item 7).

**PC-Control** keeps the legacy geometry, because it is the formal baseline as defined. The control's own forecaster also carries the 1 h error; this is recorded as a known property of the baseline, and the baseline is not changed.

## 2. How the correction works, and why the D7 report's first proposal was dropped

Static audit of the code path (no execution):

| Consumer of the timestamp | File:line | Effect if timestamps were converted |
|---|---|---|
| Forecaster solar geometry | `causal_nwp_physics.py:302-303, 334-336` | The intended fix |
| Baseline wind and demand | `system/forecasting/implementations/baseline.py` (uses `future_dt.hour`) | **Wind and demand forecasts would shift by 1 h**, which breaks parity |
| Reserve (EBR) elevation | `planner_cf_campaign_runner.py:124` passes `bundle.timestamps` to `SolarElevationProvider`, which strips `Z` and localizes Etc/GMT-1 (`stage4_low_sun_adapter.py:99-118`) | **Double conversion**: the reserve's elevation would end up 1 h wrong |
| Weather lookup, executor state chain | `planner_cf_campaign_runner.py:105-115, 140-145` | Cloud and state timing would change |

So the D7 report §5 proposal (passing UTC `…Z` strings into the forecaster) is **withdrawn**. It would have changed three things besides the geometry.

**Adopted mechanism** (`d7/PROPOSED_solar_convention.py`): in A-Fix only, the runner replaces `engine.location` on its forecaster instance with `LabelCorrectedLocation`. This wrapper subtracts 1 h from the instants passed to pvlib's `get_solarposition` and `get_clearsky`, then re-indexes the results. Everything else in A-Fix is identical to Arm A: labels, cloud values, wind, demand, `bundle.timestamps`, the reserve's elevation, the optimizer, the executor and the gates. `causal_nwp_physics.py` stays byte-identical. The wrapper refuses to be applied twice and refuses any other pvlib attribute.

## 3. Audit of reserve and forecaster as separate paths (item 4)

- **Reserve:** `SolarElevationProvider(None)` uses the pvlib fallback with Etc/GMT-1, which is already correct. It is **not touched** in any arm. (The winner loaded the 2025 decomposition CSV here. The new runner must not. The 2024 decomposition built by the same convention matches the UTC+1 calculation to 0.008°, so this is the one unavoidable difference from the original winner run. It applies equally to A and A-Fix.)
- **Forecaster:** corrected only through the wrapper, and only in A-Fix and C.
- **Executor:** uses realized SW_IN from SITES and computes no geometry.
- **Expected consistency after the fix:** the forecaster's sun elevation agrees with the reserve's within 0.05° (test below).

## 4. Arm C and the γ̂ calibration (default chosen, change it if you disagree)

Item 4 asks for the verified convention to be applied consistently. I've set C, and the γ̂ fit on the 2024 calibration months, to use the **corrected** geometry. C should therefore be compared with A-Fix, not with A. Otherwise the comparison would mix two changes. The protocol's C-vs-A comparison becomes C-vs-A-Fix; A-vs-A-Fix isolates the timestamp fix.

## 5. Fail-closed tests (item 5)

`d7/PROPOSED_test_d7a_parity.py`, plus `d7/PROPOSED_timestamp_guards.py` from D7. Both are not applied and not run:
- source files unchanged (hashes of the forecaster, adapter, planner, executor, SITES file and weather file);
- only the solar channel differs between A and A-Fix (timestamps, wind and demand are identical);
- A-Fix at label L equals legacy at label L − 1 h (exactly a 1 h geometry shift);
- reserve elevations are identical in both arms (no double conversion);
- the corrected forecaster's elevation matches the reserve's within 0.05°;
- double wrapping is refused;
- `ARM_CONFIGS["A"]` and `ARM_CONFIGS["A_FIX"]` differ only in `solar_label_correction` and the result label.

Note: the synthetic `StationState` stand-in in the tests must be checked against the real `StationState` fields when the files are applied.

## 6. Reporting (item 6)

Both A and A-Fix report the same tables:
- total fuel (L) and % vs control;
- unmet critical Wh;
- unmet non-critical Wh;
- total unmet Wh (S4);
- hours with SoC < 20% (S3);
- ΔR_CF and ΔR_P (S1, S2);
- reserve slack (J2);
- curtailment;
- diesel starts;
- fuel-starvation events;
- final SoC.

There is also a paired A-Fix − A table with Wilcoxon and BCa intervals. No direction is assumed: a worse result for A-Fix is reported the same way as a better one.

## 7. Compute budget (item 8)

| Item | MILP solves |
|---|---|
| One arm (123 origins × 24 re-plans) | 2,952 |
| PC-Control, A, B, C | 11,808 |
| **A-Fix (new)** | **2,952** |
| **Total** | **14,760** |
| Optional A + Rule D sub-arm | +2,952 (17,712) |

This replaces my earlier "about 4k" estimate. A-Fix adds 2,952 solves. Same limits as before: ≤ 4 workers, a single attempt, no automatic retries, no background jobs left running. **Your confirmation of the total is still needed before any execution.**
