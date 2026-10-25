# POLARIS — RT-01: Bounded, Read-Only Investigation of the 69.37% Renewable-Utilization Result

**Date:** 2026-10-18
**Nature of this document:** Owner-authorized, narrow, read-only investigation pass. Scope: determine ONLY whether a justified correction exists for the `renewable_utilization_pct = 69.37% < 75.0%` failure — NOT to relitigate the seven-hour dominance-violation theory (closed, per `RT01_SEVEN_HOUR_FEASIBILITY_AUDIT_AND_E2E_READINESS_REPORT.md`, not reopened here). The 75% floor is reaffirmed and untouched. No code, test, config, or register file was edited. No solver or pipeline was re-run; the one prior re-run this investigation relies on (nineteenth pass, byte-exact) is reused, not repeated. This pass performed only direct code reads and two independent hash re-verifications of already-committed files — see Section 5.

---

## 1. The exact computation and evidence underlying 69.37%

`renewable_utilization_pct` is computed in `system/evaluation/evaluator.py` (verified directly this pass, lines ~142–149 accumulation loop, lines 231–232 final ratio):

```python
total_renewables_used_wh = total_solar_used_wh + total_wind_used_wh
total_renewables_avail_wh = total_renewables_used_wh + total_curtailment_wh
renewable_utilization_pct = (total_renewables_used_wh / total_renewables_avail_wh * 100.0) if total_renewables_avail_wh > 0 else 0.0
```

`total_solar_used_wh`, `total_wind_used_wh`, and `total_curtailment_wh` are summed from each step's `DispatchPlan.solar_used`, `.wind_used`, `.renewable_curtailment` fields, restricted to the physically-executed H1 action (index 0) for the 168 closed-loop MPC steps (`is_closed_loop_mpc` branch, confirmed by direct read). This is an honest `used / (used + curtailed)` ratio over the two solvers' own bookkeeping — not a formula defect. `test_cumulative_physical_conservation_168h` (`system/tests/test_offline_runtime.py:496-548`) asserts `renewable_utilization_pct >= 75.0`; the observed value, `69.37%`, is the nineteenth pass's byte-exact pytest result (`AssertionError: 69.37 not greater than or equal to 75.0`), reused unchanged by every subsequent pass including this one — **no new test run was performed this pass.**

**Confirmed fact:** the metric formula itself (verified by direct code read, not reused from a prior report's quote) is internally consistent and not the defect.

---

## 2. The smallest supported explanation for the gap to 75%

Two structural facts, each independently re-verified by direct code read this pass (not merely cited from prior reports):

**(a) `OptionDFallbackSolver` has no mechanism to charge the battery from surplus renewable energy — confirmed fact.**
In `system/optimization/implementations/option_d.py`:
- Lines 104–106: `p_ren_to_load = min(p_ren_avail, p_crit_demand)`; `p_curtail = max(0.0, p_ren_avail - p_ren_to_load)` — any renewable above demand is unconditionally curtailed.
- A repo-wide grep of every assignment to `p_chg` in this file (line 127 `p_chg = 0.0` default; line 199 `p_chg = min(max_chg_avail_w, excess_diesel_w)`) confirms the **only** charging path is gated on `p_diesel > 0 and p_dis == 0` (line 193) — charging from excess diesel only. There is no code path anywhere in the file that routes curtailed/surplus renewable power into `p_chg`.
- By contrast, `gap19_highs_native.py`'s MILP bus-bar balance row (confirmed this pass, lines ~227–231) places solar/wind-used and `p_chg` on the same balance equation, so GAP19 can freely direct surplus renewables to the battery; Option D structurally cannot.

**(b) The scenario has substantial renewable-over-demand periods, not confined to a post-exhaustion tail — confirmed fact (reused computation).**
The twenty-first pass (`RT01_RENEWABLE_UTILIZATION_ROOT_CAUSE_REVIEW.md` §2c) computed directly from the already-committed `system/data/scenarios/synthetic_168h_endurance_scenario.json` and `system/config/solar_pv.yaml` that renewable availability exceeds `actual_demand` in 109 of 168 steps (64.9%), including 30 of the first 44 (pre-exhaustion) steps. This pass did not recompute it (not necessary — it is pure arithmetic on an unchanged input file, independent of any solver run) but confirms no contradicting evidence exists elsewhere in the record.

**Smallest supported explanation:** when `OptionDFallbackSolver` is the active dispatcher, any renewable surplus over demand is curtailed rather than banked in the battery, and this scenario has such surpluses on roughly two-thirds of all steps. The magnitude/duration of Option-D's activity is itself explained by the diesel-exhaustion/EMERGENCY-routing mechanism already on record (step ~44 exhaustion; `ecd.py`'s margin-trigger arithmetic plausibly engages EMERGENCY even earlier, per the twenty-first pass §2d) — but that earlier-trigger timing is **explicitly flagged by the prior pass as unconfirmed against an actual per-step trace**, and this pass did not attempt to confirm it (would require a pipeline re-run, out of scope here; see Section 6).

