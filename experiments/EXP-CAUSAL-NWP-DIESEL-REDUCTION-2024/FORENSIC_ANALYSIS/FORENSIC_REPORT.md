# Forensic Report: Why Arm B (Causal MEPS NWP + Physics) Burned More Diesel Than Arm A

**Experiment:** `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024` (frozen; results treated as authoritative, not rerun, not modified)
**Scope:** Forensic explanation of the frozen result only. No code changed, no experiment rerun, no tuning, no preregistration reinterpretation.
**Date:** 2026-10-04

---

## 0. Scope and Evidence Limits (read first)

- The campaign has **no hour-level records** of forecast solar, realized solar, or planned dispatch. `incremental_results.jsonl` contains the same 123 per-origin aggregates as `per_origin_results.json`. The realized SITES `SW_IN` series is not in any artifact.
- Consequence: **forecast error vs. actual solar (Q1) and the exact first A/B dispatch divergence (Q2) cannot be measured from these artifacts.** Below, I state what is measurable and what the artifacts cannot settle.
- Derived quantities (energy decompositions, correlations, the reserve-target check) are computed from the frozen per-origin and aggregate numbers using the executor's own equations.
- Files read beyond the requested list, for disclosure: `incremental_results.jsonl` (structure only), `accounting_audit.json`, `failure_audit.json`, `final_execution_manifest.json`, `output_hashes.json`, first 30 lines of `execution_log.txt`. Not opened: `system/control/router.py`, `run_diesel_reduction_campaign.py`, the YAML configs (values taken from the preregistration/manifest instead). The campaign script's mapping of `unmet_critical_load_wh` is therefore unverified (see §7).
- Full `per_origin_results.json` was read in part for display; all aggregate statistics below were computed over all 123 origins with read-only scripts.
- Solar elevation values in §3 come from an approximate NOAA-style solar-position formula, not pvlib.

---

## 1. Headline Numbers (frozen results)

| Metric | Arm A (Baseline) | Arm B (Candidate) | Arm C (Perfect foresight) | B − A |
|---|---:|---:|---:|---:|
| Diesel fuel (L) | 5,478.31 | **6,603.98** | 4,954.77 | **+1,125.67 (+20.5%)** |
| Diesel on-hours | 441 | 484 | 427 | +43 |
| Diesel startups | 367 | 324 | 279 | −43 |
| Served load (MWh) | 35.23 | 36.44 | 35.67 | +1.21 |
| Unmet, as labelled (MWh) | 9.05 | 7.84 | 8.61 | −1.21 |
| **Curtailment (MWh)** | 7.26 | **9.48** | 5.53 | **+2.22** |
| Battery throughput (MWh) | 23.63 | 26.67 | 23.09 | +3.04 |
| EFC | 59.07 | 66.68 | 57.73 | +7.61 |
| Min SOC observed (%) | 57.83 | 54.97 | 54.93 | −2.86 |
| Origins with zero curtailment | 22 | **1** | 27 | |
| Floor violations / optimizer failures | 0 / 0 | 0 / 0 | 0 / 0 | |

Paired per-origin result (A−B convention, negative = B worse), from `statistical_results.json`:
- B used more fuel in **87 / 123** origins, less in **36**, tie **0**.
- Mean Δ = −9.15 L/origin; median Δ = −8.44 L/origin; bootstrap 95% CI on mean = [−12.04, −6.38] L.
- Wilcoxon two-sided p = 4.2×10⁻⁸; one-sided "A > B" p ≈ 1.0. The result is a strong, consistent B penalty, not noise.

Accounting integrity is clean: max busbar residual 0.0 W, 0 floor violations, 0 optimizer failures (`accounting_audit.json`, `causality_audit.json`). **The result is internally consistent; the question is mechanism.**

---

## 2. Q3 — Why B Runs More Diesel: Decomposition

The executor realizes diesel as `fuel_L/h = base_fuel_lph + marginal_fuel_lpwh × P_diesel_W` per on-hour, with `base = 5.0 L/h`, `marginal = 0.00025 L/Wh` (manifest `governed_parameters`). **Startup fuel is not charged at realization.** A grep of `research_realization_executor.py` finds no `startup` term, although GAP19 charges `startup_fuel_l` (default 2.0 L) per start in its objective J3.

This gives an exact aggregate identity:

