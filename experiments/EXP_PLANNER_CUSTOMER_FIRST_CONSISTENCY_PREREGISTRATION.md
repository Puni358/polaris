# POLARIS Preregistration: Customer-First Planner/Realization Consistency (Planner-CF v1)

**Experiment identifier:** `EXP-PLANNER-CF-CONSISTENCY-2025`
**Design version:** `PLANNER-CF-PREREG-v1.1` (supersedes v1.0; corrections B1–B6 from review)
**Date (UTC):** 2026-10-06
**Governance status:** `PREREGISTRATION + IMPLEMENTATION HASHED AND TESTED — CAMPAIGN NOT RUN` (final freeze on authorization to execute; hashes in §16 and in the JSON)
**Governing decision:** `experiments/POST_STAGE4_GOVERNANCE_DECISION_RECORD.md` — customer-first realization policy. Arm A governs. Arm B is quarantined and is not used anywhere in this study.

**Referenced artifacts (read, not modified):** `experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md`; `experiments/stage4_corrected_reproduction_2025/`; `experiments/POST_CORRECTED_STAGE4_FORENSIC_AUDIT.md`; `experiments/POST_CORRECTED_STAGE4_HOUR0_TRACE.md`; `experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.md` (quarantined); `experiments/POST_STAGE4_REALIZATION_CAUSAL_GOVERNANCE_AUDIT.md`; `experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py`; `data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv`.

**Nothing in this document is a result.** Numbers quoted from earlier artifacts are labelled with their source.

---

## 0. Objective

Determine whether a **customer-first, physically realizable** controller can safely approach or reach the 40% diesel-reduction target relative to Control, and quantify the remaining gap if not. The 40% figure is a benchmark, not a gate, and the study is not required to achieve it.

**Core defect.** The planner charges the battery while Arm-A realization serves total customer demand first and charges only from residual surplus. The planned charge is then unrealizable whenever the plan sheds non-critical load. The fix is made in the planning formulation, not by forcing the executor to shed customers.

---

## 1. Physical and Customer-First Energy Accounting Contract

Per hour `t`, realized quantities (as Arm A), realized demand `D`, critical demand `D_c = min(11,600 W, D)`, non-critical demand `D_nc = D − D_c`:

1. **Supply:** `S_avail = S_pv + W + diesel_realized + discharge_realized`.
2. **Customer service (first):** `s_c = min(D_c, S_avail)`; `s_nc = min(D_nc, S_avail − s_c)`; total `s = s_c + s_nc = min(D, S_avail)`.
3. **Battery charging (after customers):** `C = min(surplus, 50 kW, room to 95% / η_c)`, `surplus = max(0, S_avail − s)`; `C = 0` while discharging.
4. **Curtailment (last):** `curt = S_avail − s − C`.
5. **Energy:** `E' = clamp(E + η_c·C − discharge/η_d, 20%, 95%)`.

With `p_flex` removed (B1), this contract has no unrealized term. A planned charge is realizable exactly when the plan's total served equals the realized customer demand that supply can cover.

**Shortfall ordering.** When `S_avail < D`, Arm A's executor serves `min(D, S_avail)` without a physical critical-first ordering. Its accounting credits critical first. The planner's ordering is critical first (J1 > J_nc). Under shortfall the planned and realized allocations can differ. This is recorded as an audited residual (G5), not corrected.

---

## 2. Where the Current MILP Can Plan Non-Realizable Charging

Verified in `research_numerical_extractor.py` (SHA-256 `95b2f3b53609a6e420a18692b4b0e3927cb47841d9e1200cce04677094a5950e`):

| # | Location | Defect | Effect |
|---|---|---|---|
| D1 | Layer B: `served + unmet_crit = critical` | served bound to critical service only | non-critical service is not a planner variable |
| D2 | R4: `served + unmet = demand` | forces all non-critical demand into unmet | non-critical load shed in every hour |
| D3 | R3 bus balance uses critical served only | charge computed from supply minus critical service | planned charge exceeds realizable `S_avail − D` by the shed amount |
| D4 | Objective `c1`: penalty only on `unmet_crit` | non-critical unmet unpriced | shedding customers is free |
| D5 | `p_flex` ∈ [0, 500 W] in R3, unpriced | a free sink with no executor counterpart | unrealizable in Arm A |
| D6 | Priorities J1(4) > J2(3) > J3(2) > J4(1) | no customer-service term above reserve | reserve can outrank customers |
| D7 | EMERGENCY row `p_dis − p_served ≤ 0` | references critical served | discharge bounded by critical service only |

Demonstrated at hour 0, origin 13 (corrected telemetry): plan critical served 11,600 W, plan unmet 6,297.78 W (= non-critical), planned charge 30,145 W. `[VERIFIED]` (`POST_STAGE4_HOUR0_MILP_CAUSAL_TRACE.md`).

---

## 3. Planner-CF v1: Research-Only Correction

Implemented as a **new** research-only module, `experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py`. It imports the frozen research extractor and does not modify it. Production GAP19 is not touched.

### 3.1 Changes (exhaustive)

- **C1 — Split served load.** `p_served_c` (critical, ≤ D_c), `p_served_nc` (non-critical, ≤ D_nc), `unmet_nc ∈ [0, D_nc]`.
  - Layer B unchanged: `p_served_c + unmet_crit = D_c`.
  - R4 replaced by the non-critical balance: `p_served_nc + unmet_nc = D − D_c`.
  - R3 bus balance uses total served `p_served_c + p_served_nc`.
- **C2 — Objective priorities (complete order, §3.3).**
- **C3 — Remove the flexible sink (B1).** `p_flex` is removed as a planner variable. Its upper bound is fixed to **0 W** and its term is removed from R3. This is a **preregistered change**. The executor has no flexible-load term, so this makes the plan's bus balance match the realized balance.
- **C4 — EMERGENCY row reference (preregistered semantic change E1).** The EMERGENCY-only row `p_dis − p_served ≤ 0` references **total** served `p_served_c + p_served_nc`.

### 3.2 Unchanged

- EBR coefficients and reserve constraint form (Layer C, 6-hour window, η = 0.92, terminal 100,000 Wh at horizon index 23 as implemented).
- Battery: 200 kWh; SOC 20–95%; charge and discharge ≤ 50 kW; η_c = η_d = 0.92.
- Diesel: 10–100 kW when on; base 5 L/h; marginal 0.25 L/kWh; startup 2.0 L in the optimizer objective (U8 option A from the realization study; the simulator accounts 0 L per start).
- Forecasts, causal NWP, router and mode propagation, τ = 0.055 W residue rule, HiGHS options (`threads = 1`, `blend_multi_objectives = False`, default tolerances).
- Simulator fuel accounting.

### 3.3 Complete lexicographic priority (B6)

| Priority | Term | Meaning | Policy class |
|---|---|---|---|
| **5** | J1: `Σ unmet_crit_t · Δt` | critical customer unmet | customer service (critical) |
| **4** | J_nc: `Σ unmet_nc_t · Δt` | non-critical customer unmet | customer service (non-critical) |
| **3** | J2: `Σ s_j2_t` | reserve shortfall | **battery-service requirement** |
| **2** | J3: `Σ (0.00025·p_diesel + 5·u_diesel)·Δt + 2.0·v_start` | fuel and startup | **economic objective, not part of the customer-service hierarchy** |
| **1** | J4: `Σ (curt_sol + curt_wind)·Δt` | curtailment | surplus disposal |

- Policy hierarchy as decided: **critical load > non-critical load > battery charging > curtailment.**
- Reserve (J2) is treated as a **battery-service requirement** that sits below customer service and above fuel. It operates through battery charging, so it is the "battery charging" tier of the policy.
- Fuel (J3) is an economic objective. It is not part of the customer-service hierarchy. It ranks below reserve and above curtailment because the policy does not rank it against either.
- Flexible load is not a term (C3).

