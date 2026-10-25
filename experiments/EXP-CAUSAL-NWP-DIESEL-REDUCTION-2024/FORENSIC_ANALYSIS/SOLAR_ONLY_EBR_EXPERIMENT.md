# Solar-Only Critical-Aware EBR Diagnostic: Six Origins

**Status:** research-only. Frozen campaign, frozen artifacts, GAP19, and production configs are untouched. No tuning.
**Harness:** `FORENSIC_ANALYSIS/solar_only_ebr_experiment.py` (imports the previous critical-aware harness and swaps only the reserve formula). Output: `FORENSIC_ANALYSIS/solar_only_ebr/origin_NN.json` (hourly logs), `all_results.json`.
**Origins:** 77, 56, 66, 23, 8, 30.

---

## 0. Formula, Isolation, and Pre-Run Checks

**Solar-only reserve (research wrapper, GAP19 unchanged):**

`EBR_so[t] = (1/η) × Σ_{k=t}^{min(t+5,23)} max(0, crit[k] − solar_gen[k]) × dt`

Units: `crit` and `solar_gen` in W, `dt` = 1 h, `η = 0.92`, so the output is in Wh. The `max(0, ·)` keeps it non-negative.

**Isolation.** Versus the wind-including arm, only the subtracted term changes (wind removed). The same wrapper, config path (24-element `ebr_target_wh` list), terminal target (100,000 Wh), `min_e` floor, executor, and forecasts are used.

**Pre-run checks (passed before the run):**
1. With zero solar, the solar-only reserve equals the governed GAP19 formula.
2. The solar-only reserve does not depend on wind (identical results with and without a wind input).
3. The solar-only reserve is at least as large as the wind-including reserve for the same inputs.
4. Non-negativity holds.

**Frozen Arm B reproduction:** all six origins reproduce the frozen fuel, unmet, curtailment, and served load (`frozen_B_reproduced = True` for all six).

**Consistency with the previous run:** the wind-including arm reproduces the previous critical-aware results exactly (fuel 256.96 L, critical reliability 94.60%), so the rerun is deterministic.

---

## 1. Results, Six Origins

| Metric | A: frozen B | W: critical-aware (solar + wind) | S: solar-only |
|---|---:|---:|---:|
| Total fuel (L) | 388.5 | 257.0 | **252.6** |
| Diesel-on hours | 31 | 18 | 18 |
| Startups | 19 | 9 | 11 |
| Curtailment (kWh) | 666.8 | 578.8 | **552.0** |
| Total unmet (kWh) | 320.2 | 359.0 | 345.6 |
| Critical unmet (kWh) | 82.6 | 90.2 | 87.5 |
| **Critical reliability** | **95.06%** | 94.60% | **94.76%** |
| Total reliability | 85.18% | 83.38% | 84.00% |
| Minimum SOC | 56.77% | 23.70% | 23.70% |
| Maximum SOC | 95.00% | 94.04% | 95.00% |
| SOC-floor violations | 0 | 0 | 0 |
| Planned terminal shortfall steps | 0 | 0 | 0 |
| Optimizer failures | 0 | 0 | 0 |

**Per origin (fuel in L; critical unmet in kWh; curtailment in kWh):**

| Origin | Fuel A / W / S (L) | Critical unmet A / W / S (kWh) | Curtailment A / W / S (kWh) | Min SOC S (%) |
|---|---|---|---|---:|
| 77 | 74.3 / 60.6 / 58.3 | 4.6 / 3.8 / 3.4 | 147.1 / 167.6 / 142.6 | 46.56 |
| 56 | 93.8 / 94.9 / 93.1 | 16.3 / 18.1 / 15.9 | 88.0 / 120.4 / 115.5 | 62.18 |
| 66 | 80.7 / 28.9 / 36.1 | 8.3 / 18.5 / 16.8 | 37.2 / 14.9 / 19.3 | 36.13 |
| 23 | 61.9 / 56.2 / 45.4 | 16.1 / 13.1 / 17.4 | 181.1 / 146.0 / 145.4 | 53.44 |
| 8 | 38.4 / 16.4 / 19.7 | 14.7 / 13.3 / 12.6 | 111.8 / 71.6 / 73.9 | 27.77 |
| 30 | 39.4 / 0.0 / 0.0 | 22.6 / 23.5 / 21.4 | 101.6 / 58.2 / 55.3 | 23.70 |

