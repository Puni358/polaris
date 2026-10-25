# POLARIS — Post-Stage-4 Reserve and Hour-0 Decision Reconciliation

**Date (UTC):** 2026-10-06
**Status:** READ-ONLY RECONCILIATION. No implementation, no campaign, no replay, no solver run, no parameter change, no production or Stage 4 artifact modified.
**Purpose:** establish exactly what SW and SW-L fed into the optimizer at each hour (especially hour 0), and whether the recorded telemetry is sufficient to explain the diesel commitment. Not a search for a better candidate.

**Labels:** `[VERIFIED]` reproduced from code, artifacts, or telemetry. `[INFERRED]` strongly supported but not directly proven. `[HYPOTHESIS]` a possible explanation that needs an experiment. `[UNKNOWN]` cannot be established from current evidence.

---

## 1. STATUS

**STATUS: COMPLETE — RECONCILIATION PARTIAL.** Several discrepancies are resolved (Section 11). Others remain open (Section 12). The governance answers in Section 14 are NO for most items. No new experiment is recommended.

---

## 2. Executive Conclusion

1. **The SW-L hour-0 diesel commitment is fully explained by the implemented reserve constraint.** SW-L's protected reserve at origin start is at least 63.0 kWh in every origin, so it needs at least 103.0 kWh stored at end of hour 0 against a 100 kWh start. There is no renewable surplus at hour 0 to charge the battery (forecast renewables are at most 7,547 W against forecast demand of 17,898 W in all origins). Diesel is therefore the only charging source, and the optimizer must satisfy the reserve before it optimizes fuel. Diesel is ON in 123 of 123 origins, and every origin that the rule forces is ON. `[VERIFIED]`

2. **The SW hour-0 commitment is not explained.** SW's index-0 reserve averages 17.7 kWh and never forces diesel, yet SW runs diesel at hour 0 in 39 origins. The index-0 rule and the full-horizon rule both fail to explain these 39. The same holds for 12 S origins. The cause is `[UNKNOWN]`; the terminal-target interaction and fuel-timing consolidation are `[HYPOTHESIS]` only. Resolving them requires a solver-level trace, which is outside this read-only scope. `[UNKNOWN]`

3. **The forensic report's wind-provenance question is resolved.** The SW wind term is not a per-origin constant and not a recorded forecast column. It is a persistence forecast whose offset is the simulator's realized wind from the previous hour (4,500 W at origin start). This reproduces the recorded SW and SW-L reserves exactly at all 123 origins for every hour whose window lies inside the recorded day. `[VERIFIED]`

4. **This is a governance-relevant finding.** The realized wind (and realized demand) enter the forecast through the station state. The preregistration says realized wind is "never in a plan," and the design says the wind forecast is a "baseline heuristic from the frozen initial state." Neither matches the implementation. `[VERIFIED]` Whether this is acceptable is a governance decision, not a technical one.

5. **The terminal target does reach the optimizer, but not as documented.** The 100,000 Wh terminal is applied at index 23 of every reoptimization's 24-hour horizon (absolute hour t+23 at step t), not at the origin day's hour 23. The logged `stage2_target_wh` column cannot show it, because it records index 0. `[VERIFIED]` Documentation ≠ implementation at this boundary.

6. **Startup cost enters the MILP objective but not the simulator's fuel.** The optimizer charges 2.0 L per start (a code default, since the YAML key is absent). The simulator charges no startup fuel. The optimizer therefore optimizes a different fuel objective from the one accounted. `[VERIFIED]`

7. **Fuel is capped at 100 L per origin, and the MILP does not see the cap.** S and SW-L each reach the cap in one origin. In that origin the executor burns fuel with zero diesel output once the stock is exhausted. `[VERIFIED]`

**Governance decision (Section 14):** A NO, B NO, C NO, D NO, E NOT YET, F NO. Do not recommend a new candidate experiment. The origin-start diagnostic is premature until the open items in Section 12 are closed.

---

## 3. Source / Code Provenance Map

### 3.1 Authoritative live path (Stage 4 campaign)

| Role | File | Verified note |
|---|---|---|
| Campaign runner | `experiments/stage4_sw_low_sun_2025_holdout/run_stage4_sw_low_sun_2025_campaign.py` (SHA-256 `8a62feb3…2f0c312`, matches freeze) | Defines `Stage4TelemetryRunner`, `InterceptingOptimizer`, `run_closed_loop_robust`. |
| Stage 4 adapter (EBR formulas) | `experiments/stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py` (SHA-256 `3427da6a…395d0`, matches freeze) | Defines `compute_variant_*_ebr`, `compute_stage2_target_vector`, `SolarElevationProvider`. |
| Research optimizer actually executed | `experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py` (SHA-256 `95b2f3b5…950e`, matches design §9) | `ResearchNumericalGAP19Optimizer.optimize()` builds its own MILP. |
| Optimizer base class | `system/optimization/implementations/gap19_highs_native.py` (SHA-256 `fd1afe10…e737`) | Imported only for `__init__`. **Its `optimize()` is never called** (the extractor contains a single `super()` call, in `__init__`). |
| Forecast bundle (solar, demand) | `system/forecasting/implementations/causal_nwp_physics.py` (SHA-256 `14e72d8a…deb710`) | `CausalNwpPhysicsForecastEngine.predict`. Wind and demand delegated to the baseline engine. |
| Forecast bundle (wind, demand) | `system/forecasting/implementations/baseline.py` (SHA-256 `905c644a…c993`; **not pinned by any governance document**) | `LocalBaselineForecastEngine.predict`. |
| Critical-demand vector | `system/research/research_critical_demand_adapter.py` | `adapt_critical_demand_vector(b, D) = [min(b, d) for d in D]`. `[VERIFIED]` |
| Closed-loop base | `system/research/closed_loop_causal_nwp_runner.py` | Instantiates `CausalNwpPhysicsForecastEngine()` (no PV config path). |
| Realization executor | `system/simulation/research_realization_executor.py` (SHA-256 `c1ab56bf…673a6`; **not pinned by any governance document**) | Realized flows, fuel, state update. |
| Config / initial state | `experiments/run_diesel_reduction_campaign.py` (`make_initial_state`, `load_canonical_configs`), `system/config/battery.yaml`, `system/config/diesel.yaml`, `system/config/solar_pv.yaml` | Initial state and parameters. |

