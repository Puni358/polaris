# POLARIS — Post-Corrected-Stage-4 Forensic Audit

**Date (UTC):** 2026-10-06
**Status:** AUDIT ONLY. No campaign run. No production code modified. No frozen original Stage 4 result modified. No corrected reproduction result modified. No correction applied to any result.
**Method:** read-only inspection of code and artifacts, plus offline analyses of existing telemetry and results files (scratch scripts outside the repository).

**Labels:** `[VERIFIED]` reproduced from code or artifacts. `[INFERRED]` a structural argument from verified facts. `[HYPOTHESIS]` a possible explanation needing an experiment. `[UNKNOWN]` cannot be established from existing evidence.

**Issue classes:** VERIFIED BUG · VERIFIED SEMANTIC MISMATCH · DOCUMENTATION ONLY · NON-MATERIAL · MATERIAL BUT REQUIRES NEW EXPERIMENT · UNKNOWN.

---

## 1. Overall Status

**STATUS: ISSUES_FOUND.** Several issues are real. None of them changes the candidate ranking or the safety conclusion on the evidence available. One issue (planned-versus-realized battery charge) and one cause (hour-0 diesel) can only be settled by a new, separately preregistered experiment or an authorised solver trace.

**Corrected numbers (as reported in the corrected summary and reproduced from the telemetry):**

| Arm | Diesel reduction | ΔR_CF (pp) | ΔR_P (pp) | Min SOC | Safety |
|---|---|---|---|---|---|
| Control B | 0.00% (6,096.90 L) | — | — | 54.99% | reference |
| S | **23.11%** | +0.640621 | +0.822681 | 20.00% | PASS |
| SW | 38.19% | +0.282287 | **−0.581490** | 20.00% | SAFETY FAILURE |
| S-L | 13.39% | +0.639338 | +1.156484 | 20.00% | PASS |
| SW-L | 13.66% | +0.740792 | +1.391137 | 20.00% | PASS |

Reproduced from `STAGE4_REPRO_123_ORIGIN_HOURLY_TELEMETRY.csv` and `..._RESULTS.csv`. `[VERIFIED]`

---

## 2. Issue Summary

| # | Issue | Status | Materiality | Can change winner? |
|---|---|---|---|---|
| 1 | Startup fuel semantics | VERIFIED SEMANTIC MISMATCH | NON-MATERIAL to ranking | No |
| 2 | Fuel-cap semantics | VERIFIED SEMANTIC MISMATCH | NON-MATERIAL to ranking | No |
| 3 | Planned vs realized battery charge | VERIFIED SEMANTIC MISMATCH | **MATERIAL BUT REQUIRES NEW EXPERIMENT** | Not shown; cannot be excluded offline |
| 4 | Terminal-target indexing | VERIFIED BUG (telemetry logging) + VERIFIED SEMANTIC MISMATCH (documentation vs implementation) | NON-MATERIAL to ranking (symmetric across arms) | No |
| 5 | Hour-0 diesel selections | UNKNOWN (cause) | MATERIAL BUT REQUIRES NEW EXPERIMENT for S | Not shown; cannot be excluded offline |
| 6 | Route-mode fix verification | Propagation VERIFIED; `emergency_constraint_active` column is a VERIFIED BUG (label, not evidence) | NON-MATERIAL | No |
| 7 | Candidate-ranking robustness / S diesel gate reporting | DOCUMENTATION ONLY (S gate unreported; its outcome passes offline) | NON-MATERIAL | No |

Full machine-readable matrix: `experiments/POST_CORRECTED_STAGE4_FORENSIC_AUDIT.json`.

---

## 3. Issue 1 — Startup Fuel Semantics

### 3.1 Code paths

