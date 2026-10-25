# EBR-OFF Diagnostic Report: Arm B, All 123 Origins

**Experiment:** `EXP-CAUSAL-NWP-DIESEL-REDUCTION-2024` (frozen; not rerun or modified)
**Harness:** `FORENSIC_ANALYSIS/ebr_ablation_123.py` (research-only). Per-origin output: `FORENSIC_ANALYSIS/ebr_ablation_123/origin_NNN.json`; combined: `all_results.json`; run log: `ebr_ablation_123_run.log`.
**Date:** 2026-10-04

---

## 0. Verification and Isolation

**Single change.** `config["ebr_target_wh"] = 0.0`. The frozen config has no such key, so the baseline uses the governed 6-hour EBR formula. Setting the key to 0 zeroes the reserve envelope for hours 0–22 and leaves the terminal target at hour 23 (100 kWh, 140 kWh with `min_e`) unchanged. The harness asserts the one-key config diff and that the terminal target is 100000 in both configs.

**Baseline reproduction: 123 / 123 origins.** Baseline Arm B reproduces the frozen per-origin diesel fuel, unmet, and curtailment to within 0.001 L and 0.01 Wh. The ablation is accepted only against this baseline.

**Execution:** all 123 ablated runs completed with status `OK`. There were **zero optimizer failures and zero safety-invariant exceptions** in either arm (the runner raises on non-OPTIMAL status or on a safety breach; none occurred).

**Limit of the verification.** Input invariance (forecast, realized inputs, initial state) was checked on the six-origin harness, not on all 123. The 123-origin run uses the same code path and the same `ebr_ablation.py` construction, but I did not repeat the step-by-step invariance check across all origins.

---

## 1. Totals, Frozen Arm B vs EBR-OFF Arm B (123 origins)

| Metric | Frozen Arm B | EBR-OFF B | Δ | Δ % |
|---|---:|---:|---:|---:|
| Total diesel fuel (L) | 6,603.98 | **2,084.78** | −4,519.2 | **−68.4%** |
| Mean diesel fuel per origin (L) | 53.69 | **16.95** | −36.7 | −68.4% |
| Diesel-on hours | 484 | 129 | −355 | −73.3% |
| Diesel startups | 324 | 72 | −252 | −77.8% |
| Curtailment (kWh) | 9,477.7 | 6,771.4 | −2,706.3 | **−28.6%** |
| Same-hour-discharge curtailment (kWh) | 9,118.2 | 6,443.2 | −2,675.1 | −29.3% |
| Total unmet (kWh, executor demand − served) | 7,844.4 | 9,172.7 | **+1,328.2** | **+16.9%** |
| Served load (kWh) | 36,435.6 | 35,107.3 | −1,328.2 | −3.6% |
| Mean reliability per origin (%) | 82.29 | 79.29 | −3.00 pp | |
| Demand total (kWh) | 44,280 | 44,280 | 0 | |

Accounting holds: served + unmet equals demand in both arms (residual −0.1 Wh over the full run, rounding).

---

## 2. Critical vs Non-Critical Unmet — **Not Measurable Cleanly; Limitation Reported, Not Inferred**

The request asks whether the reliability cost is critical or non-critical unmet. **The frozen code does not support measuring this split, so I did not produce one.**

- **The executor does no load-class allocation.** `research_realization_executor.py` lines 205–207 compute `served = min(demand, supply)` and `unmet = demand − served`. Served load is not ordered by criticality, so there is no realized critical served quantity to subtract from.
- **The critical rule is defined only on forecast demand.** `critical_demand[t] = min(11,600 W, forecast_demand[t])` (adapter and GAP19 lines 88–107). No realized critical demand series is defined in the frozen code. Applying the same rule to realized demand would be a new convention, not a measurement of the frozen system.
- **The per-hour records hold only the total.** The trace and campaign records carry `unmet_load_w` (demand − served) and planned quantities. The planned critical deficit `J1` is an aggregate over the 24-hour plan, not a realized hourly split.

**What is measured:**
- Planned critical deficit (J1 > 0): **0 reoptimizations in both arms** across 123 origins. The planner protects the planned critical load in every plan, with and without EBR.
- Planned reserve/terminal shortfall (J2 and terminal): **0 in both arms**.

So the planner's plan says critical load is protected in both arms. The extra realized unmet is in the executor's total unmet, which cannot be split into critical and non-critical with the frozen definitions. **Any statement that the cost is "predominantly non-critical" would be an inference from the objective structure, not a measurement, and I am not making it.** Attributing the unmet split needs an instrumented realization rule for load class, which is a new definition and is not part of the frozen system.

