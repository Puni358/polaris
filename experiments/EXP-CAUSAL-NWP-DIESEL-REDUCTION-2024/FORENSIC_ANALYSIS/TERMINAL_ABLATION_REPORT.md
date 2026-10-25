# Terminal-Target Ablation Report: Arm B, Six Traced Origins

**Experiment:** `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024` (frozen; not rerun or modified)
**Harness:** `FORENSIC_ANALYSIS/terminal_ablation.py` (research-only, isolated). Output: `FORENSIC_ANALYSIS/terminal_ablation/origin_{77,56,66,23,8,30}.json`, `summary.json`
**Date:** 2026-10-04

---

## 0. Isolation, Verification, and Reproduction

**The one change.** `config["terminal_target_wh"]` is set to `0.0` instead of `100000.0`. Nothing else is changed.

**Why this isolates the terminal mechanism.** A search of `system/` shows the only consumer of this value in GAP19 is `gap19_highs_native.py:151`:
`e_stage2_target[23] = max(ebr_target_wh_list[23], terminal_target_wh)`.
With `terminal_target_wh = 0`, this reduces to `EBR[23]`. The EBR reserve envelope for all hours 0–23 is unchanged. `terminal_target_wh_override` on `StationState` is `None` in this path, so the config value is the one used. The campaign's `load_canonical_configs` sets the same key, so the harness uses the same mechanism.

**Assertions run in the harness:**
- The base and ablated configs differ in exactly one key, `terminal_target_wh`. Checked with an `assert` on every run.
- Baseline Arm B reproduces the frozen per-origin fuel for all six origins (`frozen_B_reproduced = True` for all). This confirms the baseline path matches the campaign.

**Non-terminal invariants, checked step by step (0 mismatches over 6 origins × 24 steps):**
- Forecast solar at t+1 and the 24-hour solar sum, per step.
- Realized solar at t+1.
- Critical demand at t+1 and the demand forecast at t+1.
- EBR reserve target at step 0.
- Origin timestamp, target timestamp, and initial state (SOC 50%, 100 L fuel, diesel off), identical at step 0.

**Limit of the invariant check.** It compares the first hour and the 24-hour solar sum per step, not every element of the 24-hour vectors. Full-vector identity follows from the code path (the wrappers do not alter inputs) but was not compared element by element.

**Two honest notes:**
- The margin reference for the ablated run is set to 0 (`TERMINAL_WH = 0` in the harness). Reserve margins are still measured against `EBR + min_e`. The "terminal-tight" counts below therefore measure tightness against `EBR[23]`, not against 140 kWh.
- The trace's `reserve_margin_min_wh` field is the minimum over hours 0–22. It is the reserve-only measure.

---

## 1. Results: Base B vs Terminal-Removed B (per origin)

| Origin | Base fuel (L) | Ablated fuel (L) | Δ fuel (L) | Base on-h / starts | Ablated on-h / starts | Base curtail (kWh) | Ablated curtail (kWh) | Δ curtail (kWh) | Base unmet (kWh) | Ablated unmet (kWh) |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|
| 77 (2024-07-16) | 74.32 | **46.18** | −28.1 | 6 / 3 | 4 / 3 | 147.1 | **91.9** | −55.1 | 33.9 | 37.1 |
| 56 (2024-06-25) | 93.76 | **80.79** | −13.0 | 7 / 4 | 5 / 5 | 88.0 | 86.8 | −1.2 | 61.1 | 75.7 |
| 66 (2024-07-05) | 80.74 | **73.91** | −6.8 | 7 / 4 | 8 / 4 | 37.2 | **8.9** | −28.3 | 44.6 | 47.4 |
| 23 (2024-05-23) | 61.90 | 72.56 | **+10.7** | 4 / 4 | 5 / 3 | 181.1 | 198.0 | +16.9 | 63.4 | 56.7 |
| 8 (2024-05-08) | 38.38 | 19.10 | −19.3 | 3 / 2 | 2 / 1 | 111.8 | 111.8 | 0.0 | 55.0 | 61.4 |
| 30 (2024-05-30) | 39.43 | 39.43 | 0.0 | 4 / 2 | 4 / 2 | 101.6 | 101.6 | 0.0 | 62.1 | 62.1 |
| **Sum** | **388.5** | **332.0** | **−56.6 (−14.6%)** | 31 / 19 | 28 / 18 | **666.8** | **599.1** | **−67.7 (−10.2%)** | 320.2 | 340.4 |