**Hypothesis, not confirmed:** the precise step at which Option D becomes active, and therefore the exact quantitative Wh/percentage-point recovery a fix would produce, remains unquantified. What is confirmed is the *mechanism* (Option D cannot bank surplus renewables); what is not confirmed is the *exact magnitude* of its contribution to the 5.63-point gap (69.37% vs. 75.0%), nor whether 75.0% is even reachable given this scenario's battery capacity/charge-power ceiling under ideal dispatch (twenty-first pass §4.1, unadjudicated).

---

## 3. Is a safe, narrowly scoped correction demonstrated, hypothesized, or not identified?

**Not demonstrated. Hypothesized only, with the mechanism confirmed but the effect size unverified.**

The only candidate correction identified anywhere in the record — give `OptionDFallbackSolver` a renewable-to-battery charging path mirroring GAP19's bus-bar logic (surplus `p_ren_avail - p_ren_to_load` charges the battery, bounded by `max_chg_w`/SOC headroom, before falling back to curtailment) — is a structurally sound, narrowly-scoped idea (touches only `option_d.py`), but:
- No one has computed what `renewable_utilization_pct` would become after this change (requires a re-run; not performed by any pass to date, including this one).
- It is not verified whether `>= 75.0%` is even achievable under this scenario's resource mix and battery sizing even with the fix (open scenario-calibration question, twenty-first pass §4.1).
- It would be a change to a `PROTECTED_FILES` entry, requiring full Section-6 governance review regardless of how well-scoped it is.

No alternative correction (metric redefinition, scenario reparameterization, or assertion relaxation) has evidentiary support as "justified" — the owner has already explicitly declined the assertion-relaxation route (Decision 2, twentieth pass), and no metric-definition defect was found (Section 1).

**Classification: HYPOTHESIZED, not demonstrated. No correction is identified that is both (a) proven to close the gap and (b) already authorized.**

---

## 4. Tests and approvals required before any proposed correction could be implemented

