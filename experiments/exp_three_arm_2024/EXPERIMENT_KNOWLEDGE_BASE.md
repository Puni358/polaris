# EXP-THREE-ARM-2024 — Experiment Knowledge Base

**Read this file first** if you are a future AI assistant or ChatGPT session arriving at `experiments/exp_three_arm_2024/` and need to understand what this experiment is, what it found, and what remains open. It is a documentation and evidence-preservation record, not an experiment, and it does not authorize anything.

**Navigation for future sessions:**
1. Read this file first.
2. When a claim here needs independent verification, inspect the referenced frozen evidence directly (paths and hashes below) — do not take this document's word for a number without being able to trace it to `RESULTS.json`/`HOURLY_TELEMETRY.csv` or the cited source line.
3. Preserve the original candidate labels and eligibility decisions recorded here; do not relabel, re-score, or silently resolve the open questions in §6.
4. Distinguish established facts from hypotheses — both are marked explicitly throughout.
5. Do not repeat, replay, or extend this experiment without a new, separately scoped governance decision and execution authorization. This document does not grant one.

For earlier project history (preregistration, decisions D1–D11, calibration, the pre-execution governance process, and the `run_20261011T075716Z` incident and its fix), see `HANDOVER.md`, `DECISIONS_LOG.md`, and `CHANGELOG.md` — this file does not repeat that history, only the completed-run outcome and its analysis.

---

## A. Experiment identity and status

- **Name:** EXP-THREE-ARM-2024 — three-arm (plus two diagnostics) solar-forecast/reserve-policy comparison on 2024 SITES Nuolja data.
- **Purpose:** test whether netting a forecast of solar (and wind) generation against the battery's energy-based reserve (EBR) target reduces diesel fuel use relative to a reserve that ignores solar entirely, and whether that holds up under a pre-registered statistical and reliability gate (S1–S4, E1).
- **Completed run directory (immutable evidence):** `results/run_20261011T143130Z/`
- **Run dates:** started `2026-10-11T14:31:30.994463+00:00`, ended `2026-10-11T16:31:31.223481+00:00` (UTC).
- **Solve counts:** 14,760 total `PlannerCFV1Optimizer.optimize()` calls; 2,952 per arm × 5 arms (PC-Control, A, A_FIX, B, C). All 14,760 solves returned `OPTIMAL`/`FEASIBLE` (verified: 0 non-optimal rows in `HOURLY_TELEMETRY.csv`).
- **Evidence files and SHA-256 (re-verified 2026-10-11, present in this file and in `reports/FORENSIC_INVESTIGATION_ARM_A_ARM_B_2026-10-11.md`):**

  | File | SHA-256 |
  |---|---|
  | `results/run_20261011T143130Z/RUN_STATUS.json` | `4f89c4302977185168491e909a54229b8057a9ee3f43dd435427b379fbcec28f` |
  | `results/run_20261011T143130Z/RESULTS.json` | `3548db6ac78922ca78800a658443968a261bde1d15969d856ade8a173c142092` |
  | `results/run_20261011T143130Z/HOURLY_TELEMETRY.csv` | `9e5797ddfd0a7feb18b5288d449fc6020593294e3247ab7ed79b3347dd24be07` |
  | `results/run_20261011T143130Z/EXECUTED_HOUR_TELEMETRY.csv` | `641099413e42c72617edd5b36f8f4c52cf717b3f1eebee582eaa503ab49b69ec` |