**Not on the live path:** `system/optimization/implementations/milp.py` and `gap19_highs_native_milp_v2_research.py` are not imported by the campaign. `[VERIFIED]`

**Governance note:** the design-doc freeze cites GAP19 `gap19_highs_native.py` as the solver. The MILP that actually solved the campaign is the research override in the extractor. The hash-guarded base `optimize()` was not executed. `[VERIFIED]`

### 3.2 Per-step data flow

For each hour `t` of each origin, the runner:
1. Builds the bundle `bundle = forecast_engine.predict(current_state, cloud_context)`.
2. Computes `crit_w = min(11600, bundle.demand.point)` (`adapt_critical_demand_vector`).
3. Computes `ebr_used` from `bundle.solar_generation.point`, `bundle.wind_generation.point`, `crit_w`, and the L flags from `SolarElevationProvider`.
4. Sets `cfg_copy["ebr_target_wh"] = ebr_used` and calls the research optimizer.
5. Passes plan step 0 to `execute_step`, which realizes flows with **actual** solar, wind, and demand.
6. Sets `current_state = realization_res.next_state`.

`[VERIFIED]` (runner lines 100–137, 219–322; executor lines 115–292)

---

## 4. SW / SW-L Wind-Vector Provenance

### 4.1 Provenance chain

```
SOURCE            station_state.last_observed_wind_generation (scalar, W)
                    step 0:    4500.0  (make_initial_state, run_diesel_reduction_campaign.py)
                    step t≥1:  round(actual_wind_generation[t-1], 2)
                               (research_realization_executor.py:272, set from realized wind of the executed hour)
TRANSFORM         LocalBaselineForecastEngine.predict (baseline.py:39–80)
                    for h = 1..24:  w_h = max(0, round(L + 5000·sin(h·π/6), 2))
                    no scaling; perturbation only if forecast_perturbation_mode is set (not set here)
FORECAST VECTOR   baseline.wind_generation.point (24 values, W, index j ↔ horizon h = j+1)
                  passed through unmodified: causal_nwp_physics.py:434 wind_generation=base_bundle.wind_generation
S/SW ADAPTER      compute_variant_sw_ebr / compute_variant_swl_ebr take wind_w[k] unchanged (validation only: ≥ 0)
                  runner: wnd_w = list(bundle.wind_generation.point)
GAP19 (research)  wind_gen = bundle.wind_generation.point  → p_wind_max upper bound only
                  (the MILP credits wind via availability, not via the reserve target directly)
```

Where it breaks: the chain is complete. Every link is verified by code reading and by telemetry.

### 4.2 Properties

| Question | Answer | Label |
|---|---|---|
| Class / constructor | `LocalBaselineForecastEngine(pv_config_path)`; called via `CausalNwpPhysicsForecastEngine` | VERIFIED |
| Function | `LocalBaselineForecastEngine.predict` | VERIFIED |
| Input data | `station_state.last_observed_wind_generation` only (for wind); `station_state.timestamp` for alignment | VERIFIED |
| Forecast horizon | 24 hours, relative to `station_state.timestamp` | VERIFIED |
| Timestamp alignment | bundle index 0 = `state_timestamp + 1 h`. Results CSV shows origin 1 `t0_timestamp = 2025-04-30T23:00Z`, so index 0 = `2025-05-01T00:00Z` = telemetry hour 0 | VERIFIED |
| Origin alignment | per step; each reoptimization uses the step's own state | VERIFIED |
| Causal NWP? | **No.** Wind is not from NWP. It is a persistence formula. | VERIFIED |
| Synthetic? | The sinusoid `5000·sin(hπ/6)` is synthetic. The offset is the **simulator's realized wind** from the previous hour. | VERIFIED |
| Observed wind? | **Yes, through state.** `last_observed_wind_generation` is set from realized wind (executor line 272). The prior hour's realized value enters the next hour's plan. | VERIFIED |
| Heuristic? | Yes: persistence plus sinusoid. | VERIFIED |
| Repeated across horizon? | No. A single offset `L_t` is used for all 24 horizon hours, with a sinusoid in `h`. | VERIFIED |
| Modified before adapter? | No. Only `max(0, ·)` and `round(·, 2)`. | VERIFIED |