### 3.4 Realizability after correction

**Amendment A1 (2026-10-06): the realizability claim of v1.1 is WITHDRAWN.** v1.1 stated that the corrected plan satisfies `C = min(surplus, cap)` at every hour, so planned charge equals realized charge (audit G1). Forensic planned-capture evidence contradicts this: of 72 G1 mismatches, 70 are Class B (equal-objective planner curtailment ties while charging capacity was available) and 2 are Class C (terminal-hour fuel-boundary rows). G1 is unchanged and fails. Class B is NOT admitted and Class C is NOT resolved by Amendment A1. See `experiments/GOV_DECISION_LOWER_BOUND_CERTIFICATION_2026-10-06.md` §4.

## 4. Arms (Exact)

All arms use the Planner-CF v1 optimizer and Arm A realization, with the same 123 origins, causal NWP, initial state (SOC 50%, 100 L, diesel off, last observed demand 15,000 W, last observed wind 4,500 W), router, and mode propagation.

| Arm | Renewable credit in EBR | Low-sun protection | Role |
|---|---|---|---|
| **PC-Control** | none (unconditional governed EBR) | — | new control; gate basis |
| **PC-S** | solar only | OFF | efficiency candidate |
| **PC-SW** | solar + wind | OFF | unprotected candidate |
| **PC-S-L** | solar only | ON (L_k = 1[e_k < 15°]) | protected candidate |
| **PC-SW-L** | solar + wind | ON | protected candidate |
| **ORACLE-PHYS (PRIMARY, diagnostic)** | **no reserve constraint** (Layer C and J2 removed) | — | **the oracle used for NG7** (§6.2) |
| **ORACLE-CTRL (SECONDARY, diagnostic)** | Control EBR | — | secondary diagnostic only |

EBR equations are the frozen equations (corrected preregistration §5). L flags use the frozen 1-hour offset convention, disclosed and not corrected here.

**Runs:** 123 origins × 5 candidate/control arms = **615 closed-loop runs**. ORACLE-PHYS and ORACLE-CTRL each add 123 perfect-foresight closed-loop runs.

---

## 5. Gates (Preregistered Before Execution)

Evaluated against **PC-Control**, the gate basis (same planner, same realization).

**Safety (deterministic, aggregate over 123 origins, 2,952 hours each):**
- **S1 — Critical-first:** `ΔR_CF = R_CF(candidate) − R_CF(PC-Control) ≥ 0.00 pp`, else FAIL.
- **S2 — Proportional:** `ΔR_P = R_P(candidate) − R_P(PC-Control) ≥ 0.00 pp`, else FAIL.
- **S3 — SOC floor:** zero hours with realized SOC < 20.00%, else FAIL.

**Efficiency (statistical; evaluated only if S1–S3 pass):**
- **E1 — Diesel gate:** two-sided paired Wilcoxon signed-rank on `Δ_o = Fuel(PC-Control, o) − Fuel(candidate, o)`, Holm across the four candidate tests (PC-S, PC-SW, PC-S-L, PC-SW-L), adjusted `p < 0.05`; **and** BCa 95% lower bound `> 0.0 L/origin` (10,000 origin resamples, seed 42).

**Report-only (not a gate):**
- **T40:** `(Fuel(PC-Control) − Fuel(candidate)) / Fuel(PC-Control) ≥ 40.0%`, reported PASS/FAIL, not an advancement criterion.

**Winner rule:** highest diesel saving among candidates passing S1–S3 and E1.

---

## 6. Target Mathematics and Feasibility

### 6.1 Target definition

The 40% target is defined relative to **PC-Control of the same run**:
`Fuel_target = 0.60 × Fuel(PC-Control)`; `ΔFuel_needed = Fuel(candidate) − 0.60 × Fuel(PC-Control)`.

### 6.2 Feasibility oracles

**Amendment A1 (2026-10-06): oracle roles.**

- **Certified lower bound (the NG7 object).** A per-origin relaxed global MILP over the 24-hour window: full critical and non-critical service; no fuel inventory; no 10 kW diesel minimum; no reserve; no terminal SOC requirement or value; SOC bounds with a ±2 Wh margin; ±50 kW battery power; diesel maximum 100 kW; charge/discharge exclusivity; busbar balance; renewable availability; objective `5 L × on-hours + 0.00025 L/Wh × diesel energy`, with 0 L per start. Origins are independent (state resets per origin). Implemented in `global_lower_bound.py`. Its per-origin finite dual bounds `d_o` are valid lower bounds on the minimum (Amendment A1, K8).
- **ORACLE-PHYS: achievability benchmark, not a lower bound.** The rolling 24-hour perfect-foresight controller that re-solves each hour and executes hour 0. Its fuel is an achievable-policy result. It cannot independently trigger NG7, and it is not used alone for NG7.
- **ORACLE-CTRL.** Secondary diagnostic (Control EBR). Not used for NG7.

Both rolling oracles remain diagnostic. They use information no deployable controller has and are not deployable. G1 is unchanged and applies to the rolling benchmark only.

### 6.3 Oracle future inputs (B3)

Calendar: origin `o` is `forecast_start` at 2025-MM-DD 00:00 UTC. The hour offset `j` counts from origin 00:00: `j = 0` is 00:00 of the origin day and `j = 23` is 23:00. Each re-solve at step `t` (t = 0…23) uses horizon offsets `j = t … t + 23`, which extend up to offset `j = 46` past the origin day.

- **Solar:** `S_pv(j)` = `min(max(0, SW_IN(T) · 300 · 0.20 · 0.85), 60,000 W)` where `T = origin + j hours` and `SW_IN(T)` is the **actual 2025 SITES SW_IN** value at timestamp `T` in `POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv`. This is the same conversion as the executor's `pv_from_sw_in`. Timestamp labels follow the corrected runner's convention (no correction introduced here).
- **Wind:** `W(j) = max(0, round(4,500 + 5,000 · sin((j+1)·π/6), 2))`. This is the existing synthetic formula used by the corrected runner, with `h = j + 1`, which for `j ∈ [0, 23]` reproduces the recorded realized wind (`actual_wind[k] = formula(k+1)`, verified on the corrected telemetry).
- **Demand:** `D(j) = max(10,000, round(15,000 + 3,000 · cos((j+1)·π/12), 2))`, the existing synthetic formula, with the same `h = j + 1` convention (verified: `actual_demand[k] = formula(k+1)`).
- **Critical:** `D_c(j) = min(11,600, D(j))`.
- **Coverage gate (G12):** the SITES SW_IN file must contain `T` for every origin's full 47-hour window. The last origin, 2025-08-31, needs data to 2025-09-01 22:00. If coverage is absent, that origin is **BLOCKED** and no oracle result is interpreted for that origin.

### 6.4 Reference values (existing artifacts, old planner and old realization)

| Quantity | Value | Source |
|---|---|---|
| Corrected Control fuel (old planner, Arm A) | 6,096.9004 L | corrected summary |
| 40% threshold relative to that Control | **3,658.14 L** | 0.60 × 6,096.9004 |
| Current S fuel | 4,687.6902 L (23.11%) | corrected summary |
| Additional reduction S would need | **1,029.55 L** = 16.89 pp of Control = 21.96% of S | arithmetic |
| Current SW fuel | 3,768.5494 L (38.19%, fails S2) | corrected summary |
| SW reduction needed to reach 40% | 110.41 L (not eligible) | arithmetic |

These old-planner values show the scale of the gap. The study's own threshold is §6.1.

