# POLARIS STAGE 8.7 — FINAL CLOSURE AND FREEZE REPORT

## 1. Executive Summary & Final Status

Stage 8.7 evaluated the physical feasibility, proxy integrity, and predictive performance of the **Causal MEPS DNI-Anchored Direct/Diffuse Two-Head Target Architecture**.

### Final Status Classifications

| Metric / Phase | Status / Result |
| :--- | :--- |
| **8.7A Feasibility Audit** | **PASS** (100% data coverage, 8328/8328 tuples, 347/347 origins) |
| **8.7A Proxy Governance** | **APPROVED** (Formula independently reviewed & prospectively frozen) |
| **8.7B Architecture Test** | **REJECTED** (Failed G1, G2, G3, G4 on EVEN CV) |
| **OVERALL STAGE 8.7** | **CLOSED_REJECTED** |

---

## 2. Comprehensive Experimental Summary

### Stage 8.7A — Feasibility & Physical Proxy Freeze
- **Physical Feasibility:** MEPS DNI values were verified as 100% causally available across all 347 forecast origins without future data leakage.
- **Approved & Frozen Direct Solar Proxy Equation:**
  $$\text{DirectProxy}_h = \text{DNI}_h \times \max(0, \sin(\gamma_{s, h})) \times (1 - \text{terrain\_solar\_obstruction\_flag}_h)$$
- **Terrain Flag Integrity Audit:** PASSED (Verified 360° azimuth-resolved Copernicus 30m DEM horizon ray-marching out to 25 km).
- **Solar Elevation Timestamp Audit:** PASSED (Verified top-of-hour CET convention matching MEPS DNI hourly averages).
- **Implementation Version Hash:** `a7f3e891c94b20d3671f845d098e21a44e5f7b88`.

### Stage 8.7B — 5-Fold Forward-Chaining EVEN CV
- **Control Model:** Stage 8.1 37-Feature Champion (EVEN CV MAE: **37.620054 W/m²**).
- **Candidate Model:** Direct/Diffuse Two-Head Architecture (EVEN CV MAE: **49.445841 W/m²**).
- **Performance Delta:** **+11.825787 W/m²** MAE degradation.
- **Fold-level Breakdown:**
  - Fold 1: Control 49.311419 vs Candidate 77.333445 (+28.022026 W/m²) — DEGRADED
  - Fold 2: Control 70.568800 vs Candidate 79.536802 (+8.968001 W/m²) — DEGRADED
  - Fold 3: Control 40.345573 vs Candidate 59.864250 (+19.518677 W/m²) — DEGRADED
  - Fold 4: Control 25.770418 vs Candidate 28.184598 (+2.414180 W/m²) — DEGRADED
  - Fold 5: Control 2.104058 vs Candidate 2.310108 (+0.206050 W/m²) — DEGRADED
- **Folds Improved:** **0 / 5**
- **Gate Evaluation:**
  - **G1 (Delta MAE $\le -0.50 \text{ W/m}^2$):** **FAIL** (+11.825787 W/m²)
  - **G2 (Folds Improved $\ge 4/5$):** **FAIL** (0/5)
  - **G3 (Worst Fold Degradation $\le +0.50 \text{ W/m}^2$):** **FAIL** (+28.022026 W/m²)
  - **G4 (nMAE & RMSE $\le$ Control):** **FAIL** (nMAE 46.83% vs 37.97%, RMSE 81.33 vs 60.16 W/m²)
  - **G5 (100% Causality):** **PASS**
  - **G6 (Exact Control Reproduction):** **PASS** (37.620054 W/m² exact match)

---

## 3. Scientific Conclusions

1. **Target Architecture Assessment:**
   The MEPS DNI source is causally available and physically sound for constructing a direct-beam proxy. However, using that DNI information as an anchor for a direct/diffuse two-head target architecture did **not** improve surface GHI forecasting under the locked EVEN cross-validation protocol.

2. **Scope of Conclusion:**
   - This evaluation does **not** claim that DNI is physically useless in atmospheric science.
   - This evaluation does **not** claim that all possible radiation formulations are invalid.
   - The scientific conclusion is strictly limited to the following two empirical findings:
     1. DNI tested as an ordinary added scalar feature was rejected in Stage 7.2.
     2. DNI tested as the physical anchor for the Stage 8.7 direct/diffuse two-head target architecture was rejected here.

---

## 4. No Post-Hoc Rescue Audit

To preserve Stage 8.7 as a rigorous, uncompromised scientific experiment, the following governance constraints were strictly enforced following the Stage 8.7B failure:
- **No alternative proxy formula was tested.**
- **No alternative hyperparameters were tested.**
- **No architecture tuning was performed.**
- **No fold selection was performed.**
- **No horizon cherry-picking was performed.**
- **No ODD tuning was performed.**
- **No ODD result was generated.**

---

## 5. Preservation of Evidence Manifest

All historical artifacts generated across Stage 8.7 remain frozen and preserved under `stage7/stage8/stage8_7_dni_two_head/`:
- `STAGE8_7A_FEASIBILITY_REPORT.md`
- `STAGE8_7A_FEASIBILITY_DECISION.json`
- `STAGE8_7A_GOVERNANCE_REVIEW.md`
- `STAGE8_7A_GOVERNANCE_DECISION.json`
- `STAGE8_7A_PROXY_APPROVAL.md`
- `STAGE8_7A_PROXY_APPROVAL.json`
- `STAGE8_7B_EXPERIMENT_REPORT.md`
- `STAGE8_7B_GATE_DECISION.json`
- `stage8_7b_fold_results.csv`
- `stage8_7b_even_cv_summary.csv`
- `stage8_7b_control_reproduction_audit.json`
- `stage8_7b_causality_audit.json`
- `stage8_7b_leakage_audit.json`
- `stage8_7b_reproducibility_manifest.json`

---

## 6. Official Champion Protection & Final Firewall Verification

- **Current Official Champion:** Stage 8.1 700 hPa Free-Atmosphere Steering Wind Model ($U_{700}, V_{700}$).
  - **Official ODD MAE:** **36.188657 W/m²**
  - **Official ODD nMAE:** **28.0688%**
- **POLARIS Master Handoff:** `POLARIS_MASTER_HANDOFF.md` remains completely untouched.
- **Firewall Verification Metrics:**
  - ODD target reads from Stage 8.7 = `0`
  - ODD predictions from Stage 8.7 = `0`
  - ODD metrics from Stage 8.7 = `0`
  - ODD tuning from Stage 8.7 = `0`
  - `POLARIS_MASTER_HANDOFF.md` modifications = `0`
  - Stage 8.1 champion modifications = `0`

Stage 8.7 is officially **CLOSED AND REJECTED**.
