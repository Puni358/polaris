# POLARIS — Nonlinear Cloud→GHI Correction: Research Protocol & Authorization Record

**Status:** Protocol finalized for a research-only validation comparison. **Validation has NOT been executed.** **Blind evaluation is NOT authorized.**
**Date recorded:** 2026-10-10
**Scope:** This record governs exactly one experiment — the nonlinear cloud-cover-to-GHI correction candidate below, applied only to the research evaluation of PC-SW's existing solar-forecast pathway (`system/forecasting/implementations/causal_nwp_physics.py`, unmodified). It does not authorize any other experiment, model, or production/EMS/control action.

This is the first and only repository record found or created for this experiment: a repository-wide search (prior task in this investigation) for any existing document naming this candidate, its formula, or this training/validation/blind split returned zero matches. No duplicate record exists.

---

## 1. Finalized protocol

**Baseline:** `GHI_base = clear_sky_GHI * (1 - cloud_fraction)`
**Candidate:** `GHI_candidate = clear_sky_GHI * (1 - cloud_fraction)^gamma`
**Training dataset:** `data/POLARIS_v0_1_future_weather_forecasts_2024.csv` (347 origins, 2024-01-20 to 2024-12-31 — verified clean: zero missing values, zero duplicate rows, zero out-of-range `fc_cloud_cover`, zero negative `actual_SW_IN`, in a prior read-only audit in this investigation)

| Setting | Value |
|---|---|
| Gamma search grid | `[0.10, 1.00]`, step `0.01` |
| Selection objective | Minimize daylight MAE |
| Daylight condition | `solar_elevation > 0` AND `clear_sky_GHI > 0` (identical to the existing governed night-zero rule) |
| Bootstrap method | Stationary bootstrap (dependence-aware; justified by a 2024-training-only diagnostic in this investigation showing significant day-to-day residual autocorrelation through at least lag-4, ruling out simple i.i.d. origin-day cluster bootstrap) |
| Mean block length | 10 days |
| Resampling unit | Origin-day |
| Seed | `20261010` |
| Confidence interval | **Percentile bootstrap interval** — replaces the earlier-proposed BCa method, because BCa's bias/acceleration correction is not well-defined for dependent (block/stationary) resamples; this record documents the percentile interval as the **chosen protocol method**, not as a claim that its coverage properties have been empirically validated for this dataset — that validation, if ever needed, is separate future work, not performed here or implied by this choice |
| Minimum subgroup size | 20 origin-days; subgroups below this are reported as `NOT EVALUATED`, never silently passed or failed |
| Primary success criterion | The 95% confidence interval of (candidate MAE − baseline MAE) lies **entirely** below zero |
| Practical improvement margin | None additional — no minimum effect-size threshold beyond the criterion above |

**Training-only result already on record** (prior task in this investigation, 2024 data only, no validation/blind data touched): baseline (`γ=1`) daylight MAE = 96.75 W/m²; grid-minimum training MAE = 70.94 W/m² at `γ=0.26`. **This is a training-set fact only — it is not a validation result and is not treated as evidence of out-of-sample improvement.**

---

## 2. Project-lead validation authorization

Recorded verbatim, attributed to the project lead for this research project, not to any invented or external authority:

> "I authorize a research-only validation comparison of the frozen Cloud→GHI candidate against the baseline on the 242 non-blind 2025 forecast origins, subject to verifying that I have the right to use these data and that no applicable dataset, institutional, supervisory, or other external restriction prohibits this use."

**This authorization is conditional, not absolute.** A prior task in this investigation searched the repository for any document establishing data-use restrictions, licenses, or required external sign-off governing the 242 non-blind-2025 origins or the 123-origin blind population, and found none — but explicitly reported this as `UNKNOWN — NOT VERIFIED`, not as proof that no such restriction exists. **That status is unchanged by this record.** This authorization does **not** itself resolve the data-rights question; it records the project lead's conditional willingness to proceed *once* that question is independently settled.

**This record does not authorize:** production deployment, EMS or control-system action, or any access to the protected 123-origin blind population.

---

## 3. Protected blind population — unconditionally excluded

The 123-origin period 2025-05-01 through 2025-08-31 remains excluded from this authorization in every respect:
- No outcome value may be read or queried.
- No metric may be calculated on it.
- `gamma` may not be fit or tuned using it.
- It may not be used for debugging or model selection.
- **It is not unlocked by §2's non-blind validation authorization.** Any future blind evaluation requires its own, separate, explicit project-lead decision, made only after the non-blind validation protocol has run and its results are finalized — never inferred from this record.

---

## 4. Unresolved items (carried forward, not resolved by this record)

- Whether the project lead in fact holds the data-use rights referenced conditionally in §2 — `UNKNOWN`.
- Whether any applicable dataset license, institutional policy, or supervisory requirement restricts use of the 242 non-blind-2025 origins — `UNKNOWN`, not found in repository search, absence not treated as confirmation.
- The percentile bootstrap interval's empirical coverage for this specific dataset has not been separately validated (§1) — not required before proceeding, but not claimed either.

---

## 5. Explicit exclusions from this record

- No validation comparison was run in producing this record.
- No 2025 outcome value (blind or non-blind) was read, queried, or computed on.
- No `gamma` fitting beyond the already-recorded 2024 training-only result (§1) occurred.
- No production code, forecasting implementation, model artifact, EMS, or control logic was modified.
- No external authority, approver, or institutional sign-off is claimed anywhere in this record.