### 6.5 Physical relaxation bound (analytic, offline; not a solve)

From realized Control telemetry, per origin: deficit `Σ max(0, D − (S+W))`; surplus `Σ max(0, (S+W) − D)`; battery credit `η_d·(E0 − E_min) + η_c·η_d·min(surplus, 150 kWh)`; diesel energy lower bound `E_LB = max(0, deficit − credit)`; runtime `≥ ⌈E_LB / 100 kWh⌉`; fuel `LB = 0.25·E_LB + 5·runtime`. Over 123 origins: deficit 17,385.6 kWh; surplus 13,214.8 kWh; `E_LB` 3,270.1 kWh; **fuel LB 1,162.52 L (80.93% saving)**. `[VERIFIED]` offline. This bound is loose (perfect foresight; battery power, time ordering, and startups relaxed). It does not establish reachability. **Amendment A1:** the analytic bound is a sanity reference only. It is not an aggregation input, and no per-origin analytic bound is proven or used (K8).

### 6.6 Decision use of the oracles

**Amendment A1 (2026-10-06): NG7 decision rule.**

- Let `L = Σ_o d_o` be the aggregate of finite valid per-origin dual bounds from the certified lower bound (K8), and `F_c` the realized 123-origin PC-Control fuel.
- **NG7 triggers iff `L > 0.60 × F_c`** (strict). It records that the 40 % saving is physically unreachable under the stated priorities (zero-unmet set, K2).
- **NG7 is NOT EVALUABLE** until `F_c` exists. Until then no NG7 conclusion is drawn.
- **A failure to trigger NG7 does not establish reachability.**
- A 40 % saving achieved by a feasible zero-unmet trajectory (for example a rolling trajectory that meets the zero-unmet requirement) establishes achievability. The rolling benchmark may support reachability but cannot independently trigger NG7.
- ORACLE-CTRL does not trigger or cancel NG7.

## 7. Audit Gates (Planned-Value Definitions, B4–B5)

**Planned telemetry (B4).** A harness-only wrapper records, per hour and per arm, the planned values from the MILP solution vector: `served_c`, `served_nc`, `unmet_crit`, `unmet_nc`, `charge`. These are logged by the research harness from the solver solution. The production `DispatchPlan` is **not modified**. G2 and G3 use **planned** values. Realized values are used only for the outcome metrics and for the realization identity in G1.

- **G1 — Realizability identity:** under ORACLE-PHYS (forecast = realized), at every hour the planned charge equals the realized charge: `|planned charge − realized charge| ≤ 1 W`. Failure → BLOCKED.
- **G2 — Priority inversion:** at every hour and every arm, using **planned** values: `NOT (unmet_nc_t > 0 AND charge_t > 0)`. Any violation → BLOCKED.
- **G3 — Critical infeasibility (exact, B5/B7):** for every hour, using **planned** `unmet_crit_t`: a planned value `unmet_crit_t > 0` is physically feasible **only if** `S_avail_t + max_discharge_t < D_c,t`, where `S_avail_t = S_pv,t(realized) + W_t(realized) + diesel_t(planned)` (planned battery discharge is **not** included), and `max_discharge_t = min(50,000 W, (E_t − E_min)·η_dis)` using the realized state of charge `E_t` at the start of hour `t`. Otherwise **G3 fails** for that hour; any arm with a G3 failure is BLOCKED.
- **G4 — Optimizer status:** every solve `HighsModelStatus.kOptimal`; any non-optimal solve → BLOCKED.
- **G5 — Shortfall residual:** in hours with `S_avail < D`, the planned-versus-realized difference in critical and non-critical service is recorded separately. This is an audited residual, not a failure.
- **G6 — Busbar and SOC:** realized `|S_avail − (s + C + curt)| ≤ 1e−3 W` per step; SOC within 19.999–95.001%; fuel accounting `5·on_hours + 0.25·kWh` except listed starvation rows.
- **G7 — Determinism:** a repeated PC-Control run reproduces identical hourly telemetry (1e−6 W, 1e−6 L). Failure → BLOCKED.
- **G8 — Hash guards** (§9). Mismatch → BLOCKED.
- **G9 — Accounting:** exactly 123 unique origins per arm; 2,952 hours per arm; no duplicates.
- **G10 — Route propagation:** `optimizer_received_mode == route` on every row; EMERGENCY steps build 24 EM rows (counted at build time by the harness).
- **G11 — Old telemetry unmodified:** the corrected reproduction telemetry is not modified; this study writes to new paths only.
- **G12 — Oracle SITES coverage:** §6.3.

---

## 8. NO-GO Conditions

- **NG1 — Realizability:** G1 fails → the planner correction is not accepted.
- **NG2 — Priority inversion:** G2 fails in any arm → NO-GO for that arm.
- **NG3 — Critical service (defined with the same planned-versus-realized rule as G2/G3):** NO-GO for a candidate if **either** (a) G3 fails in any hour of that candidate's run, **or** (b) its realized critical-first reliability is below PC-Control's (S1 failure).
- **NG4 — Safety:** any realized SOC < 20.00% hour for a candidate → that candidate is rejected (S3).
- **NG5 — Determinism or hash failure:** G7 or G8 fails.
- **NG6 — Arm B or any storage-first/brownout realization used** in any arm or comparison → NO-GO.
- **NG7 — 40% unreachable (Amendment A1):** NG7 triggers iff `L > 0.60 × F_c`, where `L = Σ_o d_o` is the aggregate of finite valid per-origin dual bounds from the certified lower bound, `F_c` is the realized 123-origin PC-Control fuel, and the inequality is strict. NG7 is NOT EVALUABLE until `F_c` exists. Failure to trigger does not establish reachability. The rolling ORACLE-PHYS cannot independently trigger NG7. ORACLE-CTRL neither triggers nor cancels NG7.
- **NG8 — Production or frozen change:** any modification of production GAP19, the production executor, the production DispatchPlan, or any frozen artifact → NO-GO.
- **NG9 — Post-hoc change:** any change to thresholds, arms, gates, oracle definition, or corrections after results are seen → NO-GO.
- **NG10 — Quarantined provenance:** quarantined realization-run outputs used for any comparison → NO-GO for that comparison.
- **NG11 — Oracle coverage:** G12 fails for any origin → that origin's oracle result is not interpreted; if any origin is missing, ORACLE-PHYS cannot establish NG7 → BLOCKED.

---

## 9. Hash Guards

Verified before execution and after execution.

| Artefact | SHA-256 (recorded at design time) |
|---|---|
| `system/optimization/implementations/gap19_highs_native.py` (production GAP19) | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` |
| `system/simulation/research_realization_executor.py` (Arm A executor) | `c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b` |
| `system/schemas/dispatch_plan.py` (production DispatchPlan) | `21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b` |
| `system/forecasting/implementations/causal_nwp_physics.py` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` |
| `experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py` (unmodified; basis of Planner-CF v1) | `95b2f3b53609a6e420a18692b4b0e3927cb47841d9e1200cce04677094a5950e` |
| `experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_RESULTS.csv` | `8c13b904e286e25167a8eca5144e545627b6c598f36716e93fcf9ee95a2ab57e` |
| `experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv` | `6b3636d7ae4d596016f4e7b3b5fc63e9a26e374041b586b619b49afc2eec7d2e` |
| `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.md` | `e73558cfd03acd35fc55d24a055f7ccc6a31d0d973a3cc2e4443a8665ac21cd7` |
| `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.json` | `6b0bb6f7af44ef06731180d50239de222f301fa571c5862d115f7644d3be7b87` |
| `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_123_ORIGIN_RESULTS.csv` | `18d13dec71eab82919c900da52b5248699e4b5b8fa4c4ed8499aff494f4fa62b` |
| `experiments/POST_STAGE4_GOVERNANCE_DECISION_RECORD.md` | `d3239b3ac9209644606014d1d52e63d2c3103560771b9c6c42924942f93d977f` |
| `data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv` (oracle solar input; authoritative) | `d457facdbeb57b9c582b623c524c0f50717306ca083ab93028f1bd700d1e7a2e` |