For the only candidate (Option-D renewable-to-battery charging path):
1. **Owner authorization** to open a Section-6 `PROTECTED_FILES` governance review scoped *only* to `option_d.py`'s charging logic (per existing register convention for any protected-file edit).
2. **Pre-implementation quantification step** (the twenty-first pass's own "remedy 4"): a single, bounded, read-only 168h diagnostic re-run logging per-step `operating_mode`, `diesel_fuel_remaining_liters`, and curtailment, to establish (a) how much of the run Option D is actually active for, and (b) the expected Wh recovery — *before* committing to the protected-file edit. This itself requires separate owner authorization to re-run the pipeline (not granted by the current directive, which restricts this pass to already-captured evidence).
3. **Post-implementation verification**: re-run the exact 5-test closure set (`system/tests/test_offline_runtime.py -k "test_flexible_load_constraints or test_flexible_load_no_double_counting or test_per_timestep_conservation_audit or test_cumulative_physical_conservation_168h or test_long_duration_closed_loop_endurance_168h"`), confirm `renewable_utilization_pct >= 75.0` is reached without regressing the other 4 tests, and re-verify all 7 `PROTECTED_FILES` hashes plus the 6 config YAMLs and scenario-file hash against the register.
4. **Conservation/SOC-bounds/no-double-counting correctness review** of the new charging branch (same standard the register already applies to prior Option-D edits, e.g. the fourteenth-pass diesel-floor repair).
5. If the scenario-calibration question (is 75% reachable at all under this resource mix/battery sizing) is resolved "no," a **separate owner decision** would be needed before any further engineering time is spent on this path.

None of these approvals exist today. The owner has authorized only this bounded read-only pass.

---

## 5. Hash and working-tree status for relevant protected files

Independently re-hashed this pass (SHA-256) and compared against the values on record in `POLARIS_MASTER_DECISION_REGISTER.md`/`.json` (v1.9.10, §36.6/current RT-01 item) and the prior three passes' own tables:

| File | SHA-256 | Status |
|---|---|---|
| `system/control/router.py` | `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3` | match |
| `system/control/ecd.py` | `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db` | match |
| `system/optimization/implementations/option_d.py` | `cdc642f146005aee9eaf11603b46691d54d95d9490f67cf056912611bbe62511` | match |
| `system/optimization/implementations/gap19_highs_native.py` | `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737` | match |
| `system/simulation/simulator.py` | `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f` | match |
| `system/runtime/runner.py` | `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10` | match |
| `system/orchestration/manifest.py` | `7b7756932a01dbc904ee780c3e0e30f8eab36952bbea6c75610c12c927d8bb35` | match |

**Zero mismatches.** `system/config/diesel.yaml` re-confirmed to still carry no `initial_fuel_l` key.

**Working-tree status:** this repository has no commits yet (initial state); `git status --porcelain` shows the entire `system/` directory (and most of the repo) as untracked (`??`), which is the pre-existing baseline, not a change introduced by this pass. No file was staged, edited, or committed by this investigation.

---

## 6. Current RT-01 status and shortest governed path to a real end-to-end run

**RT-01 status (register v1.9.10, unchanged by this pass):** `current_state: decided` (open at the full-system level). 3 of 5 named closure tests pass; 2 of 5 fail — `test_cumulative_physical_conservation_168h` (`renewable_utilization_pct = 69.37% < 75.0%`, floor reaffirmed, not waived) and `test_long_duration_closed_loop_endurance_168h` (`system_reliability_pct = 90.04% ≠ 100.0%`, cause accepted/documented but assertion not relaxed). Neither failing test satisfies the closure rule's disjunction (literal pass, or documented-and-accepted-and-relaxed).

**Shortest governed path identified, in order:**
1. Owner authorizes the single bounded, read-only 168h diagnostic re-run (Section 4, item 2) to quantify Option D's actual activity window and the expected Wh/percentage-point recovery from a renewable-to-battery charging fix — this is the one open factual question blocking any real quantification, and is explicitly a diagnostic, not a fix.
2. Based on that result, owner decides whether to open the scoped Section-6 protected-file review for the Option-D charging path (Section 4, item 1), or to conclude 75% is not reachable under this scenario and re-scope the scenario/floor question (Section 4, item 5) instead — these are mutually exclusive next steps depending on the diagnostic's outcome.
3. If a fix is implemented, re-run the 5-test closure set and re-verify all protected-file/config/scenario hashes (Section 4, item 3) before RT-01 can close.
4. Independently and in parallel (not blocking the above): the fuel-policy follow-through decision and the matched-diesel-comparison's 3 unmet prerequisites remain separately gated per `RT01_SEVEN_HOUR_FEASIBILITY_AUDIT_AND_E2E_READINESS_REPORT.md` §2.1–2.5 (not reopened or altered by this pass).

**This investigation's single recommended next action:** the owner authorizes the bounded, read-only 168h diagnostic re-run described in Section 4 item 2 / twenty-first pass "remedy 4" — logging only `operating_mode`, `diesel_fuel_remaining_liters`, and curtailment per step, no code change — as the smallest next step that converts the Option-D hypothesis into either a quantified, reviewable fix proposal or a basis for concluding no correction is warranted.

---

## 7. Confirmation — read-only, nothing staged or committed

No code, test, config, register, or protected file was edited by this pass, other than creating this new report and its `N6_REMEDIATION_REPORTS/` mirror. No pytest, pipeline, diagnostic script, campaign, or replay harness was invoked. The seven-hour dominance-violation thread was not revisited. `winner: null`, the campaign-execution guard, `DSL-01`'s `epsilon_tol`, and the 75% floor are all unchanged. Nothing staged, committed, or pushed.