Unmet is the executor's cumulative unmet (demand − served), as recorded in the trace.

Diesel charging and same-hour-discharge curtailment:

| Origin | Step-0 plan diesel, base → ablated (kW) | Step-0 plan charge, base → ablated (kW) | Diesel-charge planned, t0 steps (base → abl) | Same-hour-discharge curtail (kWh), base → abl |
|---|---|---|---|---|
| 77 | 44.6 → **44.6** (no change) | 40.0 → **40.0** | 6 → 4 | 124.6 → 91.9 |
| 56 | 44.5 → **54.6** (rises) | 39.9 → **50.0** | 7 → 5 | 88.0 → 86.8 |
| 66 | 54.6 → **21.6** (falls) | 50.0 → 17.0 | 7 → 8 | 37.2 → 8.9 |
| 23 | 43.8 → **49.9** (rises) | 39.2 → 45.3 | 4 → 5 | 158.7 → 159.1 |
| 8 | 26.4 → **26.4** (no change) | 21.8 → 21.8 | 3 → 2 | 107.8 → 107.8 |
| 30 | 24.9 → **24.9** (no change) | 20.3 → 20.3 | 4 → 4 | 101.6 → 101.6 |

First dispatch divergence (step where decisions first differ, with the same physical state at that step):

| Origin | Base vs ablated first divergence (step) | Same state? |
|---|---|---|
| 77 | step 1 | yes |
| 56 | step 0 | yes |
| 66 | step 0 | yes |
| 23 | step 0 | yes |
| 8 | step 3 | yes |
| 30 | step 2 | yes |

Hourly diesel for the first eight steps (kW), base → ablated:
- 77: 44.6, 22.0, 0, 0, 0, 0, 0, 0 → 44.6, 10.8, 0, 0, 0, 0, 0, 0
- 56: 44.5, 0, 0, 0, 0, 0, 27.7, 55.9 → 54.6, 0, 0, 0, 0, 0, 0, 39.5
- 66: 54.6, 0, 0, 0, 0, 10.0, 10.0, 21.3 → 21.6, 23.8, 0, 0, 0, 10.0, 10.0, 18.8
- 23: 43.8, 0, 0, 0, 0, 0, 36.0, 0 → 49.9, 31.6, 0, 0, 0, 0, 0, 0
- 8: 26.4, 10.0, 0, … → unchanged
- 30: 24.9, 10.0, 0, … → unchanged

---

## 2. Did Removing Only the Terminal Target Remove the Early Diesel Charging?

**No.** Early diesel charging survives in every origin:
- In 77, 8, and 30 the step-0 diesel and charge are identical with and without the terminal target (44.6, 26.4, and 24.9 kW).
- In 56 and 23 the step-0 diesel rises when the terminal is removed (44.5 → 54.6 and 43.8 → 49.9 kW).
- In 66 it falls (54.6 → 21.6 kW), so the terminal target does drive part of the charging there.

**What does drive the early charging.** The EBR reserve envelope is tight at step 0 in every origin and in both arms, with or without the terminal target. Its minimum margin over hours 0–22 is 7.8 Wh (within SOC rounding) in all twelve cases. The reserve term is common to both arms, so it cannot explain the B−A gap by itself. What differs between arms is whether solar fills the reserve. In A the forecast surplus fills it, so no diesel is needed. In B the solar-poor forecast leaves diesel as the only source, so the reserve forces charging from diesel.

---

## 3. Terminal-Target Contribution (what it actually does)

Summed over the six origins, removing the terminal target:
- **Fuel:** −56.6 L (−14.6%). Concentrated in 77 (−28.1 L), 8 (−19.3 L), 56 (−13.0 L), 66 (−6.8 L). Origin 23 gets worse (+10.7 L). Origin 30 is unchanged.
- **Curtailment:** −67.7 kWh (−10.2%), of which −61.8 kWh is same-hour-discharge curtailment. Almost all of it is in 77 (−55.1 kWh) and 66 (−28.3 kWh). Origin 23 gets worse (+16.9 kWh).
- **Unmet:** +20.2 kWh (+6.3%). Removing the terminal target sheds more load in most origins (56 +14.6 kWh, 8 +6.4 kWh, 77 +3.2 kWh, 66 +2.7 kWh), at the cost of the fuel and curtailment savings. Origin 23 is the exception (−6.8 kWh).
- **Battery:** EFC −0.25 across the six. Terminal-tight steps fall from 3–20 per origin (base) to 0–2 (ablated), so the terminal constraint was tight in most steps, not just at step 0.