Quarantined realization study (`experiments/stage4_realization_consistency_2025/`) is referenced **only** for exclusion (NG10).

**Provenance rule.** The planner, planned-telemetry harness, oracle runner, and their unit tests are new files, hashed in §16. No existing file is edited.

---

## 10. Statistics

- **Pairing:** origin-level, origins sorted ascending, no subsetting.
- **Diesel gate E1:** two-sided Wilcoxon signed-rank; Holm across the four candidate tests (PC-S, PC-SW, PC-S-L, PC-SW-L), including the S test.
- **BCa:** 95%, 10,000 origin resamples, `scipy.stats.bootstrap(..., method="BCa", n_resamples=10000, random_state=np.random.default_rng(42))`.
- **Reliability deltas:** per-origin paired (candidate − PC-Control), BCa 95%, descriptive and gate-supporting.
- **Deterministic comparisons (required, descriptive, not gates):**
  - **D1:** PC-Control − old Control (fuel, both reliabilities), paired by origin.
  - **D2:** PC-S − old S (fuel, both reliabilities), paired by origin.
  - **D3:** PC-S − PC-Control and PC-SW-L − PC-Control (the gate basis).
  - Each reports absolute values, deltas, and BCa 95% CIs.
- **Accounting alternative (reported, not decision-bearing):** MILP-objective fuel = accounted fuel + 2.0 L × starts, with the ranking under each.
- **Amendment A1 (lower-bound statistics):** primary accounting is 0 L per start. The 2 L figure is a secondary diagnostic only (K3). Per-origin tight certification requires a feasible incumbent, a finite dual, and absolute gap ≤ 0.01 L (K6). The aggregate L is the sum of all finite valid duals (K8). Blocked origins are reported with counts and are not silently coerced.

---

## 11. Decision Rule

1. Any NO-GO in §8 applies to the arm or claim it names.
2. Candidate eligibility: S1–S3, then E1.
3. Winner: highest eligible saving (§5).
4. T40: reported PASS/FAIL. NG7 is decided by ORACLE-PHYS only.
5. The study does not declare any arm "correct" because it looks better. It reports whether the planner correction changes the eligible set and the winner relative to the corrected results, and gives the reason.

**Hypotheses (not claims):** customer-first planning serves more non-critical load, so proportional reliability is expected to rise for all arms, and diesel is expected to rise where the plan runs diesel to serve customers. Both directions are measured.

---

## 12. Feasibility Summary

| Question | Answer | Basis |
|---|---|---|
| Is 40% excluded by energy alone? | No. Relaxed physics bound 1,162.52 L (80.93%). | §6.5, offline |
| Is 40% reachable under the benchmark's physics and customer-first priorities with perfect information and no reserve? | **Unknown until ORACLE-PHYS runs.** | §6.2, §6.6 |
| Gap for current S (old planner) to 40% | 1,029.55 L (16.89 pp of Control) | §6.4 arithmetic |
| Gap for PC arms | defined by §6.1 after PC-Control runs | §6.1 |

---

## 13. Outputs (Not Executed)

All under new paths `experiments/stage4_planner_cf_consistency_2025/`: telemetry (including the planned per-hour values from §7), results, safety report, statistical report, deterministic comparison report (D1–D3), ORACLE-PHYS and ORACLE-CTRL reports, and the audit report (G1–G12). Existing corrected, frozen, and quarantined artifacts are not overwritten.

---

## 14. Status and Items Requiring Authorization

**DESIGN v1.1 — NOT EXECUTED — NOT FROZEN.** Final authorization is required. Authorization is requested for:
- (a) C1–C4, including C3 (flexible sink removed, a preregistered change) and E1 (EMERGENCY row referencing total served);
- (b) ORACLE-PHYS as the NG7 oracle, with ORACLE-CTRL as secondary;
- (c) the oracle future-input definitions in §6.3, including the SITES coverage requirement (G12);
- (d) the planned-telemetry harness logging in §7 (B4);
- (e) the 40% definition in §6.1 and the new file paths.
- (f) **Amendment A1 (2026-10-06):** lower-bound governance K1–K10 in `experiments/GOV_DECISION_LOWER_BOUND_CERTIFICATION_2026-10-06.md`, including the 60 s per-origin time limit, the 0.01 L decision-precision threshold, dual retention, the aggregation rule, and the NG7 rule. The real 123-origin lower-bound run requires a separate explicit authorization from AGY. Input and population hashes are frozen only immediately before it.

## 15. Resolution of Review Items B1–B8

| Item | Resolution in this version |
|---|---|
| **B1** p_flex | Removed as a planner variable; upper bound 0 W; preregistered change C3; no unrealized sink remains (§3.1, §3.4). |
| **B2** ORACLE for NG7 | ORACLE-PHYS (reserve-free, customer-first, perfect foresight) is the NG7 oracle; ORACLE-CTRL is secondary (§6.2, §6.6, NG7). |
| **B3** Oracle inputs | Solar from actual 2025 SITES SW_IN via the executor's conversion; wind and demand from the existing synthetic formulas with offset `h = j+1`; calendar: origin 00:00 UTC plus offset `j`, horizon `j = t…t+23`; coverage gate G12 (§6.3). |
| **B4** Planned telemetry | Harness-only logging of served_c, served_nc, unmet_crit, unmet_nc, charge from the solver solution; production DispatchPlan not modified; G2/G3 use planned values (§7). |
| **B5** G3 | Exact rule: planned `unmet_crit_t > 0` permitted only if `S_avail_t + max_discharge_t < D_c,t` with realized battery limits; otherwise G3 fails (§7). |
| **B6** Full priority | J1(5) > J_nc(4) > J2(3) > J3(2) > J4(1); reserve as battery-service requirement; fuel as economic objective outside the customer-service hierarchy (§3.3). |
| **NG3 fix** | NG3 uses the same planned-versus-realized definitions as G2 and G3 (§8). |
| **B7** G3 double-counting | S_avail_t = realized PV + realized wind + planned diesel only (no planned discharge). Infeasibility: planned `unmet_crit_t > 0` is feasible only if `S_avail_t + max_discharge_t < D_c,t`, with `max_discharge_t = min(50,000 W, (E_t − E_min)·η_dis)` (§7 G3). Same definition in MD and JSON. |
| **B8** oracle solar hash | Authoritative file `data/POLARIS_v0_1_SITES_Nuolja_2025_hourly_SW_IN.csv`, SHA-256 `d457facdbeb57b9c582b623c524c0f50717306ca083ab93028f1bd700d1e7a2e`, pinned identically in §9 and the JSON. |
| **Implementation** | Planner-CF v1, planned-telemetry harness, oracle runner, and unit tests implemented and hashed (§16). Unit/invariant tests: 23 new + 8 existing route-propagation tests passed. Campaign not run. |

## 16. Implementation Hashes (Recorded at Implementation Freeze)

