# Candidate 2: Forecast-Content Ablation — FINAL REPORT (168/168, corrected)

**This document supersedes `CANDIDATE2_REPORT.md` as the authoritative Candidate 2 result.**
`CANDIDATE2_REPORT.md` is preserved unmodified as historical evidence of the pre-fix,
82-step failed run — it is not deleted or overwritten, and it should continue to be read
as the forensic record that triggered the investigation below.

Scenario: `synthetic_168h_endurance_scenario.json`, same initial state, fuel budget (100L),
configs, physical constraints, and ECD bypass as `FINAL_168H_FORECAST_VS_REACTIVE_PROTOCOL`.
No production objective, constraint, or config changes. Frozen forecast = indices 1..23 of
solar_irradiance/solar_generation/wind_generation/demand (point/lower/upper) repeat the
index-0 value each step; index 0 unchanged.

---

## 1. What changed between the old report and this one

| | `CANDIDATE2_REPORT.md` (historical) | This report (authoritative) |
|---|---|---|
| Steps completed | 82 / 168 (run terminated) | **168 / 168** |
| Termination | `OPTIMIZATION_RUNTIME_FAILURE` at step 82 | None — completed cleanly |
| Fault count | 1 (fatal) | **0** |
| Fuel-overshoot events | not applicable (run died) | **0** |
| Runner | `run_candidate2_frozen_forecast_ablation.py` (no checkpointing) | `run_candidate2_checkpointed.py` (per-step checkpoints, resumable) |
| `milp.py` behavior | pre-fix (no post-solve binary snapping) | post-fix (binary snapping; see §2) |
| Comparison window vs real/reactive | first 82 steps only (`objective_cost_comparison_first82_apples_to_apples.json`) | full 168 steps (`objective_cost_comparison_three_way.json`) |

The old report's 82-step numbers are **not wrong for what they measured** — they are a valid partial trajectory under the pre-fix code. They are superseded here only because the run that produced them could not reach 168 steps, and because the three-way comparison is now possible over the full, intended horizon.

---

## 2. Root cause and fix (diagnosed in `diagnostics_step82/`, applied in `system/optimization/implementations/milp.py`)

### 2.1 The failure

```
OPTIMIZATION_RUNTIME_FAILURE (step 82): DispatchPlan violates charge/discharge
exclusivity at index 8: charge=0.04, discharge=45942.94.
```

### 2.2 Forensic diagnosis (read-only, `CANDIDATE2_FORECAST_CONTENT_ABLATION/diagnostics_step82/run_step82_diagnostics.py`)

The diagnostic script independently replayed the exact `StationState` entering step 82
(bit-for-bit, via the unmodified `DigitalTwinSimulator`), rebuilt the identical MILP matrices
used by production `milp.py`, and re-solved with raw, uninstrumented `scipy.optimize.milp()`
to inspect the solver's output *before* any production rounding/extraction logic touched it.

Finding: HiGHS returned the binary decision variable `u_chg` (the "battery is charging"
indicator) as `7.8e-7` — within HiGHS's own integrality tolerance of `0.0`, but not exactly
`0.0`. Production `milp.py`'s constraint 5 (`p_chg <= max_p_chg * u_chg`) is satisfied by this
near-zero binary with a correspondingly tiny but nonzero `p_chg ≈ 0.039W`. At the same
timestep, `u_dis = 1.0` and `p_dis = 45,942.94W` (a legitimate, large discharge). Because
`DispatchPlan`'s charge/discharge exclusivity check (`system/schemas/dispatch_plan.py`) uses
a `> 1e-3` threshold on the **rounded continuous** values, `p_chg = 0.04` (after 2dp rounding)
exceeded that threshold and the plan was rejected as physically inconsistent — even though
the binary semantics of the solution were "not charging."

This is a **numerical-representation artifact of the MILP→DispatchPlan boundary**, not an
error in the MILP formulation itself: the objective, all constraint coefficients, physical
bounds (battery/diesel power limits, SOC bounds, fuel budget), and the solver's own optimality
certificate were unaffected. The solver's *binary* decision was correct; only the *continuous*
companion variable it govern was left at solver-tolerance noise instead of being forced to the
binary's intended value.

### 2.3 The fix

Added to `LocalMILPEnergyOptimizer.optimize()` in `system/optimization/implementations/milp.py`,
immediately after `sol = res.x` and before output extraction:

