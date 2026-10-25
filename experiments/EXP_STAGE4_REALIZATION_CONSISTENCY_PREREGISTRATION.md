# POLARIS Preregistration: Realization-Consistency Experiment (Issue #3)

**Experiment identifier:** `EXP-STAGE4-REALIZATION-CONSISTENCY-2025`
**Design version:** `REALIZATION-CONSISTENCY-PREREG-v1.0`
**Date (UTC):** 2026-10-06
**Governance status:** `READY FOR FINAL AUTHORIZATION — NOT EXECUTED — NOT FROZEN (U1 and U8 resolved in §14.1–14.2; remaining items in §14.3 pending authorization)`
**Execution status:** **NOT RUN.** No campaign, replay, or solver run was performed to write this document.

**Governing references (read, not modified):**
- `experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md` / `.json` (corrected baseline)
- `experiments/stage4_corrected_reproduction_2025/` (arm A reference telemetry and results)
- `experiments/POST_CORRECTED_STAGE4_FORENSIC_AUDIT.md` / `.json` (Issue 3 origin)
- `experiments/POST_CORRECTED_STAGE4_HOUR0_TRACE.md` / `.json`
- `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.md` / `.json` (frozen original; unchanged)

---

## 0. Purpose and Question

The corrected Stage-4 reproduction reports S = 23.11% (conditional research winner), SW = 38.19% (safety failure), S-L = 13.39%, SW-L = 13.66%. The earlier audit (Issue 3) found that the optimizer's planned battery charge and the executor's realized battery charge disagree systematically. The mismatch is largest where the plan sheds non-critical load.

**Question this experiment answers:** does the current executor's charge semantics change the candidate ranking, the winner, or any safety classification, relative to a realization that honours the optimizer's first-step planned charge?

**The experiment does not decide which realization is correct.** It measures whether the conclusions depend on the choice.

---

## 1. Trace of the Planned-Charge → Realization Path (Answers to the Required Questions)

### 1.1 Where the MILP planned charge is produced (Q1)

- The MILP variable is `p_chg` at column `base + 4` of each hour block (`experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py`, bounds `[0, max_p_chg]`, lines 230–233).
- Its bus-balance role is row R3: `p_sol + p_wind + p_dis + p_diesel − p_served − p_chg − p_flex = 0`. `[VERIFIED]`
- The extractor reads the raw value (`raw_p_chg`, line 458), applies the τ = 0.055 W residue rule (`extract_and_correct_flows`, line 473), and writes the corrected value into `battery_charge` (line 511). `[VERIFIED]`

### 1.2 Where the planned charge is stored (Q2)

- `DispatchPlan.battery_charge` (list of 24 values in W). The extractor constructs the `DispatchPlan` with `battery_charge=battery_charge` (line 534). `[VERIFIED]`
- The corrected runner receives this object as `plan` and passes it to the executor. `[VERIFIED]`

### 1.3 Where the executor ignores or replaces the planned charge (Q3)

- `research_realization_executor.py:136`: `p_chg_plan = float(dispatch_plan.battery_charge[step_index])`. This is the **only** occurrence of `p_chg_plan` in the entire codebase (grep over `system/`, `experiments/`). The value is read and **never used**. `[VERIFIED]`
- The executor also does not read `dispatch_plan.load_served`, `dispatch_plan.unmet_load`, or `dispatch_plan.flexible_load_schedule`. `[VERIFIED]`
- The executor **replaces** the planned charge with a realized charge computed from the realized surplus (lines 213–225). `[VERIFIED]`
- The planned diesel and planned discharge are used (`p_diesel_plan`, `p_dis_plan`). `[VERIFIED]`

### 1.4 How realized battery charge is currently calculated (Q4) — arm A semantics

From `research_realization_executor.py`, in order:

1. Realized supply: `total_supply = solar_realized + wind_realized + diesel_realized + p_dis_realized`. `[VERIFIED]` (line 199–205 region)
2. Served load: `served_load = min(demand_realized, total_supply)`; `unmet_load = max(0, demand_realized − served_load)`. `[VERIFIED]` (lines 203–207)
3. Surplus: `surplus_power = max(0, total_supply − demand_realized)`. `[VERIFIED]`
4. Charge (only if not discharging, `p_dis_realized ≤ 1e−4`):
   - `dc_energy_room = max(0, max_e − curr_e)`
   - `max_ac_charge_allowed = dc_energy_room / η_c`
   - `max_charge_capability = min(max_charge_power, max_ac_charge_allowed)`
   - `p_chg_realized = min(surplus_power, max_charge_capability)`
   - `curtailment = surplus_power − p_chg_realized`
   `[VERIFIED]` (comment in code: "Charge up to surplus, bounded by battery charging capability")