---

## 3. Reliability, SOC, and Constraint Status

- **Reliability:** mean per-origin reliability falls from 82.29% to 79.29% (−3.0 pp). Total unmet rises in **101 of 123** origins (22 fall, none tie). The frozen reliability gate (unmet must not exceed baseline) is therefore failed in 101 origins.
- **Minimum SOC:** baseline 54.97%, EBR-OFF **20.00%**. The EBR-OFF minimum is exactly the 20% floor. Across origins, 83 EBR-OFF origins have a minimum below 30%.
- **Maximum SOC:** 95.0% in both arms (both hit the ceiling at least once).
- **SOC-floor violations (below 19.999%): 0 in both arms. SOC-ceiling violations: 0 in both arms.** The EBR-OFF run reaches the floor but does not go below it.
- **Terminal target status:** planned terminal shortfall is 0 in both arms, in every reoptimization. The realized hour-24 SOC is lower in the EBR-OFF run (mean 51.2% vs 78.5%). This is the expected effect of re-planning the terminal each hour, not a planned violation, as in the six-origin ablation.
- **Optimizer failures:** 0 in both arms. **Safety-invariant exceptions:** 0 in both arms.

---

## 4. Diesel and Curtailment

- **Fuel:** down in **122 of 123** origins (one origin rises; none tie). Mean per origin 53.7 → 16.9 L. The reduction is large and broad, not concentrated in a few origins.
- **Step-0 diesel:** planned diesel at the first reoptimization of each origin is **zero in all 123 EBR-OFF origins** (base: positive in all 123). The early diesel commitment is eliminated across the full campaign, not only the six traced origins.
- **Curtailment:** down in 87 origins, up in 20 (16 unchanged or near). Total −28.6%. Same-hour-discharge curtailment accounts for 95% of the remaining curtailment in both arms, consistent with the earlier ablations (the realization rule is unchanged).

---

## 5. Interpretation (within what is measured)

- The EBR reserve envelope is responsible for most of the diesel in Arm B across the campaign. Removing it cuts fuel by 68% and diesel-on hours by 73%.
- Removing it costs reliability. Unmet rises 16.9% and the reliability gate fails in 101 origins. The cost is in the executor's total unmet. Its critical share is not measured here.
- The EBR-OFF run uses the battery down to the 20% floor. It does not violate the floor, but the margin is zero in at least one origin.

---

## 6. Caveats

1. **Critical/non-critical split is not measured** (§2). This is a limitation, not a finding.
2. Input invariance was checked on six origins only (§0).
3. The EBR-OFF controller is a diagnostic: it fails the frozen reliability gate and is not a candidate.
4. Results are for Arm B only. Arm A was not ablated here.

---

VERDICT: Removing the EBR reserve envelope alone cuts diesel dramatically (−68.4% fuel across 123 origins, with step-0 diesel eliminated in every origin) and reduces curtailment by 28.6%. The cost is 16.9% more total unmet, which fails the frozen reliability gate in 101 origins. Whether that unmet is critical or non-critical cannot be measured with the frozen definitions.

FUEL BENEFIT: −4,519 L total (−68.4%); mean 53.7 → 16.9 L per origin; diesel-on hours 484 → 129; startups 324 → 72. Fuel falls in 122 of 123 origins.

CRITICAL-RELIABILITY COST: **Not measured.** The executor serves min(demand, supply) with no load-class priority, and the critical rule is defined only on forecast demand, so the realized critical/non-critical split has no definition in the frozen system. What is measured: planned critical deficit (J1 > 0) is zero in both arms in all 123 origins, and planned terminal and reserve shortfalls are zero. The realized critical cost cannot be stated.

NONCRITICAL-RELIABILITY COST: **Not measured** for the same reason. The total unmet cost is +1,328 kWh (+16.9%), and it cannot be attributed to load class. No inference is made here.

CURTAILMENT BENEFIT: −2,706 kWh (−28.6%) overall, with same-hour-discharge curtailment (95% of the remainder) following the same realization-rule mechanism as before.

NEXT SINGLE EXPERIMENT: Research-only diagnostic: add a load-class definition to the realization layer, applied identically to both arms (critical = min(11,600 W, realized demand), served critical priority within the executor), and rerun the same 123-origin Arm B baseline and EBR-OFF comparison to measure the critical/non-critical unmet split. Diagnostic only, not a replacement controller and not a production change, and the realization-rule change must be labelled as a new definition, not a frozen result.