`Fuel = 5 × on-hours + 0.00025 × Σ P_diesel(Wh)`

| | On-hours | Base term (L) | Diesel energy (MWh) | Energy term (L) | Mean P per on-hour (kW) |
|---|---:|---:|---:|---:|---:|
| A | 441 | 2,205 | 13.09 | 3,273 | 29.7 |
| B | 484 | 2,420 | **16.74** | 4,184 | **34.6** |
| C | 427 | 2,135 | 11.28 | 2,820 | 26.4 |

**Decomposition of B − A (1,125.7 L):**
- Run-hour (base) term: 5 × 43 h = **215 L (19%)**
- Diesel-energy term: 0.00025 × 3.65 MWh = **912 L (81%)**

So the penalty is mostly **more diesel energy per run-hour**, not more run-hours. B runs fewer starts (324 vs 367) but longer and at higher average power.

**Where did B's extra diesel energy go?** Solar, wind, demand are identical realized inputs across arms, so the busbar identity must balance across arms:

`ΔDiesel_E = Δserved + Δcurtailment + Δ(charge − discharge)`

`3.65 = 1.21 + 2.22 + 0.23 MWh`

- **61% of B's extra diesel energy was curtailed** (2.22 of 3.65 MWh).
- **33% served additional load** (1.21 MWh), which is exactly the unmet reduction.
- Net battery change is only +0.23 MWh.

Served-load efficiency: A = 0.155 L/kWh served, B = 0.181 L/kWh, C = 0.139 L/kWh. **B spends more fuel per delivered kWh, and much of it is wasted.**

---

## 3. Q5 — Battery / SOC Behavior

- **The battery is pinned at a reserve floor, not cycled for dispatch.** Arm A's minimum SOC is **57.83% in every origin** (all 123 values identical). This matches the governed 6-hour reserve target exactly:
  `(40,000 Wh + 6 × 11,600 W / 0.92) / 200,000 Wh = 57.83%`
  (`GAP19` lines 111–131 and 304: `E_next[t] + s_J2[t] ≥ EBR[t] + min_e`).
- B's minimum SOC is lower (54.97%, below 57.83% in 29 origins). Those cases are where forecast total demand is below 11.6 kW, which reduces the clipped critical-load window. This is a demand-forecast effect that applies to all arms, not a B-specific battery failure.
- **Battery is not binding on floor (20%) or ceiling (95%).** Neither arm approaches either bound.
- **B cycles the battery more:** +3.04 MWh throughput and +7.6 EFC. Throughput rises with curtailment (cross-origin r = 0.50), consistent with the battery being used in hours where surplus is then wasted (see §5).

**Battery is not the primary bottleneck.** It acts as a reserve, and the reserve rule is what couples the battery to diesel (§5).

---

## 4. Q4 — Why B Has +2.22 MWh More Curtailment

Curtailment in the executor (`research_realization_executor.py` lines 210–223) happens in exactly two cases:
1. A discharge is realized in the same hour (`p_dis_realized > 1e-4`), so surplus cannot be charged and is curtailed in full, or
2. The charge cap is hit (`min(50 kW, energy room / η_chg)`).

Diesel is realized at the planned value, with no down-modulation to realized need. So **any diesel committed in the plan becomes surplus if realized supply exceeds demand, and that surplus is curtailed whenever a discharge is also realized in the hour.**

Evidence from the frozen aggregates:
- Across origins, Δfuel vs Δcurtailment: **r = 0.75**. Δfuel vs Δdiesel-hours: r = 0.76. Δfuel vs Δstartups: r = 0.69. Δfuel vs Δunmet: r = −0.65.
- Curtailment is nearly universal in B: **only 1 origin of 123 has zero curtailment**, against 22 for A and 27 for C. Curtailment is structural in B's dispatch.
- The perfect-foresight arm C has **less** curtailment than A (5.53 vs 7.26 MWh). So the curtailment excess is **specific to B's forecast**, not a property of the controller alone (same GAP19, same executor).

Concrete origins (values are per-origin, from `per_origin_results.json`):

