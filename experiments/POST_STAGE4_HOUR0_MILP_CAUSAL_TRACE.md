# POLARIS — Final Hour-0 MILP Causal Trace (Stage 4 Frozen Campaign)

**Date (UTC):** 2026-10-06
**Status:** TRACE ONLY. No campaign, no replay, no altered MILP, no parameter change, no implementation, no production or Stage 4 modification. Previous reports (`POST_STAGE4_EFFICIENCY_FORENSIC_ANALYSIS.md`, `POST_STAGE4_RESERVE_DECISION_RECONCILIATION.md`) were read and not modified.
**Companion:** `experiments/POST_STAGE4_HOUR0_MILP_CAUSAL_TRACE.json` (full 24-hour step-0 input vectors and recorded hour-0 plans for all 51 target origins).

**Labels:** `[VERIFIED]` reproduced from code, governance artifacts, or telemetry. `[INFERRED]` a structural argument from verified facts that is not demonstrated by a solve. `[HYPOTHESIS]` a possible mechanism that needs an altered-model experiment. `[UNKNOWN]` cannot be established without solving an altered MILP, which this task forbids.

**Classification vocabulary (per brief §7):** FORCED = no feasible solution of the frozen model avoids hour-0 diesel. SELECTED = a diesel-off solution is feasible but the lexicographic objective prefers diesel-on. TIED = diesel-on and diesel-off are equally optimal. UNKNOWN = the artifacts do not permit classification.

---

## 1. Executive Summary

**STATUS: COMPLETE — CLASSIFICATION PARTIAL.** The model that ran is now traced end to end, and every hour-0 input is reconstructed. The three classifications are:

| Question | Classification | Basis |
|---|---|---|
| SW hour-0 (39 unexplained origins) | **UNKNOWN** | No index-0 requirement, J2 = 0 at the recorded optimum, and the decisive future-constraint or tie structure cannot be determined without an altered solve. |
| S hour-0 (12 unexplained origins) | **UNKNOWN** | Same structure. 7 origins run diesel at exactly the 10 kW minimum. |
| SW-L hour-0 (123 origins, all ON) | **SELECTED** | Not FORCED. The reserve is a soft constraint with slack `s_j2` penalized at priority 3 above fuel at priority 2. A diesel-off solution has reserve shortfall ≥ 3.04 kWh at index 0, which the recorded optimum avoids (J2 = 0). |

**Correction to the previous reconciliation.** That report called SW-L's hour-0 diesel "forced." The model does not make the reserve a hard constraint, so no feasible solution is excluded by it. The correct label is SELECTED under lexicographic priority. `[VERIFIED]`

**Primary mechanism (directly demonstrated, SW-L only):** the soft index-0 reserve constraint, penalized in the second lexicographic priority ahead of fuel, combined with zero renewable surplus at hour 0 and no battery energy above 100 kWh at origin start. `[VERIFIED]`. Caveat: global J1 interactions are not excluded (Section 6.3).

**Secondary mechanism (verified structure, consequence not established):** the MILP does not price non-critical served load or non-critical unmet load, and a flexible-load variable absorbs up to 500 W at no cost. At hour 0 the plan sheds all non-critical load to charge the battery. The executor realizes a different (surplus-based) charge. `[VERIFIED]` that the planned charge exceeds the realized charge by the non-critical demand (6,298 W) in 54% of unexplained SW origins to within 50 W. `[INFERRED]` that this shedding is what makes the hour-0 charge possible.

**Unresolved mechanism:** the future-index or terminal constraint that makes the stored energy valuable for the unexplained S and SW origins. `[UNKNOWN]`

**Governance-relevant findings not in previous reports:**
1. The EMERGENCY route label does **not** reach the MILP. The campaign's MILP always ran in NORMAL mode. `[VERIFIED]`
2. Realized critical unmet is not floor-limited. Only 0.4% of realized critical unmet energy in SW-L occurs with SOC at the floor. `[VERIFIED]` This removes the simplest "stored energy serves later unmet" argument for the realized trajectory, though not for the plan.
3. The startup mismatch changes the diesel-reduction magnitudes by up to 1.03 pp (SW), but not their ranking. `[VERIFIED]`

---

## 2. Exact Optimizer Path

### 2.1 Identity and hash

- **File:** `experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py`
- **SHA-256:** `95b2f3b53609a6e420a18692b4b0e3927cb47841d9e1200cce04677094a5950e` (recomputed 2026-10-06; matches the value pinned in `experiments/STAGE4_SW_SAFE_EFFICIENCY_RESEARCH_DESIGN.md` §9).
- **Governance coverage:** the hash is pinned in the design document. The Stage 4 freeze, manifest, and preregistration do **not** pin the extractor's hash. `[VERIFIED]`
- **Campaign import:** `run_stage4_sw_low_sun_2025_campaign.py` line 42 `from research_numerical_extractor import ResearchNumericalGAP19Optimizer, TAU_RESIDUE_W`, with `sys.path` set so the extractor directory precedes the production tree (lines 34–38). `[VERIFIED]`
- **Campaign runner hash** `8a62feb30a09a9bae7bab1261c73a1f33b857c585f2af5a37c757e29c2f0c312` matches the freeze manifest. `[VERIFIED]`

### 2.2 Class and inheritance

```
ResearchNumericalGAP19Optimizer (research_numerical_extractor.py:73)
    └── GAP19HighsNativeOptimizer (system/optimization/implementations/gap19_highs_native.py:23)
            └── EnergyOptimizer
```

- `__init__(self, tau=TAU_RESIDUE_W)` calls `super().__init__()` (extractor line 82) and sets `self.tau`, `self.last_diagnostics`. `[VERIFIED]`
- `optimize(self, forecast_bundle, station_state, config)` is **overridden** (line 84 onward). `[VERIFIED]`
- **`super().optimize()` is never called.** The only `super()` in the file is at line 82, inside `__init__`. The base class's `optimize()` does not run. The production class is inherited for its constructor and attributes only. `[VERIFIED]`
- The MILP is built inside the extractor's own `optimize()`. `[VERIFIED]`

### 2.3 Exact MILP construction

Variables: 24 hours × 15 per hour, plus 24 `unmet_crit`, plus 24 `s_j2`. Total **408** columns. `[VERIFIED]` (lines 146–176, `num_total_vars = 408`)