| Artefact | Role | SHA-256 |
|---|---|---|
| `experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py` | planner (C1 literal `p_served_c <= D_c` fix at §16.2) | `b479550e5eabcc7d745b874eee92f15b3e07d63740d20ab82e42081b64d0215a` |
| `experiments/stage4_planner_cf_consistency_2025/planned_telemetry_harness.py` | harness | `83fe05ee968dc6448a07d0f904653d79a10ecbf2582dc5935f9267db4bc3e63c` |
| `experiments/stage4_planner_cf_consistency_2025/oracle_runner.py` | oracle (updated at G2/G3 fix, §16.1) | `c9d2e6ab86411173b4fca672e491c3661d68a78e9633fa267b7963793a46fba5` |
| `experiments/stage4_planner_cf_consistency_2025/planned_execution_telemetry.py` | executed-hour telemetry and G2/G3 evaluator (new, §16.1) | `bb6dd4bb0c2415a650bd1ed6809fa5627cb193e85aed7fa3b5f9a552147bd3c8` |
| `tests/test_planner_cf_v1.py` | tests | `63adfe363c59db7dbfda148d270062694fe107a4f7bc19c27b22d10ac295771a` |
| `tests/test_planned_execution_g23.py` | tests for §16.1 (new) | `ac5cec1652496bb1d12ab7f087019add134963d581f9d5e48d4ed4c46b0ed558` |

Tests: `tests/test_planner_cf_v1.py` (23 tests: static C1–C4, model invariants on synthetic instances, harness, oracle calendar, inputs, and coverage) and `tests/test_research_route_mode_propagation.py` (8 tests). All 31 passed. No campaign, oracle evaluation, or outcome-producing run was executed.

### 16.1 G2/G3 executed-hour telemetry and evaluator (G2/G3 blocker fix, harness-only)

Added at the G2/G3 fix. This section defines the telemetry and evaluator that G2 and G3 use. It changes no planner, oracle, or gate threshold.

- **Executed-hour rule.** Each re-solve produces a 24-hour plan, but only plan hour 0 is executed before the next re-solve. Exactly one executed-hour record is kept per re-solve, so each origin yields 24 records per arm (one per realized hour). The 24 lookahead rows are not used by G2 or G3.
- **Record fields.** `origin_id`, `arm`, `step` (= realized hour), `plan_hour` (= 0), `E_t_wh` (realized start-of-hour battery energy, the state passed into the re-solve), `pv_real_w`, `wind_real_w` (realized), `planned_diesel_w`, `d_c_w` (realized critical demand, `critical_w(step)`), `max_discharge_w`, and planned `served_c`, `served_nc`, `unmet_crit`, `unmet_nc`, `charge` from hour 0.
- **max_discharge.** `max_discharge_w = min(50,000 W, max(0, (E_t − E_min)·η_dis))`, with E_min = 20% of 200 kWh = 40,000 Wh and η_dis = 0.92.
- **G2 (planned).** Violation if `planned unmet_nc > 1e-3 W AND planned charge > 1e-3 W`.
- **G3 (planned, exact).** Violation if `planned unmet_crit > 1e-3 W` and NOT `(S_avail + max_discharge_w) < d_c_w`, where `S_avail = pv_real_w + wind_real_w + planned_diesel_w`. Planned discharge is not in `S_avail`. The comparison is strict.
- **Tolerance.** 1e-3 W on the planned values, as in the existing G2 unit check. This tolerance is declared here, before any campaign run.
- **Determinism.** Records are sorted by (arm, origin_id, step) before evaluation. The evaluator output does not depend on input order.
- **Scope.** Harness-only. Production `DispatchPlan` is not modified. The evaluator performs no solve and no realization.
- **Implementation paths.** `experiments/stage4_planner_cf_consistency_2025/planned_execution_telemetry.py` (new) and `tests/test_planned_execution_g23.py` (new). `experiments/stage4_planner_cf_consistency_2025/oracle_runner.py` was edited at this fix to wire the recorder into `run_oracle_origin` (it writes `result.executed`). The file is part of this study, not production or frozen.
- **Tests.** `tests/test_planned_execution_g23.py` (12 tests: lookahead collapse, plan-hour-0 values, E_t as start-of-hour state, max_discharge, G2/G3 boundary and determinism, real-optimizer synthetic determinism) with `tests/test_planner_cf_v1.py` (23 tests). 35 passed. No campaign, oracle, or real-origin run.

### 16.2 Campaign infrastructure (research-only; campaign NOT run)

Implemented after §16.1. Nothing here runs a real origin, the oracle, or the campaign. Only synthetic, unit and invariant tests were run, plus read-only checks of frozen telemetry.

- **C1 literal fix.** The served-critical upper bound is `p_served_c <= D_c` (`p_crit`). Layer B already implies this bound, so the change is literal conformance and does not change the feasible set.
- **Campaign runner** (`planner_cf_campaign_runner.py`). Five arms per origin (PC-Control, PC-S, PC-SW, PC-S-L, PC-SW-L): 123 origins × 5 = 615 closed-loop runs. All arms reuse the frozen causal NWP forecaster, router, mode propagation and Arm A executor. Only the EBR equation differs by arm, via the frozen `stage4_low_sun_adapter` functions. Origin setup matches the corrected reproduction: t0 = forecast_start − 1 h; realized solar from the 2025 weather file; realized wind and demand from the §6.3 formulas.
- **Authorization gate.** `run_campaign` raises unless `authorized=True`. It verifies the §9 protected hashes before the first origin.
- **Executed-hour telemetry.** Each re-solve writes one record (plan hour 0) through `planned_execution_telemetry.py`, per §16.1.
- **G7 repeat.** One repeated PC-Control run on origin index 1 is compared with the campaign's own run at 1e-6 tolerance.
- **Statistics** (`planner_cf_statistics.py`). Reliability: R_CF = 100·Σserved_crit_first / Σcritical_demand; R_P likewise with served_crit_prop. Per-origin values use the same formula. S1–S3 use aggregate reliability and the SOC floor at 20.00 %. E1: Delta_o = Fuel(PC-Control,o) − Fuel(candidate,o), sorted by origin; two-sided Wilcoxon per candidate; Holm across the four candidate tests; BCa 95 % via `scipy.stats.bootstrap(method="BCa", n_resamples=10000, random_state=np.random.default_rng(42))`; eligibility requires adj p < 0.05 and BCa low > 0. E1 is evaluated only if S1–S3 pass. T40 is report-only. Winner: highest saving among eligible. D1 and D2 pair PC arms with the frozen corrected results by origin. D3 is candidate minus PC-Control. Accounting alternative: fuel + 2.0 L × starts, reported only.
- **Audit gates** (`planner_cf_audit_gates.py`).
  - G1: planned vs realized charge within 1 W on ORACLE-PHYS.
  - G2 / G3: the §16.1 evaluator over executed-hour records.
  - G4: every solver status equals `HighsModelStatus.kOptimal`.
  - G5: shortfall residual (audited, not a failure). In hours with realized S_avail < demand, planned-vs-realized critical and non-critical service differences are recorded. PASS only if every executed hour matches a realized row.
  - G6: busbar error ≤ 1e-3 W; SOC in [19.999, 95.001] %; fuel = 5·on_hours + 0.25·kWh within 1e-3 L. Starvation rows are the fuel-without-power class (diesel power 0, fuel > 0). They are listed explicitly; the gate fails only on unlisted mismatches.
  - G7: determinism at 1e-6 (§16.2 G7 repeat above).
  - G9: 123 origins and 2,952 rows per arm; no duplicate (origin, hour).
  - G10: optimizer-received mode equals route on every row; EMERGENCY steps build 24 EM rows, other steps build 0.
  - G11: corrected results and telemetry hashes unchanged.
  - G12: for every origin, the SITES window with offsets 0..46 must be present; blocked origins are listed.
