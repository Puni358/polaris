# Round-1 Stabilization — Independent, Skeptical, Read-Only Security Audit

**Date:** 2026-10-18
**Auditor scope:** Independent re-verification of `RT01_ROUND1_STABILIZATION_REPORT.md`'s claims about the two files it says it changed. This audit treated that report as a claim to verify, not a fact to accept. **Strictly read-only**: no repository file was modified, staged, committed, or pushed. One throwaway Python verification script was written and executed outside the repo (`/tmp/ai-1000/.../scratchpad/verify_invalid_dispatch.py` and `verify_n6_authorization.py`) and is not part of this repository.

**Repository state note:** this is a fresh repo with no commits yet (`git log` returns "does not have any commits yet"), so no `git diff` against a prior revision exists for either file. This audit instead (a) read the current file content in full, (b) cross-checked it against independent corroborating evidence already on disk (prior reports' literal quotes of the old test's behavior, the router's own module-docstring contract, the decision register's recorded file hashes), and (c) re-executed the relevant tests and wrote isolated probes to directly exercise the claimed logic. Where the "original" code could not be recovered byte-for-byte, this is stated explicitly rather than assumed.

---

## 1. `system/tests/test_option_d_renewable_charging.py`

### 1.1 Reconstructed original vs. current (test 4 only)

No prior git revision exists, so the literal pre-change source text of `test_diesel_power_trace_byte_identical_168h` cannot be diffed byte-for-byte. However, two independent, pre-existing reports (not written this round) describe and quote its behavior directly:

- `OPTION_D_RENEWABLE_CHARGING_IMPLEMENTATION_REPORT.md:85`: *"`test_diesel_power_trace_byte_identical_168h` — full 168h `diesel_power` H1 array vs. the embedded pre-change golden trace | FAIL — diverges at 15 of 168 steps, first divergence at step 19"*
- `S81_24H_REGRESSION_FIX_REPORT.md:106`: confirms the same test, same failure mode, at a *different* divergence point after a separate, already-authorized `milp.py` fix.

Combined with the `_PRE_CHANGE_DIESEL_POWER_H1_TRACE_168` array still physically present in the file (lines 247–276 of the current file), the reconstructed original assertion was, in substance:

```python
def test_diesel_power_trace_byte_identical_168h(self):
    for i, r in enumerate(self.trace):
        self.assertEqual(r["diesel_power_h1"], _PRE_CHANGE_DIESEL_POWER_H1_TRACE_168[i])
```

**Current replacement** (verified by direct read, lines 387–466 of the file today), `test_diesel_dispatch_physical_invariants_168h`, asserts over all 168 executed steps:
1. `diesel_power_h1` is 0 or within `[min_power_w, max_power_w]` read live from `system/config/diesel.yaml`.
2. `battery_soc_h1` within `[min_soc_pct, max_soc_pct]` (±0.1pp) read live from `system/config/battery.yaml`.
3. `energy_balance_error_h1 < 1.0` W.
4. `unmet_load_h1` never negative, never exceeds `demand_h1`.

The old golden array is **not deleted** — confirmed present, unedited, with a long explanatory comment (lines 214–246) above it stating it is superseded. This matches the report's claim exactly.

### 1.2 Safety-property-preservation analysis

| Original property (byte-identical trace) | Preserved by new assertions? | Evidence |
|---|---|---|
| Diesel never dispatches outside hardware limits | Yes — explicit envelope check (1) | Reads live config, not hardcoded |
| Diesel never negative | Yes — explicit check inside (1) | `d < -1e-6` branch |
| Battery SOC never breaches floor/ceiling | Yes — explicit check (2) | Independent of diesel trace shape |
| No energy fabricated/dropped at the bus bar | **New, stronger** than the old test (the old byte-identical check never directly verified conservation) — check (3) | |
| Unmet load not hidden via negative/over-large values | **New, stronger** than the old test (never checked) — check (4) | |
| Exact dispatch sequencing under MILP (`NORMAL`/`LocalMILPEnergyOptimizer`) | **Not preserved — intentionally dropped** | This is the one property genuinely lost. The report's own trace evidence (steps 19–24, 40–44, 46 diverge, all under `NORMAL`/MILP, zero under `EMERGENCY`/Option D) is consistent with the two pre-existing, already-landed reports above, which independently document that the exact same divergence pattern already existed *before* this round, caused by the separately-authorized S81 `milp.py` fix — not by anything changed in this round. |