```python
for t in range(H):
    base = t * K
    u_chg = 1.0 if sol[base + 11] >= 0.5 else 0.0
    u_dis = 1.0 if sol[base + 12] >= 0.5 else 0.0
    u_diesel = 1.0 if sol[base + 13] >= 0.5 else 0.0
    v_start = 1.0 if sol[base + 14] >= 0.5 else 0.0
    sol[base + 11] = u_chg
    sol[base + 12] = u_dis
    sol[base + 13] = u_diesel
    sol[base + 14] = v_start
    if u_chg == 0.0:
        sol[base + 4] = 0.0  # p_chg
    if u_dis == 0.0:
        sol[base + 5] = 0.0  # p_dis
    if u_diesel == 0.0:
        sol[base + 7] = 0.0  # p_diesel
```

Each binary (`u_chg`, `u_dis`, `u_diesel`, `v_start`) is snapped to the nearer of `{0, 1}`, and
whenever a binary snaps to `0`, its continuous companion (`p_chg`, `p_dis`, `p_diesel`
respectively) is forced to exactly `0.0` — so the bound the binary is supposed to govern is
actually enforced, not merely approximately satisfied.

### 2.4 Verification that this is purely a post-solve representation fix

Confirmed by direct inspection and by the regression/smoke evidence below — **not changed**:
objective function coefficients and weighting (`c[...]` construction, lines ~96–118),
constraint matrix construction (all 12 constraint families, lines ~148–289), variable bounds
(`lb`/`ub`, lines ~120–146), the solver call itself (`milp(c=..., integrality=..., bounds=...,
constraints=...)`, no options changed), the infeasibility-handling branch, and
`system/schemas/dispatch_plan.py`'s validation logic (exclusivity threshold, non-negativity,
schema checks — untouched). **Changed:** only the handling of `sol` between the solver call
returning and the output-extraction loop that was already present.

Evidence this is a true fix, not a workaround that hides the symptom:
- **Regression test** `tests/test_milp_binary_snapping.py`: reproduces the exact pathological
  vector (`u_chg=7.8e-7`, `p_chg=0.039`, `u_dis=1.0`, `p_dis=45942.94`) via a stubbed solver
  result and asserts the returned `DispatchPlan` is `OPTIMAL` with `battery_charge[8] == 0.0`
  and `battery_discharge[8] == 45942.94` (i.e. the large discharge is preserved exactly; only
  the solver-noise charge value is corrected).
- **Full test suite**: 138 passed both before and after the fix was applied/reverted in an
  isolated check; the same 6 pre-existing failures (unrelated: stale protected-file hashes and
  a missing-config test issue in `gap19_highs_native.py`/`runner.py`, confirmed present with
  the fix reverted too) are unchanged by this fix.
- **Step-82 smoke test** (exact scenario replay): re-solving the real, full-size step-82 MILP
  (not a synthetic stub) with the fix applied returns `OPTIMAL`, `battery_charge[8]=0.0`,
  `battery_discharge[8]=45942.94` — matching the regression test's synthetic case exactly.
- **Full 168-step rerun** (this report): zero faults, zero constraint violations across the
  entire trajectory, including step 82 itself.

---

## 3. Completion status (168-step rerun, `run_candidate2_checkpointed.py`)

| | |
|---|---|
| Requested steps | 168 |
| **Completed steps** | **168 / 168** |
| **Faults** | **0** |
| **Fuel-overshoot events** | **0** |
| **Constraint violations** | **0** |
| Total wall-clock runtime | ≈5h 38m |
| Checkpoints | 168 (`checkpoints/step_0000.json` .. `step_0167.json`), one per step, atomic writes |

Source: `milp_frozen_forecast_full_result.json`, `run_metadata.json` (both in this directory),
cross-checked against the 168 individual per-step checkpoint files on disk.

---

## 4. Full 168h comparison — Reactive vs Real-Forecast MILP vs Frozen-Forecast MILP

### 4.1 Operational / physical metrics

| Metric | Reactive baseline | MILP real forecast | MILP frozen forecast |
|---|---|---|---|
| Unmet (critical) load | 0.0 kWh | 184.15 kWh | **473.2 kWh** |
| System reliability | **100.0%** | 96.69% | 91.49% |
| Diesel fuel used | 49.5 L | 125.92 L | 38.15 L |
| Diesel energy delivered | 50.0 kWh | 243.68 kWh | 88.59 kWh |
| Diesel starts | 2 | 5 | 1 |
| Renewable energy used | 5,605.69 kWh | 5,407.44 kWh | 5,161.64 kWh |
| Renewable curtailment | 1,251.06 kWh (18.25%) | 1,449.31 kWh (21.14%) | 1,695.11 kWh (24.72%) |
| Battery throughput (charge+discharge) | 736.48 kWh | 1,407.48 kWh | 1,194.17 kWh |
| **EFC** (discharge-based, `EvaluationEngine`) | 3.6824 | 7.0374 | **5.9708** |
| Constraint violations | 0 | 0 | 0 |