- **Validation on frozen corrected telemetry (read-only).** Per-origin fuel and R_CF / R_P recomputed from the frozen telemetry match the frozen corrected results CSV at 1e-3 L and 1e-4 pp. G4 passes. G6 passes, with one listed starvation row (origin 39, hour 22, Candidate_SW, 3.6293 L fuel with diesel power 0).
- **Reports.** `build_post_run_report` writes `PC_POST_RUN_REPORT.json` and `PC_RESULT_SUMMARY.md` into the study folder at campaign time.
- **Known limits.** The campaign runner and post-run report were exercised only on synthetic data. The 47-hour causal lookahead needs a 72-hour weather table. G1 and G12 are oracle-side audits and run later with the oracle.
- **Implementation paths and hashes** (SHA-256):
  - `experiments/stage4_planner_cf_consistency_2025/planner_cf_campaign_runner.py` — `ea9400bfa11734cd6ab8427c0b6c8b872fedf73811f3cd66e38d6023ed370726`
  - `experiments/stage4_planner_cf_consistency_2025/planner_cf_hash_guards.py` — `defc138da3d56724ffaa74464c4dcb229c31314c956b52840d0bd16d902c57f0`
  - `experiments/stage4_planner_cf_consistency_2025/planner_cf_statistics.py` — `1153bd61749352847423a381ddaa0b9ed1d8724a96730675d2773bcbf21f7bb9`
  - `experiments/stage4_planner_cf_consistency_2025/planner_cf_audit_gates.py` — `7f72b4f1791bc518af426b18bebd1e4a5ce1cdcde42a127a587c3931eee95123`
  - `tests/test_planner_cf_campaign_infra.py` — `43e11f1a51f21cec58d07e8811824597163c9bedf6092c39d1ca8935fb95cb81`
  - `tests/test_planner_cf_closed_loop_synthetic.py` — `a6d5484da049596e01593d1d5a39cc33b28a7e5e4f2626320df3fe48aea9390d`
  - Planner (C1 change): `research_numerical_extractor_planner_cf_v1.py` — `b479550e5eabcc7d745b874eee92f15b3e07d63740d20ab82e42081b64d0215a`
- **Tests.** 85 passed: 36 campaign-infra, 6 closed-loop synthetic (fake origin 2099-01-01), 23 planner, 12 executed-hour, 8 route propagation.


### 16.3 Pre-execution resolutions (research-only; campaign NOT run)

- **G1 / G12 wiring.** `oracle_audit_adapter.py` converts ORACLE-PHYS / ORACLE-CTRL results into the G1 frames (realized `charge_w` vs executed `planned_charge_w`, matched on origin and hour) and calls the G12 coverage check with the SITES key set. G1 is applied to ORACLE-PHYS. The adapter starts no oracle run. Synthetic tests cover pass, fail, variant filtering and unmatched rows.
- **G7 repeat origin.** §7 does not name the repeated origin. The rule is now fixed before any run: the earliest origin in the sorted population, index 1 (2025-05-01 00:00:00). It does not depend on any outcome. This is an addition to §7 made before execution; the user must accept it before authorization.
- **G6 starvation row (origin 39, hour 22, Candidate_SW). VERIFIED.** Cumulative fuel through hour 21 is 96.3707 L of the 100 L budget, so the residual is 3.6293 L. The plan at hour 22 has diesel on (u = 1, p_diesel = 14,466.5 W, needing 5 + 0.25 × 14.47 ≈ 8.62 L). The executor's starvation branch (`research_realization_executor.py`, lines 181–185) sets `max_p = (avail − 5)/0.00025`. Because avail < 5 L, max_p = 0, so realized diesel power is 0. The branch still sets `fuel_consumed = avail_fuel`, which burns the whole residual with zero power. This is an executor property. The historical result is unchanged. No preregistration threshold changes.
- **Open issue (not resolved here, requires governance).** Neither the planner, the frozen extractor, nor GAP19 has a fuel-budget constraint. A plan can therefore schedule diesel the remaining fuel cannot supply. Starvation rows are listed by G6, but a starved planned hour can make realized charge differ from planned charge. That would affect G1 under ORACLE-PHYS, which is NG1. Options: accept G1 as written, or add a fuel-budget constraint to the planner as a new preregistered change. This is not in the current design.
- **Tests.** 85 passed (36 campaign-infra). The starvation mechanism is checked against frozen telemetry and executor source. The campaign was not run.
- **Implementation paths and hashes** (SHA-256):
  - `experiments/stage4_planner_cf_consistency_2025/oracle_audit_adapter.py` — `bba99808f4fc75b1be6efe158abad1cbb8cfc534835804e8eb0d7c996d9acdac`
  - `tests/test_planner_cf_campaign_infra.py` — `43e11f1a51f21cec58d07e8811824597163c9bedf6092c39d1ca8935fb95cb81`


### 16.4 Accepted rules and ORACLE audit driver (research-only; campaign NOT run)

- **G7 repeat origin (accepted, fixed).** The repeated PC-Control run is the earliest origin of the sorted population: index 1, forecast_start 2025-05-01 00:00 UTC. This rule is fixed before execution.
- **Fuel budget (not added).** The Planner-CF formulation is unchanged. No fuel-budget constraint is added to the planner. Any plan/realization mismatch from fuel starvation remains visible through G6 (listed starvation rows) and G1/NG1 (ORACLE-PHYS).
- **ORACLE audit driver** (`oracle_driver.py`). Requires explicit authorization, verifies the §9 hashes, and runs G12 before any oracle run. If any origin is blocked, it returns BLOCKED and runs no oracle. It runs ORACLE-PHYS and ORACLE-CTRL over the 123 origins, feeds ORACLE-PHYS into G1 through `oracle_audit_adapter`, and writes the hourly outputs and the audit report. An origin exception is recorded as BLOCKED, never skipped. A G1 failure is reported as NG1 and is not repaired. NG7 uses ORACLE-PHYS fuel against PC-Control only, and only once the campaign fuel is supplied. ORACLE-CTRL does not affect NG7.
- **Tests.** 94 passed: 36 campaign-infra, 9 oracle driver, 6 closed-loop synthetic, 23 planner, 12 executed-hour, 8 route propagation. The oracle is stubbed in all tests. No real origin, oracle, or campaign was executed.
- **Implementation paths and hashes** (SHA-256):
  - `experiments/stage4_planner_cf_consistency_2025/oracle_driver.py` — `9d0e1bcd59f5ef05472610bf926b02e7848caef547ba283dc704945171b98e6d`
  - `tests/test_oracle_driver.py` — `cafadd310df5139bdded2bd7382973b53ef1b09e1f183cf0d78c5a5908a55cc8`


### 16.5 Forensic planned-capture pass (diagnosis only; campaign NOT run)

- **Purpose.** The ORACLE-PHYS outputs did not retain planned DispatchPlan values. This pass re-runs ORACLE-PHYS over the governed 123-origin population to recover the planned telemetry, so the 72 G1 mismatches can be classified. The original ORACLE outputs stay frozen evidence.
- **Scope.** Same Planner-CF v1 formulation, same realization executor, same G1 definition (tolerance 1 W), no fuel-budget constraint, no ORACLE-CTRL, no campaign.
- **Module.** `forensic_planned_capture.py` (new). It mirrors `oracle_runner.run_oracle_origin` and keeps the DispatchPlan at each hour. It writes only to a new directory `forensic_planned_capture_<timestamp>/`, and refuses to overwrite an existing directory or any original ORACLE file.
- **Integrity.** Requires explicit authorization. Verifies §9 protected hashes before and after. Requires 123 × 24 = 2952 rows and OPTIMAL statuses. Requires the replay to reproduce `ORACLE_PHYS_HOURLY.csv` exactly (tolerance 1e-6 on charge, discharge, diesel, served, unmet, fuel, SOC and inputs). Otherwise the status is `FORENSIC_REPLAY_NONREPRODUCIBLE` and no classification is reported.
- **Classification.** Each mismatch > 1 W gets one class:
  - D: non-optimal solve, realized busbar residual > 1e-3 W, or planned balance residual > 1e-2 W.
  - A: realized charge differs from `min(realized surplus, 50 kW, room/0.92)` by more than 1 W.
  - B: planner curtailed while charge capacity was available.
  - C: starvation (planned diesel needed more fuel than remained), or A and B together.
  - E: none of the above.
  The planner-curtailment tie is tested by recomputing the 24-hour total curtailment with greedy charging, keeping discharge, diesel and served fixed. A tie is `|difference| ≤ 1 Wh`.