- **MILP J3 startup term:** `research_numerical_extractor.py:380` `c3[base+14] = startup_fuel_l`, where `startup_fuel_l = float(diesel_cfg.get("startup_fuel_l", 2.0))` (line 148). The corrected runner passes `BASE_CONFIG["diesel"]` loaded from `system/config/diesel.yaml`, which has **no** `startup_fuel_l` key. So the MILP uses the code default **2.0 L per start**. `[VERIFIED]`
- **Simulator fuel:** `research_realization_executor.py:173` `fuel_req = (base + marginal·p_diesel)·1 h`. No startup term. `[VERIFIED]`
- **Preregistration text:** `EXP_STAGE4_CORRECTED_REPRODUCTION_PREREGISTRATION.md` §3 item 6 states "startup fuel 0.0 L (mathematical model)". This does **not** match the MILP that ran (2.0 L). `[VERIFIED]`
- The `diesel.yaml` key `startup_cost: 15.0` (currency) is used only by `system/evaluation/evaluator.py` and `system/robustness/metrics.py`, not by this path. `[VERIFIED]`

### 3.2 Telemetry check (corrected)

- Accounted fuel equals `5·on_hours + 0.25·kWh` exactly, with one row off by more than 0.01 L. That row is a fuel-starvation hour (Issue 2). `[VERIFIED]`
- Starts: S 237, S-L 281, SW 159, SW-L 270, Control 308 (corrected). The start count is not constant across arms. `[VERIFIED]`

### 3.3 Effect on the diesel-reduction numbers

| Arm | Reduction, accounted | Reduction, MILP-objective (accounted + 2 L × starts) | Δ (pp) |
|---|---|---|---|
| S | 23.114 | 23.108 | −0.006 |
| S-L | 13.395 | 12.970 | −0.425 |
| SW | 38.189 | 39.124 | +0.935 |
| SW-L | 13.662 | 13.540 | −0.121 |

`[VERIFIED]`

### 3.4 Ranking impact

- Winner S (23.11%) changes by at most 0.006 pp. Its lead over SW-L (≈9.4 pp) is far larger than any accounting variant.
- The order S > SW-L > S-L holds under both accounting conventions. SW-L > S-L holds under both (13.66 vs 13.39 accounted; 13.54 vs 12.97 MILP-objective).
- Safety uses served load, not fuel, so startup accounting cannot change any safety gate. `[VERIFIED]` (`run_stage4_corrected_reproduction.py` gate code uses reliability and SOC only)
- Control's fuel is also computed from accounted fuel, so the change is common to the reference.

**Classification:** VERIFIED SEMANTIC MISMATCH. The preregistration's stated startup value (0.0 L) does not match the optimizer's (2.0 L). **NON-MATERIAL** to ranking and safety.

**Correction:** documentation/governance. Either state 2.0 L as the optimizer's startup value and report both accountings, or declare the mismatch in the preregistration. No result changes.

---

## 4. Issue 2 — Fuel-Cap Semantics

### 4.1 Code paths

- Initial fuel: `make_initial_state` gives `diesel_fuel_remaining_liters = 100.0` per origin, with no refuelling. `[VERIFIED]`
- Simulator cap: `research_realization_executor.py:168–192`. When `avail < fuel_req`, `fuel_consumed = avail`, and `diesel_realized = min(plan, (avail − base)/marginal)` (0 if avail ≤ base). `[VERIFIED]`
- MILP: no fuel-stock variable or constraint. The MILP cannot see the cap. `[VERIFIED]`
- Preregistration §3 item 7 states "cumulative fuel accounting tracks total litres consumed **without artificial clipping**." This describes the accounting; the simulator stock is a physical limit that clips delivery. `[VERIFIED]`

### 4.2 Occurrence in corrected telemetry

- Origins at 100 L: **one**, Candidate SW origin 39, reaching the cap at **hour 22**. `[VERIFIED]`
- Control maximum 89.43 L; S 96.44 L; S-L 90.59 L; SW-L 98.38 L (none capped). `[VERIFIED]`
- The frozen run had two capped origins (S and SW-L, origin 39, both at hour 22). `[VERIFIED]`

### 4.3 Can the cap affect the conclusions?