5. Energy update: `next_e = curr_e + p_chg_realized·η_c − p_dis_realized/η_d`, clamped to `[min_e, max_e]`. `[VERIFIED]`

So the realized charge is **the realized surplus after serving the realized total demand**, bounded by power and room. It has no reference to the plan's charge.

### 1.5 Can non-critical shedding create planned charging that cannot occur in realization? (Q5)

**Yes. Verified.**

- The MILP's served variable is tied to the **critical** load by Layer B: `p_served + unmet_crit = critical_demand` (extractor lines 350–353 region; `row[base+8]=1; row[idx_unmet+t]=1; rhs=p_crit`). `[VERIFIED]`
- Together with the total demand balance R4 (`p_served + p_unmet = p_dem`), this means the plan's `p_served` **is** the critical service and `p_unmet = p_dem − p_served` contains all non-critical demand. The plan sheds all non-critical load by construction. `[VERIFIED]`
- At origin hour 0 in the corrected telemetry, forecast demand is 17,897.78 W and critical demand is 11,600 W. The plan's unmet at hour 0 is therefore 6,297.78 W, exactly the non-critical demand. `[VERIFIED]` (`STAGE4_REPRO` telemetry, unmet_load and demand columns)
- The planned charge is produced from the surplus the plan keeps **after shedding**: `P_c ≈ supply − critical − flex`. The executor instead serves the shed non-critical load first (`served = min(demand, supply)`), which leaves `supply − demand` for the battery. The gap between them is the shed amount. `[VERIFIED]` for the magnitude at hour 0 (within 50 W in 54% of unexplained SW origins in the frozen run; `POST_STAGE4_HOUR0_MILP_CAUSAL_TRACE.md` §5.13). `[INFERRED]` that the same identity holds in the corrected run.
- Conclusion: a planned charge that exists only because non-critical load is shed **cannot occur** in realization when the executor serves that load. This is a semantic mismatch between the planning model and the realization model. `[VERIFIED]`

### 1.6 Intentional research semantics or harness defect? (Q6)

**Verdict: a mixed case, not a numerical bug.**