- **Tests.** `tests/test_forensic_planned_capture.py` (20 tests, synthetic). Includes the origin 46 tie reproduced from its replay horizon, and one solve on a fake 2099 origin.
- **Implementation paths and hashes** (SHA-256):
  - `experiments/stage4_planner_cf_consistency_2025/forensic_planned_capture.py` — `b690f2fedbdd22e68079018e3f9e886f12b1ec93ad5e3c073a1b558e6e437cf9`
  - `tests/test_forensic_planned_capture.py` — `bb08a9e145435f06f8202ca078e439427264d871219be70bf75a76601844a21b`
- **Tests.** 114 passed across the full suite.
- **Execution boundary.** The real 123-origin forensic capture runs from AGY only. CC has not run it.


### 16.6 Lower-bound governance pins (Amendment A1, 2026-10-06; research-only; campaign NOT run)

- **Decision record (new):** `experiments/GOV_DECISION_LOWER_BOUND_CERTIFICATION_2026-10-06.md` — `056538cb380c9ca382f07cf05291bb5ef9b3d562ff89987da99f2cd3fcc6bcf4`. The prior record `experiments/POST_STAGE4_GOVERNANCE_DECISION_RECORD.md` is preserved unchanged.
- **Lower-bound files** (synthetic-tested; real run not authorized):
  - `experiments/stage4_planner_cf_consistency_2025/global_lower_bound.py` — `8883f93bf91ee6045e9f082da662393091debcc69110324915829aaa395b647f`
  - `experiments/stage4_planner_cf_consistency_2025/global_lower_bound_loader.py` — `0de183821228003f71f43d5a004a017aa566b510b6d77fa23894f2b9a412f694`
  - `experiments/stage4_planner_cf_consistency_2025/global_lower_bound_manifest.py` — `996c0836177da561e7fc5e2316d5e9e275dc120d712a3dba3281efa535e99fea`
  - `tests/test_global_lower_bound.py` — `a15eaa2072c53f1ae3f0e945a9515244f85dd12a5d7636a370e2633d52874fce`
  - `tests/test_global_lower_bound_infra.py` — `1432855b0da764bb94dce93765f593dd8d3ed7704c49ad6d5e637ccff4573f38`
- **Configuration hash** (`global_lower_bound.config_hash`): `e4ef245e7f99c6056be067939c1f325a727c0feaa3894cb657944121d207b829`
- **Solver settings hash:** `c510da31596cb1ecece7a56c1aba34bebe32fd50155355b302fc56a490e5bb7b` — HiGHS (highspy), `threads = 1`, `output_flag = False`, `mip_rel_gap = 1e-9`, **`time_limit_s = 60.0`** (K7), absolute gap threshold 0.01 L (K6).
- **Dual-bound interpretation:** `mip_dual_bound` is the minimization lower bound. A finite value is retained as `dual_L` whether or not an incumbent exists. `-inf` is never fabricated or retained. The primal objective is never a lower bound. `mip_gap` is relative, `(U − L)/|U|`, and the module does not depend on it.
- **Explicit statements:**
  - Lower-bound validity is not tight certification.
  - A finite dual may contribute despite a gap above 0.01 L.
  - No-dual origins are BLOCKED_NO_DUAL and contribute zero under the conservative convention.
  - No real run has occurred. No real origin, ORACLE-PHYS, ORACLE-CTRL or Planner-CF campaign has been executed.
- **Tests:** 186 passed (synthetic only).

**Campaign status: NOT RUN.** Final authorization is required before execution.


## 17. Amendment A2 (2026-10-06): Planner-CF v1.2 governance — APPLIED; IMPLEMENTATION NOT PERFORMED

**Status.** Governance and archive step only. No v1.2 implementation, test, oracle run or campaign has been performed. Planner-CF v1.1 remains the governing implementation until v1.2 is implemented, pinned and audited.

### 17.1 Decisions
- **v1.1 is archived** as a completed, non-accepted campaign. Its outputs are not reclassified, re-scored or superseded in place. The v1.1 designation of PC-SW as winner is not accepted.
- **v1.2 is proposed** with two changes only: an hour-0 diesel-fuel feasibility constraint (§17.2) and an explicit G1 tie-admission rule (§17.3).
- **NG1 remains ACTIVE.** See §17.5.

### 17.2 Changes from v1.1
1. **Hour-0 fuel constraint (Class C).** For each re-solve, `5·u_diesel[0] + 0.00025·p_diesel[0] ≤ F_rem`, where `F_rem` is the remaining diesel fuel in the planning state. Only hour 0 is constrained. Hours 1–23 are not executed, and each later re-solve enforces the inventory from the realized state.
2. **G1 tie admission (Class B), §17.3.** G1 keeps its exact-equality form and 1 W tolerance, with the admission path added.

Nothing else in the formulation changes.

### 17.3 Class-B tie-admission rule
For hour 0 of each re-solve, let **P** be the planned schedule. Let **Q** be the greedy alternative over the same 24-hour horizon. Q keeps the planned served load, discharge and diesel fixed, and sets charge at each hour to `min(surplus, 50 kW, room/0.92)`, with surplus and room computed from the planned horizon and the state path, using the executor's formulas.

A planned-versus-realized charge difference at hour 0 is **admitted if and only if all seven conditions hold**:
1. Planned served load and planned unmet load equal the realized values for the hour.
2. Planned discharge and planned diesel equal the realized values for the hour.
3. J1, J_NC, J2 and J3 of P and Q are equal to within the established numerical tolerances of the existing G1 audit.
4. `|J4(P) − J4(Q)| ≤ 1 Wh` over the 24-hour horizon.
5. Planned charge plus planned curtailment equals realized surplus within 1 W. **In ORACLE-PHYS the forecast equals the realized input, so planned solar and wind availability equal the realized values for the hour.**
6. Realized charge equals `min(realized surplus, 50 kW, room/0.92)` within 1 W, the executor rule.
7. The planned hour-0 schedule satisfies the fuel constraint of §17.2. Under v1.1 this condition fails for starved hours.

Failure of any condition is a G1 failure, with no exception.

**Scope.** The rule applies only to the ORACLE-PHYS G1 audit. The 1 W tolerance and the 1 Wh criterion are existing values from the G1 audit and the forensic design. No new threshold is introduced. The rule does not affect the planned values used by the campaign's G2 and G3 gates.

### 17.4 Class C treatment
The Class-C rows are fuel-starvation cases at the terminal hour. The v1.2 hour-0 constraint excludes them, because the planned diesel becomes infeasible under the remaining inventory. They are not admitted by §17.3, which requires condition 7.

### 17.5 NG1 — remains active
The text of NG1 is unchanged: "G1 fails → the planner correction is not accepted." NG1 is evaluated against G1 as amended by §17.3. **Only ORACLE-PHYS audit results count toward NG1.** NG1 is not weakened, and it remains blocking until a v1.2 ORACLE-PHYS audit passes G1 and G12.

