# POLARIS — RT-01: Authorized Bounded 168h Diagnostic — Renewable Gap Quantification

**Date:** 2026-10-18
**Nature of this document:** Owner-authorized, bounded, ONE-TIME, read-only diagnostic pass with full per-step telemetry capture. Continuation of `RT01_69PCT_RENEWABLE_UTILIZATION_GAP_INVESTIGATION.md`. This pass converts the previously **confirmed mechanism, unconfirmed magnitude** finding (`OptionDFallbackSolver` has no renewable-to-battery charging path) into a quantified figure via one real pipeline run. **This is a diagnostic, not a fix.** No source, test, config, scenario, or governance-register file was edited. No protected file was modified (verified below). Nothing staged, committed, or pushed. RT-01 remains **OPEN**; the 75% floor is unchanged; `winner: null` and the campaign guard are untouched.

---

## 1. Exact command / scope executed

Pre-execution verification (confirms the exact scenario/fixture/command used by the failing closure test):
```
python3 -m pytest system/tests/test_offline_runtime.py -k "test_cumulative_physical_conservation_168h" -q
```
Result: **1 failed** — `AssertionError: 69.37 not greater than or equal to 75.0` — byte-exact reproduction of the baseline on record.

Diagnostic run (new script, written for this pass, extending the exact pattern of `research/rt01_diagnostics/trace_168h_endurance_scenario.py`):
```
python3 research/rt01_diagnostics/trace_168h_renewable_gap_quantification.py
```
Internally this constructs and runs exactly the same call the closure test makes:
```python
runner = PolarisLocalRunner(SYSTEM_DIR, scenario_filename="synthetic_168h_endurance_scenario.json", optimizer_type="milp")
_authorize_router_for_offline_runtime_test(runner)
report = runner.run_pipeline(steps_to_run=168)
```
called **exactly once**. Telemetry is captured by wrapping four already-constructed bound instance methods (`router.evaluate_and_route`, `optimizer.optimize`, `option_d_solver.solve`, `simulator.step`) — each wrapper calls the original, unmodified method and returns its result unchanged (same non-invasive technique as every prior RT-01 trace pass). No source file was opened for writing.

**Exit status:** `execution_status: SUCCESS_CLEAN`, `timesteps_executed: 168`. No exceptions.

**Per-step telemetry location:**
- `research/rt01_diagnostics/rt01_168h_renewable_gap_quantification_trace.json` (full trace + run summary + hash manifests)
- `research/rt01_diagnostics/rt01_168h_renewable_gap_quantification_trace.csv` (168-row flat table)
- Script: `research/rt01_diagnostics/trace_168h_renewable_gap_quantification.py`

---

## 2. Integrity checks

**Protected-file hashes (SHA-256), verified independently by shell before and after the run, and separately by the script itself:**