- **Immutable-evidence warning:** `results/run_20261011T143130Z/` must never be modified, renamed, regenerated, deleted, or overwritten. Any future analysis works from copies made elsewhere.
- **An earlier run, `results/run_20261011T075716Z/`, is also preserved immutable.** It used the same 14,760-solve configuration but FAILED post-run validation (a telemetry-string representation bug, since fixed; see `CHANGELOG.md`). It is historical evidence of that incident, not an alternative result — do not treat its numbers as comparable output.
- **Execution completion vs. validation vs. statistical findings vs. promotion eligibility — these are four separate, non-substitutable layers, and this run's outcome touches all four differently per arm:**
  1. *Execution completion* — all five arms completed (`RUN_STATUS.json` `status: COMPLETED`, all arms `COMPLETE`). This only means the solver ran to completion; it says nothing about validity.
  2. *Validation* — `RESULTS.json` exists and was produced by the post-run validator; this run passed validation (unlike `run_20261011T075716Z`). This means the telemetry is well-formed and gate-evaluable, not that any arm is good.
  3. *Statistical findings* — e.g., Arm A's and Arm C's underlying fuel-saving statistic (E1) independently passes (Wilcoxon-signed-rank, Holm-adjusted). A passing statistic is necessary but not sufficient for eligibility.
  4. *Promotion eligibility* — governed by the full gate set (S1–S4, reliability, causality, E1 family membership) and the project's own decision log (D10, D10a). **No arm is promotion-eligible in this run.** A result can pass its core fuel statistic and still be fully ineligible (Arm C is the clearest example: E1 statistic passes, but `EVALUATED: false` and the overall verdict is "NOT AN IMPROVEMENT").

---

## B/C. Candidate register

Values marked **(recomputed)** were independently reproduced in this investigation directly from `HOURLY_TELEMETRY.csv` (via `pandas.groupby` on `arm`/`origin_id`/`hour`) and matched the corresponding `RESULTS.json` field exactly. Values with no such marker were read directly from `RESULTS.json`. `NOT AVAILABLE` marks a field that genuinely has no counterpart in the frozen artifacts for that arm (not a judgment call).

### PC-Control

- **Label:** `BASELINE — LEGACY GEOMETRY (DOCUMENTED 1 H SOLAR-POSITION ERROR)`.
- **Role:** frozen comparison baseline for all other arms. Uses `compute_governed_ebr` (reserve = 6h lookahead of critical demand only, no solar/wind credit) and the causal NWP forecaster with its native (uncorrected) 1-hour solar-position timing.
- **Fuel:** 10,368.8513 L **(recomputed)**.
- **Unmet total / critical (first-served) / noncritical (Wh):** 1,032,509.69 / 329,350.79 / 703,158.90.
- **R_CF / R_P (%):** 99.038201 / 97.701459.
- **Diesel-on hours / starts:** 657 / 480. **Min SOC %:** 39.21.
- **Gates:** not applicable to itself (it is the reference, not a candidate under test).
- **Causality:** causal (forward-looking forecast only; carries the same uncorrected 1h geometry as Arm A, but it is never fed into a reserve decision because `ebr: governed` does not consume solar).
- **Promotion eligibility:** not applicable (baseline).

### Arm A