### 4.3 Reproduction

- `forecast_wind[t] = actual_wind[t−1] + 2500` holds at all 2,829 origin-hours with t ≥ 1. `[VERIFIED]`
- `forecast_wind[0] − 2500 = 4500` at all 123 origins. `[VERIFIED]`
- Reconstruction `w_j(t) = max(0, round(L_t + 5000·sin((j+1)π/6), 2))` with `L_0 = 4500`, `L_t = actual_wind[t−1]`, reproduces the recorded SW and SW-L reserve targets **exactly (0.000 Wh)** at all 123 origins for every hour t ≤ 18 (windows wholly inside the recorded day). `[VERIFIED]`

### 4.4 Corrections to the forensic report

- The forensic report applied the single-hour `forecast_wind` column across all 24 horizon steps. That was my error. The column records only step-0 values, so the reconstruction was invalid, not the code.
- The "per-origin constant" hypothesis is refuted (error ~27 kWh). `[VERIFIED]`
- The "frozen initial state" description in the design doc is wrong. The offset is realized persistence, not frozen. `[VERIFIED]`

---

## 5. EBR Reconstruction

### 5.1 Frozen formula (as implemented)

`E_EBR[t] = (1/η) · Σ_{j=0}^{5} max(0, c_{t+j} − credit_{t+j}) · Δt`, where `η = 0.92`, `Δt = 1 h`, and `credit` depends on the arm.

Implementation (adapter lines 152–347): the window is `k ∈ {t, …, t+5}` **with no truncation at 23**, because the bundle covers 24 horizon hours from each step. `[VERIFIED]`

### 5.2 Inputs

| Symbol | Source | Units | Clipping / transform | Label |
|---|---|---|---|---|
| A. `c_k` critical demand | `adapt_critical_demand_vector(11600, bundle.demand.point)` = `min(11600, D_k)`; `D_k = max(10000, round(L_d + 3000·cos((k+1)π/12), 2))`, `L_d` = previous realized demand (15,000 at origin start) | W | min and max only | VERIFIED |
| B. `s_k` solar | `bundle.solar_generation.point[k]` = `min(max(0, GHI·300·0.20·0.85), 60000)`, `GHI = max(0, cs_ghi·(1−cloud))` when elevation > 0, else 0 | W | GHI≥0, inverter clip 60 kW, round 2 dp | VERIFIED |
| C. `w_k` wind | §4 | W | max(0), round 2 dp | VERIFIED |
| D. Type | `s` and `w` are **forecast** vectors, but `w` depends on realized wind via state; `c` is forecast demand (always 11,600 W in practice) | — | — | VERIFIED |
| E. Location | §3 | — | — | VERIFIED |
| F. Units | EBR in Wh; power in W; `Δt = 1 h` so W·h = Wh | — | — | VERIFIED |
| G. Other transforms | None beyond the above | — | — | VERIFIED |

### 5.3 Reconstruction results

| Arm | Hours t ≤ 18 (window inside day) | Hours 19–23 (window extends past recorded day) |
|---|---|---|
| Control | Reconstructed as the governed constant 75,652.17 Wh, matching all rows (0 error) | Same constant; reconstructable |
| S, S-L | Exact, max error 0.000 Wh, all origins | **Not reconstructable.** Requires beyond-day forecast solar that the telemetry does not record |
| SW, SW-L | Exact, max error 0.000 Wh, all origins (with §4 wind) | **Not reconstructable** (same reason) |

**Worked example (origin 1, hour 0):**

| Arm | Recorded ebr₀ (Wh) | Reconstructed (Wh) | Abs / rel error |
|---|---|---|---|
| Control | 75,652.2 | 75,652.2 (constant) | 0 / 0 |
| S | 71,923.1 | 71,923.1 | 0 / 0 |
| SW | 22,292.4 | 22,292.4 | 0 / 0 |
| S-L | 75,652.2 | 75,652.2 | 0 / 0 |
| SW-L | 75,652.2 | 75,652.2 | 0 / 0 |

**Worked example (origin 2, hour 0):** Control 75,652.2 · S 75,652.2 · SW 26,021.5 (reconstructed 26,021.5) · S-L 75,652.2 · SW-L 75,652.2. All exact.

**Hours 1, 6, 12, 18** match exactly for all arms across all 123 origins (§5.3 first row).

Note: the comparison "actual Layer-C target" is identical to the recorded `ebr_target_wh` (the logged `stage2_target_wh` = index 0 = ebr; see §6.3), so no independent Layer-C column exists.

### 5.4 H. Does the adapter add a terminal reserve?

The adapter helper `compute_stage2_target_vector(ebr, 100000)` does (`stage2[23] = max(ebr[23], 100000)`). But the runner uses it only to **log** `stage2_vector[0]`. The optimizer does not receive this helper's output; it receives `ebr_used` and reads the terminal from `config["terminal_target_wh"]`. `[VERIFIED]`

### 5.5 I. Does GAP19 modify the target afterward?

Yes, in one place: the research extractor builds `e_stage2[t] = ebr[t]` for `t < 23` and `e_stage2[23] = max(ebr[23], terminal)` (extractor lines 209–212). No other modification. `[VERIFIED]`

### 5.6 J. Minimum terminal override