So the terminal target is a real contributor to fuel and curtailment in a subset of origins (mainly 77 and 66), with reliability traded against it. It is not the mechanism behind the early diesel charging in general.

---

## 4. Forecast-Shape Contribution

With the terminal removed, the solar-poor forecast still produces diesel charging in 77, 8, and 30 at identical step-0 values. The reserve envelope is tight in all arms, so the forecast determines whether solar can fill the reserve. That is the forecast-shape effect: B's forecast leaves the reserve dependent on diesel, while A's surplus forecast does not. Origin 30 has an accurate forecast and still charges from diesel at step 0 (24.9 kW), which shows the reserve constraint still needs diesel in some windows even when the day total is right.

Forecast shape is therefore the trigger. The reserve envelope converts it into early diesel. The terminal target adds to it in some origins but is not necessary for it.

---

## 5. Curtailment Mechanism

Same-hour-discharge curtailment is 93% of total curtailment in both base (617.9 of 666.8 kWh) and ablated (556.2 of 599.1 kWh) runs. The realization rule is unchanged, and it converts the planned discharge into curtailment whenever the sun arrives during a discharge hour. Removing the terminal target reduces it only where the plan stops discharging into a sunny hour (77, 66). Where the plan is unchanged (8, 30) or still discharges (56, 23), the curtailment stays.

---

## 6. Confidence and Caveats

- **Isolation:** strong. One consumer, asserted one-key config diff, exact baseline reproduction, and zero non-terminal mismatches in the checked fields.
- **Attribution:** moderate. The ablation shows what changes when the terminal is removed, not the full causal chain. The reserve-envelope attribution for early charging rests on tightness margins and the ablation result, not on removing the reserve term.
- **Sample:** six origins, selected for large gaps plus two controls. Not representative of the 123-origin campaign.
- **Invariant check** is partial (first hour and 24-hour sum per step), as described in §0.
- **Earlier report correction:** the hourly trace report (`HOURLY_TRACE_REPORT.md`) named the terminal target as the primary mechanism for the early diesel charging. This ablation does not support that. The terminal target is a real but partial contributor to fuel and curtailment. The reserve envelope, triggered by the solar-poor forecast shape, is the better-supported driver of the early charging. That report should be read with this correction.

---

VERDICT: Partly supported. The terminal target is a real contributor to fuel and curtailment in some origins, but it is not the primary cause of the early diesel charging. The early charging is driven by the EBR reserve envelope (tight at step 0 in every arm), triggered by B's solar-poor forecast shape.

TERMINAL-TARGET CONTRIBUTION: Removing only the terminal target cuts six-origin fuel by 56.6 L (−14.6%) and curtailment by 67.7 kWh (−10.2%), concentrated in origins 77 and 66. It does not remove early diesel charging, which survives unchanged in 77, 8, and 30 and rises in 56 and 23. Unmet load rises by 20.2 kWh, so the saving comes with reduced reliability in most origins.

FORECAST-SHAPE CONTRIBUTION: Primary trigger. B's solar-poor 24-hour forecast leaves the reserve envelope (tight in every arm) to be filled by diesel. A's surplus forecast fills it with solar. The shape persists after the terminal target is removed.

CURTAILMENT MECHANISM: Realization rule. Same-hour discharge accounts for 93% of curtailment in both runs. When the plan discharges into a sunny hour, the executor curtails the surplus rather than reducing the discharge. Removing the terminal target helps only where the plan stops discharging into the sun (77, 66).

CONFIDENCE: Moderate-high on the isolation and on the finding that the terminal target does not remove early charging (the step-0 values are identical in three origins). Moderate on the reserve-envelope attribution, which rests on tightness margins rather than a reserve-removal ablation. Six selected origins only.

NEXT SINGLE EXPERIMENT: Research-only diagnostic ablation on the same six origins, Arm B only, with the EBR reserve envelope (not the terminal) relaxed in the harness, to test whether removing the reserve constraint removes the early diesel charging. Diagnostic only, not a candidate policy or production change.
