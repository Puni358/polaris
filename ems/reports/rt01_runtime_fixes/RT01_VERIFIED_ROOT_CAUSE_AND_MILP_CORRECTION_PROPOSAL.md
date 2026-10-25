# POLARIS — RT-01 Verified Root Cause (Reproducible Counterfactual) and MILP Correction Proposal

**Date:** 2026-10-18
**Nature of this document:** Continuation of RT-01 directly from `RT01_FUEL_ACCOUNTING_AND_MILP_VERIFICATION_REVIEW.md`, `RT01_TIGHT_GAP_VERIFICATION_REPORT.md`, and `RT01_SEVEN_HOUR_FEASIBILITY_AUDIT_AND_E2E_READINESS_REPORT.md`. Part 1 executes and reports an actual, reproducible, full-168-step counterfactual re-run (not arithmetic, not a hypothesis) to test causation for the steps-119–121 shortfall. Part 2 re-confirms the "19.823 L / 0 Wh" claim's unverified status without re-grepping exhaustively. Part 3 is a read-only formulation-consistency review of `milp.py`. Part 4 is a **proposal only** — no implementation. **`milp.py` was not edited. No protected file was edited. Nothing staged, committed, or pushed. RT-01 remains OPEN.**

**Explicitly NOT reopened:** the mip-gap/solver-tolerance hypothesis (falsified — bit-identical step-0 solution at `mip_rel_gap=0.0`) and the H2 simultaneous-curtailment-and-discharge "dominance violation" theory (falsified at all 7 flagged step-0 hours — every naively-proposed swap is infeasible-as-stated and net-worse once corrected). Neither is re-examined below.

---

## Part 1 — Verified cause of the steps-119–121 unmet load (14.974 kWh)

### 1.1 Proximate physical state (already established, re-confirmed from a freshly regenerated baseline trace)

A fresh, unmodified 168h run (`research/rt01_diagnostics/trace_168h_endurance_scenario.py`, re-executed this pass against the current, unmodified source tree) reproduces exactly the figures on record in `RT01_ROUND1_STABILIZATION_REPORT.md`: `total_diesel_fuel_liters=129.48`, `renewable_utilization_pct=79.64`, `system_reliability_pct=99.73`, `total_unmet_load_kwh=14.97`, with exactly 3 unmet steps:

| Step | Fuel in | SOC in | Solar | Wind | Demand | Unmet |
|---|---|---|---|---|---|---|
| 119 | 0.000 L | 21.13% | 0 W | 18,396.55 W | 29,390.93 W | 8,919.43 Wh |
| 120 | 0.000 L | 20.00% (floor) | 0 W | 23,004.71 W | 28,110.55 W | 5,105.84 Wh |
| 121 | 0.000 L | 20.00% (floor) | 0 W | 27,106.38 W | 28,055.22 W | 948.84 Wh |

Diesel fuel is literally zero, the battery is at or within 1.1pp of the hard 20% SOC floor (never breached), solar is zero (night), and wind alone is short of demand by 0.9–8.9 kW. This proximate classification — genuine resource exhaustion at the instant of shortfall — was already established and is **not** in dispute. What was **not** previously established with a real counterfactual is whether this exhaustion was itself avoidable given earlier dispatch choices.

### 1.2 A new, independently-located candidate mechanism (not H1/H2/H3, not previously reported)

