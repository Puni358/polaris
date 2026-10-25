# Independent Audit: DIESEL_REDUCTION_CONTROL_DESIGN (AGY)

**Audit scope:** `DIESEL_REDUCTION_CONTROL_DESIGN.md`, `.json`, `_MANIFEST.json`; `gap19_highs_native.py`; the EBR forensic set (`EBR_BRANCH_FINAL_SYNTHESIS.md`, `CRITICAL_AWARE_EBR_FAILURE_REVIEW.md`, `TERMINAL_ABLATION_REPORT.md`, `EBR_ABLATION_REPORT.md`, `HOURLY_TRACE_REPORT.md`), plus `EBR_ABLATION_123_REPORT.md`, `diesel.yaml`, `battery.yaml`, and the 2024 fixture.
**Constraints honoured:** no controller experiments, no simulation, no production or design-file edits. Existing results are treated as authoritative. One read-only arithmetic check on the existing 2024 forecast fixture is reported in §4.1.

**Labels:** `VERIFIED` (checked against code or artifact), `INFERRED` (follows from verified facts, not directly measured), `UNSUPPORTED` (no authoritative basis in the repo), `BLOCKED` (cannot be assessed without data or a decision not yet made), `WRONG` (contradicted by code or artifact).

---

## 1. Verdict

**`CORRECTION_REQUIRED`**