Yes. `terminal_target_wh = config["terminal_target_wh"] = 100,000 Wh` (`run_diesel_reduction_campaign.py:82`, passed through `step_configs`). No `station_state.terminal_target_wh_override` is set in the initial state. `[VERIFIED]`

---

## 6. Terminal-Target Reconstruction

### 6.1 What reaches the optimizer

Adapter → optimizer arguments:
- `config["ebr_target_wh"]` = `ebr_used` (24-element list; no terminal).
- `config["terminal_target_wh"]` = 100,000.0 (from `BASE_CONFIG`).

Optimizer → Layer C (extractor lines 209–212, 350–353):
- `e_stage2[t] = ebr[t]` for `t = 0…22`.
- `e_stage2[23] = max(ebr[23], 100000)`.
- Layer C: `E_next[t] + s_j2[t] ≥ e_stage2[t] + min_e` for `t = 0…23`, with `min_e = 40,000 Wh`.

Final MILP: the constraint is soft (`s_j2 ≥ 0`), penalized in the J2 objective. J2 has priority 3 (second highest; J1 critical unmet has 4). **Hence the reserve is effectively hard whenever feasible.** `[VERIFIED]`

### 6.2 Effective value

Since every `ebr[23]` in the recorded telemetry is ≤ 75,652 Wh, `max(ebr[23], 100000) = 100,000 Wh` in every case. **The effective terminal reserve is exactly 100,000 Wh above floor (SOC ≥ 70%) at relative horizon index 23 of every reoptimization.** It is not EBR + 40,000, and not `max(100,000, EBR)` in any case where EBR could exceed 100 kWh. `[VERIFIED]`

### 6.3 Where it appears

- **Documentation** (design §5, preregistration §5.2): the terminal applies at the origin day's hour 23.
- **Implementation:** the terminal applies at relative index 23 of each step's horizon, i.e. absolute hour `t + 23` at step `t`. At step 0 this equals origin hour 23. At step 5 it is absolute hour 28, which is the next day. **DOCUMENTATION ≠ IMPLEMENTATION.** The boundary is the reoptimization horizon (extractor lines 209–212 applied at each step).
- **Logging:** `stage2_target_wh` = `stage2_vector[0]` (runner line ~150). Index 0 never carries the terminal, so the telemetry column cannot show it. This is a logging-index error, not an optimizer error. `[VERIFIED]`

### 6.4 Resulting terminal SOC

Realized SOC at origin hour 23 vs the 70% level (100 kWh above floor):

| Arm | Share of origins with SOC ≥ 70% at hour 23 |
|---|---|
| Control | 84.6% |
| S | 47.2% |
| S-L | 52.0% |
| SW | 33.3% |
| SW-L | 52.8% |

`[VERIFIED]`. The terminal target is in the plan, but the executed SOC does not reach it in most origins. This is because the plan uses forecast renewables and the executor uses actual ones (§7.3). `[INFERRED]` for the mechanism, `[VERIFIED]` for the outcome.

---

## 7. Fuel-Accounting Reconstruction

### 7.1 Simulator (executor) — exact formula

`fuel_req = (base_fuel_lph + marginal_fuel_lpwh · p_diesel_plan) · 1 h`, with `base = 5.0 L/h`, `marginal = 0.00025 L/Wh` (executor lines 94–95, 173). `[VERIFIED]`

If `avail_fuel < fuel_req`: `fuel_consumed = avail_fuel`; `diesel_realized = min(plan, (avail − base)/marginal)` (or 0 if `avail ≤ base`). `[VERIFIED]` (lines 181–187)

**No startup term** in the executor. `[VERIFIED]`

### 7.2 Telemetry reproduction

Using the code formula with the recorded `diesel_power` (kWh) and on/off:
- `fuel = 5·on_h + 0.25·kWh` reproduces **all 14,759 of 14,760 non-starved rows exactly** (the one exception is below). `[VERIFIED]`
- Exception: S origin 39, hour 22. Fuel 4.05 L is charged with zero diesel output, because the remaining stock covered only the base load, not the requested output. `[VERIFIED]`

The earlier least-squares fit (coefficients 5 and 0.25) is therefore the code formula, not an empirical approximation. `[VERIFIED]`

### 7.3 Startup cost — where it enters

| Location | Term | Value | Verdict |
|---|---|---|---|
| MILP objective (extractor line 380) | `c3[base+14] = startup_fuel_l`, from `diesel_cfg.get("startup_fuel_l", 2.0)` | **2.0 L** (default; key absent from `diesel.yaml`) | **Enters** |
| Simulator fuel (executor) | none | 0 | **Does not enter** |
| `diesel.yaml` `startup_cost: 15.0` | currency units, `fuel_cost_per_l 2.50` (≈ 6 L) | used only by `system/evaluation/evaluator.py` and `system/robustness/metrics.py`, **not** by the Stage 4 path | does not enter |

**Answer: A (MILP objective only).** The design's 2.0 L start is a code default in the optimizer. Three different startup values exist in the repo. `[VERIFIED]`

Consequence: SW-L (267 starts) vs SW (161 starts) implies 212 L of optimizer-side startup cost that is not charged to the accounted fuel. The optimizer minimizes a different fuel objective from the one reported. `[VERIFIED]`