- **Connection to hour-0 decisions:** none. Maximum hour-0 fuel is 5 + 0.25 × 54.6 = 18.65 L, far below 100 L. `[VERIFIED]`
- **Effect on S and SW-L:** none in the corrected run, because neither reaches the cap.
- **Effect on SW:** SW's delivered fuel in origin 39 is capped, so its reported 38.19% saving is inflated relative to an uncapped run. SW is a safety failure, so this cannot change the winner. `[VERIFIED]` for the direction; magnitude `[UNKNOWN]`.
- **Could the cap flip SW's safety gate?** SW needs +0.58 pp of proportional reliability to pass Gate 2. Denominator: 34,243 kWh total critical demand, so 0.58 pp ≈ 199 kWh. The cap acts only from hour 22 onward, so at most the two critical hours (2 × 11.6 kWh = 23.2 kWh) can be lost. That is at most **0.068 pp**, far below 0.58 pp. The cap cannot flip SW's gate. `[VERIFIED]` arithmetic

**Classification:** VERIFIED SEMANTIC MISMATCH (MILP does not model the fuel stock; the preregistration's "without artificial clipping" wording does not describe the physical stock). **NON-MATERIAL** to ranking and safety.

**Correction:** documentation. The cap should be stated in the preregistration as a physical input, and its occurrence reported. Adding a fuel-stock constraint to the MILP would change results and requires a new preregistered experiment; it must not be done as a silent fix.

---

## 5. Issue 3 — Planned vs Realized Battery Charge

### 5.1 Code paths

- **Plan:** the MILP chooses `p_chg` (R5, bounded by 50 kW), with bus balance R3 `p_sol + p_wind + p_dis + p_diesel − p_served − p_chg − p_flex = 0`. Non-critical served and unmet energy and `p_flex` (0–500 W) carry **no objective cost** (only J1 critical unmet, J2, J3, J4 curtailment are priced). `[VERIFIED]` (`research_numerical_extractor.py` objective block, lines 375–381)
- **Realization:** `research_realization_executor.py:209–230`. Served load = `min(demand, supply)` (non-critical served first). Charge = `min(surplus, charge rate, room)` where surplus is the residual after serving demand. The executor **does not** execute the plan's charge. `[VERIFIED]`

### 5.2 Quantification (corrected telemetry)

Gap = `corrected_p_chg − battery_charge` (planned minus realized, W):

| Arm | Mean gap (kW) | Median (kW) | Share of hours with gap > 1 kW | Share with \|gap\| < 1 W |
|---|---|---|---|---|
| Control B | 1.08 | 0.00 | 31.2% | 51.5% |
| S | 0.72 | 0.00 | 27.0% | 54.8% |
| S-L | 0.81 | 0.00 | 27.8% | 54.3% |
| SW | 0.49 | 0.00 | 24.1% | 56.9% |
| SW-L | 0.83 | 0.00 | 27.9% | 54.2% |

`[VERIFIED]`. The frozen run is almost identical (Control 1.07, S 0.74, SW 0.50, S-L 0.83, SW-L 0.84 kW). `[VERIFIED]`

Mean battery discharge gap is zero in every arm (planned and realized discharge agree). `[VERIFIED]`

### 5.3 Cause

- Planned charge exceeds realized charge whenever the plan serves less non-critical load than the realized surplus allows. In the frozen hour-0 analysis, planned minus realized charge equalled the non-critical demand to within 50 W in 54% of SW origins. `[VERIFIED]` for the frozen run.
- The same mechanism is expected in the corrected run because the code path is unchanged, but the identity was **not** re-verified on corrected rows. `[INFERRED]`
- Remaining residuals are the flexible-load variable (≤ 500 W) and solar forecast-versus-actual differences. `[INFERRED]`

### 5.4 Is it a harness accounting defect or forecast/realization behaviour?

- It is a **semantic mismatch between the optimizer's planning model and the executor's realization model**, not an arithmetic error. Each side is internally consistent. The planning model is optimistic because non-critical shedding is free in the objective and the executor will not shed it. `[VERIFIED]` by code reading.
- It is not purely forecast error: the gap is large and systematic at hour 0 even with zero forecast error on wind (hour-0 wind is known).

### 5.5 Can it bias candidate comparisons?

- **Scored outcomes are realized.** Safety gates and fuel use realized quantities, so the bias enters only through plan quality, i.e., the plans the candidates make.
- **Asymmetry:** the mean gap differs by arm (Control 1.08 kW, candidates 0.49–0.83 kW). Control's larger optimism is the reference; the candidates' smaller gaps mean their plans are closer to realization. Whether this shifts the 23.11 vs 13.66 comparison **cannot be determined offline**, because the counterfactual (plans with realization-aligned charge) requires a new run. `[UNKNOWN]` for magnitude.

**Classification:** VERIFIED SEMANTIC MISMATCH. **MATERIAL BUT REQUIRES NEW EXPERIMENT**: quantifying its effect on the ranking needs a separately preregistered campaign in which the planning model and the realization model agree on whether non-critical load is shed. Do not correct this in place: any change alters the optimizer's objective and results.

---

## 6. Issue 4 — Terminal-Target Indexing

### 6.1 Code path (verified end to end)

1. **Target value:** `terminal_target_wh = 100000.0` from `BASE_CONFIG` (`run_diesel_reduction_campaign.py:82`), passed to the optimizer through `step_configs` / `cfg_copy`. `[VERIFIED]`
2. **Optimizer construction:** `research_numerical_extractor.py:209–212`: `e_stage2[t] = ebr[t]` for `t < 23`; `e_stage2[23] = max(ebr[23], terminal)`. `[VERIFIED]`
3. **Constraint:** Layer C, `E_next[t] + s_j2[t] ≥ e_stage2[t] + 40,000 Wh` for `t = 0…23`, soft with J2 priority 3. `[VERIFIED]`
4. **Index meaning:** the `ebr` vector is built from the step's **own** 24-hour bundle, so index 23 is the step's horizon hour 24 (absolute hour `t + 23` at reoptimisation step `t`). At step 0 it is origin hour 23; at later steps it is in the next day. `[VERIFIED]`
5. **Logging:** `run_stage4_corrected_reproduction.py:136, 150, 303`. `stage2_target_wh = stage2_vector[0]` (index 0), so the column always equals `ebr_target_wh`. Verified: `stage2_target_wh == ebr_target_wh` on all 14,760 corrected rows. `[VERIFIED]`
6. **Realization:** the executor has no terminal term. The terminal affects only planning. `[VERIFIED]`

### 6.2 Resolution

- **IMPLEMENTATION:** the terminal floor applies at every reoptimisation's horizon index 23, not at origin-day hour 23. `[VERIFIED]`
- **DOCUMENTATION:** the historical design and the Stage 4 preregistration describe the target as the origin day's hour 23. The corrected preregistration §3 item 4 says "at horizon index 23", which matches the implementation, while its §5 horizon-edge formula is still written per origin-day `t`. So the documentation is internally inconsistent. `[VERIFIED]`
- **LOGGING:** the `stage2_target_wh` column is a **VERIFIED BUG**: it is labelled as the stage-2 target but records index 0, so it can never show the terminal. The optimizer is unaffected.

### 6.3 Materiality

- **Symmetric:** the same terminal rule applies to all five arms. Effect on the 23.11 vs 13.66 comparison: none identified. `[INFERRED]`
- Level effect is real: hour-23 realized SOC reaches 70% in 33% (SW), 47% (S), 53% (S-L), 56% (SW-L), 81% (Control). `[VERIFIED]`. This is a property of all arms and does not reorder them.

**Classification:** VERIFIED BUG (telemetry logging, non-material; correct in any future harness version without changing results) + VERIFIED SEMANTIC MISMATCH (documentation vs implementation, non-material to ranking).

**Correction:** fix the logging column in the next harness version (it must not change optimizer inputs). Correct the documentation to "horizon index 23 at each reoptimisation." Any change to the terminal rule's semantics requires a new preregistered experiment.

---

## 7. Issue 5 — Hour-0 Diesel Selections

### 7.1 Reproduced (corrected run)

Using the corrected telemetry's logged hour-0 reserve (the same index-0 formula):

| Arm | Diesel ON at hour 0 | Forced by index-0 reserve | Forced and ON | ON but not forced |
|---|---|---|---|---|
| Control | 123 | 123 | 123 | 0 |
| S | 94 | 82 | 82 | **12** |
| S-L | 123 | 123 | 123 | 0 |
| SW | 39 | 0 | 0 | **39** |
| SW-L | 123 | 123 | 123 | 0 |

`[VERIFIED]`. These counts are **identical** to the frozen run. The route-mode fix did not change hour-0 behaviour. `[VERIFIED]`

### 7.2 Status

- The earlier trace found SW-L's hour-0 diesel to be SELECTED under lexicographic priority (J2 slack above fuel), with a J1-caveat. That status is unchanged. `[VERIFIED]` at the index-0 level; `[INFERRED]` at the global level.
- The 39 SW and 12 S unexplained hour-0 diesel decisions have **UNKNOWN** causal attribution. The corrected telemetry does not contain the planned future trajectory, duals, or constraint activity. `[UNKNOWN]`

### 7.3 Materiality

- For **SW** (safety failure): non-material to the winner, since SW cannot be the winner.
- For **S** (winner): the 12 unexplained origins are 10% of the population. Whether their hour-0 diesel is a physical necessity or a degenerate tie cannot be determined. A removal test would be a counterfactual, which this audit does not perform. `[UNKNOWN]`

**Classification:** UNKNOWN (cause). **MATERIAL BUT REQUIRES NEW EXPERIMENT** for S: an authorised, read-only solver trace of the frozen corrected MILP at hour 0 for the 12 S origins, recording dual values and constraint activity, is required before S's hour-0 decisions can be classified. This is an analysis of a solve, not a campaign. It must be authorised separately.

---

## 8. Issue 6 — Route-Mode Fix Verification

### 8.1 Propagation (VERIFIED)

- Corrected runner: the only two `optimize()` calls pass `planning_state` (`run_stage4_corrected_reproduction.py:137` inside the interceptor, and `:226`). `planning_state = propagate_route_mode(current_state, route_mode)` at `:215`. `[VERIFIED]`
- Corrected telemetry: `optimizer_received_mode == route` on **all 14,760** rows. Counts: EMERGENCY 8,288 (S 1,723; S-L 1,689; SW 1,815; SW-L 1,660; Control 1,391); NORMAL 6,472. `[VERIFIED]`
- The executor's `next_state` still carries NORMAL. It is overwritten by the planning copy at every step, so the carried value cannot reach the MILP. `[VERIFIED]`
- **Old bug cannot affect corrected results via the state path.** The corrected runner does not call the frozen Stage 4 runner or the 2024 runner, and the two shared research loops it could have used are not invoked by it. `[VERIFIED]` by code reading.
- Control is also routed (1,391 EMERGENCY rows), so Control's reference changed too (6,117.97 → 6,096.90 L). The correction is symmetric across the reference and the candidates. `[VERIFIED]`

### 8.2 Evidence of constraint activation

- `emergency_constraint_active` is written as `bool(route_mode == "EMERGENCY")` (`run_stage4_corrected_reproduction.py:278`). It is **derived from the route**, not an observation of a built MILP row. It is therefore a **VERIFIED BUG** as evidence: it cannot prove activation. `[VERIFIED]`
- Offline behavioural check: realized discharge exceeding realized served load (> 1 W) occurs in 0 of EMERGENCY hours in the corrected run, versus 6 in the frozen run. This is weakly consistent with activation, but the counts are small and it is not proof. `[VERIFIED]` count; `[INFERRED]` as support.
- Direct proof of activation remains the focused tests (`tests/test_research_route_mode_propagation.py`, 8/8 passing), which count the EMERGENCY rows in the real MILP. Those tests did not run on the corrected campaign's steps.

### 8.3 Gaps in verification

- The corrected preregistration's hash manifest does **not** include `research_numerical_extractor.py` (the optimizer that ran). Its hash is pinned only in the design document. `[VERIFIED]`
- **Recommendation:** a future harness must log the number of EMERGENCY rows actually built per step (from the solver's row count), and pin the extractor's hash in the preregistration.

**Classification:** propagation **VERIFIED**. The `emergency_constraint_active` column is a **VERIFIED BUG** (evidence labelling), **NON-MATERIAL** to results. The extractor-pinning gap is **DOCUMENTATION ONLY**.

---

## 9. Issue 7 — Candidate-Ranking Robustness

### 9.1 S diesel gate was not reported

- `STAGE4_REPRO_STATISTICAL_REPORT.md` evaluates the diesel gate for **S-L and SW-L only**. The corrected preregistration's winner rule (§9.1) requires the winner to have a "statistically significant diesel reduction," but S's test is absent from the artifacts. `[VERIFIED]`
- Computed offline from the corrected per-origin results (Control minus S), using `scipy.stats`:
  - Mean saving 11.457 L/origin, median 10.396 L.
  - Wilcoxon two-sided p = 2.45 × 10⁻¹⁰.
  - BCa 95%: [8.50, 14.32] L (my implementation). `[VERIFIED]` as an offline computation.
- Validation of method: my BCa for S-L [4.31, 8.84] and SW-L [4.38, 9.12] differs from the reported intervals [4.26, 8.96] and [4.34, 9.13] by up to about 0.1 L. The reporting code's bootstrap implementation differs slightly, but the conclusions are identical. S's lower bound (≈8.5 L) is far above zero under either implementation. `[VERIFIED]`

**Classification:** DOCUMENTATION ONLY. The outcome is not in doubt, but the winner rule's significance criterion is not reported in the artifacts for the winner. The correction is to report it.

### 9.2 Robustness of S = 23.11% as the winner

| Source of possible change | Effect on S vs SW-L gap (≈ 9.45 pp) | Conclusion |
|---|---|---|
| Startup accounting (Issue 1) | ≤ 0.12 pp | No change |
| Fuel cap (Issue 2) | None on S (not capped); SW only | No change |
| Planned vs realized charge (Issue 3) | Not quantified offline | Cannot be excluded; requires experiment |
| Terminal indexing (Issue 4) | Symmetric across arms | No change identified |
| Hour-0 unexplained diesel (Issue 5) | Not quantified offline | Cannot be excluded; requires trace |
| Route propagation (Issue 6) | Already included in the corrected results | Not a residual issue |

Safety gates for S are deterministic and have margin: ΔR_CF +0.64 pp, ΔR_P +0.82 pp, zero SOC violations. The minimum SOC of 20.00% is a binding floor but not a violation. `[VERIFIED]`

**Conclusion:** no identified semantic issue can plausibly reverse the S > SW-L ordering, because the gap is ~9 pp and every offline-quantifiable source moves it by ≤ 0.12 pp. Issues 3 and 5 are unquantified and must be settled before a claim is treated as final. `[INFERRED]` for Issues 3/5 being unlikely to close a 9 pp gap; `[UNKNOWN]` for their magnitude.

### 9.3 SW's safety failure is robust

- SW's proportional deficit is −0.58 pp. The fuel cap can account for at most 0.068 pp of critical energy (Issue 2), so the cap cannot flip it. `[VERIFIED]` arithmetic.
- Planned-versus-realized charge (Issue 3) could in principle change SW's realized reliability, but SW's planned charge gap is the smallest of the five arms, so the bias direction favours SW's reliability being **less** affected by planning optimism. `[INFERRED]` only; not quantified.

### 9.4 Factorial and mechanism claims

- The corrected C4 interaction is +1.6388 pp [1.2559, 2.0576], and it excludes zero. The frozen C4 was +1.2515 pp. The corrected claim stands. `[VERIFIED]` from the corrected factorial report.
- The corrected C4 uses the corrected telemetry (route-propagated). The earlier mechanism statement ("factorial evidence supports the hypothesized low-sun protection mechanism") is retained as a research-level statement only.

---

## 10. Answer: Can S = 23.11% Be Treated as the Corrected Research Winner?

**YES, as the corrected current frozen research winner**, with the following conditions stated:

1. The S diesel gate must be **reported** in the corrected statistical report (offline computation: p = 2.5 × 10⁻¹⁰; BCa lower 8.5 L). The reporting gap is DOCUMENTATION ONLY and does not change the outcome. `[VERIFIED]`
2. Startup accounting and the fuel-cap language in the corrected preregistration must be corrected by documentation (Issues 1, 2). Neither changes the ranking. `[VERIFIED]`
3. The planned-vs-realized charge (Issue 3) and the hour-0 S unexplained decisions (Issue 5) are not closed. These are the two items that could change the S claim under a future audit, and they require the experiments named in §11. Until they are settled, the claim stands as **research** only.
4. This is **not** a production claim. `[VERIFIED]` by preregistration §9.3.

---

## 11. Required Next Actions (no campaign performed)

| Action | Type | Purpose | Authorisation |
|---|---|---|---|
| A. Report the S diesel gate in the corrected statistical report | Documentation | Winner rule compliance | Governance (no re-run) |
| B. Correct the corrected preregistration: startup 2.0 L as optimizer value, cap as physical input, terminal indexing wording | Documentation | Issues 1, 2, 4 | Governance |
| C. Fix the `stage2_target_wh` logging column and the `emergency_constraint_active` evidence column in the next harness version | Harness logging (results unchanged) | Issues 4, 6 | Separate harness change |
| D. Pin `research_numerical_extractor.py` in the corrected preregistration hash manifest | Documentation | Issue 6 | Governance |
| E. Read-only solver trace (duals, constraint activity) of hour 0 for the 12 S unexplained origins, from the frozen corrected MILP | Analysis of one solve per origin | Issue 5 | **Separate authorisation required** |
| F. A new, separately preregistered experiment comparing planning and realization semantics for non-critical load (plan-consistent shedding vs free shedding) on the 123 origins | New campaign | Issue 3 magnitude | **Separate preregistration and authorisation required; not performed** |

Nothing above modifies the corrected results. Action F is the only one that would change results, and it is explicitly not performed here.

---

## 12. Proven / Inferred / Unknown

**[VERIFIED]**
- Route propagation reaches the MILP on all 14,760 corrected rows (`optimizer_received_mode == route`).
- Corrected and frozen numerical results as reported (§1), reproduced from telemetry.
- MILP startup = 2.0 L default; simulator startup = 0; preregistration states 0.0 L.
- Accounted fuel equals the code formula (`5 h + 0.25 kWh`) except for one starvation row.
- Fuel cap reached only in SW origin 39 at hour 22 (corrected).
- Fuel cap cannot reach the hour-0 decisions (max 18.65 L at hour 0).
- Planned-minus-realized charge gap by arm (§5.2).
- Hour-0 counts identical to the frozen run (§7.1).
- S diesel gate passes offline (p = 2.5 × 10⁻¹⁰; BCa lower ≈ 8.5 L).
- The fuel cap can shift SW's critical reliability by at most 0.068 pp.
- `stage2_target_wh` never shows the terminal; `emergency_constraint_active` is route-derived.

**[INFERRED]**
- The planned-vs-realized gap is produced by the same non-critical-shedding mechanism as in the frozen run.
- The S > SW-L ordering is not reversed by any identified semantic issue.
- The EMERGENCY constraint is active in corrected runs (weak behavioural support; direct proof is in the unit tests).

**[UNKNOWN]**
- The effect of planned-vs-realized charge on the candidate comparison (Issue 3 magnitude).
- The causal attribution of the 12 S and 39 SW unexplained hour-0 diesel decisions (Issue 5).
- The magnitude of the cap's effect on SW's reported 38.19% saving.
- Whether the corrected MILP built exactly 24 EMERGENCY rows per EMERGENCY step (not logged).

---

## 13. Governance Summary

- Overall audit: **ISSUES_FOUND**.
- Requires correction (documentation or logging, results unchanged): Issues 1, 2, 4, 6, 7.
- Requires a new experiment or authorised trace before a final claim: Issues 3 and 5.
- Does **not** require correction: route propagation itself (verified); fuel-cap physics (a true physical limit, to be stated, not removed).
- **Research winner:** S = 23.11% may be carried as the corrected current frozen research winner with the conditions in §10.
- **No campaign was run.** No production or frozen artifact was modified.