No candidate is ready to implement as written. Two candidates fail for mechanical reasons (Candidate 1 can produce an infeasible model; Candidate 4's attribution is wrong). Candidate 2 is the closest to defensible, but its central safety mechanism is inactive on the test origins that motivated it. Every candidate needs the corrections listed in §7. The design's headline percentages and its "100% reliability" guarantee should be removed.

---

## 2. Verified GAP19 Facts the Design Relies On

| Item | Evidence | Label |
|---|---|---|
| Diesel binaries and bounds: `p_diesel ≥ 10 kW·u` and `≤ 100 kW·u`; startup `v_start ≥ u_t − u_{t−1}` | `gap19_highs_native.py` rows 9–11 | VERIFIED |
| **No minimum up-time and no startup delay in the MILP.** A diesel start is instantaneous in the step it is committed | No constraint on `u` over time beyond the startup tracker | VERIFIED |
| `diesel.yaml` sets `min_up_time_hours: 2`, `min_power_w: 10000`, `base_fuel 5 L/h`, `marginal 0.00025 L/Wh` | `system/config/diesel.yaml` | VERIFIED |
| `diesel.yaml` has **no startup time key**. Its `startup_cost: 15.0` is a currency penalty, not litres. GAP19 reads `startup_fuel_l`, defaulting to **2.0 L** | `diesel.yaml`; code default | VERIFIED (the 2.0 L value is a code default, not a config value) |
| Battery: 200 kWh, `min_soc 20%`, `max_soc 95%`, `η = 0.92` both ways, `P_chg ≤ 50 kW` | `battery.yaml`; code | VERIFIED |
| EBR default window is `range(t, min(t+6, 24))` | `gap19_highs_native.py` ~L124–131 | VERIFIED |
| **The EBR window shrinks at the horizon edge:** `t ≤ 18` → 6 h (75,652 Wh); `t = 19` → 5 h (63,043); `t = 20` → 4 h (50,435); `t = 21` → 3 h (37,826); `t = 22` → 2 h (25,217); `t = 23` → 1 h (12,609) | Arithmetic from the code path | VERIFIED |
| Terminal target applies only at `t = 23`: `max(EBR[23], terminal)` | `gap19_highs_native.py` ~L151 | VERIFIED |
| Layer C: `E_next[t] + s_J2[t] ≥ target[t] + E_min`, with `s_J2` at priority 3, above fuel at priority 2 | `gap19_highs_native.py` ~L298–305, objective ~L365–385 | VERIFIED |
| Bus balance is an equality with `p_flex` as a sink; curtailment is endogenous | rows 1–3, 8 | VERIFIED |
| Non-critical unmet is not penalised (only `unmet_crit` is in J1) | objective vector `c1` | VERIFIED |

---

## 3. Candidate-by-Candidate Audit

### Candidate 1: Solar Headroom Preservation

**Verdict: `WRONG` as written.**

- **Infeasibility (VERIFIED).** The cap is `E_next[t] ≤ E_max − η·Σ min(P_sol, P_chg_max)·Δt`, with `E_max = 190 kWh`. On a sunny day the sum can exceed `190/0.92 ≈ 207 kWh`, which makes the cap negative. The variable's upper bound would then sit below its lower bound (40 kWh), and the MILP is infeasible. The design has no clamp. §4.1 shows this happens on 53 of 173 fixture origins.
- **It conflicts with the reserve priority (VERIFIED from code, INFERRED in effect).** On origins where the cap is below the reserve target (115.65 kWh), `s_J2` must be positive. J2 sits above fuel. The solver will therefore burn diesel to charge the battery up to the cap, because each Wh of charge reduces J2. That is the opposite of the intended effect, and it is the mechanism the design claims to remove.
- **The "reserve floor remains intact whenever feasible" claim is WRONG.** The cap is below the reserve target on 91 of 173 origins (§4.1).
- **Units are not stated.** `P_sol_exp` is undefined as either irradiance or power. The fixture stores irradiance, so the conversion `51 · I` with the 60 kW clip is required and missing.
- **`Δ_risk_solar[k]` is never defined.** It is a free parameter with no value and no source.
- **The "50–150 kWh recovered, 15–35 L saved" claim is UNSUPPORTED.** It has no computation behind it.
- **The equation applies the same cap to all `t < sunrise` through a full-day sum.** That ignores daytime discharge and the realization rule, so the bound is not tied to the hour where headroom is needed. INFERRED.

**Correction required:** Drop the cap from the core formulation. If a headroom mechanism is still of interest, define it as a separate experiment with an explicit clamp `X_t ≥ E_min + E_stage2[t]`, and test it alone. That experiment would then need to show it does not raise J2 and diesel.

### Candidate 2: Robust Net-Deficit EBR with Firm Night-Wind Floor

**Verdict: `CORRECTION_REQUIRED`. Closest to defensible, but the central claim fails.**

- **The night-wind clamp is inactive on the test origins (VERIFIED).** The clamp applies only when `solar_elevation ≤ 0`. The design names origin 66 (2024-07-05) as the night-wind failure test case. In the 2024 fixture, 2024-07-05 has solar elevation between 1.14° and 44.32° at every hour, so the clamp never triggers. Origin 56 (2024-06-25) has the same property (1.77° to 44.96°). At 68.36°N near the solstice, the sun does not set. The design's "guaranteed zero critical failures during nocturnal wind drops" is therefore not supported for the test origins it names.
- **It is not a genuinely new mechanism (INFERRED from the EBR synthesis).** The earlier solar-only critical-aware EBR (fuel −35.0%, critical reliability −0.29 pp, FAIL) and wind-including variant (−0.46 pp, FAIL) both subtract forecast renewables from the critical-energy reserve. Candidate 2 is the same family, with a day-only wind credit and a 25 kWh floor. The floor is the only new element. Its value is not computed anywhere in the design.
- **The 25,217 Wh floor arithmetic is correct (VERIFIED).** `2 h × 11,600 W / 0.92 = 25,217.4 Wh`. But the basis for "2 hours" is UNSUPPORTED. `diesel.yaml` has no start time. Its `min_up_time_hours: 2` is a run-length minimum, not a start delay, and GAP19 does not enforce it.
- **The "5 kW firm-wind" margin is UNSUPPORTED as a real margin.** The 0.7–5.0 kW wind errors come from the synthetic wind benchmark (`4500 + 5000·sin`), not from measured wind. The EBR synthesis says so explicitly. Using the synthetic error maximum as a physical margin fixes nothing for real wind.
- **Units are not stated.** `P_solar_hat` is used as electrical power, but the fixture forecast is irradiance (W/m²). The `51 · I` conversion with its 60 kW clip is missing.
- **The realization rule is ignored (INFERRED).** The executor curtails surplus when the plan discharges in the same hour (EBR synthesis, ~93–96% of curtailment). Solar credited to the reserve may therefore never reach the battery.
- **The "100% critical reliability" guarantee is `UNSUPPORTED`.** The reserve credit uses point forecasts, so no bounded-error argument exists. The only design that gives an unconditional bound is the unconditional EBR, which is the one that costs fuel.
- **Reserve is still soft and still above fuel (VERIFIED).** The floor enters as an `s_J2` target at priority 3. Nothing makes it a hard constraint.
- **The "−35% to −45% diesel" figure is `UNSUPPORTED`.** It has no computation behind it. Note that the closest prior variant produced −35.0% fuel with a reliability failure, so the number describes the mechanism's fuel effect, not a safe outcome.

**Exact correction:**
1. Replace the `solar_elevation > 0` rule with a fixed rule: `P_wind_firm = 0` at all hours. Remove the 5 kW margin, since it is unsupported. This is V2's Mode 1, and it has a clear safety argument: wind is never credited toward the reserve.
2. Specify the solar conversion (`P_pv = min(60000, 51·I)`) and state that it uses forecast irradiance.
3. Make the solar credit an explicit, pre-registered de-rating, or drop it. Without a calibrated margin, the design is the failed prior variant.
4. Replace "2 h floor" with a value justified by a diesel start-delay measurement, or flag the floor as a governance choice.
5. Test it as one mechanism (floor alone, or wind clamp alone), not as a bundle.

### Candidate 3: Elastic Reserve Slack with Fuel Co-Optimization

**Verdict: `WRONG` as the λ derivation and `UNSUPPORTED` as a ranking.**

- **The derivation of λ is WRONG (VERIFIED arithmetic).** The design states `λ = marginal fuel cost / risk multiplier ≈ 0.00035 L/Wh`. The marginal cost in `diesel.yaml` is 0.00025 L/Wh. Dividing it by a risk multiplier gives a value below 0.00025 for any multiplier above 1. The value 0.00035 would need a multiplier of 0.71. The formula and the number do not agree, and no multiplier is given.
- **Effect of λ (INFERRED).** At 0.35 mL per Wh of reserve shortfall, filling 1 kWh of reserve by diesel costs about 0.27 L. The penalty and the fuel cost are of comparable size, so the optimizer is roughly indifferent to the reserve. The protection value is effectively removed. The design's own failure mode acknowledges this.
- **Changes the GAP19 objective structure (VERIFIED from code).** Merging J2 and J3 modifies the objective vector and the HiGHS priority set. That is a code change, not a "HiGHS configuration" as the design says. The design's zero-code claim does not hold for this candidate.
- **The "40–55% diesel" and "Medium-Low safety" ratings are `UNSUPPORTED` scoring.** No scoring function is defined.

**Exact correction:** If retained, define λ as a sweep parameter with no claimed derivation, and report the full fuel–unmet frontier across the sweep. Do not claim a physical basis. It is a Pareto exploration, not a candidate controller.

### Candidate 4: State-Triggered Just-in-Time Diesel

**Verdict: `CORRECTION_REQUIRED`. Attribution is WRONG, and the formulation is not MILP-valid as written.**

- **The 68.4% attribution is WRONG (VERIFIED).** The design says step-0 diesel commitment was "responsible for 68.4% of total diesel consumption" (`EBR_ABLATION_REPORT`). The 68.4% is the fuel reduction from removing the *whole* EBR (6,603.98 → 2,084.78 L, `EBR_ABLATION_123_REPORT.md:25`). Step-0 elimination is a component of that. No figure isolates step-0 at 68.4%.
- **The formulation is internally inconsistent (VERIFIED).** The formula sums `k = t` to `t+1`, which is two hours. The text says "next 3 hours." One of them is wrong.
- **Not linear as written for `t ≥ 1` (INFERRED).** `u_diesel[t] ≤ 𝟙(E(t) ≤ E_trigger)` is a constraint on a decision variable `E(t)`. At `t = 0`, `E(0)` is a known constant, so the constraint is a simple bound. For `t ≥ 1` it needs a big-M indicator. The design does not give one, and it does not show that the big-M is valid for the actual `E` bounds.
- **Safety depends on an instantaneous-start assumption (VERIFIED from code).** The MILP starts diesel in the same step with no delay. The design's safety claim ("diesel starts at least 2 hours before the battery reaches E_min") is therefore a property of the model, not of the hardware. The "<5 minutes" start time in §3.4 has no source (UNSUPPORTED).
- **Step-0 removal may only shift commitment (INFERRED).** The reserve still forces diesel. The trigger removes it at `t = 0` only. Under receding-horizon replanning, the same commitment can appear at `t = 1`. The "−50 to −65%" figure is UNSUPPORTED for this reason.
- **Can run without a forecast-error model (VERIFIED as a design property).** It uses only state, which makes it the only candidate that does not need an uncertainty model. Its safety, however, still rests on the instantaneous-start assumption above.

**Exact correction:**
1. Replace the 68.4% attribution with the EBR-removal figure, labelled as total fuel.
2. Resolve the 2-hour vs 3-hour inconsistency.
3. For `t ≥ 1`, write the big-M linearisation explicitly, with bounds derived from the battery state limits.
4. Model a diesel start delay as a parameter (not in the current model) before claiming safety.

### Cross-cutting: Candidate Ranking

**`UNSUPPORTED`.** The scores (9.4, 8.6, 8.1, 7.5) and the ranges (35–45%, 15–25%, 50–65%, 40–55%) have no defined scoring function and no computation. The ranking is subjective. It should not be used to choose what to implement.

---

## 4. Verified Design Errors and Unsupported Claims

### 4.1 Read-only check on existing data

I applied the design's Candidate 1 cap to the 173 origins in the 2024 fixture, using forecast irradiance and the 50 kW charge limit (no controller run):

- Cap below 40,000 Wh (infeasible): **53 of 173** origins. The minimum cap is about −123 kWh.
- Cap below 115,652 Wh (below governed reserve): **91 of 173** origins.

This is a feasibility check on existing forecasts. It is not a dispatch result.

### 4.2 Other errors

| Claim in design | Finding | Label |
|---|---|---|
| "EBR holds 57.83% SOC at all timesteps" | Holds for `t ≤ 18` only. The window shrinks for `t = 19–23` (§2) | WRONG |
| "Max(75,652 Wh, E_term) = 100,000 at t = 23" | At `t = 23` the EBR term is 12,609 Wh, not 75,652 Wh. The terminal dominates, so the 100 kWh result is correct, but the stated reason is not | WRONG (reason) |
| "Terminal pruning saves a further 10–14% fuel" | Terminal removal (six origins) gives **−14.6% fuel but +6.3% unmet (+20.2 kWh)** (`TERMINAL_ABLATION_REPORT.md`). The reliability cost is omitted | PARTIAL, misleading |
| "Terminal target forces late-afternoon charging on sunny days" | Terminal ablation: a "partial contributor," not "the primary mechanism." The trace report's claim was corrected | WRONG (overstated) |
| "Diesel dispatches at 35–55 kW" | No source | UNSUPPORTED |
| "Early charging pushes SOC to 90–95%" | No source in the cited reports | UNSUPPORTED |
| "Diesel start < 5 minutes" | Not in any config. No start-time key exists | UNSUPPORTED |
| "2-hour diesel start/lockout buffer" | `min_up_time 2 h` is a run-length minimum, not a start delay, and is not enforced by GAP19 | WRONG (basis) |
| "5 kW firm-wind margin" | Derived from synthetic wind errors (EBR synthesis). Not a physical margin | UNSUPPORTED |
| "0.00035 L/Wh shadow price" | Inconsistent with its own formula (§3, Candidate 3) | WRONG |
| "2.0 L startup fuel" | Code default; `diesel.yaml` has no such key | VERIFIED as default, UNSUPPORTED as configured value |
| "Fuel curve: 0.75, 0.35, 0.30 L/kWh at 10, 50, 100 kW" | Arithmetic correct: `(5 + 0.00025·P)/P` | VERIFIED |
| "408 variables, 312 constraints, 96 binary" | Matches the code | VERIFIED |
| "Candidate 4 eliminates the step-0 commitment across all 123 origins" | From EBR ablation (step-0 zero in 123/123 with EBR off). True for EBR-off, not for the candidate | VERIFIED for EBR-off only |
| "Guarantees 100% critical reliability" | No uncertainty model; point forecasts only; the only unconditional bound is the EBR that costs fuel | UNSUPPORTED |
| "−25% fuel, −20% curtailment" as acceptance criteria | No basis given. The control arm's own critical reliability is not shown to be 100% | UNSUPPORTED |

### 4.3 Design-internal inconsistencies

- **Candidate 2 test origins.** The "night-wind" test origin (66) has no night hours in the 2024 fixture. See §3, Candidate 2.
- **Arm 1 label.** §7.2 calls Arm 1 "Candidate 2 Alone: zero night-wind floor." Candidate 2's floor is the zero-wind clamp. The wording is ambiguous and should be fixed.
- **Hybrid acceptance vs terminal evidence.** §7.3 requires `critical_unmet = 0.0` and reliability 1.0. The terminal ablation shows that removing the terminal raises unmet load by 6.3%. The hybrid includes terminal pruning, so the two requirements conflict unless the other mechanisms offset the loss. No such offset is shown.

---

## 5. Specific Questions

**Q1. Mathematical correctness against GAP19.** Partly. Layer C, the objective priorities and the diesel bounds match the code. The EBR horizon-edge behaviour is wrong in the design (§2). The `s_J2` term is a soft target, so no formulation in the design is a hard guarantee.

**Q2. Units and SOC accounting.** Mostly consistent in Wh and W, but irradiance/power is not separated in Candidates 1 and 2 (§3). The SOC percentages are correct: 25,217 + 40,000 = 65,217 Wh is 32.6%.

**Q3. Safety properties.** None of the claimed guarantees follows from the equations. Candidate 2's guarantee depends on the inactive clamp. Candidate 1's floor is violated by its own cap. Candidate 4's guarantee depends on instantaneous starts.

**Q4. Unsupported guarantees and percentages.** All of the 100% reliability claims and all of the percentage reductions (§4.2) are UNSUPPORTED. None has a computation in the design.

**Q5. Constants and margins.** Every constant in §4.2 is UNSUPPORTED or WRONG, apart from the battery and diesel parameters that trace to `battery.yaml` and `diesel.yaml`.

**Q6. Candidate 1 implementability.** Not as written. It can be infeasible (§4.1), and its interaction with J2 pushes diesel up.

**Q7. Candidate 2 vs prior critical-aware EBR.** Same mechanism family, with a new floor and a clamp that does not fire on the named origins (§3).

**Q8. Can Candidate 2 protect critical load under the observed errors?** Not shown. The 25 kWh floor might cover the observed six-origin failures, since the largest single-hour unmet was 4.7 kWh. No calculation in the design checks this, and the errors come from the synthetic benchmark.

**Q9. Candidate 4 MILP validity.** Only the `t = 0` case is valid as a bound. The `t ≥ 1` case needs a big-M, which is not given (§3, Candidate 4).

**Q10. Terminal target removal.** Independently justified as a *measured* effect (−14.6% fuel, +6.3% unmet). Not justified as a fuel-saving component of a hybrid. It should stay a separate experiment, with its reliability cost reported.

**Q11. Causal isolation of the hybrid.** The hybrid changes three mechanisms at once. Arms 1 and 2 isolate two of them. Terminal pruning has no isolated arm, even though the terminal ablation already exists. The hybrid arm alone does not identify which mechanism caused an effect.

**Q12. Is uncertainty information required?** For a bounded reliability claim, yes. The only unconditional bound in the record is the unconditional EBR, which the evidence says costs fuel. Candidate 4 needs no forecast model, but it needs a verified diesel start delay, which the repo does not have.

**Q13. Is the ranking evidence-based?** No (§3, cross-cutting).

**Q14. Are the proposed minimal experiments sufficient?** No. Three problems:
- **Same origins used for diagnosis and test.** The six test origins (56, 77, 66, 23, 8, 30) are the origins that produced the mechanisms in the trace and terminal reports. This is contamination. There is no held-out set.
- **Too small for significance.** Six origins cannot support the Wilcoxon and bootstrap tests the design's own criteria require. The 123-origin campaign was the one that could.
- **Controls with no signal.** Origins 8 and 30 are described as controls, but the terminal ablation shows origin 8 changing by −19.3 L and origin 30 unchanged. Neither is a clean control.

---

## 6. Which Candidate Is Worth Implementing First?

**None as written.** If one must be chosen for research: **Candidate 2 with the corrections in §3**, specifically the all-hours wind clamp (Mode 1) and no solar credit beyond a pre-registered de-rating. Test it on the **full 123-origin set**, against a control with no changes, using the same EBR and terminal as the baseline, and report the fuel–unmet trade-off rather than a pass/fail on 100% reliability.

The reason to prefer it over the others is that it changes one mechanism (reserve sizing), has a clear safety argument for the wind channel, and does not need a new model. Candidate 4 is the only option that avoids forecasts, but its safety depends on a diesel start delay the repo does not contain. Candidate 1 is infeasible as written.

---

## 7. Required Corrections (Exact)

1. **Remove** the "100% critical reliability," "guaranteed," and "zero critical failures" claims from every candidate.
2. **Remove** all percentage fuel and curtailment figures (35–45%, 15–25%, 50–65%, 40–55%, 10–14%, −25%, −20%) or replace them with computed values from a pre-registered experiment.
3. **Correct** the EBR horizon statement: the 6-hour reserve (75,652 Wh) applies only for `t ≤ 18`. The window shrinks to 12,609 Wh at `t = 23`.
4. **Correct** the terminal-target attribution: "a partial contributor," with the +6.3% unmet cost stated alongside the −14.6% fuel.
5. **Candidate 1:** drop the cap from the core formulation. Define `Δ_risk_solar`, or remove it. Add a feasibility clamp if a headroom test is retained as a separate experiment.
6. **Candidate 2:** replace the elevation-gated wind rule with `P_wind_firm = 0` at all hours. Remove the 5 kW margin. Specify `P_pv = min(60000, 51·I)`. Make the solar credit a pre-registered de-rating, or drop it. Justify the floor by a diesel start-delay measurement, or label it a governance choice.
7. **Candidate 3:** remove the λ derivation. Present λ as a sweep parameter. State that it changes the objective structure, and that it is a code change.
8. **Candidate 4:** correct the 68.4% attribution to total EBR-removal fuel. Resolve the 2-h vs 3-h conflict. Give the big-M form for `t ≥ 1`. Model a start delay before claiming safety.
9. **Ranking:** remove the numerical scores or define the scoring function with inputs. Otherwise drop the ranking.
10. **Protocol:** use a held-out origin set, separate from the six diagnosis origins. Use the full 123-origin set for any significance claim. Give each mechanism its own arm, and add an isolated terminal-pruning arm.
11. **Arm 1 label:** rename to "Candidate 2 (wind clamp, no solar credit)" or whatever is finally specified.
12. **Governance:** the design's "GAP19 UNCHANGED" claim is correct for the design files, but Candidate 3 requires an objective change. That must be flagged as a code change, not a configuration.

---

## 8. What I Did Not Verify

- Whether a production config overrides the EBR default (I checked the config files for `ebr_target_wh` and found none, so the default formula applies).
- The campaign's own origin dates and IDs for origins 77, 66, 23, 8 and 30. The fixture IDs do not map to the campaign IDs. I matched dates instead, and only 2024-06-25 and 2024-07-05 were confirmed in the fixture.
- Whether `startup_fuel_l` is set anywhere outside the code default.
- Git status of the design and production files. I did not run it.
- The stated SOC figures (90–95% pre-dawn) against the traces.