### 7.4 Per-origin fuel cap (not in the MILP)

- Every origin starts with `diesel_fuel_remaining_liters = 100 L` (`make_initial_state`). There is no refuelling. `[VERIFIED]`
- The MILP does not see this budget. `[VERIFIED]`
- Maximum per-origin total fuel: Control 85.07 L, S 100.00 L, S-L 94.43 L, SW 98.04 L, SW-L 100.00 L. `[VERIFIED]`
- Origins reaching the cap: S 1 (origin 39), SW-L 1. `[VERIFIED]`

---

## 8. Hour-0 Optimization Reconstruction

### 8.1 Inputs at hour 0 (identical across arms)

| Input | Value | Source | Label |
|---|---|---|---|
| Battery SOC | 50.00% = 100,000 Wh | `make_initial_state` | VERIFIED |
| Battery bounds | 20%–95% of 200,000 Wh → `min_e = 40,000 Wh`, `max_e = 190,000 Wh` | `battery.yaml` | VERIFIED |
| Diesel previous state | `diesel_running = False` | `make_initial_state` | VERIFIED |
| Diesel start cost | 2.0 L (MILP only) | extractor default | VERIFIED |
| Diesel min / max | 10 kW / 100 kW | `diesel.yaml` | VERIFIED |
| Fuel stock | 100 L | `make_initial_state` | VERIFIED |
| Critical demand `c_0` | 11,600 W (all origins) | telemetry | VERIFIED |
| Total demand forecast `D_0` | 17,897.78 W (all origins; `L_d = 15000` at origin start) | baseline formula | VERIFIED |
| Solar forecast `s_0` | 0–547 W across origins | telemetry | VERIFIED |
| Wind forecast `w_0` | 7,000 W (all origins; `L_0 = 4500`) | §4 | VERIFIED |
| Renewable surplus at hour 0 | none: `s_0 + w_0 − D_0 < 0` in all 123 origins (max −10,351 W) | telemetry | VERIFIED |
| Battery charge/discharge limits | 50 kW each | `battery.yaml` | VERIFIED |
| Charge / discharge efficiency | 0.92 / 0.92 | extractor defaults | VERIFIED |
| Objective priorities | J1 (critical unmet) 4 > J2 (reserve shortfall) 3 > J3 (fuel + start) 2 > J4 (curtailment) 1 | extractor lines 418–441 | VERIFIED |

### 8.2 Comparison at origins 1 and 2 (hour 0)

Reserve requirement at end of hour 0 = `ebr₀ + 40 kWh`. Stored energy at start = 100 kWh.

**Origin 1** (L flags hours 0–5 = 111111; solar 13, 295, 772, 2,351 W in hours 0–3)

| Arm | ebr₀ (kWh) | Need (kWh) | Headroom (kWh) | Diesel on | Planned/executed diesel (W) | Executed charge (W) | SOC after h0 (%) |
|---|---|---|---|---|---|---|---|
| S | 71.92 | 111.92 | −11.92 | yes | 47,473 | 36,576 | 66.83 |
| SW | 22.29 | 62.29 | +37.71 | yes | 47,203 | 36,306 | 66.70 |
| S-L | 75.65 | 115.65 | −15.65 | yes | 47,473 | 36,576 | 66.83 |
| SW-L | 75.65 | 115.65 | −15.65 | yes | 47,203 | 36,306 | 66.70 |

**Origin 2** (L flags 111111; solar 0 W in hours 0–5)

| Arm | ebr₀ (kWh) | Need | Headroom | Diesel on | Diesel (W) | Executed charge (W) | SOC after h0 (%) |
|---|---|---|---|---|---|---|---|
| S | 75.65 | 115.65 | −15.65 | yes | 44,463 | 33,566 | 65.44 |
| SW | 26.02 | 66.02 | +33.98 | **yes** | 54,033 | 43,136 | 69.84 |
| S-L | 75.65 | 115.65 | −15.65 | yes | 44,463 | 33,566 | 65.44 |
| SW-L | 75.65 | 115.65 | −15.65 | yes | 54,033 | 43,136 | 69.84 |

(The Control row is omitted from this reconstruction because its reserve is the governed constant. Its hour-0 diesel is also ON.)

Origin 2 SW is ON despite 34 kWh of headroom, which is why the index-0 rule fails for SW.

Caution on the executed-charge column: the executed charge is the realized surplus (executor §6), not the plan's charge. See §12.3.

### 8.3 Population-level hour-0 rule

Test: **diesel ON iff ebr₀ + 40 kWh > 100 kWh** (the index-0 reserve requires diesel).

| Arm | Origins | Forced by index 0 | Forced and ON | ON but not forced |
|---|---|---|---|---|
| Control | 123 | 123 | 123 | 0 |
| S | 123 | 82 | 82 | **12** |
| S-L | 123 | 123 | 123 | 0 |
| SW | 123 | **0** | 0 | **39** |
| SW-L | 123 | 123 | 123 | 0 |

**Result: every forced origin is ON (100%, all arms).** The forced ⇒ ON direction holds without exception. The converse does not hold for S (12) or SW (39). `[VERIFIED]`

Checking the full horizon (any index j ≤ 17) instead of index 0 does not fix this. It over-predicts S diesel (agreement falls to 85%) because late-day reserve requirements can be met by daytime solar. `[VERIFIED]`