Per-hour block (index `base = 15t`):

| Offset | Variable | Bounds | Integrality |
|---|---|---|---|
| +0 | p_sol_used | [0, s_t] | — |
| +1 | p_wind_used | [0, w_t] | — |
| +2 | p_curt_sol | [0, s_t] | — |
| +3 | p_curt_wind | [0, w_t] | — |
| +4 | p_chg | [0, 50 kW] | — |
| +5 | p_dis | [0, 50 kW] | — |
| +6 | E_next | [40 kWh, 190 kWh] | — |
| +7 | p_diesel | [0, 100 kW] | — |
| +8 | p_served | [0, D_t] | — |
| +9 | p_unmet | [0, D_t] | — |
| +10 | p_flex | [0, 500 W] | — |
| +11 | u_chg | [0,1] | binary |
| +12 | u_dis | [0,1] | binary |
| +13 | u_diesel | [0,1] | binary |
| +14 | v_start | [0,1] | binary |

Row set (per hour unless noted), with `row` labels from the code:

| # | Row | Form |
|---|---|---|
| R1 | Solar decomposition | p_sol_used + p_curt_sol = s_t |
| R2 | Wind decomposition | p_wind_used + p_curt_wind = w_t |
| R3 | Bus balance | p_sol_used + p_wind_used + p_dis + p_diesel − p_served − p_chg − p_flex = 0 |
| R4 | Demand balance | p_served + p_unmet = D_t |
| R5 | Charge vs binary | p_chg − 50000·u_chg ≤ 0 |
| R6 | Discharge vs binary | p_dis − 50000·u_dis ≤ 0 |
| R7 | Exclusivity | u_chg + u_dis ≤ 1 |
| R8 | Battery transition | E_t − E_{t−1} − η·Δt·p_chg + (Δt/η)·p_dis = 0 (t = 0: RHS = initial energy 100,000 Wh) |
| R9 | Diesel min | p_diesel − 10000·u_diesel ≥ 0 |
| R10 | Diesel max | p_diesel − 100000·u_diesel ≤ 0 |
| R11 | Startup tracking | v_t − u_t + u_{t−1} ≥ 0 (t = 0: v_0 − u_0 ≥ −initial_running = 0) |
| LB | Layer B: critical balance | p_served_t + unmet_crit_t = c_t (per hour) |
| LC | Layer C: reserve | E_next_t + s_j2_t ≥ e_stage2_t + 40,000 (per hour, soft) |
| EM | EMERGENCY-only | p_dis_t − p_served_t ≤ 0 — **added only if `operating_mode == "EMERGENCY"`** (line 365) |

Row count: 11 × 24 + 24 + 24 = 312 in NORMAL mode; 336 if EM rows were active. `[VERIFIED]`

### 2.4 Objective and priorities

Four `HighsLinearObjective` terms, combined lexicographically with `blend_multi_objectives = False` (lines 384–415). `[VERIFIED]`

| Term | Priority | Coefficients | Content |
|---|---|---|---|
| J1 | **4** (highest) | `unmet_crit_t` coefficient = Δt per hour | critical unmet only |
| J2 | **3** | `s_j2_t` coefficient = 1 per hour | reserve shortfall (Wh) |
| J3 | **2** | `p_diesel_t`: 0.00025·Δt; `u_diesel_t`: 5.0·Δt; `v_start_t`: 2.0 | fuel (L) + startup (L) |
| J4 | **1** (lowest) | `p_curt_sol_t`, `p_curt_wind_t`: Δt | curtailment |

Not in the objective: `p_served`, `p_unmet` (non-critical), `p_chg`, `p_dis`, `p_flex`, `E_next`, battery degradation (no term exists). `[VERIFIED]`

### 2.5 HiGHS options

- `output_flag = False`, `threads = 1`, `blend_multi_objectives = False`. Set at lines 386–388. `[VERIFIED]`
- No MIP gap, feasibility, or primal tolerance is overridden. The extractor's own docstring (line 7) lists "HiGHS default tolerances." `[VERIFIED]`
- Integrality: `changeColIntegrality` for the 4 binaries per hour. `[VERIFIED]`
- `mip_gap` is recorded per step. For all 51 target origins at hour 0 it is 0.0 or below 1e-4. `[VERIFIED]` (telemetry)

### 2.6 Post-solve processing

- Residue correction (τ = 0.055 W) on raw `p_chg`, `p_dis` before `DispatchPlan` construction. `[VERIFIED]`
- The first step's plan is what `execute_step` realizes (`plan.diesel_power[0]`, `battery_charge[0]`, `battery_discharge[0]`). `[VERIFIED]`

---

## 3. Target-Origin List

**Unexplained SW hour-0 diesel (39):** 1, 2, 3, 9, 10, 16, 24, 27, 31, 32, 33, 39, 41, 43, 45, 48, 49, 57, 59, 60, 61, 73, 87, 90, 91, 98, 99, 101, 104, 106, 107, 108, 109, 110, 111, 112, 117, 120, 123.

**Unexplained S hour-0 diesel (12):** 12, 13, 18, 22, 44, 46, 62, 85, 88, 92, 95, 96.
- Of these, **7 run at exactly the 10 kW minimum:** 18, 22, 46, 85, 88, 92, 96.
- The other 5 run at 35–57 kW: 12, 13, 44, 62, 95.

All 51 origins are EMERGENCY-labelled in the telemetry route column (which, per §10.2, is not a MILP input). `[VERIFIED]`

Full horizon vectors for each origin are in the companion JSON.

---

## 4. Hour-0 MILP Input Reconstruction

### 4.1 Common inputs (all origins, all arms)

