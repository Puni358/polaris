# POLARIS — `system/control/router.py` Critical-Load Input: Fix Proposal (Not Applied)

**Date:** 2026-10-18
**Status:** Proposal only. `system/control/router.py` was **not edited**. This is a separate authorization decision from the `option_d.py` solar-accounting fix in `RT01_SOLAR_ACCOUNTING_FIX_REPORT.md`, per the governing directive's explicit instruction to keep the two apart.
**Protected-file status confirmed unchanged:** `system/control/router.py` hash `041fc2525acf8f353c15e1fa3aa4853f8fa720b25dfdfea207ca35ca178e338f`, re-verified before and after this pass's work, identical to every prior pass's recorded value.

---

## 1. The problem, as already evidenced

`EMSControlRouter.evaluate_and_route()` (`system/control/router.py`, lines ~54-61) computes its "critical load" input for the ECD (Emergency Condition Detector) survivability check as:

```python
# 2. Critical Load Trajectory (Use current demand scalar as synthetic fixture)
critical_load_w = float(current_state.last_observed_demand)
if critical_load_w <= 0.0 and bundle.demand.point:
    critical_load_w = float(bundle.demand.point[0])
if critical_load_w <= 0.0:
    critical_load_w = 30000.0  # Default prototype synthetic load floor
```

This substitutes the station's **full observed demand** (~35-48 kW for `demo_scenario.json`) for what should be the station's actual, much smaller, **protected critical-load** design value. The code's own comment admits this is a placeholder ("synthetic fixture"). Combined with the default `t_required_hours=6.0` ECD target, the battery's survivability margin against the full demand is negative at essentially every timestep, so the router classifies the station as `EMERGENCY` almost unconditionally for this scenario family — bypassing the intended `NORMAL`-route optimizer (`LocalMILPEnergyOptimizer` / GAP19) entirely in favor of `OptionDFallbackSolver`. This is the proximate, now-twice-confirmed cause of 3-5 of RT-01's 5 failures and of the previously-unmapped `test_v2_telemetry.py::test_gov_5_optimizer_deliberate_failure_preserved` failure (both fully traced in `RT01_RT02_FAILURE_FORENSICS_REPORT.md` Sections A.2/A.3, re-confirmed unchanged by `RT01_SOLAR_ACCOUNTING_FIX_REPORT.md` Section 2.3).

---

## 2. Authoritative source for actual critical-load demand

**None exists at runtime today.** The only candidate value in the repository is `system/config/loads.yaml`:

```yaml
critical_load:
  baseline_power_w: 11600.0
```