### 4.2 SOC statistics (frozen-forecast run, full trajectory)

| | Value |
|---|---|
| Min SOC | 20.98% |
| Mean SOC | 47.39% |
| Max SOC | 88.85% |
| Final SOC | 24.99% |
| Final fuel remaining | 67.85 L (of 100 L initial) |

### 4.3 Fixed-weight objective cost (identical weights applied to all three, full 168 steps)

Weights: curtailment 0.05/Wh, battery deg 0.00005/Wh (charge+discharge), diesel marginal
0.000625/Wh, diesel base 12.5/running-hour, startup 15.0/start, unmet 10.0/Wh.

| Controller | Total fixed-weight cost (168 steps) | Diesel starts |
|---|---|---|
| Reactive baseline | 62,755.17 | 2 |
| MILP real forecast | 1,914,426.55 | 5 |
| MILP frozen forecast | 4,816,953.26 | 1 |

Delta (frozen − real-forecast MILP), full 168-step window: **+2,902,526.71**, driven almost
entirely by unmet_load (+2,890,482.70 in weighted terms). Frozen-forecast unmet load is
≈2.57x real-forecast MILP's unmet load over the full 168h (vs. the ≈4.2x ratio the old
82-step-only comparison showed — the ratio is window-dependent and should not be quoted
without stating which window it was computed over).

### 4.4 Forecast accuracy (the real baseline forecast, before freezing, vs. ground truth)

| Variable | MAE | RMSE | nMAE | Bias |
|---|---|---|---|---|
| Solar irradiance (W/m²) | 280.01 | 361.52 | 0.35 | +47.49 |
| Demand (W) | 6,047.97 | 7,441.65 | 0.20 | +3,096.15 |

### 4.5 Solver runtime behavior

| | Value |
|---|---|
| Mean solve time | 110.0 s |
| Median solve time | 2.8 s |
| Max solve time | 1,155.7 s (≈19.3 min, one outlier step) |
| Min solve time | 8.7 ms |
| Status on every completed step | `OPTIMAL` |

The solve-time distribution is strongly bimodal: most steps solve in low single-digit
seconds, but a minority of steps (the frozen-horizon's repeated-value structure is the
suspected driver — see `diagnostics_step82/` diagnostics 3 and 4 for node-limit and
symmetry-breaking probes of this specific effect) take minutes. This pattern is unchanged
by the binary-snapping fix (the fix does not touch solver options, branching, or node
exploration) and persists across the full 168-step run, not just at step 82.

**MIP gap / node count were not captured per-step in this production run.** The production
`LocalMILPEnergyOptimizer.optimize()` method returns a `DispatchPlan`, which does not carry
solver-internal diagnostics such as `mip_gap` or `mip_node_count`; only `solve_time_ms`,
`constraint_status`, and `objective_value` were recorded per step (in each checkpoint's
`solver_diagnostics` block). The standalone step-82 diagnostic script
(`diagnostics_step82/run_step82_diagnostics.py`) separately captured `mip_gap`,
`mip_node_count`, and `mip_dual_bound` for step 82 in isolation (see
`DIAGNOSTIC_1_exact_solve.json` through `DIAGNOSTIC_4_symmetry_breaking.json` in that folder),
and confirmed an exact (`mip_gap` effectively 0) `OPTIMAL` solve at that step — but this
instrumentation was deliberately kept out of the production path per the task's "do not
change solver tolerances, do not add instrumentation that could change control-flow"
constraint, so it is not available for all 168 steps.

### 4.6 Provenance / hashes (`run_metadata.json`)

| File | SHA-256 |
|---|---|
| `milp.py` (post-fix) | `3f136ae7201204f425cc895e8a8ee6e41801b7609228ddee60363ac35047d1be` |
| `milp.py` (pre-fix, historical, from old `run_metadata.json`) | `16c74d86af418aa592a5dfd8d49b53136b51a6718f55094f940a7437c70d27a3` |
| `dispatch_plan.py` | `02ff5550a6fd5d67a559cd188f8e7eafaf847b0e6318d9614d30f5df340c517b` (unchanged) |
| `simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` (unchanged) |
| `baseline_forecast.py` | `905c644abdc27d4ec3a8168ff39828bcc0575a4a6e31460c0ff4bfb16c30c993` (unchanged) |
| `forecast_bundle.py` | `98c0347aff21e05694625b6a77a067e094e9407e1d037d429d8f086332ade428` (unchanged) |
| `evaluator.py` | `79af472d52aab4b63180aaccac044ee48c9893f257c4f6988ccff7da1cec8729` (unchanged) |