| Input | Value | Source |
|---|---|---|
| Initial energy / SOC | 100,000 Wh / 50% | `make_initial_state` |
| Battery capacity | 200,000 Wh | `battery.yaml` |
| Min / max energy | 40,000 Wh (20%) / 190,000 Wh (95%) | `battery.yaml` |
| Charge / discharge power limit | 50,000 W each | `battery.yaml` |
| η charge / η discharge | 0.92 / 0.92 | extractor defaults |
| Diesel initial state | `diesel_running = False` (so hour 0 is always a start if ON) | `make_initial_state` |
| Diesel min / max | 10,000 W / 100,000 W | `diesel.yaml` |
| Base fuel | 5.0 L/h | `diesel.yaml` |
| Marginal fuel | 0.00025 L/Wh (0.25 L/kWh) | `diesel.yaml` |
| Startup fuel | **2.0 L** (code default; key `startup_fuel_l` is absent from `diesel.yaml`) | extractor line 148 |
| Initial fuel | 100 L (not seen by the MILP) | `make_initial_state` |
| Terminal target | 100,000 Wh at horizon index 23 | `run_diesel_reduction_campaign.py:82` via `step_configs` |
| Route / operating mode seen by MILP | **NORMAL** | `make_initial_state`; see §10.2 |
| Critical demand | min(11,600, D_j) = 11,600 W at all 24 indices | `adapt_critical_demand_vector` |
| Total demand (step 0) | D_j = max(10,000, round(15,000 + 3,000·cos((j+1)π/12), 2)) | `baseline.py:79`, last observed demand = 15,000 |
| Wind (step 0) | w_j = max(0, round(4,500 + 5,000·sin((j+1)π/6), 2)): 7,000; 8,830.13; 9,500; 8,830.13; 7,000; 4,500; 2,000; 169.87; 0 … | `baseline.py:75` with L₀ = 4,500 |

Demand at index 0 is 17,897.78 W; the minimum over the horizon is 12,000 W. Critical demand is capped at 11,600 W at every index, so the critical-load cap is always binding. `[VERIFIED]`

### 4.2 Per-origin inputs

The following vary by origin and are in the companion JSON:
- **Solar horizon [0:24]:** the step-0 bundle's solar forecast. `[VERIFIED]` that for hours 0–18 it equals the recorded per-hour `forecast_solar`, because solar forecasts are time-invariant across steps (solar-only reserve vectors reproduce exactly, §7.1).
- **Low-sun flags [0:24]:** from `SolarElevationProvider` (Etc/GMT-1 convention). `[VERIFIED]`
- **EBR horizon [0:24]:** the adapter's window formula with the **truncated** window `min(t+6, 24)` at the step-0 bundle (`stage4_low_sun_adapter.py:179`). For hours 0–18 the window lies inside the day, and the logged per-hour `ebr_target_wh` reproduces exactly for S, S-L, and SW-L, and for SW at index 0 (§7.1). For indices 19–23 the truncated window is determined by the formula but is not cross-validated against telemetry. `[VERIFIED]` for 0–18; `[INFERRED]` for 19–23.
- **Terminal:** `max(ebr[23], 100,000)` (extractor lines 209–212). Since ebr[23] ≤ 75,652 Wh in every origin, the effective value is 100,000 Wh. `[VERIFIED]`

### 4.3 Recorded hour-0 plan and outcome (per origin)

Recorded in the companion JSON for each origin: `diesel_w`, `p_diesel_var_w`, `u_diesel`, `v_start`, corrected `p_chg`, corrected `p_dis`, `j2_shortfall_wh`, `mip_gap`, solver status, residue flag, and the realized hour-0 charge, curtailment, unmet, and SOC.

Summary across the 51 target origins:
- Solver status: `HighsModelStatus.kOptimal` for all 51. `[VERIFIED]`
- J2 (`j2_shortfall_wh`) at hour 0: **0.0 for every arm and every origin.** `[VERIFIED]`
- Discharge at hour 0: 0 in all 39 SW origins and 12 S origins (corrected `p_dis = 0`). `[VERIFIED]`
- Curtailment at hour 0: 0 in all 51 origins. `[VERIFIED]`
- Realized unmet at hour 0: 0 Wh in 44 origins; 603–889 Wh in 7 S origins (see §5.3). `[VERIFIED]`
- Residue correction fired at hour 0 in 3 SW origins (61, 99, 106), each zeroing a sub-picowatt battery flow. Not decision-relevant. `[VERIFIED]`

---

## 5. Constraint-by-Constraint Analysis

Each item states the mechanism, the constraint evidence, and the verdict on whether it can make hour-0 diesel FORCED, SELECTED, or TIED.

### 5.1 A — Critical-load feasibility (J1, Layer B)

- **Evidence:** critical demand at hour 0 is 11,600 W. Wind at hour 0 is 7,000 W (forecast). Solar at hour 0 is 0–547 W. Without diesel, the critical load needs battery discharge of at least 11,600 − 7,000 − s₀ ≈ 3,000–4,600 W. `[VERIFIED]`
- **Bus balance with diesel-off and charge c > 0:** supply = w + s ≤ 7,547 W; served_crit ≥ 11,600 − u_crit; hence u_crit ≥ 4,053 + c W. A diesel-off solution that charges at hour 0 must therefore carry a hour-0 critical shortfall of at least 4.05 kWh, which is J1-penalized at the top priority. `[VERIFIED]` (arithmetic from R3, R4, LB, and R7)
- **Verdict:** critical feasibility alone does **not** force diesel at hour 0. Diesel-off with discharge serves the critical load (no critical unmet at hour 0). It is the reserve term (5.2) that requires charging. `[VERIFIED]`

### 5.2 B — Reserve feasibility (J2, Layer C)

- **Structure:** E_next_t + s_j2_t ≥ e_stage2_t + 40,000 for every index t, with s_j2 ≥ 0 and penalized at priority 3. The reserve is **soft**. `[VERIFIED]`
- **Index 0 for SW-L:** e_stage2_0 ≥ 63.04 kWh in every origin, so the requirement is ≥ 103.04 kWh. Diesel-off with no charge leaves E_0 ≤ 100 kWh, so s_j2_0 ≥ 3.04 kWh. `[VERIFIED]` (R8 with no charge and no discharge; the case with discharge is worse)
- **Index 0 for SW, S, Control:** e_stage2_0 ≤ 60 kWh in every SW origin (mean 17.7 kWh), so diesel-off at index 0 has zero shortfall. The index-0 reserve does **not** force diesel for these origins. `[VERIFIED]`
- **Later indices:** for indices 1–23, the reserve can be met by charging at any hour ≤ index with diesel or with solar where available. Whether the recorded diesel-on hour-0 solution is needed to meet a later index cannot be decided without solving. `[UNKNOWN]`

### 5.3 C — Terminal reserve (Layer C, index 23)

