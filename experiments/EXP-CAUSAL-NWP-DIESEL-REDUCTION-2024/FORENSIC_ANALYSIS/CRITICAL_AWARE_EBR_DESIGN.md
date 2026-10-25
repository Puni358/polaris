# Critical-Aware EBR: Design Only

**Status:** design only. Nothing implemented, nothing run. GAP19, configs, frozen artifacts, and the campaign are untouched.
**Source:** `system/optimization/implementations/gap19_highs_native.py` (EBR at lines 111–131, terminal merge at 146–151, reserve constraint at 297–306, critical demand at 88–107).

---

## 1. How the current EBR is calculated

**FACT.** For each hour `t = 0..23`, GAP19 computes a 6-hour critical-energy requirement over window `[t, min(t+5, 23)]` (lines 127–131):

```
EBR[t] = (1 / eta_dis) × Σ_{k=t}^{min(t+5,23)} critical_demand[k] × dt
```

With `eta_dis = 0.92` and `dt = 1 h`, a full 6-hour window at the 11,600 W ceiling gives `EBR = 75,652 Wh`.

The reserve constraint (lines 297–306) is:

```
E_next[t] + s_J2[t] ≥ E_stage2_target[t] + min_e,   min_e = 40,000 Wh (20% of 200 kWh)
```

`E_stage2_target[t] = EBR[t]` for `t < 23`, and `max(EBR[23], terminal)` at `t = 23`. `s_J2` is a slack penalised at priority 3, above diesel fuel (priority 2).

So the full-window reserve is `75,652 + 40,000 = 115,652 Wh = 57.83%` SOC. This matches the frozen minimum SOC of 57.83% in every Arm A origin.

---

## 2. Which demand quantity feeds it

**FACT.** `critical_demand` comes from, in priority order (lines 88–100):
1. `forecast_bundle.demand_critical`, if the bundle supplies one;
2. `config["critical_demand_w"]`, a 24-element list. The research adapter fills this with `min(11,600, bundle.demand.point)` at every step;
3. `config["critical_demand_ratio"]` × forecast demand.

In the campaign, path 2 is used. The input is the **forecast total demand** from `LocalBaselineForecastEngine` (persistence plus a diurnal cosine). It is **not** the realized demand, and it is **not** conditioned on solar at all.

---

## 3. Why this causes the observed diesel commitment under Arm B

**FACT.** The EBR reserve is a fixed requirement on battery energy, set by the critical-load ceiling. It does not change with the solar forecast. Forecast demand is 10,000–18,000 W, so `min(11,600, demand)` is about 11,600 W in most hours, and the target is nearly constant at about 57.8% SOC.

**INFERENCE.** Solar forecasts only determine whether solar can fill that reserve. In Arm A, the surplus forecast (6,092 W·m²·h per origin) fills it, so no diesel is needed. In Arm B, the forecast is solar-poor on cloud-saturated and timing-shifted days, so nothing fills the reserve, and GAP19 charges it from diesel (the step-0 diesel commitment). The ablation supports this: removing EBR eliminates step-0 diesel in all 123 origins.

The reserve is therefore **unconditional on what the forecast says renewables will deliver**. It holds 6 hours of full critical load as stored energy even when the forecast already covers that load with solar. That is the source of the unnecessary reservation.

---

## 4. Minimal research-only alternative: critical-aware EBR

**PROPOSED RESEARCH CHANGE.** Reserve only the critical energy that the forecast does **not** cover with renewables in the same window:

```
EBR_ca[t] = (1 / eta_dis) × Σ_{k=t}^{min(t+5,23)} max(0, critical_demand[k] − solar_gen[k] − wind_gen[k]) × dt
```

Here `solar_gen[k]` and `wind_gen[k]` are the forecast renewable powers (W) from the same bundle, and `critical_demand[k]` is unchanged (`min(11,600, forecast demand)`).

Properties of this design:
- **Critical-load protection is preserved by construction in the plan.** The reserve covers any critical energy the forecast leaves unserved by renewables, over the same 6-hour window. The critical-first logic is not weakened.
- **Unnecessary reservation is removed.** Hours where forecast renewables cover the critical load no longer force battery storage or diesel.
- **Terminal target is unchanged.** `e_stage2_target[23] = max(EBR_ca[23], terminal)` keeps the 100 kWh floor, so the terminal mechanism is not altered.
- **Known risk to measure:** if the solar forecast over-predicts, `EBR_ca` is too small and realized critical unmet can rise. That is the reliability trade-off the experiment must measure, not assume away.

---

## 5. Can it be isolated without touching GAP19 production?

**FACT.** Yes, with no change to GAP19 and no config-key change beyond the research harness. Two facts make this possible:
- GAP19 accepts a **24-element list** for `config["ebr_target_wh"]` (lines 117–120). It uses the list directly instead of the governed formula.
- The research runner calls `optimizer.optimize(bundle, state, step_configs)` **once per hour**, with the bundle in hand. A research wrapper around the optimizer can compute `EBR_ca[t]` from `bundle.solar_generation.point`, `bundle.wind_generation.point`, and `bundle.demand.point`, put it in a copied config, and pass that to GAP19 unchanged. This is the same pattern as the `Rec` wrapper used in the traces.

**INFERENCE.** The change is isolated to the research harness. GAP19, the router, the executor, and the configs are not modified. The terminal target and the ablation boundary stay as they are, because only `ebr_target_wh` is replaced, the same single-key diff the EBR ablation already used.

**Caveat:** `wind_gen` must be included, because the frozen formula counts wind-free critical energy. If wind is excluded from the subtraction, the reserve is overstated. Wind forecasts here are persistence-based, so their effect should be measured, not assumed.

---

## 6. Single experiment to test it

**Proposed single experiment (not run):**
- **Scope:** the six traced origins (77, 56, 66, 23, 8, 30) first, Arm B only.
- **Arms:** frozen Arm B (governed EBR), EBR-OFF (already done), and critical-aware EBR `EBR_ca` as defined in §4, with the wrapper in §5.
- **Prerequisite:** per-hour logging of supply, served, diesel, and discharge, so the critical-unmet split can be measured under the planner's own convention. The earlier 123-origin split is blocked for this reason.
- **Measure:** step-0 diesel, fuel, unmet split (critical and non-critical), critical reliability, min SOC, and terminal status.
- **Pass criteria, set before running:** critical reliability no worse than frozen Arm B, and fuel reduced relative to frozen Arm B. Failing the first criterion means the alternative is rejected, whatever the fuel result.

---

## Summary

| Question | Answer |
|---|---|
| 1. How EBR is calculated | `EBR[t] = (1/0.92) Σ_{k=t}^{t+5} critical[k]`, reserve `E_next[t] ≥ EBR[t] + 40 kWh` (FACT) |
| 2. Demand quantity | Forecast total demand, capped at 11.6 kW, from the persistence baseline; not realized, not solar-conditioned (FACT) |
| 3. Why diesel is committed | Reserve is unconditional on renewable forecasts, so solar-poor forecasts force diesel charging (FACT for the structure, INFERENCE for the mechanism) |
| 4. Minimal alternative | Reserve only critical energy not covered by forecast renewables: `max(0, critical − solar − wind)` (PROPOSED RESEARCH CHANGE) |
| 5. Isolable without GAP19 change | Yes: the research wrapper passes a 24-element list through the existing config path (FACT for the path, INFERENCE for the isolation) |
| 6. Single experiment | Six origins first, with per-hour logging, against frozen Arm B and EBR-OFF; pass criteria set in advance (§6) |