---|---|---|---|---:|
| 77 | 74.3 / 60.6 / 58.3 | 4.6 / 3.8 / 3.4 | 147.1 → 142.6 (W) → — | 46.56 |
| 56 | 93.8 / 94.9 / 93.1 | 16.3 / 18.1 / 15.9 | 88.0 → 115.5 (W) → — | 62.18 |
| 66 | 80.7 / 28.9 / 36.1 | 8.3 / 18.5 / 16.8 | 37.2 → 19.3 | 36.13 |
| 23 | 61.9 / 56.2 / 45.4 | 16.1 / 13.1 / 17.4 | 181.1 → 145.4 | 53.44 |
| 8 | 38.4 / 16.4 / 19.7 | 14.7 / 13.3 / 12.6 | 111.8 → 73.9 | 27.77 |
| 30 | 39.4 / 0.0 / 0.0 | 22.6 / 23.5 / 21.4 | 101.6 → 55.3 | 23.70 |

---

## 2. Pre-Registered Decision

**Rule:** C (solar-only) passes only if it reduces fuel versus A **and** critical reliability is no worse than A.

- **Fuel:** reduced by 135.9 L (−35.0%), from 388.5 L to 252.6 L. Condition met.
- **Critical reliability:** 95.06% → 94.76%, a fall of **0.29 percentage points**. Condition **not** met.

**Decision: FAIL.**

---

## 3. What the Solar-Only Variant Changes Relative to the Wind-Including Arm

- **Fuel is slightly lower** (252.6 vs 257.0 L). Diesel-on hours are unchanged (18), with startups slightly higher (11 vs 9).
- **Critical reliability is slightly better** (94.76% vs 94.60%). Critical unmet falls from 90.2 to 87.5 kWh, which is 2.7 kWh less.
- **Curtailment is lower** (552.0 vs 578.8 kWh, −4.6%) and about 17% below frozen B.
- **Critical unmet is still higher than frozen B** (87.5 vs 82.6 kWh, +4.9 kWh). Critical reliability is still below frozen B, so the rule still fails.

Removing the wind term recovers part of the critical reliability cost but not all of it, and it keeps most of the fuel saving. Origin 66 illustrates this: critical unmet falls from 18.5 to 16.8 kWh with the solar-only reserve, but is still double the frozen 8.3 kWh.

---

## 4. Mechanism (Consistent With the Failure Review)

- The reserve is no longer released by forecast wind, so it is held through the night hours where forecast wind had previously released it.
- Fuel stays low for the same reason as the wind-including arm: the reserve is smaller where forecast solar covers the load (the daytime hours), and diesel-on hours (18) are unchanged.
- Critical unmet remains above frozen B. This is consistent with the failure-review finding that the shortfall comes at night, when forecast solar is near zero. A solar-only reserve is then close to the full governed reserve at those hours, so it is no longer the failure driver, but the remaining shortfall is still not eliminated.
- Min SOC is 23.7% (above the 20% floor). Zero floor violations.

---

## 5. Caveats

1. **Six origins only, fixed in advance.** The sample cannot establish behaviour over the 123-origin campaign.
2. **Critical convention.** The reliability comparison uses the `min(11.6 kW, realized demand)` convention fixed before the earlier diagnostic. The planner-convention question is still open, and the pass/fail decision depends on it.
3. **Synthetic wind.** The wind benchmark is a formula (see the wind-error analysis). The fuel and reliability effects of removing wind from the reserve are specific to this benchmark.
4. **No tuning.** The formula is as stated in §0, and it was not changed after seeing results.

---

VERDICT: FAIL under the pre-registered rule. The solar-only variant reduces fuel more than the wind-including arm (−135.9 L vs frozen B) and reduces curtailment, but critical reliability still falls 0.29 pp versus frozen B. Removing wind from the reserve recovers part of the reliability cost but not all of it.

FUEL_CHANGE: 388.5 → 252.6 L (−135.9 L, −35.0%). Diesel-on hours 31 → 18. Startups 19 → 11.

CRITICAL_RELIABILITY_CHANGE: 95.06% → 94.76% (−0.29 pp). Critical unmet 82.6 → 87.5 kWh (+4.9 kWh). Better than the wind-including arm (94.60%), but still below frozen B.

CURTAILMENT_CHANGE: 666.8 → 552.0 kWh (−114.8 kWh, −17.2%). Lower than the wind-including arm (578.8 kWh).

NEXT_SINGLE_EXPERIMENT: Re-run the six-origin solar-only arm (arm S only) under the planner's forecast-based critical convention, with the reserve otherwise unchanged. This tests whether the residual critical-reliability shortfall (−0.29 pp) survives the convention that is still unresolved. It is a convention check, not a tuning step, and needs approval because it requires new dispatch solves.
