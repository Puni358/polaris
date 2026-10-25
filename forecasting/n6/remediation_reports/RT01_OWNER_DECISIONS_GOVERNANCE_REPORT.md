# POLARIS — RT-01 Owner Decisions & Minimal Governance Pass (v1.9.9 → v1.9.10)

**Date:** 2026-10-18
**Nature of this document:** Twentieth pass in the `N6_REMEDIATION_REPORTS/` series, continuing directly from `RT01_METRIC_FIX_AND_FUEL_POLICY_REPORT.md` (nineteenth pass). Mirrored verbatim in `N6_REMEDIATION_REPORTS/`.
**Scope confirmation up front:** This is a **pure documentation/governance-recording pass**. No code, test, or config file was edited. No diagnostic, full test suite, campaign, diesel comparison, training run, or tuning was executed. Nothing staged, committed, or pushed. The project owner recorded 3 explicit decisions on the two dependencies the nineteenth pass left open (Section 4 / §35.6 of the prior report); this report records them, interprets RT-01's own closure rule against them, and states exactly what remains open.

---

## 1. Closure rule — read and quoted verbatim before any edit was made

Per the directive's explicit instruction, `RT-01`'s own `closure_test` field (`POLARIS_MASTER_DECISION_REGISTER.json`, `items[].id=="RT-01"`, as corrected by the seventeenth pass, §33) was re-read in full rather than assumed. Its substance, verbatim:

> "...all 5 named tests in `system/tests/test_offline_runtime.py` — `test_flexible_load_constraints`, `test_flexible_load_no_double_counting`, `test_per_timestep_conservation_audit`, `test_cumulative_physical_conservation_168h`, `test_long_duration_closed_loop_endurance_168h` — pass, or a documented, owner-accepted explanation exists for why the residual is expected and the tests' assertions should be relaxed."

This is a **disjunction** with a **conjunctive second branch**: either (A) all 5 tests literally pass, or (B) — for whatever tests do not pass — a documented, owner-accepted explanation exists for why the residual is expected, **and** the tests' assertions should be relaxed. Documentation and owner acceptance of a cause, by itself, is not sufficient under branch (B) unless the assertion is also relaxed; and branch (B) requires owner acceptance, not merely owner awareness.

---

## 2. The 3 owner decisions, as recorded

### Decision 1 — Fuel policy: Option (c) selected

The owner selects **Option (c)** from the nineteenth pass's decision-ready proposal (`RT01_METRIC_FIX_AND_FUEL_POLICY_REPORT.md` Section 4): retain the synthetic `100` L `initial_fuel_l` default and the current no-refueling behavior. The 168-hour scenario's fuel-exhaustion mechanism — 167 of 168 steps route `EMERGENCY`/`OptionDFallbackSolver` after diesel exhausts at hour ~45 (eighteenth pass diagnostic, §34.2) — is documented as a **prototype-scenario limitation**, not fixed.

- `system/config/diesel.yaml` is **not** edited (it already carries no `initial_fuel_l` key; confirmed unchanged this pass).
- No `PROTECTED_FILES` entry (`router.py`, `ecd.py`, `option_d.py`, `gap19_highs_native.py`, `simulator.py`, `runner.py`, `manifest.py`) is edited.
- Fuel capacity is **not** raised; no refueling/resupply logic is added.
- This decision is explicitly a disposition of the **current prototype scenario's own modeled assumptions**. It does **not** assert, imply, or establish that real-station fuel-reserve capacity, burn rate, or resupply logistics are known, measured, or authorized. The register's own §27 (`ECD-01` Decision A) text — the real-station logistics value "remains `NOT_ESTABLISHED` until separately supported ... and authorized" — stands unchanged and uncontradicted.

### Decision 2 — Renewable utilization: the 75% floor is NOT waived