- The terminal target at index 23 is max(ebr₂₃, 100,000 Wh), i.e., 140 kWh total energy (SOC 70%) at the end of horizon hour 23. `[VERIFIED]`
- **Whether it drives hour 0 is `[UNKNOWN]`.** The step-0 bundle covers origin hours 0–23, so index 23 is the origin day's hour 23. Whether day renewables alone can raise energy from ~100 kWh to 140 kWh is an energy-balance question the frozen constraint set answers only by solving. `[UNKNOWN]`
- **Observation (not evidence of causation):** the recorded plan's end-of-hour-0 energy is ~133–146 kWh in some SW origins (e.g., origin 61: 143.7 kWh; origin 91: 140.2 kWh). This is consistent with, but does not establish, a terminal-driven charge. `[INFERRED]` as a consistency check only.
- **Realized SOC at hour 23 reaches 70% in only 33% (SW) and 47% (S) of origins** (previous report §6.4). `[VERIFIED]`

### 5.4 D — Battery SOC trajectory (R8)

- E_next is the planned trajectory. R8 links consecutive hours. Hour 0 has the initial energy as its RHS. `[VERIFIED]`
- The hour-0 charge determines E₀, which bounds all later indices by the battery transition, so it is the only energy source before hour 1. `[VERIFIED]`

### 5.5 E — Battery charge/discharge limits (R5, R6, R7)

- Charge limit 50 kW. In **5 SW origins (61, 91, 109, 110, 117) the recorded plan charges at exactly 50,000 W**, i.e., the rate limit is active. `[VERIFIED]`
- In those 5 origins the realized charge (43.7–44.0 kW) is less than the plan (50 kW). The gap is covered by the non-critical shedding in §5.7. `[VERIFIED]`
- Discharge is zero at hour 0 in all target origins, so R7 is inactive at hour 0. `[VERIFIED]`

### 5.6 F — Diesel minimum output (R9)

- Diesel must be ≥ 10 kW when ON. For the 7 S origins at exactly 10,000 W (18, 22, 46, 85, 88, 92, 96), **R9 is binding at hour 0**: the planner wanted less than 10 kW of diesel output, but the minimum forced 10 kW. `[VERIFIED]` (telemetry `p_diesel = 10000.0`)
- Consequence: the 10 kW minimum adds 10 kW of supply; with critical 11.6 kW and wind 7 kW, that supply is partly absorbed into a 4.9–5.4 kW plan charge. `[VERIFIED]` (plan `corrected_p_chg` 4,900–5,400 W)
- **Verdict for these 7 origins:** the hour-0 diesel is required by R9 **only if** the optimizer wanted to run diesel at all. Whether it wanted to is the question in §5.9. `[UNKNOWN]`

### 5.7 G — Diesel maximum output (R10)

- Not binding at hour 0. Largest recorded hour-0 diesel is 54,600 W against a 100,000 W maximum. `[VERIFIED]`

### 5.8 H — Diesel startup binary (R11)

- `initial_diesel_running = False`. Hour 0 ON therefore sets v_start₀ = 1. In all 123 origins for SW-L and Control, and in the 94 S and 39 SW ON origins, `v_start_0 = 1` exactly when diesel is ON. `[VERIFIED]`
- The startup binary is a binary coupling term (P). Its cost is in J3 (§5.9).

### 5.9 I/J/K — Diesel startup, base, and marginal fuel cost (J3)

- J3 coefficients: marginal 0.00025·Δt per W, base 5·Δt per on-hour, startup 2.0 per start. **All three are constant in t.** `[VERIFIED]` (code lines 375–381)
- **Consequence:** the fuel objective has no time preference. Any feasible reshuffling of a diesel block between hours, with the same kWh, on-hours, and starts, leaves J3 unchanged. This is the structural basis for a TIED or degenerate classification (§7). `[INFERRED]`
- Per-hour diesel cost at hour 0: 5 L base + 0.25 L/kWh marginal + 2 L startup. For a 54.6 kW hour: 5 + 13.65 + 2 = 20.65 L in the MILP objective (18.65 L accounted). `[VERIFIED]`

### 5.10 L — Battery degradation

- **No degradation term exists** in the objective or constraints. `[VERIFIED]` (absence in code, extractor lines 352–381 and 384–415)

### 5.11 M — Curtailment (J4, R1–R2)

- Curtailment appears only in J4, the lowest priority. At hour 0, curtailment is zero in all target origins (no renewable surplus). `[VERIFIED]`
- J4 cannot force diesel: lowering curtailment would require more supply, which is not available at hour 0. `[VERIFIED]`

### 5.12 N — Unmet load

- **Critical unmet** (J1) is penalized at the top priority. At hour 0 it is zero in all target origins (realized, §4.3). `[VERIFIED]`
- **Non-critical unmet** (p_unmet) carries **no objective term** and is bounded only by demand (R4). The MILP can therefore shed non-critical load for free. `[VERIFIED]` (code: c1 has only `unmet_crit`; p_unmet has no coefficient)
- This is the mechanism in §5.13 below.

### 5.13 Non-critical load shedding and the flexible-load variable (P, Q)

- Served non-critical load (`p_served − critical part`) and the flexible variable `p_flex` (0–500 W) carry **no cost** in J1–J4. `[VERIFIED]`
- R3 lets the optimizer trade served non-critical load for battery charge at no objective cost, bounded by supply. `[VERIFIED]`
- **Identity test:** for the 39 SW origins, `corrected_p_chg − battery_charge` (plan minus realized charge) equals the non-critical demand 6,297.8 W to within 50 W in 21 origins (54%). The median absolute residual is 18.5 W. Maximum residual 1,132 W. `[VERIFIED]`
- **Interpretation:** consistent with the plan serving only the critical load at hour 0, and with the residual bounded by `p_flex` (≤ 500 W) and by solar forecast-versus-actual differences. Not every origin is fully reconciled. `[INFERRED]` for the full mechanism; `[VERIFIED]` for the numeric identity in the majority.

### 5.14 O — Lexicographic objective ordering

