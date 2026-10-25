# Critical-Aware EBR Experiment: Six Origins

**Status:** research-only experiment. Frozen campaign and frozen artifacts untouched. GAP19 and production configs untouched.
**Harness:** `FORENSIC_ANALYSIS/critical_aware_ebr_experiment.py`. Per-origin output with hourly logs: `FORENSIC_ANALYSIS/critical_aware_ebr/origin_NN.json`; combined: `all_results.json`.
**Origins:** 77, 56, 66, 23, 8, 30 (no others run).

---

## 0. Formula, Units, and Pre-Run Checks

**Arm C reserve (research wrapper, GAP19 unchanged):**

`EBR_ca[t] = (1 / η_dis) × Σ_{k=t}^{min(t+5, 23)} max(0, crit[k] − solar_gen[k] − wind_gen[k]) × dt`

- `crit[k] = min(11,600 W, forecast demand[k])`, the frozen adapter rule.
- `solar_gen`, `wind_gen`: forecast powers in **W** from the same bundle. `TimeseriesForecast` validates `unit == "W"` for both (`forecast_bundle.py` lines 76–78). `solar_gen` is the PV-transformed power, not irradiance.
- `dt = 1 h`, `η_dis = 0.92`. W × h = Wh, so the output is in **Wh**.
- `max(0, ·)` keeps every term non-negative, so `EBR_ca ≥ 0`. The function asserts finiteness and non-negativity on every call.
- The 20% minimum reserve (`min_e = 40,000 Wh`) is unchanged in GAP19's constraint. It is the floor on `E_next`, so the reserve cannot fall below it.
- The terminal target is unchanged. GAP19 still computes `max(EBR_ca[23], 100,000 Wh)`.

**Pre-run checks (run in each worker before the arms):**
1. **Identity check:** with zero renewables, `EBR_ca` equals the governed GAP19 formula. Asserted, and passed (otherwise the workers would have failed).
2. **Non-negativity:** asserted on every hour of every run.
3. **Config isolation:** Arm B's config differs from the base in one key, `ebr_target_wh`. The terminal target is 100,000 in both.
4. **Injection path:** the research optimizer wrapper passes a copied config with a 24-element `ebr_target_wh` list. GAP19 already accepts that format (lines 117–120). No production code changed.

**Critical convention (fixed before the run):** `critical_realized[t] = min(11,600 W, realized demand[t])`, served first, then non-critical. This is the convention in the completed load-class diagnostic. It is accounting only and does not change dispatch. The planner-convention sensitivity was blocked earlier, so this choice is a caveat on the result (§5).

---

## 1. Reproduction of Frozen Arm B

**Frozen Arm B reproduces the frozen results for all six origins** (fuel, total unmet, curtailment, and served load within tolerance).

---

## 2. Results, Six Origins (aggregate; Arm A = frozen Arm B, Arm B = EBR-OFF diagnostic, Arm C = critical-aware)

| Metric | A: frozen B | B: EBR-OFF (diagnostic) | C: critical-aware |
|---|---:|---:|---:|
| Total fuel (L) | 388.5 | 94.4 | **257.0** |
| Diesel-on hours | 31 | 6 | 18 |
| Startups | 19 | 4 | 9 |
| Curtailment (kWh) | 666.8 | 444.5 | 578.8 |
| Total unmet (kWh) | 320.2 | 415.1 | 359.0 |
| Critical unmet (kWh) | 82.6 | 105.6 | 90.2 |
| Non-critical unmet (kWh) | 237.6 | 309.5 | 268.7 |
| **Critical reliability** | **95.06%** | 93.68% | **94.60%** |
| Total reliability | 85.18% | 80.78% | 83.38% |
| Minimum SOC | 56.77% | 22.62% | 23.70% |
| Maximum SOC | 95.00% | 91.14% | 94.04% |
| SOC-floor violations | 0 | 0 | 0 |
| Planned terminal shortfall steps | 0 | 0 | 0 |
| Optimizer failures | 0 | 0 | 0 |

Served plus unmet equals demand in every arm.

**Per origin (fuel in L, critical reliability in %, critical unmet in kWh, curtailment in kWh):**

