# EBR Reserve-Envelope Ablation Report: Arm B, Six Traced Origins

**Experiment:** `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024` (frozen; not rerun or modified)
**Harness:** `FORENSIC_ANALYSIS/ebr_ablation.py` (research-only, isolated). Output: `FORENSIC_ANALYSIS/ebr_ablation/origin_{77,56,66,23,8,30}.json`, `summary.json`. The `EBR_OVERRIDE` hook was added to `trace_hourly.py` (margin reference only, default `None`).
**Date:** 2026-10-04

---

## 0. Isolation and Verification

**The one change.** `config["ebr_target_wh"] = 0.0`. The frozen config has no such key, so the baseline uses the governed 6-hour EBR formula.

**Why this isolates EBR.** In GAP19 (`gap19_highs_native.py` lines 113–151) the config key is the only consumer of the EBR list when no station-state override is set. The value becomes `ebr_target_wh_list = [0.0]*24`, which gives:
- `e_stage2_target[t] = 0` for hours 0–22. The reserve envelope `E_next[t] ≥ EBR[t] + min_e` reduces to the physical floor only.
- `e_stage2_target[23] = max(0, terminal_target_wh) = terminal_target_wh`. The **terminal target is preserved exactly** (100 kWh, so 140 kWh including `min_e`).

**Assertions checked in the harness:**
- The base and ablated configs differ in exactly one key, `ebr_target_wh`. Checked on every run.
- `terminal_target_wh` is 100000 in both configs.
- The baseline config has no `ebr_target_wh` key, so it runs the governed formula.

**Baseline reproduction (required first):** baseline Arm B reproduces the frozen per-origin fuel for all six origins (`frozen_B_reproduced = True` for all). For example, origin 56: 93.7559 L, matching the frozen value.

**Input invariance (0 mismatches over 6 origins × 24 steps):** forecast solar (t+1 and 24-hour sum), realized solar, critical demand, demand forecast, the terminal floor at t23 (`j2_target_t23_wh`, expected to stay at 140,000 Wh including `min_e`), origin and target timestamps, and the initial state (SOC 50%, 100 L, diesel off).

**Limits:** (a) the input check compares the first hour and the 24-hour solar sum per step, not every element of the 24-hour vectors. (b) The ablated EBR-target field is excluded from the invariance check by design, since it is the variable being ablated. (c) The margin fields in the ablated run are measured against `min_e` (since the EBR is zero), not against the formula.

---

## 1. Totals: Baseline B vs EBR-Removed B (six origins, sums)

| Metric | Baseline B | EBR-removed B | Δ | Δ % |
|---|---:|---:|---:|---:|
| Diesel fuel (L) | 388.5 | **94.4** | −294.2 | **−75.7%** |
| Diesel on-hours | 31 | 6 | −25 | −80.6% |
| Diesel startups | 19 | 4 | −15 | −78.9% |
| Diesel energy (kWh) | 934.1 | 257.4 | −676.6 | −72.4% |
| Diesel-to-battery (proxy, kWh) | 633.1 | 183.2 | −450.0 | −71.1% |
| Battery charge (kWh) | 909.3 | 639.3 | −270.0 | −29.7% |
| Battery discharge (kWh) | 421.8 | 511.3 | +89.5 | +21.2% |
| Unmet, as recorded (kWh) | 320.2 | **415.1** | **+94.9** | **+29.6%** |
| Curtailment (kWh) | 666.8 | 444.5 | −222.3 | −33.3% |
| Same-hour-discharge curtailment (kWh) | 617.9 | 441.5 | −176.4 | −28.5% |
| Steps with step-0 diesel charging | 31 | 6 | −25 | −80.6% |

Per-origin fuel, base → ablated (L): 77: 74.3 → 16.9; 56: 93.8 → 61.6; 66: 80.7 → 15.9; 23: 61.9 → 0.0; 8: 38.4 → 0.0; 30: 39.4 → 0.0.

---

## 2. Did EBR removal eliminate the early diesel commitment?

**Yes, at the decision point, in all six origins.** At step 0 the planned diesel is:

| Origin | Base step-0 diesel (kW) | Ablated step-0 diesel (kW) | Base step-0 charge (kW) | Ablated step-0 charge (kW) |
|---|---:|---:|---:|---:|
| 77 | 44.6 | **0.0** | 40.0 | 0.0 |
| 56 | 44.5 | **0.0** | 39.9 | 0.0 |
| 66 | 54.6 | **0.0** | 50.0 | 0.0 |
| 23 | 43.8 | **0.0** | 39.2 | 0.0 |
| 8 | 26.4 | **0.0** | 21.8 | 0.0 |
| 30 | 24.9 | **0.0** | 20.3 | 0.0 |

Diesel charging steps (step 0) fall from 31 to 6 across the six origins. In the ablated run, diesel is almost entirely absent: 6 on-hours in total, against 31 in the baseline.

**First dispatch divergence:** step 0 in all six origins. The physical state is identical at that step (SOC 50%, 100 L, diesel off), so the divergence is in the decision alone, and it comes from the EBR term.

Diesel that remains in the ablated run is limited to a few hours per origin (on-hours 0–8 per origin, see `ebr_ablation/origin_*.json` for the hour-by-hour values).

---

## 3. The Reduction Comes at a Reliability Cost

**Unmet load rises in every origin** (sum +94.9 kWh, +29.6%):

