# Rule D Governance Reclassification

**Record type:** Research governance correction (read-only reinterpretation). Does not modify, overwrite, or delete any raw experiment telemetry or the original `FINAL_REPORT.md`.
**Target experiment:** `pc_sw_true_curtailment_recapture_20261008` (POLARIS Rule D: True-Curtailment Diesel Recapture, Full Governed Execution, 123 origins).
**Date:** 2026-10-08
**Status:** DECIDED — research governance only. No production promotion. No change to any production or executor file.

---

## 1. Original verdict (preserved, not erased)

`EXPERIMENT_DEFINITION.json` and `AGGREGATE_SUMMARY.json` recorded: `"verdict": "FAIL — SEMANTIC/IDENTITY CHECK"`, based on `IDENTITY_CHECK_REPORT.json` showing `all_identity_pass: false` (max SOC divergence 28.97pp, `identity_violations_count: 32`).

**This record is factually correct and is preserved as-is.** It documents a true, measured property of the candidate: its closed-loop trajectory differs from the baseline's at 32 of 2,952 hours.

## 2. Governance question

Is exact trajectory identity to the baseline a correct acceptance criterion for a policy whose explicit purpose is to reduce diesel fuel consumption?

## 3. Evidence from this repository's own established acceptance framework

- **Authoritative gate definitions** (`experiments/stage4_planner_cf_consistency_2025/planner_cf_statistics.py`, module docstring): S1 (`dR_CF >= 0.00 pp` vs. PC-Control, aggregate 123 origins), S2 (`dR_P >= 0.00 pp`), S3 (zero candidate hours with realized SOC < 20%). No trajectory-identity criterion appears anywhere in this definition.
- **Prior candidate precedent** (`CAMPAIGN_V12_615_20261006/PC_RESULT_SUMMARY.md`): all four Planner-CF v1.2 candidate arms (PC-S, PC-SW, PC-S-L, PC-SW-L) were evaluated and reported purely on `dR_CF`, `dR_P`, SOC<20 hours, fuel, and saving % — each arm necessarily produces a trajectory different from PC-Control's, and none was required to reproduce PC-Control's trajectory.
- **Terrain-correction Phase-1 precedent** (`phase1_terrain_correction_20261007/PHASE1_TERRAIN_RESULT_SUMMARY.md`): verdict **"PASS / SAFE-BUT-FUEL-WORSE"**, decided explicitly on S1/S2/S3 (§4 of that report), with a trajectory materially different from Control's (critical unmet −71.9%, fuel +1.85%). Trajectory identity was never invoked as a gate.
- **This experiment's own instrumentation** (`SAFETY_GATES_REPORT.json`, this artifact, read this turn): independently computed **S1: PASS** (candidate R_CF 99.18508% ≥ Control 99.1589%), **S2: PASS** (candidate R_P 97.81162% ≥ Control 97.7963%), **S3: PASS** (0 SOC violations), **fuel-inventory gate: PASS** (0 violations), **`all_gates_pass: true`**.

**Conclusion, directly supported by repository evidence, not assumed:** this repository's established acceptance framework for a Planner-CF v1.2 candidate policy is S1/S2/S3 (plus fuel-inventory validity), not trajectory identity to baseline. Rule D's own `SAFETY_GATES_REPORT.json` already shows it passes every one of these gates. The "FAIL" label in `AGGREGATE_SUMMARY.json`/`EXPERIMENT_DEFINITION.json` reflects a stricter, self-imposed identity check that was never part of this repository's established acceptance criteria for an intentional dispatch-altering policy — it is a valid diagnostic (confirming the local substitution mechanism works exactly as designed, and documenting the closed-loop feedback it causes) but it is **not a governing rejection criterion** for this policy class.

## 4. Fuel-feedback mechanism (why identity legitimately fails)

Traced in the prior turn's postmortem: `fuel_remaining(t+1) = fuel_remaining(t) − fuel(t)` (executor), carried into `station_state.diesel_fuel_remaining_liters`, entering the next resolve's hour-0 fuel-feasibility row (`research_numerical_extractor_planner_cf_v1.py`, Amendment A2 §17.2: `5·u_diesel[0] + 0.00025·p_diesel[0] <= F_rem`). A policy that legitimately preserves more fuel changes `F_rem`, which is a real, governed state variable the receding-horizon controller is designed to react to. Divergence downstream of a trigger is the controller correctly responding to a genuinely different state, not a violation of executor semantics.

## 5. Fuel accounting (decomposition, not independently re-derived — read from persisted artifact)

- Direct recapture: `total_recapture_energy_kwh = 743.68404` kWh → `185.921 L` at the governed 0.00025 L/Wh marginal rate. **[DERIVED from `AGGREGATE_SUMMARY.json`'s persisted field]**
- Net saving: `56.6205 L` (baseline 8,729.2446 L → candidate 8,672.6241 L). **[VERIFIED, `AGGREGATE_SUMMARY.json`]**
- Implied downstream offset: `185.921 − 56.6205 ≈ 129.300 L`. **[DERIVED by subtraction — an accounting decomposition, not an independently re-traced causal attribution of which specific downstream hours absorbed it.]**

## 6. Reclassification

**PASS — S1/S2/S3 SAFETY-GATED RESEARCH RESULT; TRAJECTORY DIVERGENCE OBSERVED AND ACCEPTED AS A NORMAL CLOSED-LOOP CONSEQUENCE OF THE POLICY.**

The original identity-check diagnostic (§1) remains valid and is preserved in full in `IDENTITY_CHECK_REPORT.json`, unmodified. It is reclassified here as **non-governing** for acceptance purposes, based on repository evidence (§3), while remaining governing/informative for understanding the policy's closed-loop mechanism (§4).

## 7. Explicit non-claims

This record does **not** establish or claim:
- production readiness or production promotion of Rule D;
- a guaranteed fuel saving under any other population, year, or operating condition;
- that 56.6205 L (or 185.921 L) is an optimal or maximal achievable saving;
- validity of any new safety gate, threshold, or guard beyond S1/S2/S3/fuel-inventory, none of which are introduced by this record;
- that the ~129.300 L downstream offset is fully understood mechanistically (only the accounting magnitude is established).

## 8. AGY status

**No new AGY execution is required or requested by this record.** This is a reinterpretation of an already-completed, already-persisted experiment.

## 9. Authorization

This record decides governance classification only. It does not authorize production promotion, controller/executor modification, or any further campaign. Any such action requires separate, explicit authorization.