---

## 9. Binding Constraints / Objective Explanation

### 9.1 SW-L (123/123 ON)

**Binding constraint: Layer C at index 0, with J2 priority over J3.**

Chain of necessity, each step verified:
1. SW-L's index-0 reserve is ≥ 63.04 kWh in every origin (the minimum in the population), so the requirement is ≥ 103.04 kWh. `[VERIFIED]`
2. The start is 100 kWh. Net energy must rise by ≥ 3.04 kWh before the end of hour 0. `[VERIFIED]`
3. No renewable surplus exists at hour 0 (§8.1), so energy can only rise by diesel charging. `[VERIFIED]`
4. Diesel charging requires diesel ON. The J2 reserve term outranks J3 fuel, so the optimizer meets the reserve at the cost of diesel, rather than trading the reserve away for fuel. `[VERIFIED by priority ordering; the solve itself was not re-run]`
5. Result: diesel ON in 123/123. `[VERIFIED]`

**Why SW-L and not S:** under SW-L, the low-sun flag is 1 at the origin start (the protection rule), which removes all renewable credit from the index-0 window. The index-0 reserve then equals the governed Control reserve whenever the window is protected. S keeps the solar credit in the window, which lowers the requirement below 100 kWh in 41 of 123 origins. `[VERIFIED]`

### 9.2 S (82 forced, 94 ON)

The 82 forced origins are ON (100%). The 12 unforced ON origins are not explained by the index-0 rule. `[UNKNOWN]`

### 9.3 SW (0 forced, 39 ON)

Index-0 reserve averages 17.7 kWh and is never forcing. The 39 ON origins are not explained by the index-0 rule, the full-horizon rule, or the renewable-surplus test. `[UNKNOWN]`

Candidate explanations, none tested:
- `[HYPOTHESIS]` The 100 kWh terminal at index 23 (requires SOC ≥ 70% at horizon hour 23) may not be reachable from forecast renewables alone, so the optimizer schedules some diesel at hour 0 to reduce later diesel cost. Under J3, each diesel-on hour costs a fixed 5 L base plus a 2 L start, so consolidating diesel into fewer hours is cheaper, which can favour hour 0.
- `[HYPOTHESIS]` A later-hour reserve (index 1–17) may bind once solar is included in the window.

Either hypothesis would need a solver trace with the full 24-hour model to confirm. That is outside this read-only scope. `[UNKNOWN]` until then.

### 9.4 Objective tradeoff summary

- Under J2 > J3, a feasible reserve is never traded for fuel.
- For SW-L, the reserve is feasible only with diesel charging, so the fuel cost is incurred.
- Startup (2 L in J3) is a small fixed cost per start; the 5 L/h base is the main per-hour cost.
- Whether a lower reserve would have been feasible without diesel is not a question the constraint set can answer from telemetry alone. It is a policy question.

---

## 10. S vs SW vs S-L vs SW-L Comparison

| Quantity (hour 0) | Control | S | SW | S-L | SW-L |
|---|---|---|---|---|---|
| Initial SOC / energy | 50% / 100 kWh | same | same | same | same |
| Mean ebr₀ (kWh) | 75.65 | 64.15 | **17.72** | 73.11 | 71.54 |
| SW-L ebr₀ min (kWh) | — | — | — | — | **63.04** |
| Index-0 forced (count) | 123 | 82 | 0 | 123 | 123 |
| Diesel ON at hour 0 | 123 | 94 | 39 | 123 | 123 |
| ON but not forced | 0 | 12 | 39 | 0 | 0 |
| Reserve governed by protection? | no (constant) | no | no | yes | yes |

**Why SW-L commits diesel at hour 0 in essentially every origin while S does so much less:**
- SW-L's protection rule replaces renewable credit with zero at low sun, so the index-0 reserve is the governed Control value (≥ 63 kWh, typically ~72–76).
- That reserve requires ~103–116 kWh at end of hour 0. The start is 100 kWh, and there is no renewable surplus to fill the gap.
- So SW-L's hour-0 diesel is a **forced consequence of the protected reserve**, not a fuel tradeoff chosen by the optimizer. `[VERIFIED]`
- S's reserve keeps solar credit in the window, so it falls below the start in 41 origins, and diesel is not forced there. `[VERIFIED]`
- SW's reserve is low (wind credit), so the index-0 requirement is covered by stored energy and diesel is not forced. Its 39 ON origins are unexplained. `[UNKNOWN]`

**SW vs SW-L:** the difference at hour 0 is entirely the protection rule (L = 1 → credit removed), which lifts the reserve from ~18 kWh to ~72 kWh. `[VERIFIED]`

**S vs S-L:** same mechanism for solar-only credit. S-L's hour-0 reserve is 73.1 kWh, so diesel is forced in all origins. `[VERIFIED]`

**S vs SW-L:** both commit diesel in most origins, but SW-L forces it in all 123 origins. S's unforced diesel (12) is not understood. `[VERIFIED]` for the forced parts; `[UNKNOWN]` for the rest.

---

## 11. Resolved Discrepancies