- **Label:** `LEGACY_REPRODUCTION — KNOWN TIMESTAMP DEFECT`.
- **Implementation vs. Control:** same causal forecaster (`causal_nwp_gamma1`, uncorrected 1h geometry), but switches to `compute_variant_sw_ebr` (reserve nets forecast solar+wind against critical demand) and feeds the forecast solar point into that formula (`ebr_solar: "forecast_point"`). [`scripts/run_three_arm_2024.py:62-83`](scripts/run_three_arm_2024.py#L62-L83)
- **Fuel:** 8,877.0390 L **(recomputed)**. **Saving:** 14.387440% **(recomputed)** — independently reproducible from frozen telemetry.
- **Unmet total / critical (first-served) / noncritical (Wh):** 909,623.60 / 278,723.00 / 630,900.60.
- **R_CF / R_P (%):** 99.186049 **(recomputed)** / 97.957128.
- **Diesel-on hours / starts:** 563 / 359. **Min SOC %:** 20.00.
- **Per-origin:** 28/123 origins (22.8%) use *more* fuel than Control **(recomputed)**; mean saving 12.128555 L/origin.
- **S1/S2/S3 PASS:** true/true/true. **S4_point PASS** (31 worse, 43 equal, 49 better). **S4_strict PASS** (bootstrap upper bound −269.16 Wh/origin ≤ 0).
- **E1 (statistical):** `EVALUATED: true`, `PASS: true` (Wilcoxon p = 8.24×10⁻¹⁴, Holm-adjusted, family size 2).
- **`in_E1_family`:** true. **`causal`:** true.
- **Reason for ineligibility despite passing gates:** `promotion_eligible: false` — by design, because of the documented 1-hour solar-position timestamp defect in the forecaster it relies on (see Arm A_FIX for the isolated effect of that defect).
- **Limitation:** the 14.39% figure is partly attributable to the uncorrected geometry defect, not solely to the EBR-formula change — see the A_FIX comparison and `reports/FORENSIC_INVESTIGATION_ARM_A_ARM_B_2026-10-11.md` §3/§6.

### Arm A_FIX

- **Label:** `DIAGNOSTIC — NOT PROMOTION-ELIGIBLE`.
- **Implementation vs. Control:** identical to Arm A, with one change — the forecaster's solar-position calls are wrapped by `LabelCorrectedLocation`, shifting pvlib's clock by −1h to correct the label/UTC mismatch. [`scripts/solar_convention.py`](scripts/solar_convention.py); applied at [`scripts/run_three_arm_2024.py:235-237`](scripts/run_three_arm_2024.py#L235-L237). Nothing else differs from Arm A.
- **Fuel:** 9,204.2447 L. **Saving:** 11.231780%.
- **Unmet total (Wh):** 1,317,586.64. Critical (first-served): 484,814.38. Noncritical: 832,772.26.
- **R_CF / R_P (%):** 98.584202 / 97.117253.
- **Diesel-on hours / starts:** 572 / 375. **Min SOC %:** 20.00.
- **S1 PASS:** **false** (dR_CF = −0.454 pp). **S2 PASS:** **false** (dR_P = −0.584 pp). **S3 PASS:** true.
- **S4_point:** **false** (80 worse, 13 equal, 30 better vs. Control). **S4_strict:** **false** (upper bound +3,350.92 Wh/origin > 0).
- **`reliability_gates_PASS`:** **false**. **`in_E1_family`:** false (no E1 block; `NOT AVAILABLE`).
- **`causal`:** true. **`promotion_eligible`:** false.
- **Explicit framing — do not present A_FIX as a successful replacement for A.** Correcting the timestamp defect *reduces* the reported fuel saving (14.39% → 11.23%) and simultaneously exposes material reliability regressions (S1, S2, S4 point and strict all fail; `reliability_gates_PASS: false`) that Arm A's biased forecast had partly masked. A_FIX exists to isolate the defect's effect, not to serve as a cleaner Arm A.
- **Known incompleteness:** A_FIX is not in the E1 statistical family, so it has no Wilcoxon/BCa block — its per-origin statistical detail is less complete than Arm A's or Arm B's. This is a genuine evidence gap, not an oversight in this document.

### Arm B

- **Label:** `NONCAUSAL — DIAGNOSTIC — NOT DEPLOYABLE`.
- **Implementation vs. Control:** same `compute_variant_sw_ebr` reserve formula as A, but the solar term fed into it (and into the planner) is the **realized SITES SW_IN measurement** for the entire 24h forecast horizon at each decision point — not a forecast. [`scripts/run_three_arm_2024.py:262-270`](scripts/run_three_arm_2024.py#L262-L270); the rebuilt forecast bundle is explicitly tagged `"status": "NONCAUSAL_PERFECT_FORESIGHT_DIAGNOSTIC_ONLY"` in code.
- **Fuel:** 6,758.5723 L **(recomputed)**. **Saving:** 34.818505% **(recomputed)** — independently reproducible from frozen telemetry.
- **Unmet total (Wh):** 975,519.58 **(recomputed)**. **Critical unmet:** 0.0 (R_CF = 100.000% **(recomputed)**). **Noncritical unmet:** 975,519.58 Wh — i.e., all of Arm B's unmet energy is noncritical.
- **R_P (%):** 97.840638.
- **Diesel-on hours / starts:** 450 / 264. **Min SOC %:** 20.00.
- **Per-origin:** 75/123 origins worse than Control on total unmet energy, 48 better, 0 tied **(recomputed, matches `S4_point`)**.
- **S1/S2/S3 PASS:** true/true/true (both are point-service-rate checks that Arm B, with perfect critical service, passes).
- **S4_point PASS:** true (nominal; the point rule is satisfied in aggregate). **S4_strict PASS:** **false** — bootstrap upper bound on the mean paired delta = **+1,862.30 Wh/origin > 0**.
- **`reliability_gates_PASS`:** **false**. **`in_E1_family`:** false (noncausal arms are never in the family; `NOT AVAILABLE`).
- **`causal`:** **false**. **`promotion_eligible`:** false (and never eligible, by design — the label states this explicitly).
- **Why the large pooled saving does not override noncausality or the failed strict test:** Arm B's EBR input is information that does not exist at real decision time (future realized solar). Even with that oracle information, the paired per-origin comparison shows a majority of origins (61%) performing worse than Control on total unmet energy, concentrated in a heavy tail (11,600–13,900 Wh lost at the worst five origins) — exactly the failure mode the strict paired bootstrap test exists to catch. A pooled/mean-level improvement is not sufficient evidence of a safe policy; the per-origin distribution matters, and here it fails the project's own pre-registered criterion. Arm B must never be treated as a deployable champion regardless of its percentage.

### Arm C

- **Label:** `RESEARCH-ONLY CANDIDATE — NOT PROMOTION-ELIGIBLE (CALIBRATED POINT + LOWER-BOUND RESERVE)`.
- **Implementation vs. Control:** `compute_variant_sw_ebr` reserve, fed by a calibrated point forecast (`calibrated_gamma_hat_point`) for the planner and a calibrated lower-bound quantile for the EBR reserve (`ebr_solar: "calibrated_lower_bound"`), using the validated calibration artifact (`calibration/ARM_C_CALIBRATION.json`, SHA-256 `0fd914dd...3d70e0`, bound in this run's `RUN_STATUS.json`). [`scripts/run_three_arm_2024.py:271-299`](scripts/run_three_arm_2024.py#L271-L299)
- **Fuel:** 7,702.5780 L. **Saving:** 25.714259%.
- **Unmet total (Wh):** 2,698,158.14. **Critical (first-served):** 1,141,296.75. **Noncritical:** 1,556,861.39.
- **R_CF / R_P (%):** 96.667085 / 93.944196 — the lowest reliability of all five arms.
- **Diesel-on hours / starts:** 529 / 325. **Min SOC %:** 20.00.
- **Per-origin:** 109/123 origins worse than Control, 11 better, 3 tied.
- **S1 PASS:** **false** (dR_CF = −2.371 pp). **S2 PASS:** **false** (dR_P = −3.757 pp). **S3 PASS:** true.
- **S4_point PASS:** **false**. **S4_strict PASS:** **false** (upper bound +16,121.84 Wh/origin > 0 — the largest regression of any arm).
- **`reliability_gates_PASS`:** **false**.
- **E1 (statistical):** the underlying fuel-saving statistic passes (`E1_STAT_PASS: true`, Wilcoxon p = 4.46×10⁻²⁰), but `E1.EVALUATED: false` and the arm's overall verdict is `"NOT AN IMPROVEMENT (reliability gate failed or not evaluable)"`. This is the clearest illustration in this run of why a passing fuel statistic does not imply eligibility: C's statistic passes, but the arm is blocked by its reliability-gate failure before that statistic can be acted on.
- **`in_E1_family`:** true (fuel statistic evaluated for the family even though the overall arm is not an improvement). **`causal`:** true. **`promotion_eligible`:** false.
- **Note:** Arm C's reliability failure is driven primarily by critical unmet energy (1,141,296.75 Wh, nearly 4× Control's 329,350.79 Wh) — a different failure mode from Arm B's, whose unmet energy is entirely noncritical. Do not conflate the two arms' reliability failures as the same phenomenon.

---

## D. Shared mechanism and scientific interpretation

- The single largest observed difference between Control and every other arm (A, A_FIX, B, C) is the EBR reserve formula: `compute_governed_ebr` (Control) vs. `compute_variant_sw_ebr` (all candidates) — netting forecast solar/wind against the 6-hour critical-demand reserve target. [`stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py:125-227`](../stage4_sw_low_sun_2025_holdout/stage4_low_sun_adapter.py#L125-L227)
- **This is a reserve-policy/control-design difference, not proof of better forecast accuracy.** The same formula is used by both causal arms (A, A_FIX, C) and the noncausal arm (B); the magnitude of the fuel saving each arm reports depends on how good (or how illegitimate) the solar term fed into that shared formula is, not on the formula itself.
- **Arm A** uses a causal forecast with a known timing defect (1h solar-position misalignment from a UTC/UTC+1 label mismatch). This is still forward-looking information, just miscalculated.
- **Arm B** uses future realized solar and is noncausal — information that cannot exist at real decision time.
- **Arm A and Arm B must not be treated as equivalent evidence.** A's defect is a fixable implementation bug inside a legitimate forecasting approach (A_FIX demonstrates the fix); B's defect is definitional — there is no "fix" for perfect foresight that preserves its causal validity, because removing the foresight removes the arm's entire premise.
- Identical realized conditions and initial states across all five arms (verified: `actual_demand`, `actual_wind`, `critical_demand`, realized `actual_solar`, `timestamp`, and hour-0 `soc_before` are each single-valued across arms when pivoted by `(origin_id, hour)`) support a fair, apples-to-apples comparison of reserve policies and forecast inputs — but this parity does not make a noncausal input (Arm B) operationally valid. Parity establishes that the *comparison* is fair; it does not establish that any individual arm's input is realizable in deployment.

---

## E. Failure and limitation register

| ID | Candidate/subsystem | Finding | Severity/consequence | Status | Evidence reference | Implications | Next safe action |
|---|---|---|---|---|---|---|---|
| F1 | Arm A | 1-hour solar-position timestamp defect (UTC label actually UTC+1) inflates reported saving | Medium — ~3.16 pp (≈22% relative) of the 14.39% figure is not attributable to the EBR-formula change alone | **Confirmed** (code-level defect; magnitude bounded by A vs. A_FIX delta) | `scripts/solar_convention.py`; A vs. A_FIX in `RESULTS.json` | A's 14.39% should not be quoted without this caveat | Backlog item 1 (offline per-hour reconstruction) |
| F2 | Arm A | 28/123 origins (22.8%) use more fuel than Control despite a positive pooled saving | Low-medium — saving is not universal across days | **Confirmed** (recomputed from telemetry) | `HOURLY_TELEMETRY.csv`, per-origin `diesel_fuel` sums | Pooled percentage alone overstates consistency | Backlog item 1 |
| F3 | Arm A_FIX | S1, S2, S4 (point and strict) all fail; `reliability_gates_PASS: false` | High — correcting the known defect exposes reliability regressions Arm A's bias had masked | **Confirmed** | `RESULTS.json` arms.A_FIX | A_FIX must not be read as a safer Arm A | None proposed — diagnostic result, informs F1 only |
| F4 | Arm B | Noncausal input: realized SITES SW_IN used as the solar forecast for the full future horizon | High (definitional) — the arm's entire premise is unrealizable at decision time | **Confirmed** (by code and by the arm's own explicit `NONCAUSAL_PERFECT_FORESIGHT_DIAGNOSTIC_ONLY` tag) | `scripts/run_three_arm_2024.py:262-270` | 34.82% must never be read as a deployable saving | None — diagnostic by design, not intended to be fixed |
| F5 | Arm B | `S4_strict` fails; 75/123 origins worse than Control on total unmet energy despite a lower pooled total | High | **Confirmed** (recomputed) | `RESULTS.json` arms.B.S4_strict; per-origin recompute | Pooled improvement can hide majority-of-origins regressions | Backlog item 2 (trace EBR/dispatch for worst B origins) |
| F6 | Arm C | Reliability gates fail across the board (S1, S2, S4 point+strict); 109/123 origins worse; critical unmet ≈4× Control | High | **Confirmed** | `RESULTS.json` arms.C | C's 25.71% fuel saving is not an improvement under the full gate set, despite C's own fuel statistic passing | None proposed in this document; any further work on C needs its own scoping |
| F7 | A_FIX | Incomplete statistical block — no E1/Wilcoxon/BCa data (not in E1 family) | Low — limits direct per-origin variance comparison to A and B | **Unresolved** (structural, not a bug) | `RESULTS.json` arms.A_FIX (absent E1 key) | Comparisons involving A_FIX's statistical significance are not possible with current artifacts | Would need a new, separately authorized evaluation if ever required |
| F8 | All arms | No per-row solar-forecast-error or EBR-component-decomposition column in telemetry | Medium — limits mechanistic attribution to aggregate deltas | **Unresolved** (artifact gap) | `HOURLY_TELEMETRY.csv` schema | Hour-by-hour causal chain from forecast bias to dispatch outcome cannot be fully reconstructed | Backlog items 1–2 |
| F9 | Arm A, Arm B | Inability to fully attribute each reserve decision to each dispatch outcome without further intermediate evidence | Medium | **Unresolved**, labeled **hypothesis** where mechanism is proposed (e.g., B's regression concentration, A's worst-origin weather signature) | `reports/FORENSIC_INVESTIGATION_ARM_A_ARM_B_2026-10-11.md` §7 | Current mechanistic claims beyond the aggregate deltas are plausible, not established | Backlog items 1–3 |

---

## F. Governance and decision record

- **Final winner:** `null` (`RESULTS.json` `winner: null`, `winner_note: "No arm in EXP-THREE-ARM-2024 is promotion-eligible; a winner change needs a separate governance decision."`).
- **No candidate is promotion-eligible.** PC-Control is the baseline (not a candidate). A, A_FIX, B, C all report `promotion_eligible: false`.
- **No governance decision was changed by this investigation or by this documentation pass.** This knowledge base and the forensic report are read-only analyses and a documentation record; they carry no authority to alter D10, D10a, the winner field, or any gate threshold.
- **Arm B is never to be treated as a deployable champion**, regardless of its 34.82% figure, because its input is noncausal (unrealizable at decision time) and it fails the strict paired reliability test.
- **Arm A is research-only** because of its documented, partially-quantified timestamp defect and its `promotion_eligible: false` status — not because its statistics failed (they passed).
- **Any follow-up requiring optimization, solver replay, or operational execution requires its own, separately scoped execution authorization.** Nothing in this document, the forensic report, or the backlog in §G constitutes or implies such an authorization.
- **No R5 work is in scope** of this experiment, this investigation, or this documentation pass.
- This document does not manufacture approvals and does not authorize any future execution.

---

## G. Research backlog (proposals only — nothing in this section has been executed)

Ordered by information value, smallest/safest first:

1. **[UNEXECUTED PROPOSAL]** Offline-only reconstruction of forecast-vs-realized solar error, computed on a *copy* of the frozen telemetry (never the original), with particular attention to Arm A's 28 fuel-regression origins. No solver, no new authorization needed — pure arithmetic on already-frozen data.
2. **[UNEXECUTED PROPOSAL]** Trace the EBR reserve target and dispatch decisions for selected origins (Arm A's worst fuel-regression origins; Arm B's worst S4 regression origins — 12, 122, 49, 107, 55) using only existing artifacts, if they support it without executing a solver.
3. **[UNEXECUTED PROPOSAL]** Only if (1) and (2) prove insufficient: propose a separately authorized, narrowly scoped diagnostic replay (not an evaluation run) of specific origins. This is a proposal to seek authorization for, not an instruction to perform — no replay has been run, and none should be run without its own explicit, separately scoped execution authorization.

---

## Detailed investigation report

The full forensic analysis (methodology, exact reproduction steps, formulas, and additional per-arm detail) is preserved separately to avoid duplicating it here: [`reports/FORENSIC_INVESTIGATION_ARM_A_ARM_B_2026-10-11.md`](reports/FORENSIC_INVESTIGATION_ARM_A_ARM_B_2026-10-11.md).

CSV telemetry contents are not duplicated into Markdown anywhere in this knowledge base or the forensic report; all telemetry-derived figures above were computed directly from `HOURLY_TELEMETRY.csv`/`EXECUTED_HOUR_TELEMETRY.csv` and are cited by column/field name, not reproduced as raw data.
