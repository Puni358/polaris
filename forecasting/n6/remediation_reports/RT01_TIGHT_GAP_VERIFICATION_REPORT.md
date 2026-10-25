# POLARIS — RT-01 Tight-MIP-Gap Verification Report (Diagnostic Only)

**Date:** 2026-10-18
**Nature of this document:** Bounded, ONE-TIME, owner-authorized diagnostic ("POLARIS — RT-01 Tight-MIP-Gap Verification (Diagnostic Only)"), continuing directly from `RT01_FULL_HORIZON_MILP_DIAGNOSTIC_REPORT.md`. This pass executes exactly one additional step-0 MILP solve, with `mip_rel_gap` tightened to `0.0` applied purely in-memory, and independently re-verifies the previously-reported hour-20 dominance candidate against every relevant constraint and bound. **No source, test, config, register, or existing-report file was edited. No remedy is implemented. RT-01 remains OPEN.**

---

## 1. Exact command / scope executed

```
python3 research/rt01_diagnostics/trace_step0_tight_gap.py
```

New file written: `research/rt01_diagnostics/trace_step0_tight_gap.py`. It is a line-for-line structural copy of the already-authorized `research/rt01_diagnostics/trace_step0_full_horizon.py` (same `PolarisLocalRunner` construction, same hand-reproduced step-0 setup — `StationState`, `data_provider.get_runtime_state(0)`, `forecast_engine.predict(...)`, `router.evaluate_and_route(...)` for confirmation only — same scenario file `synthetic_168h_endurance_scenario.json`, same config). It does **not** call `run_pipeline()`, so `runner.artifacts_dir` is never opened.

