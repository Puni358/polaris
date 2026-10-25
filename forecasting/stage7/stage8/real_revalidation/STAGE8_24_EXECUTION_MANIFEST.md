# POLARIS STAGE 8.24 EXPERIMENT — EXECUTION MANIFEST

- **Experiment ID:** `POLARIS_STAGE8_24_GOVERNED_EXPERIMENT`
- **Route Name:** Stage 8.24 Orographic Flow Regime Expansion (`ctx_u_perp` + `ctx_mountain_froude`)
- **Execution Timestamp:** `2026-09-13T16:50:30Z`
- **Specification:** [`STAGE8_OROGRAPHIC_FLOW_REGIME_EXPERIMENT_SPEC.md`](file:///home/punith-bs/.gemini/antigravity/brain/c1ea6e2d-9ca7-4067-9424-926a8be17b43/STAGE8_OROGRAPHIC_FLOW_REGIME_EXPERIMENT_SPEC.md)

---

## 1. Summary Outcome

The governed execution of Stage 8.24 across the 173 EVEN benchmark origins produced the following validation metrics:

- **EVEN Control MAE:** `37.6308 W/m²` (Stage 8.1 37-feature HGB champion)
- **EVEN Candidate MAE:** `38.0280 W/m²` (39 features: 37 + `ctx_u_perp` + `ctx_mountain_froude`)
- **EVEN Delta MAE:** **`+0.3972 W/m²`** (Degraded)
- **Improving Folds:** `1 / 5 folds` (Fold 1: -0.0424 W/m²)
- **Worst Fold Degradation:** `+1.1857 W/m²` (Fold 3)

---

## 2. Gate Verification Audit

- **G1 (MAE Margin <= -0.50 W/m²):** **FAIL** (`+0.3972 W/m²`)
- **G2 (Fold Consistency >= 4/5):** **FAIL** (`1 / 5 folds`)
- **G3 (Worst Fold Tolerance <= +0.50 W/m²):** **FAIL** (`+1.1857 W/m²`)
- **G4 (nMAE & RMSE Non-Degradation):** **FAIL**
- **G5 (Causal Integrity):** **PASS** (100% causal $t_0=00:00\text{ UTC}$)
- **G6 (Control Reproduction):** **PASS** (`37.6308 W/m²`)

---

## 3. Candidate Freeze & Stop Protocol

Because EVEN validation gates failed:
1. **Candidate freeze protocol took effect immediately.**
2. Official ODD evaluation was **NOT** executed (`ODD_RUN = FALSE`).
3. ODD target data remained strictly uninspected (`ODD_TARGET_ACCESS = FALSE`).
4. Final Verdict: **`REJECTED_ON_EVEN`**.
5. The Stage 8.1 37-feature HGB model remains the operational champion.

---

## Final Governance Statement

- **Stage 8.24 REJECTED ON EVEN.**
- **ODD dataset remains 100% untouched.**
- **Stage 8.1 37-feature model remains operational champion (ODD daytime nMAE 28.0688%).**
- **No model changes, master handoff changes, or route registry changes.**
