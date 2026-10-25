# POLARIS — T4 RECONSTRUCTION BLOCKER & AUDIT REPORT

**Date (UTC):** 2026-09-16  
**Target:** T4 — Stage 8.1 Champion Difficulty (`mean |SW_IN_actual - SW_IN_pred_OOF|` over H7–H12)  
**Status:** DROPPED / UNAVAILABLE  

---

## 1. Reason for Blocker

Target T4 requires genuine out-of-fold (OOF) predictions for the frozen Stage 8.1 champion under the matching 5-fold `GroupKFold` split across EVEN forecast origins.

A forensic audit of the POLARIS codebase and artifacts revealed that:
1. **No pre-existing Stage 8.1 EVEN OOF prediction CSV artifact exists** in the repository. The only stored row-level prediction file for Stage 8.1 is `stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv`, which contains ODD held-out test predictions ($N=173$).
2. **Official Stage 8.1 Development CV:** In `run_stage8_1.py`, Stage 8.1 was evaluated using a 5-fold expanding-window / forward-chaining CV split. Under that split, the first 29 EVEN origins were used only for training and were **never predicted out-of-fold**.
3. **Official Stage 8.1 Champion:** For ODD evaluation, the official Stage 8.1 model was fit on **all 174 EVEN origins simultaneously**, producing no EVEN OOF predictions.
4. **Governance Rule:** Per Section 2, Section 5, and Section 10 of the preregistration, in-sample predictions, approximate predictions, or non-matching fold schemes are strictly prohibited. If genuine matching-fold Stage 8.1 EVEN OOF predictions cannot be reconstructed from pre-existing artifacts, **T4 MUST BE DROPPED**.

---

## 2. Governance Impact on Section 9 Decision Rules

- The original preregistered Section 9 decision rule requires at least **2 of 4 targets** to satisfy $\Delta R^2 \ge 0.03$ AND bootstrap 95% CI excluding zero.
- With T4 dropped, only 3 active targets remain (T1, T2, T3).
- **Enforced Governance Constraint:** The 2-of-4 formal hit threshold is **retained without modification**. It is NOT weakened or converted to "2 of 3". Because T4 is unavailable, a formal Section 9 hit cannot be achieved using T1–T3 alone under the 2-of-4 rule.
- Targets T1, T2, and T3 are computed and interpreted diagnostically to evaluate hypotheses M1, M2, and M3.