The owner explicitly declines to accept `69.37% < 75.0%` (`test_cumulative_physical_conservation_168h`'s `renewable_utilization_pct` assertion) as an adequate outcome, and explicitly declines to weaken the `>= 75.0` threshold or to label the result "acceptable."

- This is recorded as a **real, unresolved failure under current scenario assumptions** — pending either a further owner decision or separately authorized engineering work.
- It is tracked as an **independent, separately-owned unresolved outcome** from `test_long_duration_closed_loop_endurance_168h`'s `90.04% != 100.0%` residual, even though both share the same proximate scenario context (the diesel-exhaustion/`EMERGENCY`-fallback-dispatch mechanism).
- **No inference is drawn or authorized** that resolving Decision 1 differently in the future (Option (a) or (b)) would restore `renewable_utilization_pct >= 75.0%`. The nineteenth pass's own §35.6 already flagged this as "plausible but not verified," requiring a re-run after any such change; this pass performs no such re-run and reaches no such conclusion. The two outcomes remain independently tracked.

### Decision 3 — Metric semantics: the nineteenth pass's correction is retained, unchanged

`system/tests/test_offline_runtime.py::test_cumulative_physical_conservation_168h` keeps exactly the assertions the nineteenth pass applied:

```python
self.assertIn("FALLBACK_TO_TOTAL_UNMET_LOAD", dispatch_safety["critical_unmet_source"])
self.assertGreaterEqual(ems_eval["renewable_utilization_pct"], 75.0)
```

- No assertion that critical-unmet energy is zero, and no assertion that `critical_unmet_total_wh == "UNKNOWN_NOT_VERIFIED"`, is reinstated or added. The nineteenth pass's own schema trace (§35.2) — direct code read of `system/evaluation/evaluator.py`, `system/safety/reserve_policy_guard.py`, and `system/schemas/dispatch_plan.py` — already established that literal string is structurally unreachable on the `critical_unmet_total_wh` field for any schema-valid `DispatchPlan` (that field is a required, non-optional constructor argument; the actual fallback value is the number `553842.6` Wh).
- `system/tests/test_offline_runtime.py` is **not edited** by this pass. Decision 3 is a reaffirmation of already-correct, already-applied behavior, not a new change — verified by re-reading the file (no diff performed, since no edit was made or needed).

---

## 3. Closure-rule interpretation applied to these 3 decisions

| Test | Status | Branch (A): literally passes? | Branch (B): documented + accepted + assertion relaxed? | Closure bar met? |
|---|---|---|---|---|
| `test_flexible_load_constraints` | passes (unchanged) | Yes | n/a | Yes |
| `test_flexible_load_no_double_counting` | passes (unchanged) | Yes | n/a | Yes |
| `test_per_timestep_conservation_audit` | passes (unchanged) | Yes | n/a | Yes |
| `test_cumulative_physical_conservation_168h` | fails (`69.37 < 75.0`) | No | No — Decision 2 explicitly withholds acceptance; no assertion relaxed | **No** |
| `test_long_duration_closed_loop_endurance_168h` | fails (`90.04 != 100.0`) | No | Partial — Decision 1 documents/accepts the *cause*, but no assertion was relaxed (out of scope for a documentation-only pass; not authorized) | **No** |

**Conclusion: the closure bar is not met.** Two of 5 named tests still fail. For neither failing test does the full conjunctive branch (B) hold: `test_long_duration_closed_loop_endurance_168h` has an accepted explanation but no relaxed assertion; `test_cumulative_physical_conservation_168h` has neither an accepted explanation nor a relaxed assertion. **`RT-01.current_state` therefore remains `decided` (open at the full-system level) — not changed by this pass.**

This pass did not re-run `python3 -m pytest system/tests/test_offline_runtime.py -k "..."`; the pass/fail values above are reused verbatim from the nineteenth pass's own byte-exact evidence (3 passed, 2 failed — `69.37 not >= 75.0` and `90.04 != 100.0`), per the directive's explicit instruction not to re-run diagnostics.

---

## 4. Protected-file hash integrity — before and after

All 7 `PROTECTED_FILES` entries re-hashed before and after this pass's documentation-only edits (register `.md`/`.json` + this new report; no source, test, or config file touched):

| File | SHA-256 | Before | After |
|---|---|---|---|
| `system/control/router.py` | `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3` | match | match |
| `system/control/ecd.py` | `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db` | match | match |
| `system/optimization/implementations/option_d.py` | `cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511` | match | match |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | match | match |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | match | match |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | match | match |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | match | match |

All 7 values are byte-identical before and after, and exactly match the v1.9.9-recorded (nineteenth-pass) baseline. **Zero mismatches. No `PROTECTED_FILES` entry, `diesel.yaml`, test file, frozen artifact, or safety-gate authorization was edited this pass.**

---

## 5. Safety and campaign boundaries — preserved, unchanged

- `winner: null` — unchanged, not touched.
- The campaign-execution guard (`CampaignExecutionNotAuthorizedError`, unconditional) — unchanged, not invoked.
- `DSL-01`'s deferred `epsilon_tol` — unchanged, still unset.
- Frozen Stage 8.1/N6 assets — unchanged, not accessed.
- Sealed 2025 blind-data restrictions — unchanged, not accessed.

None of these required any action this pass; they are restated here only to confirm the directive's explicit preservation requirement was checked, not assumed.

---

## 6. Files changed this pass

| File | Change |
|---|---|
| `POLARIS_MASTER_DECISION_REGISTER.md` | New **Section 36**; running amendment-history date line extended with a twentieth-pass summary; version `1.9.9` → `1.9.10` |
| `POLARIS_MASTER_DECISION_REGISTER.json` | New top-level `amendment_2026_10_18_twentieth_pass_rt01_owner_decisions_governance_pass` key; `RT-01.owner_decision_record` gains `pass_2026_10_18_twentieth_pass_owner_decisions_and_minimal_governance_pass`; `version` `1.9.9` → `1.9.10`; `date` updated |
| `N6_REMEDIATION_REPORTS/POLARIS_MASTER_DECISION_REGISTER.md` / `.json` | Mirrored verbatim |
| `RT01_OWNER_DECISIONS_GOVERNANCE_REPORT.md` (this file) + `N6_REMEDIATION_REPORTS/` mirror | New |

**No production code, test file, `diesel.yaml`, or `PROTECTED_FILES` entry was edited.** Nothing staged, committed, or pushed.

---

## 7. RT-01 status and what still requires separate owner approval

**RT-01 remains OPEN.** `RT-01.current_state` is `decided` (open at the full-system level) — **unchanged by this pass**, per the closure-rule analysis in Section 3. 3 of 5 named tests pass (unchanged); 2 of 5 still fail, for the same two independently-tracked reasons established by the nineteenth pass, now explicitly dispositioned by the owner's 3 decisions but not closed by them.

**Still requiring a separate, further owner decision before RT-01 can close:**

1. **Fuel-policy follow-through:** whether to authorize Option (a) (an owner-supplied, provenance-backed `initial_fuel_l` liter value) or Option (b) (modeled refueling/resupply logic, requiring a full Section-6 `PROTECTED_FILES` governance review) — instead of, or at some future point in addition to, Option (c). Option (c) is the owner's selection *for now* (Decision 1) and does not foreclose revisiting this.
2. **Renewable-utilization disposition:** whether, or under what separately authorized engineering work, the `69.37%` outcome is ever to be accepted, or brought to `>= 75.0%`. Explicitly **not** resolved by this pass (Decision 2) — this is the single most load-bearing open item from this pass's own scope.
3. **Any future re-run:** if either (1) or (2) is resolved later, the affected test(s) must be re-run and this register updated before RT-01 can be considered for closure. No re-run was performed, implied, or assumed by this pass.

No test, config, or protected file beyond the documentation edits listed in Section 6 was changed. Nothing staged, committed, or pushed.