This is register item `CL-01`'s owner-decided value (11.6 kW). It is **not** a measured or validated figure for the real Nuolja station — it is explicitly and repeatedly self-labeled throughout the repository's own documentation as `SYNTHETIC_ENGINEERING_SCENARIO`, with `REAL_NUOLJA_CRITICAL_LOAD = NOT_ESTABLISHED` (see register item `EVID-02`, and `POLARIS_MASTER_DECISION_REGISTER.md` Section 1's "third" headline fact). No live telemetry-derived critical-load signal exists in `ForecastBundle`, `StationState`, or any config file.

## 3. Is that source available and validated for the relevant operating context?

**Available:** yes, as a static config value, always present (`loads.yaml` is checked into the repository and loaded by `configs`).
**Validated:** no. It is a prototype/engineering placeholder, not a measured or certified design value for the actual Nuolja station's protected load. Using it as a *routing* input (as opposed to its current, narrower use elsewhere in the EBR/dispatch-sizing stack) would be relying on an unvalidated number to decide whether the system is in `EMERGENCY` mode — a safety-relevant classification.

## 4. Safe behavior when the value is missing, stale, or only a synthetic fixture

The proposal's governing safety principle: **a routing change must never become less conservative than today merely because an unvalidated number happens to exist in a config file.** Concretely:

- If `configs["loads"]["critical_load"]["baseline_power_w"]` is present, numeric, and positive, use it as `critical_load_w`.
- If it is absent, zero, negative, or non-numeric, **fall back to the current (full-demand) behavior unchanged** — i.e., preserve today's conservative-by-default posture rather than inventing a different default. This is the same fail-safe pattern the existing code already uses (`current_state.last_observed_demand` → `bundle.demand.point[0]` → `30000.0` floor), just with the validated/config-supplied value taking priority over all three when it exists.
- No change is proposed to silently trust a future live critical-load telemetry feed (register `EVID-02`) without a separate validation step; that is explicitly out of scope here and remains `EXTERNAL_EVIDENCE_REQUIRED`.
- The 11.6 kW value itself must continue to be labeled synthetic in any report or log output the router produces — this proposal does **not** ask to relabel it as validated station demand, consistent with the directive's explicit boundary.

## 5. Proposed routing change

Replace (lines ~54-59):

```python
# 2. Critical Load Trajectory (Use current demand scalar as synthetic fixture)
critical_load_w = float(current_state.last_observed_demand)
if critical_load_w <= 0.0 and bundle.demand.point:
    critical_load_w = float(bundle.demand.point[0])
if critical_load_w <= 0.0:
    critical_load_w = 30000.0  # Default prototype synthetic load floor
```

with:

```python
# 2. Critical Load Trajectory
# Prefer the station's configured protected critical-load design value
# (loads.yaml, SYNTHETIC_ENGINEERING_SCENARIO per EVID-02/CL-01 -- not a
# validated station measurement) over the full observed-demand placeholder,
# falling back to the pre-existing behavior unchanged when no config value
# is present, to preserve fail-safe conservatism.
critical_load_w = float(
    configs.get("loads", {}).get("critical_load", {}).get("baseline_power_w", 0.0)
)
if critical_load_w <= 0.0:
    critical_load_w = float(current_state.last_observed_demand)
    if critical_load_w <= 0.0 and bundle.demand.point:
        critical_load_w = float(bundle.demand.point[0])
    if critical_load_w <= 0.0:
        critical_load_w = 30000.0  # Default prototype synthetic load floor
```

This is a single-expression substitution with a fallback chain preserved verbatim underneath it — no interface change, no new config schema.

## 6. Safety implications

This would make `EMERGENCY` routing **substantially less frequent** for `demo_scenario.json`-like conditions: 11.6 kW endures far longer against the same battery/diesel sizing than ~35-48 kW does, so the ECD survivability margin would be positive (or far less negative) at most timesteps where it is currently negative. This is a **reduction in conservatism**, not a pure bugfix, and must be reviewed as a safety-relevant behavior change:

- The current over-conservative behavior is not itself unsafe (it never under-protects load) — it is operationally misleading, since it makes the `EMERGENCY` classification nearly meaningless as a discriminator and routes essentially everything to the heuristic fallback solver instead of the intended MILP/GAP19 optimizer.
- Flipping to the 11.6 kW value would change *which* optimizer dispatches in many scenarios (MILP/GAP19 instead of `OptionDFallbackSolver`), which itself changes dispatch behavior beyond just the routing threshold and must be evaluated holistically, not assumed benign.
- No regression in actual critical-load protection is expected (critical load is still the explicit protection target inside `OptionDFallbackSolver`'s own priority logic when `EMERGENCY` is reached), but this must be demonstrated, not assumed.

## 7. Focused tests required before any such change (not run or added by this pass)

- `system/tests/test_rt01_rt02_failure_forensics_regressions.py::TestRouterCriticalLoadSubstitutionCausesPermanentEmergencyRouting::test_demo_scenario_step0_routes_emergency_not_normal` — must then assert `route == "NORMAL"` for the nominal demo_scenario.json step-0 case (its own docstring already says to re-check this).
- All 18 tests in `tests/test_gap19_ecd_option_d.py` (exercises E3 preserved/limiting-resource logic) — must still pass unchanged.
- `system/tests/test_s81_e2e_integration.py` tests 10, 11, 14, and 15, plus all 5 RT-01 tests in `system/tests/test_offline_runtime.py` — re-run to confirm unmet-load/fuel numbers move in the expected direction (generally down, since NORMAL-route MILP/GAP19 would now run) without introducing any *new* conservation residual.
- A new, explicit test asserting critical load is still fully served under a genuine resource-scarcity scenario even with the lower 11.6 kW threshold (to directly verify the "reduction in conservatism is not a reduction in actual protection" claim in Section 6, rather than assuming it).

## 8. Rollback procedure

Single-file, single-expression change (one block replacing another, five lines added net). Trivial to revert: restore the original five-line block. No schema, interface, or config-file-format change; no migration needed in either direction.

---

**This proposal is not applied. `router.py`'s hash is confirmed unchanged (Section 1 header). A separate, explicit owner/governance authorization is required before any edit to this protected file**, per the same Section-6/Batch-3-style review the forensics report already called for.