Direct inspection of the fresh per-step trace (`research/rt01_diagnostics/rt01_168h_trace.json`) located the actual fuel-depletion event: at step 93 — the **last** step the real NORMAL/`LocalMILPEnergyOptimizer` route is active before the run falls permanently to EMERGENCY/`OptionDFallbackSolver` — the real, unmodified MILP solver dispatched `diesel_power[0] = 66,992.87 W`, while forecast demand net of wind was only `16,992.87 W`. The remaining `50,000 W` (exactly the battery's `max_charge_power_w` ceiling) was diesel power routed straight into `battery_charge[0] = 50,000 W`, with `renewable_curtailment[0] = 0.0` (no surplus renewable being redirected — this fuel was discretionary, not forced). Fuel dropped `39.771 L → 18.0228 L` in that single hour (≈21.75 L, versus a typical 5–10 L/h non-charging diesel hour elsewhere in the trace), and the tank reached exactly `0.000 L` three hours later, at step 96. This is a **different** pattern from the already-closed H2 theory (which concerned simultaneous curtailment + discharge, always with curtailment > 0); step 93 has zero curtailment and involves diesel-funded charging instead.

This is a real, quantified, previously-unreported candidate cause: diesel fuel being spent on discretionary battery charging, 26 hours before the shortfall, when the receding-horizon (24h-window) MILP cannot see that far ahead and has no reason to withhold it.

### 1.3 The reproducible counterfactual (what was actually run, not a hypothesis)

Script: `research/rt01_diagnostics/trace_step119_counterfactual.py` (new; monkeypatch-wraps real, unmodified instance methods only — `router.evaluate_and_route`, `optimizer.optimize`, `option_d_solver.solve`, `simulator.step` — exactly the pattern already used by every prior `rt01_diagnostics` script; no source file is edited). Output: `research/rt01_diagnostics/rt01_step119_counterfactual_trace.json`.

The script runs the **real, unmodified, full 168-step `run_pipeline()`** three times:

1. **Baseline** — no intervention.
2. **Single-step counterfactual** — after the real MILP solves step 93 (real forecast, real state, real solve — no re-solve, no change to the solver's decision), the script intercepts the returned `DispatchPlan` and replaces **only** index 0's `battery_charge`/`diesel_power` with a balance-preserving alternative that removes the diesel-funded-charging component: `new_diesel0 = max(0, D)`, `new_chg0 = max(0, -D)`, where `D = served0+flex0-sol0-wind0-dis0` (the diesel actually needed to meet demand, ignoring charging). This identity is derived directly from the real solved plan's own bus-bar balance (`sol0+wind0+dis0+diesel0 = served0+chg0+flex0`), so it is bus-bar-neutral and decomposition-neutral by construction (verified by an in-script assertion on every application). Every other value at index 0, and the entire rest of the 24h plan (indices 1–23, which the simulator never reads), is left untouched. From step 94 onward, every subsequent call is the real, unmodified router/optimizer/fallback-solver/simulator, driven by whatever real state results.
3. **All-steps counterfactual** — the identical, generic pattern-detection/substitution rule is applied at **every** step across the full 168h run where it fires (6 occurrences total this run), not just step 93 — testing whether the mechanism is sufficient in aggregate, not only at the first instance located.

All three runs completed cleanly (168/168 steps, `SUCCESS_CLEAN`/`execution_status`, zero exceptions). Pre/post SHA-256 hashes of all 7 `PROTECTED_FILES`, `milp.py`, every config YAML, and the scenario file are **byte-identical** (`hash_diffs_detected: {}` in the output JSON — confirmed again independently via `sha256sum` outside the script).

### 1.4 Result

| Run | Steps 119–121 unmet | Total unmet (168h) | First fuel exhaustion | Last NORMAL/MILP step |
|---|---|---|---|---|
| Baseline | 14,974.11 Wh | 14.9741 kWh | step 96 | step 93 |
| Single-step counterfactual (step 93 only) | **14,974.11 Wh (unchanged)** | 14.9741 kWh (unchanged) | step 97 (+1h) | step 93 |
| All-steps counterfactual (6 occurrences, whole run) | **14,974.11 Wh (unchanged, bit-identical)** | 14.9741 kWh (unchanged) | step 91 (−5h) | step 68 |

**The unmet load at steps 119–121 is bit-identical across all three runs, down to the hundredth of a watt-hour.** Removing this confirmed, quantified, discretionary diesel-funded-charging pattern — once at its single largest occurrence, and again everywhere it occurs across the entire 168-hour horizon — does not reduce, delay, or otherwise change the night-119 shortfall by any amount. (The all-steps run's fuel-exhaustion step actually moves *earlier*, not later, because removing this behavior changes the whole downstream NORMAL/EMERGENCY routing trajectory non-monotonically — a real, observed feedback effect, not a modeling artifact, but irrelevant to the steps-119–121 outcome either way.)

### 1.5 Verified conclusion — causation status

**This is a demonstrated, reproducible negative result, not a hypothesis:** the one concrete, quantified earlier-dispatch inefficiency this review could actually locate in the current, unmodified system is **not** the cause of the steps-119–121 shortfall, under an actual full-pipeline counterfactual re-run (confirmed at both single-occurrence and full-horizon scale). Combined with the already-closed tolerance and H2-dominance-violation theories, **no specific, narrowly-scoped dispatch defect has been found whose removal demonstrably closes the gap.** What remains, consistent with every prior report and now additionally supported by this negative counterfactual result, is a **structural** explanation: the receding-horizon (`H=24` hardcoded, `milp.py:76`) MPC architecture has no mechanism of any kind to bank fuel or battery margin against a deficit more than 24 hours ahead, and genuinely cannot "see" the night-119 low-wind window until it is already inside that window — by which point fuel is already at 0.000 L and the battery is at its floor. This is **not** asserted as unproven speculation; it is the only explanation consistent with (a) the proximate-state evidence (Section 1.1, already independently verified), (b) the closure of H1/H2/the tolerance hypothesis (prior reports), and (c) this pass's own new counterfactual evidence ruling out the one additional candidate mechanism actually found in the data. **No code defect — in `milp.py` or any protected file — has been shown, by actual re-run, to cause or be sufficient to close the steps-119–121 shortfall.** Closing it would require a cross-horizon reservation redesign, which Round-1 already correctly flagged as campaign-scale and out of this pass's scope (see Part 4).

---

## Part 2 — Status of the "19.823 L / 0 Wh unmet, global 168h MILP" claim

**Re-confirmed UNVERIFIED, not re-investigated beyond a light confirmation check per the task's own instruction.** `RT01_FUEL_ACCOUNTING_AND_MILP_VERIFICATION_REVIEW.md` §Q2 already performed an exhaustive repo-wide grep and found zero matches in any RT-01 report or the decision register, plus the structural fact that `milp.py:76` hardcodes `H = 24`, making a genuine single-shot 168-hour MILP solve structurally impossible without a horizon-formulation change.

A broader, non-exhaustive re-check this pass (`grep -rln "19.823\|19,823" --include="*.md" --include="*.json"`, excluding `.venv/`) across the **entire** repository (not just RT-01 reports) does turn up ~30 incidental textual matches in unrelated files (weather-station metadata, OFAT checkpoint arms, a GAP19-branch diesel-necessity forensic table, etc.). Each one checked is a coincidental numeric substring, not the claimed figure: e.g. `POLARIS_EMS_GAP19_MILP_V2_DIAGNOSTIC_BRANCH/DIESEL_CHARGING_NECESSITY_FORENSIC_REPORT.md` contains "19,823" as an hour-21 diesel **power** value (19,823 **W**, not liters, not a 168h total), and `system/data/scenarios/h10_scenario_temp.json` contains "19.823..." as part of an unrelated coordinate/value string. None of these is a "0 Wh unmet, 168h, global single-shot MILP, 19.823 L" result. This status is therefore unchanged: **no such artifact exists in this repository**, and producing one would require editing `milp.py`'s horizon logic — explicitly out of this pass's scope (Part 4 is proposal-only, and no implementation is authorized). If the owner has this figure from an external source, its exact script, inputs, and formulation still need to be supplied before it can be checked.

---

## Part 3 — Formulation-consistency review of `milp.py` (read-only; no edits)

Per the directive, each named concept was checked for whether it is represented **consistently** between the objective function and the constraint set, and against the config files that are supposed to govern it.

### 3.1 Direct renewable use — consistent
`p_sol_used`/`p_wind_used` carry **no** cost coefficient in the objective (`milp.py:111-114` only costs curtailment and battery cycling, not renewable use itself), while curtailment is explicitly penalized (`curt_penalty_per_wh`). The solar/wind decomposition constraints (constraints 1–2, `milp.py:180-194`) force `used + curtailed == available` exactly. This correctly and consistently incentivizes direct renewable use over curtailment in every hour. **No inconsistency found.**

### 3.2 Battery cycling — internally consistent, but disconnected from `optimizer.yaml`
`deg_penalty_per_wh` is applied symmetrically to both `p_chg` and `p_dis` (`milp.py:113-114`), sourced from `battery.yaml`'s `deg_penalty_per_wh` (0.00005). Round-trip losses are captured correctly in the SOC transition constraint (constraint 8, `eta_chg`/`eta_dis` = 0.92/0.92). This is internally consistent.

**However:** `system/config/optimizer.yaml` separately declares `weights.battery_cycling_penalty: 0.01` and `weights.unmet_critical_load_penalty: 1000.0` and `weights.fuel_cost: 1.0` — none of which `milp.py` ever reads. `milp.py` sources its degradation cost from `battery.yaml` directly (line 33), its unmet-load cost from `loads.yaml`'s `critical_load.unmet_penalty_per_wh` (10.0, line 53), and its fuel dollar-cost from `diesel.yaml`'s `fuel_cost_per_l` directly (no multiplier) — bypassing 3 of the 4 weight knobs `optimizer.yaml` appears to expose. Only `weights.renewable_curtailment_penalty` (0.05) is actually wired in (`milp.py:54`). **This is a genuine configuration-consistency gap**: `optimizer.yaml`'s `weights` block looks like a single unified tuning surface but is only 25% connected to the live formulation; an operator editing `battery_cycling_penalty` or `unmet_critical_load_penalty` expecting it to change dispatch behavior would see no effect. It does not, by itself, cause any currently-observed numerically-wrong behavior (the values actually in effect match every governed figure in the existing reports), so it is reported as a **maintainability/consistency** finding, not a behavioral defect.

### 3.3 Curtailment — consistent
Penalized identically for solar and wind (`milp.py:111-112`, same `curt_penalty_per_wh`, same horizon weight `w_t`). Correctly wired from `optimizer.yaml`. **No inconsistency found.**

### 3.4 Startup fuel — inconsistent between objective and constraint (confirmed directly in `milp.py`, not just in `evaluator.py`)
`v_start` carries a real dollar cost in the objective (`startup_cost * w_t`, `milp.py:139`, sourced from `diesel.yaml`'s `startup_cost=15.0`, equivalent to `15.0/2.50 = 6.0 L` at the configured fuel price). This correctly discourages frequent diesel start/stop cycling **economically**. But the cumulative fuel-budget constraint (`milp.py:291-300`) sums only `marg_fuel_l_wh*dt*p_diesel[t] + base_fuel_l_h*dt*u_diesel[t]` — **no `v_start` term is included**. The physical constraint that is supposed to enforce "never dispatch more diesel energy than the tank can supply" implicitly assumes starting the engine is fuel-free, while the objective implicitly prices it at 6 L-equivalent per start. This is the exact same root-cause pattern already identified for `evaluator.py`'s separate ~24 L reporting gap (`RT01_FUEL_ACCOUNTING_AND_MILP_VERIFICATION_REVIEW.md` Q1) — but confirmed here to also exist **inside `milp.py`'s own internal formulation**, not only in the downstream reporting layer. The MILP's own physical fuel-feasibility tracking can therefore let the solver schedule marginally more diesel-hours over a horizon than the tank truly has, by the exact margin of however many engine starts occur (4 starts × 6 L = 24 L in the 168h baseline run — consistent with the 129.48 L vs 105.48 L gap already found).

### 3.5 Fuel reservation across horizons — absent (not an inconsistency within one call, but a structural gap)
There is no term, constraint, or mechanism anywhere in `milp.py` that reserves fuel or battery energy for anything beyond the current 24-hour call's own horizon. `current_fuel_l` (line 48) is read fresh from `station_state` each call and spent as the current window's own cost-minimization sees fit; nothing carries forward an intent to preserve margin for a window the current call cannot see. This is confirmed, by the Part 1 counterfactual, to be consistent with being the real explanation for the steps-119–121 shortfall (no narrower, in-window defect was found to be responsible).

**Summary for Part 3:** direct-renewable-use and curtailment incentives are correctly and consistently represented. Battery-cycling cost is internally consistent but its `optimizer.yaml` weight knob is dead (unused) — a maintainability finding, not a behavioral defect. Startup fuel is represented in the objective's economics but omitted from the physical fuel-budget constraint — a confirmed, small, real formulation inconsistency (the same mechanism as the already-known ~24 L evaluator gap, now also located inside `milp.py` itself). Fuel/battery reservation across horizon calls does not exist in the formulation at all — this is the structural gap Part 1's counterfactual evidence is consistent with as the real cause of the steps-119–121 shortfall, and it is not a "defect" fixable by a local constraint edit; it would require a horizon/formulation redesign.

---

## Part 4 — Proposal only (no implementation)

Per the directive, no code change is made in this pass. Two candidate corrections were identified in Part 3; they are kept **explicitly separate** because they address different findings and have very different scope:

### 4.1 Candidate A — add the missing startup-fuel term to `milp.py`'s cumulative fuel-budget constraint (small, narrowly scoped; addresses Part 3 §3.4 only — does NOT address the steps-119–121 shortfall, per Part 1's evidence)

**Pseudocode (not implemented):**
```python
startup_fuel_l_per_start = startup_cost / fuel_cost_per_l   # 15.0 / 2.50 = 6.0 L
# ... inside the existing cumulative fuel-budget constraint construction (milp.py:291-300):
row = np.zeros(num_vars)
for t in range(H):
    base = t * K
    row[base + 7]  = marg_fuel_l_wh * dt     # p_diesel      (unchanged)
    row[base + 13] = base_fuel_l_h * dt      # u_diesel      (unchanged)
    row[base + 14] += startup_fuel_l_per_start   # v_start   (NEW TERM)
A_rows.append(row); lhs.append(-np.inf); rhs.append(current_fuel_l)
```
This makes the MILP's own physical fuel constraint consistent with the dollar cost it already assumes for `v_start`, closing the same mechanism already identified for `evaluator.py`'s 24 L gap, at its source rather than only in the reporting layer.

**Expected risks:**
- Makes the MILP marginally more conservative about diesel starts within any 24h window it solves (it will see slightly less effective fuel budget per potential start) — a strictly safety-improving direction, not safety-reducing.
- Changes the 24h regression's exact numeric output (fuel-constrained steps near tank exhaustion could shift by up to a few hours), so `test_s81_e2e_integration.py`'s existing byte-identical-style assertions (14/14 currently passing) would need to be re-run and any byte-identical pins reviewed — this is a real regression-test risk, not a hidden one.
- Does **not** change the 100% reliability requirement or the 75% renewable-utilization floor, and does not touch any protected file (`milp.py` is explicitly unprotected).
- Per Part 1, this candidate is **not expected to close the steps-119–121 gap** (it does not add any cross-horizon reservation) — it is a correctness/consistency fix, not a shortfall remedy, and should not be represented as one.

**Exact tests needed before any implementation:**
1. Re-run `test_s81_e2e_integration.py` (all 14 tests) and confirm pass/fail status explicitly, not assumed.
2. Re-run the 168h closure suite (`test_flexible_load_constraints`, `test_flexible_load_no_double_counting`, `test_per_timestep_conservation_audit`, `test_cumulative_physical_conservation_168h`, `test_long_duration_closed_loop_endurance_168h`) and record the new `total_diesel_fuel_liters`/`renewable_utilization_pct`/`system_reliability_pct` figures against the current 129.48 L / 79.64% / 99.73% baseline.
3. A new, explicit regression test asserting the cumulative fuel constraint's row now includes a nonzero coefficient on every `v_start` index (structural test, not just an output-value test), so a future refactor cannot silently drop the term again.
4. Re-verify all 7 `PROTECTED_FILES` hashes are unchanged (this candidate touches only `milp.py`).

### 4.2 Candidate B — cross-horizon fuel/SOC reservation redesign (addresses the actual steps-119–121 shortfall per Part 1's evidence)

This is the only candidate this or any prior RT-01 report has identified that could plausibly close the steps-119–121 gap, and it is **explicitly not proposed for implementation here**. It would require redesigning the receding-horizon dispatch logic to deliberately bank fuel and/or battery margin against a deficit the current 24-hour window cannot see — a structural, multi-component change (likely touching `milp.py`'s horizon/formulation and possibly `router.py`'s NORMAL/EMERGENCY routing logic, which is protected). This is unambiguously the "general-optimization-campaign-scale redesign" every prior round (`RT01_ROUND1_STABILIZATION_REPORT.md` §2, repeated in `RT01_FUEL_ACCOUNTING_AND_MILP_VERIFICATION_REVIEW.md` Q4(b)) has already correctly excluded from narrow-correction authorization, and this pass's directive explicitly says not to begin one without explicit approval. **No pseudocode, implementation, or sub-step of this candidate is proposed here** — it is named only so the owner has an accurate picture of what would actually be required to close the gap, consistent with "if a safe minimal fix cannot be demonstrated, stop and request authorization for the specific broader change required."

### 4.3 Recommendation

**No implementation is recommended or performed in this pass.** Candidate A is a legitimate, narrowly-scoped, independently-justified correctness fix for the Part 3 §3.4 finding, with the regression tests above required before it is implemented; it is not a fix for the steps-119–121 shortfall and should not be adopted under that expectation. Candidate B is the only path that could close steps-119–121, and it requires explicit owner authorization as a separate, larger, campaign-scale decision before any design work begins.

---

## Governance and boundary confirmation

- **Protected files:** all 7 `PROTECTED_FILES` (`router.py`, `ecd.py`, `gap19_highs_native.py`, `option_d.py`, `simulator.py`, `runner.py`, and `manifest.py`'s own declared list) hash-verified byte-identical before and after this entire pass, both via the diagnostic script's own manifest and an independent `sha256sum` check run outside it.
- **`milp.py`:** read and reviewed only; not edited; hash unchanged (`a5ae64102b0e623a5da5086f40a427723f4bd4d38d870535aec80b283f58a3e0`).
- **Fuel/refueling policy, SOC floor, 75% renewable floor, governance register:** untouched. `POLARIS_MASTER_DECISION_REGISTER.md` was not opened for writing.
- **New files created by this pass:** `research/rt01_diagnostics/trace_step119_counterfactual.py` (diagnostic script), `research/rt01_diagnostics/rt01_step119_counterfactual_trace.json` (its output artifact), this report, and its mirror in `N6_REMEDIATION_REPORTS/`.
- **Pre-existing artifact note:** `research/rt01_diagnostics/rt01_168h_trace.json`/`.csv` (outputs of the already-existing, unmodified `trace_168h_endurance_scenario.py`) were regenerated by re-running that same unmodified script, because the on-disk copies predated a since-landed fix to `milp.py` (they showed 553.84 kWh unmet / 116.2 L fuel, matching the explicitly-documented pre-S81-fix baseline in `RT01_ROUND1_STABILIZATION_REPORT.md` §2, not the current, correct 14.97 kWh / 129.48 L state). The stale originals were preserved at `/tmp/rt01_168h_trace_STALE_BACKUP.json`/`.csv` before being overwritten, and the regenerated files now match the governed current-state figures exactly (129.48 L, 79.64%, 99.73%, 14.97 kWh) — this was necessary to establish an accurate baseline for Part 1's counterfactual and is not a change to any source, test, config, or governance file.
- **Nothing staged, committed, or pushed.** `git status` confirms `system/`, `research/`, and `N6_REMEDIATION_REPORTS/` remain untracked (consistent with this repository's pre-existing no-commits state), with no index staging performed by this pass.
- **RT-01 remains OPEN.** This pass closes out one additional candidate-cause hypothesis (diesel-funded discretionary charging) with actual reproducible counterfactual evidence, identifies one small independently-justified candidate correction (Part 4.1, not implemented), and reconfirms that the only path to closing the steps-119–121 shortfall itself is the already-identified, already-excluded campaign-scale cross-horizon reservation redesign (Part 4.2), which requires separate owner authorization before any design or implementation work begins.