- Priority: J1 (4) > J2 (3) > J3 (2) > J4 (1). Implemented via HiGHS priority values; `blend_multi_objectives = False`. `[VERIFIED]`
- **Effect on SW-L:** J2 = 0 at the recorded optimum (hour 0). Any diesel-off solution has J2 ≥ 3.04 kWh at index 0, unless it carries a J1 hour-0 shortfall of at least 4.05 kWh (§5.1). Either way it is lexicographically worse than the recorded solution at the hour-0 level. `[VERIFIED]` for the index-0 arithmetic.
- **Limit of this argument (§6.3):** J1 is evaluated over the whole horizon, not hour 0. A diesel-off solution could in principle lower global J1 by keeping energy for later hours. The realized record does not show that later unmet is energy-limited (§6.4), so this alternative is not excluded. `[UNKNOWN]` for that alternative.

### 5.15 P — Binary coupling

- Charge/discharge exclusivity (R7) is inactive at hour 0. Startup coupling (R11) is active (§5.8). Diesel ON/OFF coupling (R9, R10) is active only for the S 10 kW origins (§5.6). `[VERIFIED]`

### 5.16 Q — Minimum generation

- R9 is binding in 7 S origins (§5.6). It is not binding in any SW origin (all SW origins run diesel at ≥ 35 kW). `[VERIFIED]`

### 5.17 R — End-of-horizon constraint

- Terminal index 23 (§5.3). `[UNKNOWN]` whether it drives hour 0.

### 5.18 S — Any constraint that makes hour-0 diesel useful for future hours

- The only mechanism that links hour-0 charge to future hours is R8 (battery transition) together with the future reserve constraints in LC. The future constraint that uses the stored energy is not identified without solving. `[UNKNOWN]`

### 5.19 Route and operating-mode constraint (not in the brief list; found by trace)

- The EM row (`p_dis − p_served ≤ 0`) is added only when the extractor sees `operating_mode == "EMERGENCY"`. The extractor reads `station_state.operating_mode`. The initial state sets it to `"NORMAL"`. The router computes an EMERGENCY assessment but does not write it to station state. The executor carries `operating_mode` forward unchanged. `[VERIFIED]` (router.py, executor line 273, extractor line 95–96)
- **Consequence:** the MILP ran in NORMAL mode for every step of every origin, so the EM row was never active. The EMERGENCY/NORMAL route labels in the telemetry (8,288 EMERGENCY rows, 6,472 NORMAL) describe the router's assessment and are not MILP constraints. `[VERIFIED]`

---

## 6. Forced vs Selected vs Tied Classification

### 6.1 SW-L hour-0 diesel (123/123 ON)

**SELECTED.** `[VERIFIED]` at the index-0 level; `[INFERRED]` at the global level.

- Diesel-off, no-charge: index-0 shortfall ≥ 3.04 kWh → J2 > 0 vs recorded J2 = 0. Lexicographically worse.
- Diesel-off, with hour-0 charge: impossible without diesel (no surplus, §5.1), except by incurring a hour-0 critical shortfall ≥ 4.05 kWh (J1 worse at the hour level).
- Therefore no diesel-off solution attains the recorded hour-0 lexicographic position. A diesel-on solution is feasible and preferred. The frozen model does not make the reserve a hard constraint, so this is not FORCED.

### 6.2 SW hour-0 diesel (39 unexplained ON origins)

**UNKNOWN.** `[UNKNOWN]`

- No index-0 shortfall is avoided by diesel: the index-0 requirement is ≤ 60 kWh and the start is 100 kWh. J2 at index 0 is zero without diesel. `[VERIFIED]`
- The hour-0 charge does not come from the critical load. It comes from non-critical load shedding (§5.13) and the 50 kW rate limit in 5 origins (§5.5).
- Which later constraint values the hour-0 charge (later reserve index, terminal, or J1) is not identified without solving. A TIED structure is structurally plausible (§7.2), but is not demonstrated. A SELECTED structure by a later constraint is equally consistent with the record. The record does not decide between them. `[UNKNOWN]`

### 6.3 S hour-0 diesel (12 unexplained ON origins)

**UNKNOWN.** `[UNKNOWN]`

- **7 origins at the 10 kW minimum (18, 22, 46, 85, 88, 92, 96):** diesel is ON at minimum output and charges 4.9–5.4 kW while shedding 0.6–0.9 kWh of realized non-critical load. The optimizer chose diesel at the lowest allowed output; R9 forces the 10 kW floor, but does not decide whether diesel runs at all. `[VERIFIED]` for the numbers, `[UNKNOWN]` for the reason.
- **5 origins at 35–57 kW (12, 13, 44, 62, 95):** no distinguishing feature in the recorded data. `[UNKNOWN]`

### 6.4 Global-J1 caveat (applies to SW-L and to the classification boundary)

- Realized critical unmet is positive in all 123 SW-L origins over the day (max 58.2 kWh per origin). `[VERIFIED]` So the optimum's J1 is not zero globally, and J1 cannot be used as a zero-level tie-breaker.
- The realized record shows that critical unmet is almost never at the SOC floor (0.4% of SW-L realized critical unmet energy; 0% for S and Control). `[VERIFIED]` This does not support an argument that stored energy at hour 0 would reduce later unmet.
- Consequently the SW-L SELECTED label rests on the index-0 J2 argument. A global-J1 alternative is not excluded. `[UNKNOWN]` for that alternative.

---

## 7. Solver Degeneracy Analysis

### 7.1 What is verified

- `mip_gap` is 0.0 for the target origins (except one S origin at 6.5e-5 and one at 8.9e-5). The solver reports optimality. `[VERIFIED]`
- Residue correction fired at hour 0 in 3 origins, zeroing flows of order 1e-11 W. Numerical, not decision-relevant. `[VERIFIED]`
- The fuel objective is constant in time (§5.9). `[VERIFIED]`

### 7.2 Degeneracy candidates

| Source | Present? | Evidence |
|---|---|---|
| Multiple optimal solutions | **Possible** | Time-invariant J3 with block-shift freedom (§5.9). Not demonstrated. `[INFERRED]` |
| Zero-cost variables | **Yes** | p_served, p_unmet (non-critical), p_flex, E_next at unconstrained indices carry no cost. `[VERIFIED]` |
| Objective ties | **Possible** | At J2 = 0 and J1 at the same level, J3 decides; J3 has no time preference. `[INFERRED]` |
| HiGHS lexicographic behaviour | Present by design | Priority ordering applied sequentially. `[VERIFIED]` |
| Numerical tolerance | Negligible at hour 0 | Residues ~1e-11 W. `[VERIFIED]` |
| Binary degeneracy | Possible | Startup binary has no time preference (§5.8–5.9). Not demonstrated. `[INFERRED]` |
| Deterministic but arbitrary incumbent | **Possible, not excluded** | The record cannot distinguish a unique optimum from one of several equal-cost optima. `[UNKNOWN]` |