Config/scenario hashes (station, battery, diesel, solar_pv, loads, optimizer, scenario) are
identical to the historical run's `run_metadata.json` — no config or scenario changes were
made between the two runs. Full hash table is in `run_metadata.json` in this directory.

Initial state (both runs, identical): `timestamp=2024-06-01T00:00:00Z`, `battery_soc_pct=50.0`,
`battery_energy_wh=100000.0`, `diesel_running=false`, `diesel_fuel_remaining_liters=100.0`.

---

## 5. What Candidate 2 (corrected) establishes

- The step-82 `OPTIMIZATION_RUNTIME_FAILURE` was a **post-solve binary/continuous-variable
  representation inconsistency** at the MILP→DispatchPlan boundary, not a flaw in the MILP's
  economic formulation, constraints, or physical limits. **FACT**, diagnosed via independent
  forensic replay and confirmed via regression test, scenario-exact smoke test, and a clean
  full 168-step rerun.
- With the fix applied, the frozen-forecast MILP completes the full 168h scenario with zero
  faults and zero constraint violations. **FACT.**
- Frozen-forecast MILP performs materially worse than real-forecast MILP on unmet load,
  reliability, and curtailment, but uses less fuel and starts the diesel generator less often
  — i.e. the frozen forecast does not simply make the controller "worse" uniformly; it changes
  *which* resource gets sacrificed (reliability/renewables-utilization vs. fuel/diesel-cycling).
  **FACT** (full 168h, this run).
- The previously-reported qualitative conclusion — "forecast content materially changes MILP
  behavior" — holds over the full horizon, not just the first 82 steps. **FACT**, now on firmer
  footing (full trajectory rather than a truncated one).

## 6. What Candidate 2 (corrected) does NOT establish

- **This does NOT establish that forecasting (or the real-forecast MILP) is universally better
  than reactive control.** Over the same full 168h window, the reactive baseline achieves
  *zero* unmet load, 100% reliability, and a two-orders-of-magnitude lower fixed-weight cost
  than either MILP variant. Candidate 2 only isolates the effect of forecast *content* within
  the MILP controller — it is not a MILP-vs-reactive adjudication, and the large MILP-vs-reactive
  cost gap (tracked separately in `05_Forensics/MILP Correctness Bug Investigation (Oct 2026)`
  in the knowledge vault) is **not resolved or explained by this fix**. The binary-snapping fix
  only prevents a crash; it does not change the MILP's objective trade-offs, and the underlying
  question of why MILP real-forecast unmet load is so much higher than reactive's remains open.
- This does NOT establish that the bimodal solve-time pattern (mean 110s, median 2.8s, one
  outlier at ~19 min) is fully understood or resolved — only that it no longer causes a crash.
  Diagnostics 3/4 in `diagnostics_step82/` probed node-limits and symmetry-breaking as candidate
  explanations for step 82 specifically; whether the same mechanism explains the outliers
  elsewhere in the 168-step trajectory was not re-verified per-step in this run (no per-step
  MIP gap/node count instrumentation — see §4.5).
- This does NOT re-validate or change the MILP objective, the optimizer formulation, or the
  forecasting system — none of those were touched, per task scope.
- The forecast-degradation ladder (frozen vs. real vs. perfect-information, and intermediate
  degradation levels) proposed as the next research phase remains **future work** — Candidate 2
  only covers two of those points (frozen, real) plus the independent reactive baseline.

---

## 7. Artifacts

- `milp_frozen_forecast_full_result.json` — full 168-step per-step trajectory + post-hoc metrics (authoritative)
- `run_metadata.json` — provenance (config/code/output SHA-256, initial state, fault record)
- `objective_cost_comparison_three_way.json` — fixed-weight cost, all three controllers, full 168 steps
- `checkpoints/step_0000.json` .. `step_0167.json` — per-step checkpoints (state before/after, forecast bundle, dispatch plan, solver diagnostics)
- `PROGRESS.json` — final status (`"status": "complete"`, `"step": 168`)
- `diagnostics_step82/` — forensic root-cause diagnostics (unchanged, read-only tool and its outputs)
- `CANDIDATE2_REPORT.md` — **historical**, pre-fix 82-step report (preserved, not modified)
- `run_candidate2_checkpointed.py` — the checkpointed runner used to produce this result
- `run_candidate2_frozen_forecast_ablation.py` — the original (non-checkpointed) runner, preserved for provenance