| Origin (t0) | Fuel A → B (L) | On-hrs A → B | Starts A → B | Curtail A → B (kWh) | Throughput A → B (kWh) | Min SOC A → B |
|---|---|---|---|---|---|---|
| 56 (2024-06-25) | 41.53 → **93.76** | 3 → 7 | 3 → 4 | 15.3 → **88.0** | 177.1 → 212.3 | 57.83 → 62.95 |
| 66 (2024-07-05) | 37.58 → **80.74** | 3 → 7 | 3 → 4 | 0.0 → **37.2** | 151.6 → 231.9 | 57.83 → 57.83 |
| 77 (2024-07-16) | 21.85 → **74.32** | 2 → 6 | 2 → 3 | 54.4 → **147.1** | 201.6 → 224.9 | 57.83 → 62.56 |
| 111 (2024-08-19) | 38.19 → **73.88** | 3 → 5 | 3 → 3 | 0.0 → **43.1** | 149.6 → 243.3 | 57.83 → 67.61 |
| 40 (2024-06-09) | **48.20 → 18.19** | 4 → 2 | 3 → 1 | 97.2 → 57.1 | 236.8 → 188.9 | 57.83 → 56.14 |
| 118 (2024-08-26) | **54.64 → 36.56** | 5 → 2 | 3 → 2 | 20.9 → **0.0** | 120.8 → 159.5 | 57.83 → 67.28 |

Pattern: **B loses where it runs diesel and curtails** (56, 66, 77, 111). **B wins where it absorbs surplus into the battery and avoids curtailment** (40, 118). In origin 118, B curtails zero and throughput rises instead.

Origin 1 (2024-05-01), the first origin: A 56.89 L (5 on-h, 3 starts, curtail 112.4 kWh) vs B 51.85 L (4 on-h, 2 starts, curtail 145.0 kWh). This is a small B win on fuel but already a curtailment penalty.

---

## 5. Q6 — Controller Objective and Economics (the mechanism that connects the above)

From `gap19_highs_native.py`, the lexicographic priorities are **J1 (unmet critical) > J2 (reserve shortfall) > J3 (diesel) > J4 (curtailment)**.

Three facts follow directly from the code:

1. **Reserve outranks fuel.** J2 (priority 3) is lexicographically above J3 (priority 2). The planner will buy diesel to satisfy the 6-hour reserve envelope and the horizon-end terminal target before it minimizes fuel. At t = 23 the terminal target is `max(EBR, 100,000 Wh) + 40,000 Wh = 140 kWh` (70% SOC), re-imposed every hour (`terminal_target_wh = 100,000` is a `SIMULATED_RESEARCH_ASSUMPTION` per the preregistration).
2. **Curtailment is last.** J4 (priority 1) is only a tie-breaker, so the planner does not economize on surplus that its own diesel creates.
3. **Non-critical shedding is free.** J1 counts only `P_unmet_crit`; `p_unmet` (total unmet) has no objective term. Serving non-critical load costs diesel, so the planner sheds it at no penalty. This is why reliability is ~80% in every arm, including the perfect-foresight arm C.

**Startup economics mismatch:** GAP19 charges 2 L per start in J3, but the executor charges 0. The planner therefore over-penalizes starts relative to what is realized, which biases it toward longer runs. Both arms share this bias. It cannot alone explain the B−A gap, because it does not differ by arm in a way the data isolates, but it is a documented model inconsistency, and it is consistent with B's pattern of fewer starts and more run-hours.

Combining these: **B's forecast leads a controller whose reserve rule (J2 > J3) and no-curtailment-penalty (J4) cause it to commit diesel that the executor cannot absorb, and B's forecast is what triggers this, since C under the same controller does not show it.**

---

## 6. Q1 and Q2 — What the Artifacts Can and Cannot Show

**Q1, forecast error vs. actual solar:** Not measurable from these artifacts. The realized SITES `SW_IN` and per-hour forecast arrays are absent. Forecast-side facts that are verifiable from code:

- **Arm A** is `800 × sin((h−4)π/16) × 0.75` for hours 04–20 UTC and **zero otherwise**. It is date-independent and cloud-blind. Peak 600 W/m² at 12 UTC. Daily sum 6,092 W·h/m².
- **Arm B** is `max(0, GHI_ineichen × (1 − cloud_fraction))` with MEPS 18Z cloud cover, zeroed only when the sun is below the horizon.
- Solar elevation at Nuolja (68.36°N), mid-June (approximate): 00–03 UTC = 2.7°, 4.9°, 8.3°, 12.6°; 20–23 UTC = 6.6°, 3.7°, 2.1°, 1.8°. **In June the sun is above the horizon for all 24 hours, while Arm A forecasts zero for roughly 9 of them.** The magnitude is low-angle (small GHI), so this is a bias, not a dominant error.
- Arm A caps clear-sky at 600 W/m², roughly 25% below the peak of a clear-sky curve at a 45° solar elevation (estimate, not computed here).