- **Intentional surplus semantics (evidence for):** the executor's charge logic is explicit and commented ("Charge up to surplus, bounded by battery charging capability"). The Stage-4 research design (`STAGE4_SW_SAFE_EFFICIENCY_RESEARCH_DESIGN.md` §7) states that "Diesel charging, curtailment, and EMERGENCY/NORMAL routing are not directly modified. They are reported as interactions." The surplus rule was therefore inherited deliberately as realization physics. `[VERIFIED]` (code comment and design text)
- **Unintended element (evidence against a fully intentional design):** the executor reads the planned charge (`p_chg_plan`, line 136) and then discards it. A read with no use is not a design. Either the planned charge was meant to be honoured and the code was not finished, or the read is leftover. `[VERIFIED]` that it is dead; intent `[UNKNOWN]`.
- **Undocumented:** neither the Stage-4 preregistration nor the corrected preregistration states how planned charge is realized. The corrected preregistration does not mention the charge semantics at all. `[VERIFIED]`
- **Classification:** a **harness semantic mismatch, undocumented, with an unused planned-charge read.** It is not a numerical error and not a physical-law violation, because the realized energy balance closes (busbar error ≤ 1e−3 W, `[VERIFIED]` from the corrected run's balance check). It is a question of which realization the research is measuring.

---

## 2. Realization Arms

Both arms use identical optimizer output: the same MILP, the same plans, the same forecasts. Only the realization of each step's dispatch differs. **Under B the closed loop diverges from A from the first step on, because the realized SOC feeds the next MILP.** Each arm's trajectory is therefore a full closed-loop run, not a post-hoc re-accounting.

### 2.1 Arm A — CURRENT REALIZATION

Existing executor semantics **exactly as used in corrected Stage-4**: `ResearchRealizationExecutor.execute_step` in `system/simulation/research_realization_executor.py` (SHA-256 `c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b`), unmodified. Realized charge = realized surplus (§1.4). Planned charge is discarded (§1.3).

### 2.2 Arm B — PLAN-CONSISTENT REALIZATION

Realized battery charging honours the optimizer's first-step planned charge, **subject only to physically realizable energy accounting and the governed battery constraints**. Non-critical load is **not** given any priority or shedding policy beyond what the plan's own ordering implies.

Inputs for step `t` (all taken from the corrected runner's existing per-step quantities; no new optimizer output is needed):

| Symbol | Definition | Source |
|---|---|---|
| `S_pv` | realized solar power (W) | executor `pv_from_sw_in(actual_SW_IN)` (as A) |
| `W` | realized wind power (W) | `actual_wind_generation` (as A) |
| `D` | realized total demand (W) | `actual_demand` (as A) |
| `D_c` | realized critical demand, `min(11,600, D)` | as runner `d_crit` |
| `P_d` | planned diesel power (W) | `plan.diesel_power[0]` (as A) |
| `P_dis` | planned discharge (W) | `plan.battery_discharge[0]` (as A) |
| `P_c` | planned charge (W) | `plan.battery_charge[0]` (residue-corrected MILP value) |
| `P_f` | planned flexible load (W) | `plan.flexible_load_schedule[0]` |
| `E` | current stored energy (Wh) | state (as A) |

Steps:

1. **Diesel and discharge:** `diesel_realized`, `p_dis_realized` computed exactly as in A (fuel starvation rule, power limit, energy above floor). `[IDENTICAL TO A]`
2. **Realized available supply:** `S_avail = S_pv + W + diesel_realized + p_dis_realized`.
3. **Critical service:** `s_c = min(D_c, S_avail)`. Critical load is served first, as the MILP's J1 objective requires.
4. **Planned charge (realized):**
   - If `p_dis_realized > 1e−4`: `C = 0` (as A).
   - Else: `C = min(P_c, max(0, S_avail − s_c), 50,000 W, max(0, max_e − E) / η_c)`.
5. **Flexible load (realized):** `F = min(P_f, max(0, S_avail − s_c − C))`.
6. **Non-critical service (residual):** `n = min(D − D_c, max(0, S_avail − s_c − C − F))`. Non-critical load receives only the energy left after critical service and the realized planned charge. **It is a residual, never a planned decision.**
7. **Served and unmet:** `served = s_c + n`; `unmet = D − served`.
8. **Curtailment:** `curt = S_avail − served − C − F` (≥ 0 by construction).
9. **Energy update:** `E' = clamp(E + η_c·C − p_dis_realized/η_d, min_e, max_e)`, with the same clamp as A.
10. **Busbar check:** `S_avail = served + C + F + curt` must hold within 1e−3 W.

**Why this ordering is plan-implied:** the plan serves critical load (§1.5), decides a charge from what remains, and leaves non-critical load unserved. Arm B reproduces that ordering by charging before serving residual non-critical load. It adds no shedding amount and no policy. The alternative of honouring the plan's shed amount in watts, or capping served at the plan's absolute served value, would eliminate non-critical service entirely; that is a load-service policy, not a charge semantic, and is **excluded** (§14, U1).

**Consistency check (one-step, recorded hour-0 inputs, no solve):** applying step 4 to recorded hour-0 inputs reproduces the plan's first-step charge in **100% of arm-origins** (5 arms × 123 origins). `[VERIFIED]` This shows the plan is realizable on recorded hour-0 inputs under B. It is a consistency check, not an outcome.

### 2.3 Physical-realizability rule (defined before the experiment)

- **R1 (charge shortfall is not a failure):** if `C < P_c`, the difference `δ_c = P_c − C ≥ 0` is recorded as the planned-vs-realized charge error. No re-planning, no additional shedding, no fail state.
- **R2 (critical shortfall is realized unmet, not a failure):** if `s_c < D_c`, the shortfall is realized unmet and enters the reliability accounting. No fail state.
- **R3 (no energy from nothing):** `C ≤ max(0, S_avail − s_c)` is enforced; the charge cannot exceed available supply.
- **R4 (SOC bounds):** discharge is limited by energy above floor (as A). Charge is limited by room to `max_soc` (as A). Violations of the 20% floor are counted, not corrected.
- **R5 (busbar closure):** any step with busbar error > 1e−3 W is a BLOCKED audit event (§9).
- **R6 (A-side identity):** arm A has no new rule. Its shortfall `P_c − C_A` may be positive or negative and is recorded as-is.

---

### 2.4 Optimizer identity: what is identical and what is not (required by the governance review)

**Claim, stated precisely:** arms A and B use the **same optimizer code, configuration, and exogenous inputs**, and differ **only** in the realization step. They do **not** produce identical optimizer outputs beyond hour 0, because the closed loop feeds the realized state back into the next MILP. This divergence is the mechanism under test, not a violation of the design.

Verified on the corrected telemetry (`STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv`, 123 origins × 24 hours × 5 arms):

| Optimizer input | Identical across all five arms, per (origin, hour) | Source of the input |
|---|---|---|
| forecast solar, forecast wind, forecast demand | 100.00% | causal NWP and wind/demand persistence (which uses the previous *realized* wind/demand, identical across arms) |
| critical demand | 100.00% | `min(11,600, D_forecast)` |
| actual solar, actual wind, actual demand | 100.00% | simulator realized inputs (arm-independent) |
| low-sun flag and solar elevation | 100.00% | ephemeris, timestamp-only |
| timestamp | 100.00% | origin calendar |
| **battery SOC at start of hour** | identical at hour 0 for 100% of origins; differs from hour 1 onward in 94.7% of arm-hours | **state-dependent** (realized under each arm's realization) |
| **route mode (EMERGENCY/NORMAL)** | differs across arms in 36.5% of (origin, hour) pairs | **state-dependent** (router reads SOC and fuel) |
| fuel stock, diesel running state | state-dependent | realized under each arm |

Consequences for the design:
- **Same optimizer:** yes. Both arms call the same extractor code with the same configuration (`critical_demand_w`, `ebr_target_wh` per arm, terminal 100,000 Wh, startup 2.0 L, HiGHS options). The MILP is not altered.
- **Same inputs at hour 0:** yes. Both arms receive identical hour-0 state, forecasts, and route. The hour-0 MILP output is therefore identical across A and B. This is the testable identity, verified in the audit (§9, G11).
- **Same inputs afterwards:** no. From hour 1, state-dependent inputs (SOC, fuel, route) differ between A and B as a consequence of realization. This is a property of closed-loop evaluation and is reported, not hidden.
- **Only realization differs:** yes, in the sense that the realization step is the only place where A and B are specified differently. Every later difference in the trajectory is traceable to that step through the state.

**Audit gate added:** G11 (§9). At hour 0, the optimizer's inputs and outputs (plan diesel, charge, discharge, served, unmet, objective values J1–J4) are identical between A and B for every origin. Failure → BLOCKED.

## 3. What Is Held Fixed (Identical in Both Arms)

- 123 origins: calendar `2025-05-01` to `2025-08-31` inclusive, `forecast_start` at 00:00 UTC; origin ids 1–123, unique. `[VERIFIED]` as in the corrected preregistration §4.
- Five arms: Control B, S, SW, S-L, SW-L, with the corrected-reproduction equations (corrected preregistration §5).
- Synthetic demand and wind formulas; causal NWP (`fc_cloud_cover`, `previous_day1` seamless); the same forecast engine (`causal_nwp_physics.py`, SHA-256 `14e72d8a…deb710`).
- Initial state per origin: 50% SOC (100,000 Wh), diesel off, 100 L fuel, last observed demand 15,000 W, last observed wind 4,500 W (`make_initial_state`).
- Battery: 200 kWh; SOC 20–95%; charge and discharge ≤ 50 kW; η_c = η_d = 0.92.
- Diesel: 10–100 kW when on; 5 L/h base; 0.25 L/kWh marginal. **Startup: frozen by §14.2 (option A):** the optimizer charges 2.0 L per start in its objective (code default), and the simulator's reported fuel charges 0 L per start. Both are reported (§6).
- Terminal target 100,000 Wh at horizon index 23 of each reoptimization (as implemented; documentation issue noted in the audit).
- Reserve formulas, 6-hour lookahead, η = 0.92, 15° rule, solar ephemeris, 1-hour offset (all as corrected).
- Router and mode propagation: `propagate_route_mode` (SHA-256 `80456f8776925860ad20c407ec92f3ac78dbd387f4863ea48dc1917490e89376`).
- Objective hierarchy J1 > J2 > J3 > J4 and HiGHS options (`threads=1`, `blend_multi_objectives=False`, default tolerances).
- τ = 0.055 W residue rule.
- Safety gates and statistical methodology (§7, §8).

---

## 4. Factor Design and Accounting

- **Factors:** realization semantics (A, B) × arm (Control B, S, SW, S-L, SW-L).
- **Confirmatory runs:** 123 origins × 5 arms × 2 realizations = **1,230 origin-arm-realization runs**, each a full 24-hour closed loop (2,952 hours per arm per realization; 29,520 arm-hours in total).
- **Reference reproduction:** arm A must reproduce the corrected telemetry (§9, gate G1). This is a determinism check, not an extra run.
- **Diagnostic (optional, not decision-bearing):** none in this preregistration. Any additional diagnostic arm requires its own amendment.

---

## 5. Primary Outcomes (Per Arm, Per Realization)

1. Total diesel fuel (L), accounted as `Σ diesel_fuel`.
2. Paired diesel saving vs Control under the same realization: `Δ_o = Fuel_Control,r(o) − Fuel_candidate,r(o)`, total and in percent.
3. Critical-first reliability (%), accounting as corrected: `Σ min(d_crit, served) / Σ d_crit`.
4. Proportional critical reliability (%), accounting as corrected: `Σ served · d_crit/d_real / Σ d_crit`.
5. Minimum realized SOC (%) over all hours.
6. SOC-floor violations: count of hours with realized SOC < 20.00%.

## 6. Secondary Outcomes

Unmet load (kWh); curtailment (kWh); diesel-on hours; diesel startups (off→on transitions, hour 0 counted from initial off state); EFC = `(Σ battery_charge + Σ battery_discharge) / (2 × 200,000 Wh)` (as corrected); planned-vs-realized charge error `δ_c` (per hour and per origin, W and kWh); per-origin paired deltas for all outcomes.

---

## 7. Safety Gates (Unchanged)

For each realization `r` and candidate `c`, against Control B under the **same** realization:

- **Gate 1:** `ΔR_CF = R_CF(c,r) − R_CF(Control,r) ≥ 0.00 pp`.
- **Gate 2:** `ΔR_P = R_P(c,r) − R_P(Control,r) ≥ 0.00 pp`.
- **Gate 3:** no hour with realized SOC < 20.00%.

Gates are deterministic and evaluated on aggregate point estimates over 123 origins, as in the corrected preregistration. Safety precedes efficiency.

## 8. Statistical Methodology (Preserved)

- **Pairing:** origin-level, origins sorted ascending; no subsetting, trimming, or origin selection.
- **Diesel gate test (per realization):** two-sided Wilcoxon signed-rank on `Δ_o`. **Holm correction across the four candidate tests** (S, SW, S-L, SW-L) within each realization. The S diesel test is included explicitly, since the corrected summary did not report it.
- **Bootstrap:** BCa 95% CI, 10,000 origin resamples, seed 42, implemented with `scipy.stats.bootstrap(…, method="BCa", n_resamples=10000, random_state=np.random.default_rng(42))`. (A prior run's BCa differed from this implementation by up to about 0.1 L; the implementation used for this experiment is fixed here.)
- **Reliability deltas:** per-origin paired differences (candidate − Control, pp), BCa 95% CIs, descriptive and used only for the sensitivity thresholds in §10.
- **A-vs-B deltas:** for each arm, per-origin paired differences `B_o − A_o` for fuel (L), `ΔR_CF` and `ΔR_P` (pp, per origin), min SOC, unmet, curtailment, and startups. BCa 95% CIs and Wilcoxon two-sided, with Holm across the five arms per outcome.
- **Winner rule (as corrected preregistration §9):** highest saving among safety-qualified candidates whose diesel gate passes, under each realization.

## 9. Audit Gates (Must Pass Before Any Result Is Interpreted)

- **G1 — Determinism:** arm A reproduces the corrected telemetry exactly: for all 14,760 corrected rows, identical `diesel_power`, `battery_charge`, `battery_discharge`, `soc_after`, and `unmet_load` (tolerance 1e−6 W). Failure → **BLOCKED**.
- **G2 — Accounting:** exactly 123 unique origin ids per arm and realization; exactly 2,952 hourly rows per arm and realization; total 14,760 arm-hours per realization and 29,520 across both realizations. Duplicate or missing origins → **BLOCKED**.
- **G3 — Optimizer status:** every step `HighsModelStatus.kOptimal` (no infeasible, no time-limit). Any non-optimal step → **BLOCKED**.
- **G4 — Route propagation:** `optimizer_received_mode == route` on every row (as corrected). Any mismatch → **BLOCKED**.
- **G5 — EMERGENCY rows built:** on every EMERGENCY step the MILP must build exactly 24 EMERGENCY rows. This requires the new harness to count rows at build time (logging only; no model change). Any miss → **BLOCKED**.
- **G6 — Busbar closure:** `|S_avail − (served + C + F + curt)| ≤ 1e−3 W` at every step in both arms (as recorded in the executor's own check). Any violation → **BLOCKED**.
- **G7 — SOC accounting:** `E' = clamp(E + η_c·C − p_dis/η_d)` reproduces the recorded SOC to 1e−2 %. SOC bounds 19.999%–95.001% as in the runner. Violation → **BLOCKED**.
- **G8 — Fuel accounting:** accounted fuel equals `5·on_hours + 0.25·kWh` on every row except recorded starvation rows, which are listed and counted. Any other mismatch → **BLOCKED**.
- **G9 — Planned/realized reconciliation:** for each step record `P_c`, `C`, `δ_c`, plan served, realized served, plan unmet, realized unmet. The reconciliation must be complete on every row. Missing fields → **BLOCKED**.
- **G11 — Hour-0 optimizer identity:** for every origin, the hour-0 optimizer inputs (state, forecasts, route, EBR vector, terminal target) and outputs (`p_diesel`, `p_chg`, `p_dis`, `p_served`, `p_unmet`, `p_flex`, `v_start`, objective values J1–J4) are identical between arms A and B. Failure → **BLOCKED**.
- **G10 — Hash guards:** §11 hashes verified at startup and at the end of the run. Mismatch → **BLOCKED**.

## 10. Decision Rule and Classification

Preregistered thresholds (chosen before the run, not tuned on results):
- **Material saving difference:** `|Δ saving| ≥ 1.0 pp` for any candidate, with BCa CI excluding zero.
- **Material reliability difference:** `|ΔR_CF| ≥ 0.10 pp` or `|ΔR_P| ≥ 0.10 pp` for any candidate, with BCa CI excluding zero.
- **Ranking difference:** a pairwise saving difference between safety-qualified candidates whose sign flips between A and B, with BCa CI excluding zero.

Justification (fixed before the run): the S vs SW-L gap is ≈9.4 pp; the earlier audit bounded accounting-induced changes at ≤ 0.12 pp; 0.10 pp of critical reliability equals about 34 kWh of critical energy over the holdout. Thresholds are stated here and will not be altered after results are seen.

Classification, in precedence order (first matching class applies):

1. **BLOCKED:** any audit gate in §9 fails.
2. **SAFETY-CHANGING:** any candidate's Gate 1, 2, or 3 status differs between A and B (point estimates).
3. **RANKING-CHANGING:** the winner under A differs from the winner under B, or any safety-qualified pairwise ordering flips with a CI excluding zero.
4. **SENSITIVE:** winner and safety classification unchanged, ordering unchanged, but at least one material difference (§10 thresholds) exists.
5. **ROBUST:** none of the above.

**"Winner" is defined as in the corrected preregistration §9.1.** S is not presumed to remain the winner. Whichever candidate the rule selects under each realization is reported.

**Not a basis for choosing a realization:** the experiment does not declare A or B correct because one gives better fuel or reliability. Both are reported; the classification concerns only whether the conclusions depend on the choice.

---

## 11. Hash Guards

| Artefact | SHA-256 (at preregistration time) |
|---|---|
| `system/simulation/research_realization_executor.py` (executor; arm A unmodified) | `c1ab56bf92eab7c1bacb2108b241d97d84f4e935dff9a33fd8f6bd0675b73a6b` |
| `system/optimization/implementations/gap19_highs_native.py` (production GAP19) | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` |
| `system/schemas/dispatch_plan.py` | `21c0b83e878debf1e7d4c4ee9d472bb17aa84ef545a2f1b9cbb222940fd7fb0b` |
| `system/forecasting/implementations/causal_nwp_physics.py` | `14e72d8a49b962c70175451fa60c349412d936db02073b2eed746a762cdeb710` |
| `system/control/router.py` | `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f` |
| `system/schemas/station_state.py` | `e763439a6ddecbbadb9287f99258e595ab7f23f0eb9a7377f5a54beb7661df88` |
| `system/research/route_mode_propagation.py` | `80456f8776925860ad20c407ec92f3ac78dbd387f4863ea48dc1917490e89376` |
| `experiments/candidate_s_sw_campaign_2024/research_numerical_extractor.py` | `95b2f3b53609a6e420a18692b4b0e3927cb47841d9e1200cce04677094a5950e` |
| `experiments/stage4_corrected_reproduction_2025/run_stage4_corrected_reproduction.py` | `770cb61b0a73f3f8c66fd3918419ef31768dd88b47306a47bd60d1e3b06d3ecc` |
| `experiments/EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md` | `4f438f466a285d2d230edda168075f883919317922de3a5866dbb7ca5cdac14b` |
| `experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv` (arm A reference) | `6b3636d7ae4d596016f4e7b3b5fc63e9a26e374041b586b619b49afc2eec7d2e` |
| `experiments/stage4_corrected_reproduction_2025/STAGE4_REPRO_123_ORIGIN_RESULTS.csv` (arm A reference) | `8c13b904e286e25167a8eca5144e545627b6c598f36716e93fcf9ee95a2ab57e` |
| `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.md` (frozen original) | `e73558cfd03acd35fc55d24a055f7ccc6a31d0d973a3cc2e4443a8665ac21cd7` |
| `experiments/STAGE4_2025_SW_LOW_SUN_RESEARCH_FREEZE.json` (frozen original) | `6b0bb6f7af44ef06731180d50239de222f301fa571c5862d115f7644d3be7b87` |
| `experiments/stage4_sw_low_sun_2025_holdout/STAGE4_123_ORIGIN_RESULTS.csv` (frozen original) | `18d13dec71eab82919c900da52b5248699e4b5b8fa4c4ed8499aff494f4fa62b` |

The new realization module (arm B) and its runner are not yet written. They must be created as **new research-only files** (for example `system/research/plan_consistent_realization.py` and a new runner under `experiments/`) and their hashes recorded in the freeze before execution. Production files are not to be edited.

---

## 12. Implementation Boundary (Can This Run Without Changing Production Code?)

**Yes, provided these conditions hold:**

- Arm A uses the existing executor unchanged (§2.1). `[VERIFIED]` that this needs no production change.
- Arm B is a new research-only realization that reads the same `DispatchPlan` fields the executor already receives: `battery_charge`, `battery_discharge`, `diesel_power`, `flexible_load_schedule`. All are stored on the plan. `[VERIFIED]` (`dispatch_plan.py`, extractor lines 511–541). No extractor or MILP change is required for B.
- The row count needed by gate G5 is obtained by counting rows at build time inside the new harness (a spy over `highspy.Highs.addRow`, as in the focused tests). This is harness instrumentation, not a model change.
- Production code, the extractor, the MILP, the forecasts, the frozen Stage-4 artefacts, and the corrected-reproduction artefacts are not modified.

**Unresolved:** whether the governance accepts the research-only harness for arm B and the instrumentation of G5 (§14, U9).

---

## 13. Expected Behaviour (Hypotheses, Not Claims)

- **H-A (proportional reliability):** under B, non-critical load is served only from residual energy after the planned charge. Proportional reliability is expected to be lower under B for all arms, because `served` falls. The effect should be similar across arms, since all arms plan the same non-critical shedding structure. A differential effect would be a candidate-ranking concern.
- **H-B (SOC and charge):** under B, realized charge is closer to plan, so realized SOC is expected to be higher on average than under A, and the planned-vs-realized error is expected to fall to zero whenever the plan is realizable.
- **H-C (fuel):** the direction of any diesel change is not predicted. The closed loop can increase or decrease diesel through SOC feedback. This is the quantity the experiment measures.
- **H-D (ranking):** the ranking is expected to be unchanged unless candidates differ in how much their plans rely on the surplus-as-realized assumption. This is the question the experiment tests, not an assumption.

These are not predictions to be confirmed. Any of them may fail, and the classification in §10 applies regardless.

---

## 14. Unresolved Ambiguities (Require Governance Sign-Off Before Freeze)

- **U1 — RESOLVED (§14.1).**
- **U2 — Flexible-load realization.** B treats planned flex as a sink after the charge (`F = min(P_f, residual)`), bounded by 500 W. The alternative (flex = 0) changes energy by at most 0.5 kW per hour. Confirm.
- **U3 — A's critical-first accounting under shortfall.** Arm A's executor serves total demand from total supply (`min(D, S)`), while the accounting credits critical first. This asymmetry is part of A's existing semantics and is kept as is. Confirm that this is to be measured, not corrected.
- **U4 — Demand forecast bias.** Realized demand sits about 2.8 kW below forecast on average (range −3.7 to 0 kW; the forecast is persistence from the previous realized demand). Under B this bias flows into residual non-critical service, not into the charge. It is a planning feature and is not changed.
- **U5 — Holm family.** The four candidate diesel tests per realization form one Holm family. The earlier corrected report used two. Confirm the broader family.
- **U6 — Thresholds.** The thresholds in §10 (1.0 pp saving, 0.10 pp reliability) are stated before any result. Confirm they are acceptable as material.
- **U7 — Determinism (G1).** If arm A does not reproduce the corrected telemetry exactly on re-execution (for example, because of platform numerical differences), the experiment is **BLOCKED** until the cause is established. The required action is to determine the cause, not to relax the tolerance.
- **U8 — RESOLVED (§14.2).**
- **U9 — Arm B harness and instrumentation.** Confirm that a new research-only realization and the build-time row-count instrumentation (G5) are acceptable under the governance rules for research harnesses.
- **U10 — The dead read `p_chg_plan` (§1.3).** Arm A keeps it unused, since A is defined as the existing semantics. Confirm that this is to be recorded as a known defect rather than corrected in A.

---

### 14.1 U1 — Plan-consistent realization: resolved

**Arm B means exactly this realization order, per step:**

1. critical load served from realized supply;
2. planned battery charge realized, capped by remaining realized supply, the 50 kW limit, and room to 95%;
3. planned flexible load realized as a sink, capped by remaining supply;
4. non-critical load served from whatever realized supply remains.

**Status of arm B (stated explicitly):**
- B is a **research diagnostic realization semantics**.
- B **does NOT establish the correct operational load-priority policy.** Nothing in this experiment asserts that critical-first-then-charge-then-residual is how the microgrid should operate.
- B is designed **only** to test whether the existing planned-versus-realized charge mismatch materially changes candidate conclusions.

**Why "honour planned served load literally" is excluded.** The plan's served variable is tied to the critical load by Layer B (§1.5). Honouring it literally would serve **only the critical load in every hour** and set non-critical service to zero for every arm. That changes the load-service policy for all arms and collapses proportional reliability by construction, so any difference it produced would measure a load-service policy change, not the charge-realization mismatch. It is therefore excluded and not reported as an arm.

**Residual effect, stated for transparency:** B serves less non-critical load than A in hours where the plan charges, because charge is realized before residual non-critical service. This is the mismatch's own consequence, not an added policy. The experiment measures it and does not treat it as a design choice.

### 14.2 U8 — Startup fuel: resolved as option A (preserve extractor semantics)

**Facts established:**
- `system/config/diesel.yaml` has no `startup_fuel_l` key. The only startup key present is `startup_cost: 15.0` (currency units), which the Stage-4 path does not read.
- The research extractor reads `startup_fuel_l` with default **2.0 L** (`research_numerical_extractor.py:148`) and charges it in the MILP objective (`c3[base+14]`, line 380). `[VERIFIED]`
- The realization executor charges **0 L** per start. `[VERIFIED]`
- The corrected preregistration (§3, item 6) states "startup fuel 0.0 L (mathematical model)." That describes the simulator's fuel accounting, not the optimizer, and it contradicts the optimizer's 2.0 L. `[VERIFIED]`

**Options considered:**
- **A — preserve the actual extractor semantics (2.0 L in the optimizer objective; 0 L in reported simulator fuel).**
- **B — exclude startup fuel from this experiment.** Rejected: excluding it requires changing the MILP objective (forbidden by this experiment's own rules) or changing the accounting, which would make A and B incomparable with the corrected reproduction.
- **C — another governance decision.** Not required; the actual semantics are fixed by code and are the same as the corrected reproduction.

**Selected: option A, frozen explicitly.**
- The optimizer objective uses **2.0 L per start**, the code default, held as a constant in the extractor. The harness must **not** read a startup value from configuration. The YAML key is absent, so any read would silently fall back to the default. The constant is frozen by hash guard (§11).
- **Reported diesel fuel** (the primary outcome) is the **simulator's accounted fuel**, which charges 0 L per start. This is the same quantity as the corrected reproduction, so results are comparable.
- **Secondary accounting** (reported alongside, not decision-bearing): MILP-objective fuel = accounted fuel + 2.0 L × startups. Both accountings are reported for every arm and realization, and the ranking under each is reported.
- The corrected preregistration's "0.0 L" wording is a **documentation error** about the optimizer. It is not corrected in this experiment and must be corrected by governance in that document, without changing any result.

**Why A:** it is the only option that leaves the optimizer unchanged, keeps the reported outcome comparable with the corrected reproduction, and tests the realization mismatch in isolation. Startup contributions are reported under both accountings, so the question of whether startup accounting alters any conclusion is answered by the experiment itself.

### 14.3 Remaining items (proposed defaults; pending final authorization)

- U2 (flex sink versus zero), U3 (critical-first accounting under shortfall in A), U4 (demand forecast bias), U5 (Holm family of four per realization), U6 (thresholds 1.0 pp and 0.10 pp), U7 (determinism gate), U9 (research-harness approval and build-time row-count instrumentation), U10 (dead read `p_chg_plan` kept in A). Each keeps the default stated in §14 earlier, and each is listed for the final authorization.

## 15. Pre-Registered Timeline and Outputs (Not Executed)

- Outputs (new, not overwriting corrected or frozen results): `experiments/stage4_realization_consistency_2025/` with per-realization telemetry, results, safety reports, statistical reports, A-vs-B delta tables, and an audit report covering G1–G10.
- Run order: (1) hash guards; (2) determinism run of A (G1) — stop if it fails; (3) arm B; (4) audit; (5) statistics; (6) classification per §10.
- No run may begin until §14 is resolved and this document is frozen with its hash recorded.

---

## 16. Immutability

This preregistration is frozen only after the §14 ambiguities are resolved. The hash of this file is recorded in `experiments/EXP_STAGE4_REALIZATION_CONSISTENCY_PREREGISTRATION.json` and must be verified before any execution. Post-registration changes to thresholds, arms, outcomes, or the B rule are not permitted; any such change requires a new preregistration.

**STATUS:** READY FOR FINAL AUTHORIZATION — NOT EXECUTED — NOT FROZEN. Freeze occurs only on final authorization, and the hash is then recorded in the JSON.
