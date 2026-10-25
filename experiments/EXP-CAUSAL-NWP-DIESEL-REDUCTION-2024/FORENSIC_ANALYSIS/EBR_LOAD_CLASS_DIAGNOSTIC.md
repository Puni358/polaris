# EBR Load-Class Diagnostic: Arm B, 123 Origins

**Status:** DIAGNOSTIC. Research-layer realized load-class definition. These are **not** frozen campaign results and must not be reported as such.
**Experiment:** `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024` (frozen; not rerun or modified)
**Harness:** `FORENSIC_ANALYSIS/ebr_loadclass_123.py`. Per-origin output: `FORENSIC_ANALYSIS/ebr_loadclass_123/origin_NNN.json`; combined: `all_results.json`; log: `ebr_loadclass_123_run.log`.
**Date:** 2026-10-04

---

## 0. Definition, Why It Does Not Change Dynamics, and Verification

**Load-class definition (research layer only):**
- `critical_realized = min(11,600 W, realized_total_demand)` per hour. The non-critical part is the remainder, `realized_demand − critical_realized`.
- When supply is insufficient, critical load is served first, then non-critical load.

**Why this is exact and does not alter the dispatch.** The executor's battery, diesel, curtailment, and SOC updates depend only on total supply (solar + wind + diesel + battery discharge) and total demand. They do not depend on how served load is split. The critical-first split therefore allocates the same total served energy. Fuel, SOC, startups, curtailment, and total unmet are identical to the frozen dynamics. Only the critical / non-critical split of unmet is new. The split is computed from the recorded per-hour realized quantities. No production code was changed.

**Verification (the required gate):**
- **Arm A reproduces the frozen Arm B totals in 123 / 123 origins** (fuel, total unmet, curtailment, served load).
- **The split reconciles with the executor:** the critical-first served total equals the executor's served load in every hour, with a maximum absolute residual of 0.04 Wh.
- **Zero optimizer failures and zero safety exceptions** in both arms across all 123 origins.

**Important finding from the verification:** the frozen field `unmet_critical_load_wh` equals the **total** unmet (demand − served) for all 123 origins. It is not critical-only. The frozen label is misleading, and this is now confirmed from the reproduction, not inferred.

---

## 1. Results, 123 Origins (Arm A = frozen Arm B, Arm B = EBR removed)

| Metric | A: frozen Arm B | B: EBR removed | Δ (B − A) | Δ % |
|---|---:|---:|---:|---:|
| Diesel fuel (L) | 6,603.98 | 2,084.78 | −4,519.2 | −68.4% |
| Diesel-on hours | 484 | 129 | −355 | −73.3% |
| Startups | 324 | 72 | −252 | −77.8% |
| Curtailment (kWh) | 9,477.7 | 6,771.4 | −2,706.3 | −28.6% |
| Total unmet (kWh) | 7,844.4 | 9,172.7 | +1,328.2 | +16.9% |
| Total served (kWh) | 36,435.6 | 35,107.3 | −1,328.2 | −3.6% |

**Load-class split (kWh):**

| Class | Demand | A served | B served | A unmet | B unmet | Δ unmet |
|---|---:|---:|---:|---:|---:|---:|
| Critical (min(11.6 kW, demand)) | 34,243.2 | 32,007.2 | 31,912.7 | 2,236.0 | 2,330.5 | **+94.5** (+4.2%) |
| Non-critical (remainder) | 10,036.8 | 4,428.4 | 3,194.6 | 5,608.4 | 6,842.2 | **+1,233.7** (+22.0%) |
| Total | 44,280.0 | 36,435.6 | 35,107.3 | 7,844.4 | 9,172.7 | **+1,328.2** (+16.9%) |

**Reliability:**

| Reliability | A | B | Δ (pp) |
|---|---:|---:|---:|
| Critical | 93.47% | 93.19% | −0.28 |
| Non-critical | 44.12% | 31.83% | −12.29 |
| Total | 82.29% | 79.29% | −3.00 |

**SOC and safety:**
- Minimum SOC: A 54.97%, B 20.00% (at the floor, not below it). Maximum SOC: 95.0% in both.
- SOC-floor violations (below 19.999%): 0 in both arms. Ceiling violations: 0 in both.
- Optimizer failures: 0 in both arms.

**Origin-level direction:**
- Critical unmet rises in 77 origins and falls in 35.
- Non-critical unmet rises in 102 origins and falls in 21.
- Critical unmet is above zero in all 123 origins in both arms. Realized critical load is not fully served even in the frozen baseline, though the planned critical deficit is zero (see §4).

---

## 2. Most Important Result: Critical or Non-Critical Load?