| Origin | Base unmet (kWh) | Ablated unmet (kWh) | Δ (kWh) |
|---|---:|---:|---:|
| 77 | 33.9 | 52.1 | +18.1 |
| 56 | 61.1 | 79.9 | +18.9 |
| 66 | 44.6 | 82.8 | +38.1 |
| 23 | 63.4 | 77.3 | +13.8 |
| 8 | 55.0 | 57.0 | +2.0 |
| 30 | 62.1 | 66.0 | +3.9 |

The planned critical-load shortfall (J1) is **zero at every reoptimization in both arms**, and so is the reserve/terminal shortfall (J2 and terminal). So the planner still protects the critical load in its plan. The increase is in the executor's recorded unmet, which is demand minus served. Because non-critical shortfall carries no objective penalty (`p_unmet` is not in J1), the extra unmet is most likely non-critical load shed to save diesel. **I did not verify this split:** the trace records the executor's total unmet, not the critical part of realized unmet, so the claim is inferred from the zero planned J1 and the GAP19 objective structure, not measured.

**SOC:** the reserve floor is gone, as expected. Minimum SOC falls to 22.6–34% (ablated minimum across six: 22.62%, no origin below the 20% floor). Baseline minimum SOC was 56.8–63% in these origins.

**Terminal target:** the planned terminal target (140 kWh at t+24) is met in every reoptimization: planned terminal shortfall is zero in both arms. The **realized** SOC at hour 24 is lower in the ablated run (32–62% vs 72–90% baseline). This is expected, not a failure: the terminal target is re-planned every hour, so the realized hour-24 SOC is not the planned t+24 value. The terminal constraint is not violated in the plan, but the realized battery ends lower.

**Constraints that do bind after removal:** the terminal floor (tight in 9–20 steps per origin, against 3–20 in the baseline) and the SOC floor (realized minimum 22.6%, close but not violated). The planner uses the battery to serve load and holds the terminal, which lowers realized SOC.

**Against the frozen reliability gate:** unmet must not exceed the baseline (preregistration §9). The ablated run exceeds it in all six origins. The ablation is a diagnostic, not a candidate, so this result is recorded, not acted on.

---

## 4. Forecast-Shape Contribution

With EBR removed, the solar-poor forecast no longer produces diesel commitment at step 0 in any origin. Diesel-to-battery drops 71%. So the forecast shape is **not sufficient** to force diesel. The EBR reserve is what converts a solar-poor forecast into diesel.

The forecast shape still matters, but its effect moves into the battery and unmet load instead: the planner covers the solar-poor window with stored energy, and the cost appears as lower SOC and more unmet load rather than as fuel.

In origin 30, the forecast was accurate. Its base step-0 diesel (24.9 kW) falls to zero in the ablation as well, so the EBR reserve drives the diesel there too, even without a forecast error.

---

## 5. Curtailment

Curtailment falls 33% overall (−222 kWh), and same-hour-discharge curtailment falls 28%. The cause is the same as before: when the plan discharges into a sunny hour, the executor curtails the surplus (§5 of the terminal ablation). With less diesel, the surplus is smaller, but the realization rule is unchanged, so same-hour-discharge still makes up 99% of curtailment in the ablated run (441.5 of 444.5 kWh).

---

## 6. Confidence and Caveats

- **Isolation:** strong. One consumer, asserted single-key config diff, exact baseline reproduction, and zero input mismatches.
- **Diesel elimination:** strong at the decision point (step 0 is zero in all six, and the state is identical). Fuel totals are strong in these six origins.
- **Reliability cost:** measured as recorded unmet. The critical/non-critical split is inferred, not measured (§3).
- **Sample:** six origins, selected for large gaps plus two controls. The 123-origin campaign is not covered.
- **Interpretation:** the ablation shows what changes when the reserve is removed, not the whole causal chain. The reserve is the constraint that forces diesel in this solar-poor setting, but a cheaper reserve would be a different controller, which this report does not propose.

---

VERDICT: The EBR reserve envelope is the dominant driver of the early diesel commitment. Removing it alone eliminates step-0 diesel in all six origins and cuts six-origin fuel by 75.7%. The cost is more unmet load (+29.6%) and lower SOC, not terminal failure.

EBR CONTRIBUTION: Primary. Step-0 diesel is zero in all six origins once EBR is removed (base: 24.9–54.6 kW). Diesel on-hours fall from 31 to 6, and fuel from 388.5 L to 94.4 L. The terminal target is still held in the plan, so the reduction is attributable to the reserve envelope alone.

FORECAST-SHAPE CONTRIBUTION: Necessary but not sufficient. The solar-poor forecast no longer produces diesel commitment once EBR is removed, so the reserve is what turns the forecast shape into diesel. Its effect moves into battery use and unmet load instead.

RELIABILITY TRADEOFF: Real. Recorded unmet rises in all six origins (+94.9 kWh, +29.6%), and minimum SOC falls to 22.6–34% (no floor violation). The planned critical load is still protected (planned J1 = 0), so the extra unmet is most likely non-critical shedding, but that split is not measured. The ablated run fails the frozen unmet gate in all six origins.

CONFIDENCE: High on the isolation, on the step-0 diesel elimination, and on the fuel and unmet totals within these six origins. Moderate on the critical/non-critical split, which is inferred from the planned J1 values and the objective structure. Six selected origins only.

NEXT SINGLE EXPERIMENT: Research-only diagnostic on all 123 origins, Arm B only, with the EBR reserve envelope removed (same harness, same config change) and with realized unmet split into critical and non-critical components, so the reliability tradeoff can be attributed to the load class. Diagnostic only; no replacement controller and no production change.