### 7.3 What this means for the report

- For **SW-L**, the diesel-on solution is preferred by a strict lexicographic margin at the index-0 level (§6.1). Degeneracy is not the explanation there.
- For **SW and S (unexplained)**, the recorded diesel-on solution may be one of several equal-cost optima. The record does not show this. It is therefore **not** labelled a physical necessity. `[UNKNOWN]`

---

## 8. S / SW / SW-L Divergence Mechanism

### 8.1 Forecast/constraint/objective differences at hour 0

| Quantity at hour 0 | S | SW | SW-L |
|---|---|---|---|
| Solar credit in reserve window | solar forecast × 1 | solar forecast × 1 | solar × (1 − L_k) = 0 wherever L = 1 |
| Wind credit in reserve window | none | forecast wind (7,000 → 2,000 …) | wind × (1 − L_k) = 0 wherever L = 1 |
| Index-0 reserve | mean 64.2 kWh | mean 17.7 kWh | mean 71.5 kWh, minimum 63.0 kWh |
| Index-0 requirement vs 100 kWh start | above in 82/123 | never above (0/123) | above in 123/123 |
| Diesel ON at hour 0 | 94/123 | 39/123 | 123/123 |
| Diesel ON not explained by index 0 | 12 | 39 | 0 |
| Reserve constraint type | soft (priority 3) | soft (priority 3) | soft (priority 3) |
| Fuel objective | identical | identical | identical |

`[VERIFIED]`

### 8.2 The specific difference

- **The forecast difference is the wind credit (SW, SW-L) and the low-sun removal (SW-L, S-L).** The fuel objective and the reserve formulation are identical across the three arms. `[VERIFIED]`
- **S vs SW-L:** SW-L's protected reserve equals Control's reserve (75.65 kWh) wherever L is 1 across the window. That makes the index-0 requirement exceed the 100 kWh start in all 123 origins, so diesel is selected in all 123 under J2. S keeps the solar credit, so its requirement falls below 100 kWh in 41 origins, and J2 does not select diesel there. `[VERIFIED]`
- **SW vs S:** SW's requirement is far below 100 kWh in every origin, so the index-0 J2 term does not select diesel in SW. SW's 39 hour-0 diesel decisions therefore come from a term that is not the index-0 reserve. `[VERIFIED]` that the index-0 term is absent; `[UNKNOWN]` which term is present.
- **Why SW has more unexplained hour-0 diesel than S:** SW's requirements are lower overall, so SW has more energy at hour 0 and fewer index-0 forcings. Whether that makes later-index or terminal requirements more or less likely to drive hour-0 charging is `[UNKNOWN]` without solving.

I am **not** attributing SW's difference to "wind" in general. The specific mechanism is the forecast wind offset (L_t = realized previous-hour wind, §forensic-report §4) and the index-0 reserve it produces. `[VERIFIED]`

---

## 9. Fuel-Accounting Implications

### 9.1 Components

| Component | MILP objective (J3) | Simulator (executor) |
|---|---|---|
| Base | 5.0 L × on-hours | 5.0 L × on-hours (exact) |
| Marginal | 0.25 L/kWh × diesel energy | 0.25 L/kWh × diesel energy (exact) |
| Startup | **2.0 L × starts** | **not charged** |

`[VERIFIED]`

### 9.2 Is the startup component constant across arms?

**No.** Start counts: Control 308, S 236, S-L 284, SW 161, SW-L 267. `[VERIFIED]`

### 9.3 Quantified effect on the diesel-reduction comparison

| Arm | Accounted fuel (L) | MILP-objective fuel (L) | Reduction, accounted | Reduction, MILP-objective |
|---|---|---|---|---|
| Control | 6,117.97 | 6,733.97 | — | — |
| S | 4,648.33 | 5,120.33 | 24.02% | 23.96% |
| S-L | 5,334.13 | 5,902.13 | 12.81% | 12.35% |
| SW | 3,885.02 | 4,207.02 | 36.50% | **37.53%** |
| SW-L | 5,221.32 | 5,755.32 | 14.66% | 14.53% |

`[VERIFIED]` (MILP-objective fuel = accounted + 2.0 × starts; computed from frozen telemetry.)

**Interpretation:**
- The ranking S-L < SW-L < S < SW is unchanged under either accounting. `[VERIFIED]`
- The S vs SW-L gap changes from 9.36 pp to 9.43 pp. `[VERIFIED]`
- The largest change is SW: +1.03 pp under MILP-objective accounting, because SW has the fewest starts. `[VERIFIED]`
- Startup is 7.7–9.6% of the MILP objective depending on arm. `[VERIFIED]`
- **The frozen Stage 4 fuel totals are not altered.** This is a sensitivity statement, not a correction. `[VERIFIED]`

### 9.4 What the mismatch means

- The optimizer minimized a fuel objective that charges startups; the reported comparison does not. The reported diesel reduction is the accounted fuel, which is the physically relevant quantity. The optimizer was therefore slightly biased against starts relative to the accounting. `[INFERRED]` that this affects which hour-0 solution is chosen. `[UNKNOWN]` by how much.

---

## 10. Fuel-Cap Implications

### 10.1 Occurrence

- Each origin starts with 100 L. No refuelling. The MILP does not see this. `[VERIFIED]`
- **Two origins reach the cap:** S origin 39 and SW-L origin 39. Both hit it at **hour 22**. `[VERIFIED]`
- No other arm reaches it. Control's maximum is 85.07 L; S-L's is 94.43 L; SW's is 98.04 L. `[VERIFIED]`

### 10.2 Connection to hour-0 unexplained diesel

- **None.** Maximum possible hour-0 fuel is 5 + 0.25 × 54.6 = 18.65 L, far below 100 L. The cap cannot bind at hour 0. `[VERIFIED]`
- Origin 39 is in the SW unexplained list. Its hour-0 diesel is not connected to the cap, since the cap is reached at hour 22. `[VERIFIED]`