| File | Hash | Status |
|---|---|---|
| `system/control/router.py` | `b2a46bc5...e90f3` | match, pre = post |
| `system/control/ecd.py` | `091358c0...1c96db` | match, pre = post |
| `system/optimization/implementations/option_d.py` | `cdc642f1...911be62511` | match, pre = post |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10...c118a2e737` | match, pre = post |
| `system/simulation/simulator.py` | `8c44f757...4204c74b3c5e5f` | match, pre = post |
| `system/runtime/runner.py` | `6d1671b6...5680d062f8dc53b10` | match, pre = post |
| `system/orchestration/manifest.py` | `7b775693...5610c12c927d8bb35` | match, pre = post |

**Zero mismatches. All 7 hashes identical before and after this pass.** (Full hex digests are recorded in the trace JSON's `pre_run_protected_file_hashes`/`post_run_protected_file_hashes`.)

**Artifact isolation:** `system/artifacts/{latest_dispatch_plan.json, latest_forecast_bundle.json, run_report.json}` are not tracked/protected source — every prior RT-01 trace pass that calls `run_pipeline()` discloses that these three caches get regenerated. This script snapshots their bytes immediately before its own run and restores them byte-for-byte immediately after (`artifact_isolation_restore_result: {all three: True}` — verified by the script). Note for full transparency: the Section-1 pytest verification run (needed to confirm the baseline) itself also regenerated these same two non-protected caches *before* this diagnostic script took its own snapshot, so their content now reflects the 168h-endurance-scenario run rather than whatever unrelated run preceded this session — consistent with standard, previously-disclosed behavior of this test suite, and not a change to any protected, tracked, or governance-relevant file. `run_report.json` ended up byte-identical regardless (deterministic content).

**Working tree:** `git status --porcelain` shows the entire `system/` and `research/` trees as untracked (`??`) — the pre-existing baseline (no commits exist in this repo). Nothing was staged or committed by this pass.

---

## 3. Analysis

### 3.1 Is the 69.37% baseline reproduced?

**Yes, exactly.** Both the direct pytest run (Section 1) and this diagnostic's own `run_report["ems_evaluation"]["renewable_utilization_pct"]` return **69.37**. Independently recomputing `used/(used+curtailed)` from this trace's own per-step records gives **69.3720%** — matching to 4 decimal places. `system_reliability_pct = 90.04%` also reproduces the figure on record. The prior, pre-existing trace (`rt01_168h_trace.json`, predating the step-0 full-horizon finding) shows identical route/solver counts, confirming this run is consistent with that earlier baseline.

### 3.2 Exact steps and duration Option D is active

**`OptionDFallbackSolver` is active for 167 of 168 steps (99.4% of the run) — steps 1 through 167 continuously.** Only step 0 uses `LocalMILPEnergyOptimizer` under the `NORMAL` route. Route counts: `{'NORMAL': 1, 'EMERGENCY': 167}`.

**New, previously-unconfirmed fact established by this trace:** EMERGENCY routing (and therefore Option D) engages at **step 1**, not at diesel-fuel exhaustion. At step 1, `battery_margin_hours = -0.4506` (already negative), `limiting_resource = BATTERY`, `preserved_resource = DIESEL`, while `fuel_before_l = 100.0` (diesel fuel is still full). Diesel is actually drawn on for only 11 of the 168 steps (steps 19–24 and 40–44), with literal fuel exhaustion (`fuel_after_l` hits 0.0) at **step 44** — matching the prior hypothesis about step-44 exhaustion, but that exhaustion happens 43 steps *after* EMERGENCY/Option-D routing had already begun. The router's battery-margin trigger, not diesel exhaustion, is what puts Option D in control almost the entire horizon. This corrects the earlier investigation's framing (which treated diesel exhaustion as the plausible trigger) with direct trace evidence.

### 3.3 Total renewable available, used, curtailed, with conservation checks

| Quantity | Value (Wh) |
|---|---|
| Total renewable available (H1, forecast solar+wind) | 6,856,749.79 |
| Total renewable used (H1, solar_used+wind_used) | 4,756,665.16 |
| Total renewable curtailed (H1) | 2,100,084.63 |

**Conservation check:** `used + curtailed` = 6,856,749.79, exactly matching `available` to within floating-point noise (max per-step residual: 1.46×10⁻¹¹ W across all 168 steps). The bus-bar energy-balance residual Option D itself computes (`energy_balance_errors[0]`) is **exactly 0.0 W for all 168 steps** — no double-counting, no unaccounted energy. 111 of 168 steps (66.1%) have nonzero curtailment, consistent with the prior investigation's independent ~65% estimate from forecast-vs-demand arithmetic. Curtailment occurring specifically during the Option-D-active window: 2,066,984.59 Wh (98.4% of all curtailment, expected since Option D governs 99.4% of steps).

### 3.4 Curtailment occurring while the battery could physically accept charge

For every one of the 111 curtailing steps, a post-hoc, per-step upper bound was computed from the **already-observed, unmodified** pre-step battery energy, respecting the actual configured SOC ceiling (95%), charge-power limit (50,000 W), and charge efficiency (0.92) — `eligible_for_charging_upper_bound_w = min(curtailment, max_chg_avail_w)`. Result: **the eligible/curtailed ratio is exactly 1.0 at every single curtailing step** (min = max = 1.0 across 111 steps) — i.e., under this frozen-trajectory calculation, the battery's charge-power ceiling and SOC headroom never once bound as a constraint on recovering the curtailed energy. Total eligible-for-charging upper bound = **2,100,084.63 Wh = 100% of total curtailment**.

### 3.5 Defensible upper bound on recoverable renewable energy and utilization

- **Upper bound if all eligible Wh were recovered:** utilization = (4,756,665.16 + 2,100,084.63) / 6,856,749.79 = **100.00%**.
- **Upper bound restricted to the Option-D-active window only** (the scoped correction's actual reach, since it would only ever modify `option_d.py`): (4,756,665.16 + 2,066,984.59) / 6,856,749.79 = **99.52%**.
- **Amount needed to exactly clear the 75% floor:** 385,897.18 Wh of additional recovered renewable use — just **18.4% of total curtailment** (18.7% of Option-D-window curtailment).

**Explicit assumptions / why this is an upper bound, not a demonstrated recoverable figure:** this is a **static, single-step, frozen-trajectory** calculation against the *already-executed, unmodified* run — it does not re-simulate what would actually happen if a charging branch existed. It assumes (a) no other dispatch decision in the same or later steps changes; (b) the ECD's routing/preserved-resource choice and the battery's SOC-dependent discharge availability in subsequent steps are unaffected by charging more now; (c) the per-step headroom ceiling computed from the *observed* trajectory stays valid under a counterfactual where SOC is higher entering later steps. In reality, charging earlier raises SOC entering later steps, which changes discharge headroom and could change diesel/battery dispatch choices downstream — a genuine dynamic effect this static upper bound does not capture. Actual recovered utilization after a real implementation could therefore be lower than 100%, though the margin above the 75% floor requirement (needing only ~18.4% of curtailment) is large enough to leave substantial room for such second-order losses.

### 3.6 Is the 75% floor physically reachable under the unchanged scenario and battery sizing?

**Not proven, but strongly and quantifiably supported as plausible — classified as a credible review candidate, not a demonstrated result.** The static upper bound (100%) clears the 75% floor with a wide margin (needing recovery of only 18.4% of curtailed energy, and the charge-power/SOC-headroom ceiling never binds in the observed trajectory), which is meaningfully different from a marginal or borderline case. This is the strongest evidence this investigation thread has produced to date, but it remains a single-step static bound, not a re-simulated dynamic result, so it does not by itself prove a real implementation would clear 75%.

---

## 4. Limitations

- Static, frozen-trajectory upper bound only — no counterfactual re-simulation of an actual charging branch was performed or attempted (prohibited by this pass's scope).
- Does not account for second-order/compounding effects of higher SOC entering subsequent steps on later dispatch, EMERGENCY routing, or diesel usage.
- Covers only the synthetic 168h endurance scenario at its current battery/diesel sizing; not generalized to other scenarios.
- Diesel-comparison, campaign execution, model training/tuning, and sealed/blind data remain out of scope and were not touched.

---

## 5. Recommended next decision (one)

The owner decides whether to authorize a scoped Section-6 `PROTECTED_FILES` governance review of `option_d.py`'s charging logic (the only candidate correction identified to date), informed by this pass's quantified finding that the required recovery (18.4% of curtailment) is small relative to the demonstrated upper bound (100%) and that EMERGENCY/Option-D governs 99.4% of this scenario's horizon. No further diagnostic re-run is proposed or launched by this pass.

---

## 6. Confirmation — read-only, nothing staged or committed

No source, test, config, scenario, or governance-register file was edited. No `PROTECTED_FILES` entry was modified (hashes verified identical before/after, Section 2). No assertion was relaxed, no metric redefined. No training, tuning, campaign, diesel comparison, or sealed/blind data access occurred. No follow-up diagnostic was launched automatically. Nothing staged, committed, or pushed. `winner: null`, the campaign guard, and the 75% floor are unchanged. RT-01 remains **OPEN** pending its existing closure rule.

**CONCLUSION: QUANTIFIED — REVIEW CANDIDATE**