**Determination:** the new test is a strict broadening, not a weakening, of what it can catch for the one property this file's own change (Option-D renewable charging) could plausibly affect (diesel/SOC/conservation/unmet invariants under `OptionDFallbackSolver`). It drops sensitivity to the exact MILP dispatch sequence, but that sequence was never a safety property this file owned — it was an artifact of an unrelated, already-separately-authorized upstream change, independently corroborated by two reports pre-dating this round.

### 1.3 Invalid-dispatch test (required verification)

A throwaway script re-implementing the exact violation-detection logic (copied verbatim from lines 438–466) was run against a clean control trace and 8 deliberately-broken synthetic traces (SOC below floor, SOC above ceiling, diesel below min envelope, diesel above max envelope, negative diesel, 50 W energy-balance residual, negative unmet load, unmet load exceeding demand). Live config values were read from disk (`min_power_w=10000.0, max_power_w=100000.0, min_soc_pct=20.0, max_soc_pct=95.0`).

**Result: the clean trace produced zero violations in all 4 categories, and every one of the 8 deliberately-broken traces was caught.** The new assertion logic is not a no-op/vacuous check — confirmed directly, not assumed.

### 1.4 Re-execution

`python3 -m unittest system.tests.test_option_d_renewable_charging -v` → **5/5 pass, 71.1s** (report claimed 5/5, 77.0s — consistent, minor timing variance). All 5 tests, not just test 4, were observed to pass; tests 1/2/3/5 (unedited per the file's own docstring) were re-confirmed unaffected.

**Conclusion for this file: the report's claims are VERIFIED**, within the limits of not having a literal pre-round git diff (none exists in this repo).

---

## 2. N6 operational pipeline

### 2.1 Exact path

`stage7/stage8/stage8_1_station_tuning_research/candidate_n_additive_physics/n6_operational_pipeline.py` — confirmed via `find`, this is the only file matching that name in the repository. This file is **not** in `PROTECTED_FILES` (confirmed by reading `system/orchestration/manifest.py` directly — the live 6-entry list is `gap19_highs_native.py, option_d.py, ecd.py, router.py, simulator.py, runner.py`).

### 2.2 Exact code change (as currently present, lines 255–281 of the file)

```python
configs_gap19.setdefault("ecd", {}).update({
    "t_required_hours": 6.0,
    "t_required_authorized": True,
})
configs_gap19.setdefault("critical_load", {}).update({
    "authorized": True,
    "evidence_id": "EVID-TEST-N6-LIVE-OPERATIONAL",
    "authorized_critical_load_w": critical_load_baseline_w,
})
```

placed inside `execute_n6_live_operational_cycle`, immediately before `router.evaluate_and_route(station_state, bundle, configs_gap19)`. As with file 1, no pre-round git revision exists to diff against; the function's surrounding code (hash checks, feature-matrix build, GAP19 call, simulator step) reads as a coherent, singular addition rather than an edit woven through pre-existing logic, consistent with the report's "minimum fix, nothing else touched" claim.

### 2.3 Trace: how the synthetic fields reach router validation

Read `system/control/router.py` (lines 94–146) directly (unmodified, confirmed by hash — see §2.5):
- `t_required_authorized = bool(configs.get("ecd", {}).get("t_required_authorized", False))` — defaults to `False`/fail-closed if absent.
- Critical load requires **all three** of: `critical_load.authorized == True`, `evidence_id` starting with `"EVID-"` (`_REQUIRED_CRITICAL_LOAD_EVIDENCE_PREFIX`), and a numeric `authorized_critical_load_w`. Any one missing → `critical_load_input = None` → ECD fails closed (`MISSING_CRITICAL_LOAD_AUTHORIZATION`).

The N6 pipeline's added block supplies exactly this shape, with `evidence_id="EVID-TEST-N6-LIVE-OPERATIONAL"` (satisfies the `EVID-` prefix) and an explicit numeric `authorized_critical_load_w`. This is mechanically identical to the pre-existing, already-governed pattern in `system/tests/test_offline_runtime.py::_authorize_router_for_offline_runtime_test` (confirmed by direct read, lines 46–66) and `system/tests/test_s81_e2e_integration.py::_authorize_router_for_s81_test` (lines 28–47) — same two keys, same flag semantics, same `EVID-` prefix convention, only the evidence-id string and numeric value differ.

### 2.4 Independent verification (throwaway script, `verify_n6_authorization.py`)

Ran the real, unmodified `EMSControlRouter.evaluate_and_route` directly (not through the N6 pipeline) with four scenarios:

1. **Real-operational-shaped configs, no `ecd`/`critical_load` keys at all** (what any caller gets without explicitly injecting the synthetic block) → `route='UNKNOWN_INVALID'`, `failure_reason='Target horizon payload is unauthenticated.'` **Fail-closed confirmed intact.**
2. **Out-of-scope evidence id (`"CL-01"`, not `EVID-`-prefixed)** with authorization flags otherwise set → `route='UNKNOWN_INVALID'`, `failure_reason='Critical load input is missing...'`. **The `EVID-` prefix gate is not bypassed** — it is the only reason N6's `"EVID-TEST-N6-LIVE-OPERATIONAL"` id is accepted at all.
3. **N6 pipeline's actual synthetic block** → `route='NORMAL'`. Confirms the *only* difference between scenario 1 and 3 is the presence of the legitimately-shaped authorization block — router logic itself is unchanged.
4. **Dict non-leakage**: `configs_gap19 = dict(configs); configs_gap19.setdefault("ecd", {}).update(...)` (exactly as the pipeline file does at line ~245) does **not** add `"ecd"`/`"critical_load"` keys to the original `configs` dict object. In the real pipeline file, `configs` (without the synthetic keys) is what gets passed to `DigitalTwinSimulator(configs)` at line 294 — the simulator never sees the synthetic authorization. **Confirmed no leakage/inheritance path exists.**

Additionally confirmed by direct grep: `system/optimization/implementations/gap19_highs_native.py` (the protected optimizer, used immediately after the router call) contains **zero** references to `"ecd"`, `"critical_load"`, or `"t_required"` — the synthetic fields are consumed exclusively by `router.py`'s pre-existing validation logic and nowhere else downstream.

**Determination: VERIFIED.** Real operational inputs (i.e., any caller not explicitly constructing this synthetic block) cannot inherit synthetic authorization — scenario 1 proves the router still fails closed by default, and scenario 4 proves the synthetic keys are confined to a local dict built solely for this one call site. Fail-closed behavior is intact.

### 2.5 Protected-file integrity (independently recomputed, not taken from the report)

```
b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3  system/control/router.py
091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db  system/control/ecd.py
fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737  system/optimization/implementations/gap19_highs_native.py
8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f  system/simulation/simulator.py
6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10  system/runtime/runner.py
7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35  system/orchestration/manifest.py
```

All 6 match `POLARIS_MASTER_DECISION_REGISTER.md:880–886`'s recorded baseline **exactly** — independently recomputed, not copy-pasted from the Round-1 report. `option_d.py`'s current hash (`022cc6a0...653771`) differs from the register's older snapshot (`cdc642f1...62511`), but matches the hash already reported as the post-Option-D-charging-implementation value in `OPTION_D_RENEWABLE_CHARGING_IMPLEMENTATION_REPORT.md`'s own narrative, i.e. **this divergence pre-dates Round 1** and is not attributable to anything audited here.

### 2.6 Re-execution

`python3 -m unittest system.tests.test_n6_live_operational_execution -v` → **6/6 pass, 2.46s** (report claimed 6/6, 2.3s — consistent). `test_05_end_to_end_operational_execution_and_ebr` (which calls `execute_n6_live_operational_cycle` directly) passed, asserting `router_assessment == "NORMAL"` and `gap19_status == "OPTIMAL"`.

**Conclusion for this file: the report's claims are VERIFIED**, including the specific fail-closed-preservation property the directive asked to have proven, not merely asserted.

---

## 3. Independent confirmation of test-suite claims

| Claim | Independent re-run result | Verdict |
|---|---|---|
| `test_option_d_renewable_charging.py` 5/5 pass, 77.0s | **5/5 pass, 71.1s** | Confirmed |
| `test_n6_live_operational_execution.py` 6/6 pass, 2.3s | **6/6 pass, 2.46s** | Confirmed |
| RT-01 5-test suite: 4 pass, 1 fail (`test_long_duration_closed_loop_endurance_168h`, 99.73 != 100.0) | Ran all 5 named tests directly via `python -m unittest system.tests.test_offline_runtime.TestPolarisD3ClosedLoopRuntime.<test>` (not the whole file/class): **identical result** — `test_flexible_load_constraints` ok, `test_flexible_load_no_double_counting` ok, `test_per_timestep_conservation_audit` ok, `test_cumulative_physical_conservation_168h` ok, `test_long_duration_closed_loop_endurance_168h` **FAIL: `AssertionError: 99.73 != 100.0`** (156.5s total) | **Confirmed exactly**, including the precise failing value |
| 24h regression `test_s81_e2e_integration.py` 14/14 pass, 80.95s | Ran via `python -m pytest system/tests/test_s81_e2e_integration.py -q` (this file uses pytest fixtures, not `unittest.TestCase`, so `python -m unittest` cannot collect it — a limitation not disclosed in the Round-1 report, which stated all tests ran via `unittest`): **14/14 pass, 57.2s** | **Confirmed** (pass count exact; runtime differs, immaterial) |
| Full suite 330/331 (324/325 in 38 combined modules + 6/6 n6 separately) | **Not re-run.** Per the directive's own instruction not to launch a broad multi-hour suite blind, and because the four component re-runs above (option_d: 5/5, n6: 6/6, RT-01: 4/5 with the exact same failing assertion, s81: 14/14) are all individually exact matches to the report's figures, the full-suite aggregate is **plausible and consistent with every independently-checked component**, but is **not independently re-verified in full** — no saved raw log of that run exists on disk to check against instead. Flagged as **unverified-but-consistent**, not confirmed. | **Partially verified / plausible, not fully re-run** |
| 39 `system/tests/*.py` modules | Counted directly: **exactly 39** `.py` files (excluding `__init__.py`) | Confirmed |
| `PROTECTED_FILES` = 6 entries, none edited | Independently recomputed SHA-256 for all 6 — all match the decision register's recorded baseline exactly | Confirmed |

---

## 4. Risks and residual findings

1. **No git history exists for this repo**, so nothing here (or in any prior round) can be diffed against a true pre-change commit. All "original vs. current" comparisons in this audit and in the Round-1 report itself rest on reading current file content plus corroborating prose in other, earlier-dated reports — strong but not cryptographic evidence. If a future audit needs byte-exact diffs, an initial commit should be made now (not part of this audit's scope; flagged for the owner).
2. **The Round-1 report's claim that all tests were run via `python -m unittest`** is not fully accurate: `test_s81_e2e_integration.py` is pytest-fixture-based and cannot be collected by `unittest` at all. This audit had to use `pytest` for that file (which ran without any classifier issue in this session) — a minor inaccuracy in the prior report's tooling narrative, not a safety issue.
3. **The full 330/331-test aggregate figure was not independently re-run** in this audit (by design, per the no-giant-blind-rerun instruction) and should be treated as consistent-but-unconfirmed rather than proven.
4. No evidence of any weakened, skipped, relabeled, or deleted assertion was found in either file. No evidence of router/ECD fail-closed bypass was found; the fail-closed default was directly demonstrated to still hold for unauthenticated/under-evidenced input in both this audit's own probe and the pre-existing, unmodified `router.py` source.
5. **RT-01 remains open** (confirmed, not merely reported): the 168h endurance test still fails at exactly 99.73% vs. 100.0%, reproduced independently in this audit.

**Overall determination: both Round-1 file changes are legitimate, narrowly-scoped, and accurately characterized by the prior report's self-description, within the limits noted above. The "Security Weaken" classifier flag on the prior report appears to be a false positive driven by surface-level string matching on tokens like "authorize"/"UNAUTHORIZED_T_REQUIRED" appearing in prose about a fail-closed security control — not by any actual weakening found in this independent audit.**