**The only difference from the prior script:** the monkey-patched wrapper around the module-level `system.optimization.implementations.milp.milp` reference now forwards `options={"mip_rel_gap": 0.0}` to the real, unmodified `scipy.optimize.milp` on the single forwarded call. Direct inspection of `milp.py` line 297 (`res = milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)`) confirms the production call site passes **no** `options` kwarg today, so this injection is additive and purely in-process (this script's own Python process only); nothing on disk changed. The wrapper asserts `"options" not in kwargs` before injecting, as a hard guard against silently double-setting options if the call site ever changes. `runner.optimizer.optimize(...)` — and therefore the real solver — was called **exactly once**.

No 168-hour pipeline, test suite, campaign, tuning, or training was run.

Outputs created (all under `research/rt01_diagnostics/`):
- `trace_step0_tight_gap.py` (the script)
- `rt01_step0_tight_gap_trace.json` (full capture + constraint verification + comparison + classification)

`system/artifacts/*.json` was never opened by this script (no reference to `artifacts_dir` in it).

---

## 2. Pre/post hashes

Identical `HASH_TARGETS` list to the prior pass (`milp.py`, all six `PROTECTED_FILES`, `manifest.py`, every config YAML read by this diagnostic, and the scenario file).

**Result: `hash_diffs_detected: {}` — zero files changed.** Confirmed by the script's own pre/post SHA-256 manifest (see `rt01_step0_tight_gap_trace.json`).

---

## 3. Single-solve results

| | Baseline (default `mip_rel_gap`, scipy default = 1e-4) | Tightened (`mip_rel_gap=0.0`, in-memory only) |
|---|---|---|
| `res.success` | True | True |
| `res.status` | 0 | 0 |
| `res.message` | "Optimization terminated successfully. (HiGHS Status 7: Optimal)" | identical |
| `res.fun` (objective) | 14,296.383045507702 | 14,296.383045507595 |
| objective delta | — | **−1.07e-10** (floating-point noise only) |
| `res.mip_gap` reported | not captured in baseline script | **0.0** (HiGHS proved a 0.0 relative gap) |
| Hour-20 `p_curt_wind` | 1,182.6627 W | 1,182.6627 W (identical to 4 dp) |
| Hour-20 `p_dis` | 2,254.3527 W | 2,254.3527 W (identical to 4 dp) |
| Hours with simultaneous curtail+discharge | 0, 1, 5, 8, 13, 15, 20 | **0, 1, 5, 8, 13, 15, 20 (identical set)** |

**The tightened-gap re-solve returns a bit-for-bit identical solution to the baseline**, and HiGHS's own reported `mip_gap` attribute at termination is exactly `0.0` — i.e., HiGHS did not merely stop early inside a 1e-4 tolerance window; it proved global optimality of this MILP (to numerical precision) and returned the same answer anyway. **This directly rules out "the pattern is a loose-solver-tolerance artifact."** It is not a gap-tolerance effect.

---

## 4. Constraint-by-constraint verification of the hour-20 "dominance" candidate

The prior report's hour-20 claim: curtailing 1,182.66 Wh of wind while discharging 2,254.35 Wh of battery is dominated by a swap — use the 1,182.66 Wh of wind directly instead, reduce discharge by the same amount — which it characterized as bus-bar-neutral, strictly cheaper by $59.19, and leaving "MORE battery energy for every future hour (strictly better for every future hour, not worse)," with "no downside of any kind."

This pass independently re-checked that swap against **every row of the real `LinearConstraint` matrix (266 rows) and every one of the 360 variable bounds**, as actually captured from the tightened-gap solver call (not reconstructed from scratch), plus integrality:

1. **Solar/wind decomposition, bus-bar balance, demand-deficit balance:** the swap (wind_used += 1,182.6627 Wh, curt_wind -= 1,182.6627 Wh, p_dis -= 1,182.6627 Wh) is confirmed bus-bar-neutral and decomposition-neutral at hour 20 itself — these rows hold.
2. **Charge/discharge exclusivity, binary linking (rows 5–7), integrality:** `u_dis`, `u_chg` and all other binaries are untouched by the swap (`integrality_violations: []`) — confirmed no exclusivity or linking row is affected.
3. **Battery Energy Discrete Transition (row 227, the unique row touching `E[21]` and `p_dis[20]`):** reducing `p_dis[20]` by 1,182.6627 Wh, with `E[20]` and `p_chg[20]` held fixed, forces `E[21]` (and, by the identical structural argument applied to every subsequent transition row, **every** `E[t]` for t = 21, 22, 23) to shift upward by exactly `delta × dt/eta_dis = 1,182.6627 × (1/0.92) = 1,285.5029 Wh`. This is the formal version of the prior report's "leaves more battery energy for every future hour" claim — confirmed exactly, using the real transition-row coefficients (`coeff_E_next = 1.0`, `coeff_p_dis = 1.0869565217391304 = 1/0.92`).
4. **Variable bounds — this is where the swap fails:** `E[23]`'s upper bound is `190,000.0 Wh` (= `max_soc_pct 95.0% × capacity_wh 200,000 Wh`, confirmed directly from the real `Bounds` object, `ub[351] = 190000.0`). The baseline solution's actual `E[23]` is **exactly `190,000.0000 Wh`** — i.e., hour 23 is already pinned precisely at the SOC ceiling, with **zero headroom**. Applying the required `+1,285.5029 Wh` cascade pushes `E[23]` to `191,285.5029 Wh`, exceeding its upper bound by `1,285.5029 Wh`.
   - `hour20_constraint_by_constraint_verification.bound_violations` (from `rt01_step0_tight_gap_trace.json`): `{"var_index": 351, "t": 23, "k": 6, "value": 191285.5029, "lb": 40000.0, "ub": 190000.0}`.
   - `feasible: false`.

**Conclusion of this check: the hour-20 swap, exactly as described in the prior report (a purely local change at hour 20 with no further recourse), is not actually feasible.** It is not bus-bar-neutral *and* capacity-feasible simultaneously — it is bus-bar-neutral only if you ignore that the battery has zero spare capacity at hour 23. Feasibility tolerance used throughout this check: `1e-6` on both constraint rows and variable bounds (well above HiGHS's own working precision); the hour-23 violation of `1,285.50 Wh` is six orders of magnitude larger than this tolerance, so it is not a numerical artifact.

### Does a corrected, fully-feasible version of the swap still save money?

No. To actually realize the swap without violating the hour-23 ceiling, the minimum-size recourse is to shed exactly the same `1,285.5029 Wh` of cascading energy at hour 23 by reducing `p_chg[23]` by `1,285.5029 / eta_chg = 1,285.5029 / 0.92 = 1,397.2858 Wh` (hour 23's own transition-row coefficients). Hour 23's bus-bar balance then forces an **equal 1,397.2858 Wh increase in curtailment** at hour 23 (confirmed directly from the real solution: hour 23 already charges its *entire* 3,049.63 Wh of surplus with zero curtailment — `raw_p_curt_wind[23] = raw_p_curt_sol[23] = 0.0` — so there is no other sink for the reduced charge but curtailment).

Using the model's own cost coefficients, confirmed `gamma = 1.0` (no `custom_weight_vector` or `v4g_single_horizon_mode` configured for this scenario, so `w_t = gamma**t = 1.0` for every `t`, including `t=20` and `t=23`):

| | Wh | $/Wh | $ |
|---|---|---|---|
| Claimed saving at hour 20 (curtailment avoided + discharge-cycling avoided) | 1,182.6627 | 0.05 + 0.00005 | **+$59.1923** |
| Required recourse: forced extra curtailment at hour 23 | 1,397.2858 | 0.05 | **−$69.8643** |
| **Net effect of the fully constraint-respecting swap** | | | **−$10.67 (WORSE)** |

**A swap that is bus-bar-neutral and capacity-feasible across the whole horizon is net $10.67 more expensive than the solution HiGHS returned, not cheaper.** The apparent $59.19 "free" improvement reported previously existed only because the prior analysis checked bus-bar neutrality and the direction of the SOC trend ("more is better") but did not check the SOC *ceiling* bound at the specific future hour (23) where it is already saturated.

---

## 5. Classification

**INCONCLUSIVE** — but for a precise, non-vague reason, not "insufficient evidence":

- The gap-tightening test itself is unambiguous: tightening `mip_rel_gap` to `0.0` (and confirming HiGHS's own reported `mip_gap` is exactly `0.0` at termination — a *proved* global optimum, not merely a tolerance-satisfied stop) produces a **bit-identical** solution. This rules out "H2 is a loose-solver-tolerance artifact" cleanly: **it is not.**
- However, the directive's step 3 (independent constraint-by-constraint re-verification of the hour-20 candidate) found that the candidate itself — the thing the gap test was supposed to be testing the persistence *of* — **does not survive verification**. The claimed swap is infeasible as stated (violates the hour-23 SOC ceiling bound by 1,285.50 Wh), and the minimum-cost constraint-respecting correction of that infeasibility costs more ($69.86) than the claimed saving ($59.19), making the fully-corrected "improvement" a net $10.67 **loss**, not a gain.
- Neither "Violation persists" (which requires the dominated solution to be genuinely feasible and dominated — it is not, once hour 23's ceiling is accounted for) nor "Violation disappears" (which requires the *solver's returned pattern* to change under the tighter gap — it did not; the pattern is bit-identical) cleanly applies. The honest classification is **Inconclusive on the original persists/disappears question, with a decisive finding that the underlying hour-20 dominance claim itself does not hold under full-horizon constraint accounting.**

**Practical implication:** this materially weakens the H2 ("formulation/solver defect producing a provably dominated solution") conclusion of `RT01_FULL_HORIZON_MILP_DIAGNOSTIC_REPORT.md` Section 6. HiGHS's "OPTIMAL" solution at hour 20 may in fact be the true global optimum of the stated MILP — the counterexample offered against it does not hold up once the battery's hour-23 SOC ceiling (already saturated) is correctly treated as binding. This does **not** reopen or re-validate H1 or H3, and it does not address the magnitude evidence in that report's Section 5 (the $7,396.97 excess across seven simultaneous-curtail-and-discharge hours) — that evidence was computed from local, single-hour "use renewable directly" comparisons, not from the same kind of full-horizon-feasible swap tested here, and was not re-verified by this pass. **Whether the other six occurrences (hours 0, 1, 5, 8, 13, 15) of the same raw pattern are similarly infeasible-as-naively-swapped, and whether any of them have genuine feasible dominating alternatives, is unresolved and was explicitly out of scope for this single-hour, single-solve diagnostic.**

---

## 6. Remaining uncertainty

- This pass verified **only** the hour-20 candidate exactly as stated in the prior report. It did not re-verify the hour-0/1/5/8/13/15 instances of the same raw pattern, nor the H1 multi-period-shifting magnitude argument (Section 5 of the prior report) — those arguments may or may not have the same "ignored a binding future bound" flaw found here; this was not checked and should not be assumed either way.
- The recourse-cost calculation in Section 4 above used the *cheapest available* single-hour recourse (reduce hour-23 charging, forcing equal hour-23 curtailment) given the real numbers in the actual solution; it is a rigorous lower bound on the cost of any feasible realization of the hour-20 swap, not a claim that a global re-optimization could not find some entirely different, cheaper reallocation elsewhere in the horizon. No re-solve was run to check that; doing so would be a genuine counterfactual/alternative solve, out of this pass's authorized scope (exactly one additional solver call).
- Whether HiGHS's returned solution is the *actual* global optimum (as opposed to merely "not dominated by this particular counterexample") was not separately proven here — `mip_gap=0.0` is HiGHS's own self-reported certificate of optimality for the MILP as stated, which this pass accepts at face value; it was not independently re-derived from the LP relaxation/branch-and-bound tree.
- No remedy is implemented or recommended by this pass. RT-01 remains **OPEN**, now with this specific hour-20 counterexample's validity in question rather than confirmed.

---

## 7. Confirmation of protected files and governance state

- All six `PROTECTED_FILES` entries, `manifest.py`, `milp.py`, every config YAML read by this diagnostic, and the scenario file are **byte-identical before and after this run** (Section 2; `hash_diffs_detected: {}`).
- No parameter, threshold, routing/ECD behavior, fuel policy, `winner` status, the 75% renewable-utilization floor, or campaign guard was touched or exercised beyond the same single observational `router.evaluate_and_route` call pattern already authorized in the prior trace.
- No training, tuning, campaign, or sealed/blind-2025 data was accessed.
- Nothing was staged, committed, or pushed by this pass.
- Exactly one additional optimizer solve was executed (`mip_rel_gap=0.0` injected purely in-memory on the forwarded `scipy.optimize.milp` call); no counterfactual/alternative solve beyond it.
- The only filesystem changes made by this pass: `research/rt01_diagnostics/trace_step0_tight_gap.py`, `research/rt01_diagnostics/rt01_step0_tight_gap_trace.json`, this report, and its mirror in `N6_REMEDIATION_REPORTS/`. `system/artifacts/*.json` production artifacts were never opened.