### 10.3 Effect on the fuel comparison

- In origin 39, accounted fuel is capped: S 100.0 L, SW-L 100.0 L, Control 75.26 L, S-L 94.43 L, SW 87.22 L. `[VERIFIED]`
- The uncapped planned fuel for S and SW-L in origin 39 is not recorded. The effect on each arm's total is therefore **UNKNOWN** in magnitude, but bounded by the planned-but-undelivered diesel after hour 22 for that origin. `[UNKNOWN]`
- One origin of 123 is affected. The comparison can change only through that origin's diesel and reliability. `[INFERRED]`

---

## 11. Planned vs Realized Battery

### 11.1 What the MILP planned at hour 0

- Planned charge: `corrected_p_chg` (recorded). Planned discharge: `corrected_p_dis` (recorded). Planned diesel: `diesel_power` (recorded, equal to `p_diesel`). `[VERIFIED]`
- The MILP's planned energy E_next at hour 0 is **not** recorded directly. It is implied by R8 from the initial energy and the planned charge and discharge. `[INFERRED]` for the implied value.

### 11.2 What the simulator realized

- Realized diesel equals planned diesel in all target origins at hour 0 (no starvation). `[VERIFIED]`
- Realized charge is the **surplus rule** (executor §6): charge = min(surplus after serving demand, charge rate, room). It is **not** the planned charge. `[VERIFIED]`
- Realized served load = min(demand, supply). Realized non-critical load is served first. `[VERIFIED]`

### 11.3 Why they differ (code)

1. The MILP serves only the critical load at hour 0 (§5.13). The executor serves all demand it can. `[VERIFIED]` (identity in §5.13)
2. The MILP's charge is a decision variable bounded by supply; the executor's charge is the residual. `[VERIFIED]`
3. Actual solar and wind differ from forecast (for solar at hour 0: 0–547 W forecast; actual is not separately recorded at hour 0 in the companion). `[INFERRED]` a minor source at hour 0.

### 11.4 Is the hour-0 diesel decision based on planned or realized quantities?

**Planned.** The MILP chooses hour-0 diesel using planned quantities (forecast-based reserve targets, planned charge and discharge, and the planned E_next). The realized battery trajectory then differs. `[VERIFIED]`

### 11.5 Does this invalidate Stage 4?

- The diesel decision is made on the planned state. The realized diesel equals the planned diesel. The **accounted fuel is therefore the realized outcome of the planned decision**, which is consistent with the frozen evaluation design. `[VERIFIED]`
- The planned-vs-realized gap affects the **SOC interpretation** (realized SOC at hour 23 reaches 70% in only 33–53% of origins), not the fuel accounting. `[VERIFIED]`
- The brief asks us not to treat this as automatically invalidating. This report does not. The gap is recorded and bounded. `[VERIFIED]`

---

## 12. Proven / Inferred / Unknown

**[VERIFIED]**
- Optimizer identity, hash, class, inheritance, and `super()` usage (§2).
- MILP construction: 408 columns, 312 rows in NORMAL mode, four lexicographic objectives with priorities 4/3/2/1 (§2.3–2.4).
- The hour-0 step-0 reserve vector for S, S-L, and SW-L equals the logged per-hour reserve on hours 0–18 exactly (§4.2).
- Index-0 arithmetic: SW-L requirement ≥ 103.04 kWh vs 100 kWh start; diesel-off with no charge leaves shortfall ≥ 3.04 kWh (§5.2, §6.1).
- No renewable surplus at hour 0 in any origin (§5.1).
- J2 = 0 at hour 0 for every arm and origin (§4.3).
- Constant time coefficients in J3 (§5.9).
- Non-critical served and unmet load and `p_flex` carry no objective cost (§5.13).
- EMERGENCY row never active (§5.19).
- Planned-minus-realized charge equals non-critical demand within 50 W in 54% of unexplained SW origins (§5.13).
- Startup counts differ across arms, and the MILP-objective reduction differs from the accounted one by −0.46 to +1.03 pp (§9).
- Fuel cap reached in origin 39 by S and SW-L at hour 22 (§10).

**[INFERRED]**
- SW-L's hour-0 diesel is SELECTED because of the index-0 J2 term (§6.1), with a global-J1 caveat.
- The hour-0 charge in SW and S unexplained origins is funded by non-critical load shedding, which costs nothing in the objective (§5.13).
- J3's time-invariance makes TIED structures plausible for SW and S (§5.9, §7.2).
- The startup mismatch biases the optimizer slightly against starts (§9.4).

**[HYPOTHESIS]** (not solved; each needs an altered-model experiment that this task forbids)
- H-S1: the 12 unexplained S hour-0 origins are driven by a later-index reserve or the terminal, with diesel placed at hour 0 by tie-breaking.
- H-S2: the 7 S origins at 10 kW minimum are selected because a small hour-0 charge reduces a later J2 term at a cost below alternatives.
- H-SW1: the 39 unexplained SW origins are driven by the terminal at index 23 combined with J3 consolidation.
- H-SW2: the 39 SW origins are TIED: equal-cost diesel placement across hours.

**[UNKNOWN]**
- Which constraint (later reserve index, terminal, or J1) values the hour-0 charge in SW and S unexplained origins.
- Whether any diesel-off solution attains the same global lexicographic optimum (requires a solve).
- Dual values, which the artifacts do not record.
- Planned E_next at hour 0 (not logged).
- Actual solar and wind at hour 0 relative to forecast in the companion (not separately logged).
- Uncapped planned fuel for origin 39 (S and SW-L).
- The full reason for the 2 MILP-visible route labels mismatch beyond §5.19.

---

## 13. Governance Decision