| # | Item | Resolution | Label |
|---|---|---|---|
| R1 | Forensic: SW wind term does not reproduce from recorded columns | Wind is persistence on previous realized wind + sinusoid (§4). Exact for all 123 origins, t ≤ 18. | VERIFIED |
| R2 | Forensic: per-origin constant wind hypothesis | Refuted (error ~27 kWh). | VERIFIED |
| R3 | Forensic: terminal rule in telemetry (hour-23 reserve 75.65 kWh vs 100 kWh) | Telemetry logs index 0; the terminal is at index 23 of each step's horizon and does reach the optimizer (§6). | VERIFIED |
| R4 | Forensic: startup cost absent from fuel | Startup is in the MILP objective (2.0 L) and absent from simulator fuel (§7.3). | VERIFIED |
| R5 | Forensic: fuel formula fitted, not reconstructed | Code formula reproduces all non-starved rows exactly (§7.2). | VERIFIED |
| R6 | Design: wind forecast = "baseline heuristic from frozen initial state" | Incorrect. It is persistence on realized previous-hour wind. Recorded as a documentation error. | VERIFIED |
| R7 | Forensic: "GAP19" as the solver | The executed MILP is the research override in the extractor; the base `optimize()` is not executed. | VERIFIED |
| R8 | Hour-0 reserve formula for S, SW, S-L, SW-L, Control | Exact reconstruction (§5.3). | VERIFIED |
| R9 | Hour-23 reserve reconstruction for Control | The governed constant 75,652 Wh is reproduced; the logged value is index 0 of a 24-hour vector. | VERIFIED |

---

## 12. Remaining Discrepancies

| # | Item | Status | Label |
|---|---|---|---|
| U1 | Hours 19–23 reserve for S/SW/S-L/SW-L: window extends past the recorded day, and beyond-day solar is not recorded | Cannot be reconstructed from telemetry | UNKNOWN |
| U2 | Hour-0 diesel ON but not forced by index 0: S 12 origins, SW 39 origins | Cause unexplained; needs a solver trace | UNKNOWN |
| U3 | Plan vs executed battery charge: the MILP's planned charge matches the executed charge in only 55% of hours (mean absolute difference 2–6 kW) | The MILP's SOC path is not the realized path. Executor sets charge from realized surplus (executor §6). | VERIFIED (mismatch); cause of its effect on reserve compliance UNKNOWN |
| U4 | Governance: realized wind and realized demand enter the forecast through the station state (persistence). Preregistration says realized wind is "never in a plan." | Conflict between documentation and implementation | VERIFIED (conflict); acceptability is a governance decision |
| U5 | Two solar-elevation conventions in one run: the L flag uses `Etc/GMT-1` (one-hour offset); the forecast solar uses physical UTC elevation (`causal_nwp_physics.py:~330`, `utc=True`) | Confirmed. The L flag disagrees with the physical 15° test in 246 of 2,952 window hours (8.3%): 123 flagged low-sun while the sun is above 15°, and 123 the reverse | VERIFIED |
| U6 | Terminal documentation (origin hour 23) ≠ implementation (relative index 23 at every step) | Documented boundary. Recommend documentation correction after governance review | VERIFIED |
| U7 | Terminal not reached by executed SOC in most origins (33–53% at hour 23 for S, SW, S-L, SW-L) | Plan vs execution mismatch (U3) | VERIFIED (outcome); cause INFERRED |
| U8 | Fuel stock of 100 L per origin, not seen by the MILP: S and SW-L each reach the cap in one origin | Effect on those origins' reliability and fuel is not quantified | VERIFIED (occurrence); effect UNKNOWN |
| U9 | Executor charges 0 starts; the MILP charges 2.0 L per start | Optimizer objective ≠ accounted fuel | VERIFIED |
| U10 | Three different startup values in the repo: 2.0 L (MILP, Stage 4), 6 L (`startup_cost 15 / 2.50`, evaluator and metrics), 0 L (executor) | Inconsistent; the Stage 4 path uses 2.0 L and 0 L | VERIFIED |
| U11 | Governance hash coverage: `baseline.py`, `research_realization_executor.py`, `closed_loop_causal_nwp_runner.py`, `research_critical_demand_adapter.py` are not pinned by any governance document | A hash-guard gap | VERIFIED |
| U12 | Executor fuel starvation charges base fuel with zero diesel output (S origin 39, hour 22, 4.05 L) | Small accounting artifact | VERIFIED |
| U13 | Terminal and reserve Layer C is soft (`s_j2`) and priority-ordered; the realized shortfall path is not recorded | Diagnostic gap | UNKNOWN |
| U14 | The brief's manifest path `experiments/STAGE4_2025_SW_LOW_SUN_LOW_SUN_RESEARCH_FREEZE_MANIFEST.json` does not exist. The correct path `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE_MANIFEST.json` was used. | Brief typo; no artifact affected | VERIFIED |

---

## 13. Proven / Inferred / Unknown

**[VERIFIED]**
- The SW/SW-L wind vector, its provenance, and its exact reserve reconstruction for hours 0–18 (§4, §5.3).
- The EBR formula reconstruction for all five arms at hours 0–18.
- The terminal reaches the optimizer as 100,000 Wh at relative index 23 of every step; documentation differs.
- The startup term is in the MILP objective (2.0 L) and absent from simulator fuel.
- The fuel formula `5 L/h + 0.25 L/kWh` reproduces all non-starved rows exactly.
- The index-0 forced-⇒-ON rule holds for 100% of forced origins in all arms.
- SW-L's hour-0 diesel is forced by the protected reserve in 123/123 origins, given no renewable surplus at hour 0.
- SW's 39 hour-0 diesel commitments are not explained by the index-0 reserve.
- Realized wind and realized demand enter the forecast through the station state.
- Two solar-elevation conventions are in use; the L flag disagrees with the physical test in 246 window hours.
- Plan and executed battery charge differ in 45% of hours.