**EBR removal sacrifices primarily non-critical load.**
- Of the +1,328 kWh increase in total unmet, **+1,234 kWh (about 93%) is non-critical**, and **+94.5 kWh (about 7%) is critical**.
- Critical reliability moves only −0.28 pp (93.47% → 93.19%). Non-critical reliability falls −12.3 pp (44.1% → 31.8%).
- The critical-load reliability cost is small in absolute terms (+94.5 kWh over 123 origins, about 0.8 kWh per origin).

This confirms the earlier inference from the objective structure, which had said the cost was most likely non-critical shedding. It is now measured, under the research-layer definition, and it is consistent with the frozen planner: the planned critical deficit (J1) is zero in both arms, and non-critical shortfall carries no objective penalty.

---

## 3. Fuel, Curtailment, and the Price Paid

- **EBR fuel cost:** EBR removal lowers fuel by 4,519 L (−68.4%). Diesel-on hours fall 73% and startups fall 78%.
- **Curtailment benefit:** −2,706 kWh (−28.6%). The same-hour-discharge mechanism from earlier ablations remains the cause of the remaining curtailment.
- **What the fuel saving costs:** about 1,328 kWh of additional total unmet, of which about 1,234 kWh is non-critical and about 95 kWh is critical.

---

## 4. Critical Unmet Is Not Zero Even in the Frozen Baseline

The planned critical deficit (J1) is zero at every reoptimization in both arms, yet realized critical unmet is above zero in all 123 origins in both arms (A: 2,236 kWh total). The critical shortfall is therefore a realization effect, not a planned one. It comes from the gap between the forecast and realized supply, which the planner cannot cover after the fact in the hour it occurs. This is a property of the frozen dynamics and is the same in both arms. It is not created by EBR removal, which adds only 94.5 kWh.

---

## 5. Caveats

1. **Research-layer definition, not frozen.** The critical-first split is an accounting definition applied to frozen dynamics. It changes the reliability labelling, not the dispatch. Results must not be presented as frozen campaign results.
2. **Dispatch invariance is argued from the code and checked by reproduction.** The reproduction of the fuel, unmet, curtailment, and served totals in 123 / 123 origins supports it. I did not separately compare hourly dispatch between this run and the earlier EBR-OFF run, though the totals match the earlier run to rounding.
3. **Dependence on the 11.6 kW convention.** The critical share depends on the governed 11.6 kW ceiling applied to realized demand. A different critical definition would change the split, not the totals.
4. **EBR-OFF is a diagnostic.** It fails the frozen reliability gate and is not a candidate controller.

---

VERDICT: EBR removal sacrifices primarily non-critical load. Of the +1,328 kWh increase in total unmet, about 93% is non-critical and about 7% is critical. Critical reliability moves only −0.28 pp, while non-critical reliability falls −12.3 pp.

EBR FUEL COST: EBR removal is what drives the fuel benefit, not a cost. Fuel falls 4,519 L (−68.4%), diesel-on hours fall 73%, and startups fall 78%. In this sense EBR is the source of most of the diesel use in Arm B.

CRITICAL-LOAD COST: Small. Critical unmet rises by 94.5 kWh (+4.2%), which is about 0.8 kWh per origin. Critical reliability falls 93.47% → 93.19%. Critical unmet is above zero in every origin in both arms, so most of it is a realization effect present in the frozen baseline too.

NONCRITICAL-LOAD COST: Large. Non-critical unmet rises by 1,234 kWh (+22%). Non-critical reliability falls from 44.1% to 31.8%. This accounts for about 93% of the total reliability cost.

CURTAILMENT BENEFIT: −2,706 kWh (−28.6%). The remaining curtailment is 95% same-hour-discharge, following the realization-rule mechanism from earlier ablations.

RELIABILITY TRADEOFF: Total reliability falls 82.29% → 79.29% (−3.0 pp). Almost all of that is non-critical load. The planned critical load is still protected in the plan (J1 = 0). The frozen label `unmet_critical_load_wh` is in fact total unmet, so earlier reliability statements that treated it as critical should be read with that correction.

CONFIDENCE: High on the split arithmetic, the 123 / 123 reproduction, and the non-critical concentration (93%), because they come from recorded per-hour quantities and reconcile with the executor to 0.04 Wh. Moderate on how the cost should be interpreted, since it depends on the research-layer definition of critical load (min(11.6 kW, realized demand)). Results apply to Arm B only.

NEXT SINGLE EXPERIMENT: Research-only sensitivity of the load-class split to the critical definition: rerun the same 123-origin Arm A / Arm B comparison with the critical ceiling set to 11.6 kW against the forecast-demand ceiling rule used in the frozen planner (critical = min(11.6 kW, forecast demand) applied to realized outcomes), to check whether the 93% non-critical attribution holds under the planner's own critical convention. Diagnostic only; no replacement controller and no production change.