Therefore, **whether B's forecast is more or less accurate than A's is unknown from these artifacts.** This is the single most important missing measurement. The C result (perfect foresight beats A by 523 L) shows that better solar information helps. It does not show that B's specific forecast is better than A's.

**Q2, first A/B dispatch divergence:** The first solve, origin 1 (t0 = 2024-04-30T23:00Z), already sees different 24-hour solar vectors (A is zero at 00–04 UTC; B is nonzero where the sun is above the horizon). The divergence is therefore at **origin 1, step 0**, and the origin-1 totals already differ (A 56.89 L vs B 51.85 L). The step-0 *action* difference cannot be extracted without the per-step plan records.

---

## 7. Caveats and Open Verification

1. **Label check.** The executor's `unmet_load_w` is `demand − served` (total, not critical-only, `research_realization_executor.py` lines 205–207). The per-origin key is called `unmet_critical_load_wh`. I did not open the campaign script that maps it, so the label is unverified. The reliability and "reduced unmet" claims depend on which quantity it is. The core diesel/curtailment finding does not depend on this.
2. **Startup fuel omitted at realization** (§5). This is a model inconsistency in the frozen code, not a claim about B.
3. **Per-hour data absent** (§6). The forecast-accuracy and first-divergence questions need a re-derivation that the frozen artifacts cannot provide.

---

## 8. Classification

| Candidate | Verdict | Basis |
|---|---|---|
| FORECAST (B's solar is simply worse) | Not established | Forecast accuracy unmeasured. C under the same controller beats A, so information helps, but B's accuracy is unknown. |
| CONTROLLER (objective ordering) | Contributing | J2 > J3 buys diesel for reserve; J4 curtailment unpenalized. Same ordering applies to A, so it does not explain the B−A gap alone. |
| BATTERY | Not primary | Pinned at the 57.83% reserve; floor and ceiling never approached. |
| DIESEL ECONOMICS | Contributing | Startup fuel charged in planner, not in realization; 81% of the B penalty is diesel energy, not run-hours. |
| **FORECAST-CONTROLLER INTERACTION** | **Best supported** | Same controller with perfect forecast (C) shows less curtailment than A. B's forecast alone produces the diesel-energy surplus that is curtailed (61% of B's extra diesel energy), and B's curtailment is near-universal. |

---

## 9. Summary of Quantitative Findings

- B − A diesel = **+1,125.7 L (+20.5%)**, 87/123 origins worse, p = 4×10⁻⁸ (two-sided).
- **81%** of the penalty is extra diesel energy (+3.65 MWh); **19%** is extra run-hours (+43 h).
- **61%** of that extra diesel energy is curtailed (2.22 MWh); **33%** serves extra load (1.21 MWh); battery net ≈ 0.
- Curtailment: B curtails in **122/123** origins vs. 101/123 for A. Δfuel vs Δcurtailment r = 0.75.
- Battery pinned at the reserve (57.83%); not binding on floor or ceiling.
- Arm C (perfect foresight, same controller) has **less** curtailment than A, so the curtailment excess is specific to B's forecast.

---

PRIMARY BOTTLENECK: FORECAST-CONTROLLER INTERACTION. B's solar forecast drives a controller whose reserve rule (J2) outranks diesel fuel (J3) and whose curtailment term (J4) is unpenalized, so it commits about 3.65 MWh more diesel energy. The executor cannot absorb that surplus, and 2.22 MWh of it is curtailed (61%). Forecast accuracy itself is unmeasured, so FORECAST cannot be ruled in or out from these artifacts.

NEXT EXPERIMENT: Research-only instrumented hourly trace of origins 56, 66, 77 and 118 under Arms A and B, with no change to dispatch rules. For each hour, log forecast solar against realized SW_IN, planned vs. realized diesel, planned charge and discharge, the J2 reserve shortfall, and a curtailment cause code (same-hour discharge vs. charge-cap). This is about 192 solves and isolates whether the curtailment comes from committed diesel met by same-hour discharge, which would confirm the mechanism in §4–§5.