| # | Question | Answer | Reason |
|---|---|---|---|
| A | Is the hour-0 SW behaviour causally explained? | **NO** | 39 origins unexplained; the candidate constraints are identified but not decided. |
| B | Is the hour-0 S behaviour causally explained? | **NO** | 12 origins unexplained; 7 at the 10 kW minimum with no decided cause. |
| C | Is the SW/SW-L reserve pathway fully understood? | **YES** (pathway); **NO** (binding behaviour) | Inputs, truncated windows, wind provenance, and Layer C are reconstructed for step 0 and verified for hours 0–18. Which later indices bind is not determined. |
| D | Is the terminal implementation fully understood? | **YES** (implementation); effect on hour 0 **NO** | The 100,000 Wh target at index 23 of the step-0 horizon, soft in Layer C, is verified. Whether it drives hour-0 diesel is not. |
| E | Is the fuel-accounting boundary fully understood? | **YES** | Base and marginal are identical in both places. Startup is 2.0 L in the MILP only, with the arm-dependent effect quantified in §9.3. |
| F | Is the frozen Stage-4 comparison numerically valid as a research result? | **CONDITIONAL** | See the conditions below. |
| G | Is it valid to design the next experiment? | **NOT YET** | A and B are NO. The §14 evidence is missing. |

**Conditions for F (CONDITIONAL):**
1. The MILP ran in NORMAL mode throughout; the EMERGENCY constraint was never active. The research claims must say so. `[VERIFIED]`
2. The MILP optimizes a fuel objective with 2.0 L startups that the accounting does not charge. The diesel-reduction ranking is unchanged, but the magnitudes differ by up to 1.03 pp. `[VERIFIED]`
3. Origin 39 caps S and SW-L's fuel at 100 L at hour 22. The effect is unquantified and confined to one origin. `[VERIFIED]` / `[UNKNOWN]`
4. Realized wind and demand enter the forecast through state persistence. This conflicts with the preregistration's "never in a plan" language. This is a governance question, not a computational error. `[VERIFIED]`
5. Realized and planned battery trajectories differ (§11). This affects SOC interpretation, not fuel accounting. `[VERIFIED]`

**Research result numerically valid is not production-valid.** The frozen campaign reproduces from its telemetry and code. It is a research result under a research MILP, and it is not a production validation.

---

## 14. Whether a Next Experiment Is Now Justified

**NOT YET.**

What is missing (none of these requires a campaign rerun, but each requires either a solver trace under explicit authorization or a governance decision):

1. **Solver-level dual or constraint-activity trace at hour 0** for the 51 target origins, from the frozen model with its recorded inputs. This would decide the binding later constraint and SELECTED vs TIED. It is an altered-model experiment only if diesel is fixed; a plain trace of the frozen solve is not. Authorization is needed.
2. **Planned E_next at each hour** from the frozen model's solution, to compare planned and realized trajectories directly.
3. **Governance decision on the startup cost**: whether starts belong in the objective, the accounting, both, or neither, with the source value.
4. **Governance decision on the NORMAL-mode MILP**: whether the research claims must be restated for NORMAL-only optimization.
5. **Governance decision on realized-state persistence** in the forecast (§13 F4).
6. **Governance decision on the non-critical shedding** freedom: whether non-critical load should carry an objective cost. Any change would be a new preregistered convention, not a correction.

Until items 1 and 2 are answered, the hour-0 mechanism for the 51 unexplained SW and S origins, and the causal basis of the SW-vs-SW-L difference beyond the index-0 term, are not established.

---

## 15. Current Project Status

- **CURRENT FROZEN RESEARCH WINNER: S — 24.02% diesel reduction (accounted fuel), safety-qualified.** Retained. The frozen numbers are not shown to be wrong. `[VERIFIED]`
- **SW:** 36.50%, safety failure (proportional −0.356 pp). Unchanged. `[VERIFIED]`
- **SW-L:** 14.66%, safety-qualified. Unchanged. `[VERIFIED]`
- **S-L:** 12.81%, safety-qualified. Unchanged. `[VERIFIED]`
- **40% target:** not achieved.
- **Production superiority:** **not claimed.**
- **S production-validated: NO.**

---

## 16. Required Final Response

**STATUS:** COMPLETE (trace); classification partial.

**SW HOUR-0:** UNKNOWN (39 origins).

**S HOUR-0:** UNKNOWN (12 origins).

**SW-L HOUR-0:** SELECTED (123 origins, not FORCED; the reserve is soft at priority 3 above fuel at priority 2).

**PRIMARY MECHANISM:** SW-L: the soft index-0 reserve penalized at J2 (priority 3), above fuel (priority 2), with zero renewable surplus at hour 0 and a 100 kWh start below the protected requirement of at least 103 kWh. Directly demonstrated at the index-0 level.

**SECONDARY MECHANISM:** the MILP prices neither non-critical served load nor the flexible-load variable, so the plan sheds non-critical load to charge the battery at hour 0. The realized charge differs as a consequence (identity verified in 54% of unexplained SW origins within 50 W).

**UNRESOLVED MECHANISM:** the later-index or terminal constraint that values the hour-0 charge in the unexplained S and SW origins.

**CURRENT FROZEN RESEARCH WINNER:** S — 24.02%

**IS S PRODUCTION-VALIDATED:** NO

**IS STAGE 4 INVALID:** CONDITIONAL. It is not invalid as a research result under the frozen research MILP. Its validity is conditional on: NORMAL-mode-only optimization (EMERGENCY constraint never active), the startup mismatch (magnitudes up to 1.03 pp), the origin-39 fuel cap (unquantified), and the governance question on realized-state persistence.

**IS NEXT EXPERIMENT JUSTIFIED:** NOT YET.

### Strongest evidence

1. **Index-0 arithmetic and J2 priority for SW-L** (§5.2, §6.1): SW-L requirement ≥ 103.04 kWh, start 100 kWh, zero hour-0 renewable surplus, J2 = 0 at the recorded optimum for every arm.
2. **Constraint and objective extraction** from the frozen extractor: 408 columns, 312 rows, four priorities 4/3/2/1, soft reserve, non-critical load unpriced, startup 2.0 L in J3 only.
3. **Step-0 reserve reconstruction** matching the logged reserve exactly for S, S-L, and SW-L on hours 0–18 (0.0 Wh error, §4.2).
4. **EMERGENCY row never active** (router does not write station state; executor carries NORMAL forward), from code and the telemetry route labels (§5.19).
5. **Planned-minus-realized charge identity** equal to non-critical demand within 50 W in 21 of 39 SW origins (§5.13).
6. **Startup sensitivity** (§9.3): the ranking S-L < SW-L < S < SW is unchanged, and the largest change is +1.03 pp for SW.

Limits of these results: no altered solve was run, so the SW and S unexplained origins remain UNKNOWN. The §14 evidence is the next step.