| Origin | Fuel A → C | Critical reliability A → C | Critical unmet A → C | Curtailment A → C |
|---|---|---|---|---|
| 77 | 74.3 → 60.6 | 98.33 → 98.64 | 4.6 → 3.8 | 147.1 → 167.6 |
| 56 | 93.8 → 94.9 | 94.15 → 93.51 | 16.3 → 18.1 | 88.0 → 120.4 |
| 66 | 80.7 → 28.9 | 97.03 → **93.35** | 8.3 → **18.5** | 37.2 → 14.9 |
| 23 | 61.9 → 56.2 | 94.20 → 95.30 | 16.1 → 13.1 | 181.1 → 146.0 |
| 8 | 38.4 → 16.4 | 94.74 → 95.23 | 14.7 → 13.3 | 111.8 → 71.6 |
| 30 | 39.4 → 0.0 | 91.87 → 91.56 | 22.6 → 23.5 | 101.6 → 58.2 |

---

## 3. Pre-Registered Decision

**Rule:** PASS only if Arm C reduces fuel versus frozen Arm B **and** critical reliability is no worse than frozen Arm B.

- Fuel: **reduced** by 131.6 L (−33.9%). Condition met.
- Critical reliability: **95.06% → 94.60%**, a fall of **0.46 percentage points**. Condition not met.

**Decision: FAIL.** Arm C saves fuel, but it does so at a critical-reliability cost, which the rule does not allow. EBR-OFF is diagnostic only and is not a success target; it is reported for context.

---

## 4. Mechanism

- **Fuel falls because the reserve shrinks.** Arm C's reserve counts only critical energy the forecast does not cover with renewables. Hours where forecast solar covers the critical load carry no reserve, so less diesel is committed. Diesel-on hours fall 31 → 18 and startups 19 → 9.
- **Critical reliability falls where the forecast over-covers.** The clearest case is origin 66. The mechanism is inferred from the earlier timing finding (forecast solar peaks at 09 UTC, realized at 12–13 UTC). I have not checked this run's hourly logs for origin 66, so the cause is not yet confirmed. Critical unmet rises from 8.3 to 18.5 kWh and critical reliability falls from 97.0% to 93.4%. This is the forecast-timing risk named in the design, and it is what the experiment was built to measure.
- **Curtailment rises.** Curtailment goes 666.8 → 578.8 kWh overall, but rises in origins 77 and 56, where the forecast shape still leaves same-hour-discharge surplus.
- **Minimum SOC is lower, not violated.** It falls from 56.8% to 23.7%, close to the 20% floor and above it. Zero floor violations.
- **Terminal target holds in the plan.** Planned terminal shortfall is zero in all arms. Realized hour-24 SOC is lower in Arm C than in the frozen baseline.

---

## 5. Caveats

1. **Critical convention is unresolved.** The decision uses `min(11.6 kW, realized demand)`, fixed before the run. Under the planner's forecast-based convention the critical-unmet figures could differ. Dispatch would not change, but the reliability comparison that decides PASS or FAIL could, and this has not been tested. The earlier sensitivity was blocked for this reason.
2. **Six origins.** The sample was fixed in advance. It cannot establish behaviour across the 123-origin campaign.
3. **Forecast-timing sensitivity.** The reserve depends on the forecast's timing. Origin 66 shows that a timing error can release reserve that realized solar does not cover in time.
4. **No tuning.** The formula was not changed after seeing results. It is the one stated in §0.

---

VERDICT: FAIL under the pre-registered rule. Critical-aware EBR cuts fuel by 131.6 L (−33.9%) versus frozen Arm B, but critical reliability falls 0.46 percentage points, so the rule does not pass.

FUEL CHANGE: −131.6 L (−33.9%), 388.5 → 257.0 L. Diesel-on hours 31 → 18, startups 19 → 9.

CRITICAL-RELIABILITY CHANGE: 95.06% → 94.60% (−0.46 pp). Critical unmet rises 82.6 → 90.2 kWh (+7.6 kWh). Origin 66 accounts for most of the rise (8.3 → 18.5 kWh).

CURTAILMENT CHANGE: 666.8 → 578.8 kWh (−88.0 kWh, −13%). Rises in origins 77 and 56, falls elsewhere.

SOC CHANGE: Minimum SOC 56.8% → 23.7%, above the 20% floor. Zero floor violations. Maximum 95.0% → 94.0%.

PRIMARY MECHANISM: The reserve falls where forecast renewables cover the critical load, which cuts fuel. Where the forecast timing is wrong (origin 66), that released reserve is not available when realized solar lags, so critical load goes unmet.

NEXT SINGLE EXPERIMENT: Re-run the same six origins for Arm C only, with the critical convention set to the planner's forecast-based rule (min(11.6 kW, forecast demand), capped at realized demand) and the reserve otherwise unchanged. This tests whether the critical-reliability failure, which the pass rule turns on, survives the convention that is still unresolved. No formula change and no tuning.