**[INFERRED]**
- SW-L's extra hour-0 diesel is a consequence of the protected reserve rather than a fuel tradeoff, because J2 outranks J3 and no renewable surplus exists.
- Realized-state persistence is a plausible reason the plan and executed SOC diverge (U3, U7), though not directly proven.

**[HYPOTHESIS]**
- H1: the SW hour-0 diesel commitments are driven by the 100 kWh terminal at index 23 combined with fuel consolidation under J3 (§9.3).
- H2: a later-hour reserve requirement (index 1–17) binds once solar credit is in the window.
- H3: the protected hour-0 reserve could be lower only if the policy allowed credit at low sun; this is a policy question, not a mechanism question.

**[UNKNOWN]**
- Beyond-day forecast values for S/SW reserves at hours 19–23 (U1).
- The cause of the 39 SW and 12 S unforced hour-0 diesel commitments (U2).
- The realized effect of the 100 L fuel cap on the two affected origins (U8).
- Whether a reserve-shortfall path is recorded anywhere (U13).

---

## 14. Recommendation and Governance Decision

### 14.1 Is the origin-start diagnostic justified?

**Not yet.** Its premise was "is the hour-0 commitment necessary for safety?" This reconciliation shows that for SW-L the commitment is **forced by the implemented reserve rule**, so the diagnostic would test the reserve policy itself, not a mechanism. For SW, the commitment is unexplained, so the diagnostic would test a behaviour we cannot yet describe. A replay built on either would be premature.

### 14.2 Governance answers

| # | Question | Answer | Reason |
|---|---|---|---|
| A | Is the SW/SW-L EBR input provenance fully reconciled? | **NO** | Hours 19–23 cannot be reconstructed (U1); the realized-wind-in-plan conflict (U4) is unresolved. |
| B | Is terminal-target implementation fully reconciled? | **NO** | Effective value and placement are verified, but documentation ≠ implementation (U6), and the logged column does not show the terminal. |
| C | Is fuel accounting fully reconciled? | **NO** | Simulator formula is exact, but startup is in the optimizer objective and not in accounting (U9), and the fuel cap and starvation are not in the MILP (U8, U12). |
| D | Is the hour-0 diesel decision causally explained from the actual optimizer inputs? | **NO** | Explained for SW-L (123/123) and for all forced origins. Not explained for SW (39) or S (12). |
| E | Is the proposed origin-start diagnostic now justified? | **NOT YET** | D is NO, and the question has shifted to the reserve policy itself (§14.1). |
| F | Should we design a new preregistration now? | **NO** | Requires the items in §15 first. |

Because A–D are NO, **no new candidate experiment is recommended.** The missing evidence is in §15.

---

## 15. Evidence That Must Be Frozen Before Any Next Experiment

1. **Solver trace for hour 0** (read-only, single-step, under explicit authorization): for origins where SW runs diesel without an index-0 requirement, record the MILP's binding constraints and dual values, with the full 24-hour model. This resolves U2 and tests H1/H2.
2. **Beyond-day forecast record**: the 24-hour bundle at each step (solar, wind, demand), so hours 19–23 reserves can be reconstructed (U1).
3. **Planned vs executed trajectory**: per step, the planned `E_next`, planned charge/discharge, and executed charge/discharge, so U3 and U7 can be quantified.
4. **Startup policy decision**: a governed statement of whether starts belong in the optimizer objective, the accounting, both, or neither, with the value and source (U9, U10). This is a governance decision.
5. **Terminal semantics decision**: whether the terminal is intended at the origin day's hour 23 or at relative index 23 of each reoptimization. Then correct the documentation or the implementation, not both silently (U6).
6. **Wind and demand provenance decision**: whether realized-state persistence in the forecast is acceptable under the preregistration's "never in a plan" language (U4). This is a governance decision, not a code fix.
7. **Solar-elevation convention decision**: whether the L flag should use physical UTC elevation. Any change would be a new preregistered convention, not a correction to Stage 4 (U5).
8. **Hash-guard coverage**: pin `baseline.py`, `research_realization_executor.py`, `closed_loop_causal_nwp_runner.py`, and `research_critical_demand_adapter.py` in any future governance record (U11).
9. **Fuel-cap treatment**: decide whether the 100 L stock is a governed input the MILP must see (U8).

---

## 16. Production and Frozen-Artifact Boundary

- No production file modified. No Stage 4 artifact, freeze, preregistration, or governance file modified.
- No new code written in the repository. The analysis used scratch files outside the repository only.
- The campaign was not re-run. No optimizer was invoked. All numbers are reconstructions from recorded telemetry and code reading.
- Stage 4 remains frozen. S remains the current winner (24.02%). SW-L remains the safety-leading alternative (14.66%). SW remains a safety failure (36.50%). The 40% target is not achieved.
