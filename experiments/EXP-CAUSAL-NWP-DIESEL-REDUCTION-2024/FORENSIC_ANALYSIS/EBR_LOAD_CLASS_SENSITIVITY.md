# EBR Load-Class Sensitivity: Blocker Report

**Status:** STOPPED. The accounting-only sensitivity cannot be computed from the stored outputs without rerunning dispatch. Nothing was approximated and no result is reported.
**Requested:** recompute the critical/non-critical unmet split using the planner's convention, `critical_realized[t] = min(11,600 W, forecasted_total_demand[t])`, for the same 123 origins, Arm B vs EBR-OFF Arm B, without rerunning optimization or changing dispatch.

---

## Why It Is Blocked

The planner's convention changes the split only through the critical-served term, which depends on supply in each hour:

`served_critical[t] = min(critical_demand[t], supply[t])`

Here `supply[t] = solar[t] + wind[t] + diesel[t] + battery_discharge[t]`. Diesel and battery discharge are dispatch outputs. The split needs them **per hour**.

What is stored for the 123 origins (`FORENSIC_ANALYSIS/ebr_loadclass_123/origin_NNN.json`, `ebr_ablation_123/origin_NNN.json`):
- per-origin totals only (fuel, unmet, curtailment, served, and the earlier split);
- **no per-hour served, supply, diesel, or discharge values**, which I verified by inspecting the keys (`per-step arrays present? False`).

Per-hour records exist only for the six traced origins (77, 56, 66, 23, 8, 30) in `hourly_trace/` and `ebr_ablation/`. They cannot support a 123-origin result.

The forecast-demand half is recoverable. The baseline demand forecast is persistence-based and deterministic, so `forecasted_total_demand[t]` can be reconstructed from realized demand. Only the served/supply half is missing.

The only way to get the per-hour served and supply values for 123 origins is to rerun the dispatch with per-step logging. That would rerun optimization, which this request rules out.

---

## Convention Question Also Needs Your Decision

Even with per-hour data, `min(11,600, forecasted_total_demand[t])` can exceed realized demand in an hour. Non-critical demand would then go negative. Two options:
- **(a)** cap critical at realized demand, `min(11,600, forecast[t], realized[t])`. This keeps the split non-negative and matches the planner's own clipping rule (critical ≤ total demand).
- **(b)** use the uncapped value and report the negative residual. This is not a valid split.

I recommend (a), but it is a convention choice, so I did not make it on your behalf.

---

## What Would Unblock It

1. **Permission to rerun the frozen-dispatch harness with per-hour logging** for the 123 origins, Arm B and EBR-OFF. This reproduces the same dispatch (already verified against the frozen totals) and records per-hour supply, served, diesel, and discharge. It does not change any dispatch rule. The campaign's own results stay untouched. Output would go to a new folder.
2. **Confirmation of the capping convention** (a) or (b) above.

Once both are given, the sensitivity is an accounting pass over those logs, with no optimization, and the report would state whether the ~93% non-critical share holds under the planner's convention.

---

VERDICT: Not determined. The requested sensitivity cannot be computed from stored outputs because it needs per-hour supply and served values that were never saved for the 123 origins.

CRITICAL-UNMET SHARE: Not computed.

NONCRITICAL-UNMET SHARE: Not computed. The earlier ~93% figure rests on the research-layer definition, min(11.6 kW, realized demand). Whether it holds under the planner's forecast-based convention is untested.

ROBUSTNESS: Not established. The earlier result is not confirmed under the planner's convention, and this report does not claim it is.

NEXT SINGLE EXPERIMENT: With your permission, rerun the frozen-dispatch harness for the 123 origins (Arm B and EBR-OFF Arm B) with per-hour logging of supply, served, diesel, and discharge, and confirm capping option (a). Then apply the planner's critical convention as an accounting pass. No optimization or dispatch change.