### 17.6 What does NOT change
- C1–C4, the priority order J1 > J_nc > J2 > J3 > J4, the flexible-sink removal, the EMERGENCY row, and the 100 L initial inventory.
- The realization executor, GAP19, DispatchPlan, the causal forecaster, the router, and the frozen extractor.
- The lower-bound formulation, its certification and its pins (Amendment A1, §16.6). The lower bound does not depend on the planner.
- Safety gates S1–S3, the E1 diesel gate, the 40 % target (relative to PC-Control of the same run), and the decision rule.
- G2, G3, G4, G6, G7, G9, G10 and G11.
- No tie-break, alternative objective, parameter sweep or extra arm is introduced.

### 17.7 v1.1 archive and recoverability
- The v1.1 source and test files are preserved unchanged under `experiments/stage4_planner_cf_consistency_2025/archive/v1.1/`, with `ARCHIVE_MANIFEST.json`. Each archived file matches its original byte-for-byte, and each pinned v1.1 hash is verifiable from the archive.
- The v1.1 campaign outputs (`PC_HOURLY_TELEMETRY.csv`, `PC_EXECUTED_HOUR_TELEMETRY.csv`, `PC_POST_RUN_REPORT.json`, `PC_RESULT_SUMMARY.md`), the standalone PC-Control run (`control_only_20261006T122455Z/`), the ORACLE-PHYS and ORACLE-CTRL outputs, and the forensic capture directory are archived as completed, non-accepted v1.1 artifacts.
- **ORACLE-CTRL outputs are NOT required by G1 and are NOT regenerated under v1.2.** They remain archived v1.1 artifacts.

### 17.8 Acceptance eligibility
v1.2 results are eligible for acceptance **only after** all of the following hold:
- the fresh ORACLE-PHYS v1.2 audit passes G1 under §17.3 and G12;
- the v1.2 post-run gates in §17.10 pass;
- the v1.2 campaign is run in full, including PC-Control, under the unchanged decision rule.

### 17.9 Stale artifacts and hash impact
**Become stale and require new pins under v1.2:**
- `research_numerical_extractor_planner_cf_v1.py` (v1.1 `b479550e…`), to be edited only after archival.
- `planner_cf_audit_gates.py` (`7f72b4f1…`), which gains the §17.3 evaluator.
- `oracle_audit_adapter.py` (`bba99808…`) and `oracle_driver.py` (`9d0e1bcd…`), which carry the G1 path.
- `forensic_planned_capture.py` (`b690f2fe…`), whose tie check uses the same greedy construction.
- `test_planner_cf_v1.py` (`63adfe36…`), `test_oracle_driver.py` (`cafadd31…`), `test_forensic_planned_capture.py` (`bb08a9e1…`), `test_planner_cf_campaign_infra.py` (`43e11f1a…`), `test_planner_cf_closed_loop_synthetic.py` (`a6d5484d…`), `test_planned_execution_g23.py` (`ac5cec16…`).
- `planner_cf_campaign_runner.py` (`ea9400bf…`), if its campaign path changes.
- The preregistration MD and JSON.

**Unchanged:** the lower-bound files and pins, the executor, GAP19, DispatchPlan, the causal forecaster, the router, the frozen extractor, `planner_cf_statistics.py` (`1153bd61…`) and `planner_cf_hash_guards.py` (`defc138d…`). These are unchanged unless a later v1.2 step changes them.

### 17.10 Rerun order (approved 10-step sequence)
1. Apply A2 and pin governance, preserving the v1.1 archive. *(Done in this step.)*
2. Implement v1.2.
3. Run the new tests and the full synthetic regression.
4. Pin the v1.2 implementation hashes and verify the pins.
5. Run the ORACLE-PHYS v1.2 audit over all 123 origins, with planned capture and G12 coverage.
6. Gate: G1 and G12 must pass. Stop on failure.
7. Run the 615-run v1.2 Planner-CF campaign, including PC-Control.
8. Run the post-run gates (§17.11).
9. Evaluate NG7 with the v1.2 F_c. The lower bound L is unchanged.
10. Make the final acceptance decision under the unchanged decision rule.

### 17.11 Required tests and post-run gates
**Before the run:**
- With `F_rem` = 4.4193 L and a 16 kW diesel request, the planner chooses zero diesel.
- For cases where the v1.1 hour-0 fuel requirement is ≤ F_rem, v1.2 must reproduce the v1.1 hour-0 solution and objective within the established numerical tolerances. Cases where the v1.1 fuel requirement exceeds F_rem are expected to differ.
- At the constraint boundary the constraint is tight.
- With `F_rem` = 0 the model is feasible with diesel off.
- The realized starvation branch is never reached in v1.2 synthetic runs.
- The tie evaluator admits a synthetic row meeting all seven conditions, and rejects a row failing each condition in turn.
- The tie evaluator rejects a row whose hour-0 plan is starved.
- Repeated solves are deterministic.
- The existing tests pass, and any change is documented as expected.

**After the run:**
- Completeness: 123 origins, 14,760 hourly rows, no optimizer or step errors.
- Solver status: every solve is OPTIMAL (G4).
- Accounting: busbar, SOC and fuel (G6). Any fuel mismatch is listed explicitly.
- Determinism: G7.
- Identities: G9 and G10.
- Protected artifacts: G11.
- Safety, fuel and target gates applied exactly as written, and NG1 evaluated and reported.

### 17.12 Governance statement
This amendment is an approved governance step. It introduces no numerical threshold beyond those already in the study (the 1 W G1 tolerance and the 1 Wh J4 criterion). It introduces no hidden tie-break, objective change, or formulation change beyond §17.2.

**Campaign status: NOT RUN. v1.2 implementation: NOT PERFORMED.**

### 17.13 v1.2 implementation hash pins (pinning step; campaign NOT run)
The v1.2 implementation and test files below replace the v1.1 pins in §17.9. The v1.1 values remain in `archive/v1.1/ARCHIVE_MANIFEST.json`. No solver, oracle, campaign or test was executed to produce these pins. They were computed from the files on disk.

| Path (relative to repository root) | SHA-256 (v1.2) |
|---|---|
| `experiments/stage4_planner_cf_consistency_2025/research_numerical_extractor_planner_cf_v1.py` | `a8dd9fc7d84e3d2344ba4f99ba1b1cd0ec2165a83d8f7af438b69f8178815093` |
| `experiments/stage4_planner_cf_consistency_2025/planner_cf_audit_gates.py` | `6f3d2cc4d7ae1c006a7ac0e2f70f668d64364f114be59d8604f4c71ff64b9654` |
| `experiments/stage4_planner_cf_consistency_2025/oracle_runner.py` | `a65adcb32fc48f53cb3db547107ab8d0183449cdfa8bb24f2602be6b6b817f20` |
| `experiments/stage4_planner_cf_consistency_2025/oracle_audit_adapter.py` | `c5aee087b2a8cdf9ccc28f81642002374fbe4a3ccfc7a125201da84c981ba802` |
| `experiments/stage4_planner_cf_consistency_2025/oracle_driver.py` | `a21da5cc462accbb4e69cc2682e31f15576301c43aa795295e7efc2e098346e1` |
| `tests/test_planner_cf_v1.py` | `e660f2d56bd155b15102f80abc1c45cd99094c0fdbf980d94b1d9f6742a6b25e` |
| `tests/test_planner_cf_v12.py` | `cccc28c49e11ce75e28ab737d917ea6561f0d594d40070caad0f79ee8b237c32` |
| `tests/test_oracle_driver.py` | `31ffb352dc3d171bf7d1e2cf6b4baa8be78f08162371e2f9648125b696ebc01a` |
| `tests/test_oracle_v12_integration.py` | `f2753cd7287f4195f98d497fb895faab8984d9a1408a32d09b7ae934b31d2984` |

The protected artifacts in §9 and the v1.1 archive are unchanged by this pinning step.
