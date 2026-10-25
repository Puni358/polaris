# POLARIS Phase 10 — Final Closure Checkpoint

**Date:** 2026-09-14  
**Status:** `PHASE10_CLOSED_ALL_CANDIDATES_REJECTED`  
**Protected Champion:** Stage 8.1 37-feature HGB — **UNCHANGED / NOT MODIFIED**  
**ODD Firewall:** **INTACT / UNTOUCHED** — Zero ODD rows loaded, evaluated, or accessed by any candidate.

---

## 1. Executive Summary & Objective

Phase 10 was conducted to evaluate whether learning complex neural architecture representations (temporal sequence modeling, shared multi-horizon embeddings, or disagreement-gated residual corrections) on top of the frozen Stage 8.1 37-feature set could yield statistically robust improvements over the protected Stage 8.1 HGB champion baseline.

All three candidate architectures were rigorously evaluated under the locked Phase 10 EVEN-only cross-validation firewall protocol:
1. **Candidate A (BiGRU Temporal Sequence Model)** — **REJECTED ON EVEN**
2. **Candidate B (Shared MLP + 24-Horizon Embedding)** — **REJECTED ON EVEN**
3. **Candidate C (Disagreement-Gated Residual MLP)** — **REJECTED ON EVEN**

No candidate met the locked pass criteria (Gates G1–G6). Under the strict Phase 10 protocol:
- No candidate earned authorization for ODD evaluation.
- No rescue variants (A.1, B.1, C.1) are permitted.
- The official Stage 8.1 37-feature HGB champion remains unchanged and protected.
- **Phase 10 architecture research is formally CLOSED.**

---

## 2. Locked Phase 10 Protocol & Evaluation Firewall

Every experiment in Phase 10 adhered strictly to the locked governance protocol:

1. **Protected Champion:** The Stage 8.1 37-feature HGB champion remains the official baseline and is not modified or replaced.
2. **Absolute ODD Firewall:** ODD origins (174 origins / 4,176 rows) are completely firewalled and inaccessible during candidate development and evaluation.
3. **EVEN-Only Evaluation:** Development and out-of-fold (OOF) scoring are conducted exclusively on EVEN origins (173 origins / 4,152 rows).
4. **No Feature Modifications:** All models use the exact 39-column feature matrix (14 static + 25 horizon-varying) established in Stage 8.1.
5. **No Hyperparameter Sweeping:** Hyperparameters were frozen prior to inspection of OOF results; no tuning sweeps were permitted.
6. **Locked Gates (G1–G6):**
   - **G1:** Aggregated ΔMAE ≤ −0.50 W/m² (vs. control)
   - **G2:** Folds improved ≥ 4/5
   - **G3:** Maximum fold degradation ≤ +0.50 W/m²
   - **G4:** Candidate nMAE ≤ control nMAE AND Candidate RMSE ≤ control RMSE
   - **G5:** Causal availability & data parser compliance
   - **G6:** Exact control reproduction against locked reference
7. **No Rescue Variants:** Upon rejection of a primary candidate, no sub-variants (C.1, C.2, etc.) are allowed.
8. **No Unauthorized ODD Access:** ODD evaluation is strictly prohibited for any rejected candidate.

---

## 3. Candidate A — Final Status: REJECTED ON EVEN

### 3.1 Overview & Architecture
Candidate A evaluated a temporal sequence regressor designed to model cross-horizon dependencies across the 24-hour forecast window.
- **Architecture:** `Dense(39->32, ReLU)` → `Dropout(0.2)` → `BiGRU(hidden=16 per dir)` → `Dropout(0.2)` → `Dense(32->1, linear)`
- **PyTorch Parameter Count:** **6,113**
- **Note on Experiment Validity:** An initial prototype attempt using a flattened `sklearn` MLP proxy was invalidated during audit. The valid experiment reported here was executed with standard PyTorch `nn.GRU` preserving the exact `[batch, 24, 39]` sequence structure.

### 3.2 EVEN-OOF Results (5-Fold GroupKFold)
- **Aggregate OOF MAE:** **54.7022 W/m²**
- **Aggregate OOF RMSE:** **126.5499 W/m²**

| Fold | Test Origins | MAE (W/m²) | RMSE (W/m²) | Bias (W/m²) |
|---:|---:|---:|---:|---:|
| 1 | 35 | 53.0343 | 122.1581 | −45.9053 |
| 2 | 35 | 46.8871 | 111.8654 | −37.1397 |
| 3 | 35 | 45.4633 | 108.1309 | −38.7683 |
| 4 | 34 | 69.3759 | 151.2010 | −60.8768 |
| 5 | 34 | 59.3008 | 135.4479 | −51.0647 |

### 3.3 Gate Verdict
- **G1 (ΔMAE ≤ −0.50):** **FAIL** (Aggregate MAE 54.70 W/m² vs control ~26.37 W/m²)
- **G2 (Folds Improved ≥ 4/5):** **FAIL** (0/5 folds improved)
- **G3 (Max Degradation ≤ +0.50):** **FAIL** (Large degradation across all folds)
- **G4 (nMAE & RMSE ≤ Control):** **FAIL**
- **G5 (Causal Compliance):** **PASS**
- **G6 (Control Reproduction):** Not evaluated (decisively rejected by G1–G4)

**Verdict:** **REJECTED ON EVEN.** ODD was not evaluated. No rescue variants permitted.

---

## 4. Candidate B — Final Status: REJECTED ON EVEN

### 4.1 Overview & Architecture
Candidate B evaluated a joint multi-horizon regressor featuring a shared representation trunk and learned 24-horizon categorical embeddings.
- **Architecture:** Shared MLP (`39->64->32->1`) + 8-dim horizon embedding, trained jointly across all 24 horizons per origin.

### 4.2 EVEN-OOF Results
- **Candidate B:** MAE = **26.0112 W/m²**, RMSE = **54.2820 W/m²**, nMAE = **20.1750%**, Bias = −2.7713 W/m²
- **Reconstructed Control:** MAE = **26.3668 W/m²**, RMSE = **55.2513 W/m²**, nMAE = **20.4507%**, Bias = −0.1291 W/m²
- **Aggregate ΔMAE:** **−0.3556 W/m²**

| Fold | Control MAE | Candidate B MAE | ΔMAE (B − Control) | Improved? |
|---:|---:|---:|---:|:---:|
| 0 | 29.1137 | 27.0406 | −2.0731 | **Yes** |
| 1 | 22.8351 | 24.0944 | **+1.2593** | No |
| 2 | 25.5086 | 25.6572 | +0.1486 | No |
| 3 | 30.0997 | 28.8913 | −1.2084 | **Yes** |
| 4 | 24.3254 | 24.4093 | +0.0839 | No |

### 4.3 Gate Verdict
- **G1 (ΔMAE ≤ −0.50):** **FAIL** (−0.3556 W/m² did not reach −0.50 threshold)
- **G2 (Folds Improved ≥ 4/5):** **FAIL** (Only 2/5 folds improved)
- **G3 (Max Degradation ≤ +0.50):** **FAIL** (+1.2593 W/m² on Fold 1 exceeded +0.50 threshold)
- **G4 (nMAE & RMSE ≤ Control):** **PASS** (nMAE 20.175% ≤ 20.451%, RMSE 54.282 ≤ 55.251)
- **G5 (Causal Compliance):** **PASS**
- **G6 (Control Reproduction):** **HONESTLY APPROXIMATE** (Reconstructed same-pipeline control, documented as non-exact)

**Verdict:** **REJECTED ON EVEN.** ODD was not evaluated. No rescue variants permitted.

---

## 5. Candidate C — Final Status: REJECTED ON EVEN

### 5.1 Overview & Architecture
Candidate C evaluated a Disagreement-Gated Residual MLP targeting the untested hypothesis from Phase 9 (pairing model disagreement with learned directional residual gating).
- **Architecture:** 
  - Input: 39 standardized features (row-wise, independent)
  - Frozen Anchor: raw `pred_stage4_fold` (unstandardized W/m²)
  - Shared Trunk: `Dense(39->16, ReLU)` → `Dropout(0.2)`
  - Magnitude Head: `Dense(16->1, linear)` → $m(x)$
  - Gate Head: `Dense(16->1, sigmoid)` → $g(x) \in [0, 1]$
  - Applied Correction: $g(x) \times m(x)$
  - Final Output: $\hat{y} = \text{anchor} + (g(x) \times m(x))$
- **PyTorch Parameter Count:** **674** exactly (verified via direct instantiation)
- **Hyperparameters:** Adam lr=1e-3, $\beta=(0.9, 0.999)$, $\epsilon=1\text{e-}7$, weight decay=1e-4, MAE loss, batch=8 origins, max_epochs=300, patience=20, CPU.

### 5.2 Pre-Training Audit (15/15 PASS)
Before training, a 15-point audit was performed and passed cleanly:
1. CSV located correctly at path -> **PASS**
2. 39 features present -> **PASS**
3. 347 total origins present -> **PASS**
4. Split counts (173 EVEN / 174 ODD) -> **PASS**
5. 24 rows per origin -> **PASS**
6. Horizon range 1..24 -> **PASS**
7. 0 NaNs in inputs/targets/anchor -> **PASS**
8. Row-independence verified -> **PASS**
9. Anchor identity (`pred_stage4_fold`) -> **PASS**
10. Additive unscaled anchor path -> **PASS**
11. **Scaler probe EVEN-only isolation:** Probe fit strictly on `even_probe_df`, eliminating ODD feature exposure -> **PASS**
12. Parameter count exactly 674 -> **PASS**
13. Architecture matches frozen specification -> **PASS**
14. No ODD feature values in calculations -> **PASS**
15. **Honest G6 treatment:** Reconstructed control compared against locked reference -> **PASS**

### 5.3 EVEN-OOF Results & Reference Comparisons
- **Candidate C:** MAE = **27.0940 W/m²**, RMSE = **56.1025 W/m²**, nMAE = **21.01%**, Bias = −0.6006 W/m²
- **Paired Reconstructed Control:** MAE = **26.4522 W/m²**, RMSE = **55.2715 W/m²**, nMAE = **20.52%**, Bias = +0.1240 W/m²
- **Locked Prior Reference:** MAE = **26.3668 W/m²**, RMSE = **55.2513 W/m²**, nMAE = **20.4507%**
- **Aggregate ΔMAE (vs. Paired Control):** **+0.6418 W/m²** (worse)

#### Fold-by-Fold Breakdown

| Fold | Candidate MAE | Control MAE | ΔMAE (vs Control) | Candidate RMSE | Candidate nMAE | Candidate Bias | Improved? |
|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | 28.0672 | 29.1246 | **−1.0574** | 58.7187 | 22.14% | −1.1934 | **Yes** |
| 2 | 24.4340 | 22.3244 | **+2.1096** | 51.5253 | 21.25% | +3.8746 | No |
| 3 | 27.0914 | 26.6015 | +0.4899 | 57.4712 | 22.91% | +2.4879 | No |
| 4 | 30.6395 | 29.7559 | +0.8836 | 60.2090 | 20.19% | −11.6241 | No |
| 5 | 25.2875 | 24.4930 | +0.7945 | 52.0357 | 18.99% | +3.2470 | No |

### 5.4 Gate Verdict
- **G1 (ΔMAE ≤ −0.50):** **FAIL** (+0.6418 W/m² vs control)
- **G2 (Folds Improved ≥ 4/5):** **FAIL** (Only 1/5 folds improved)
- **G3 (Max Degradation ≤ +0.50):** **FAIL** (+2.1096 W/m² on Fold 2 exceeded +0.50 threshold)
- **G4 (nMAE & RMSE ≤ Control):** **FAIL** (nMAE 21.01% > 20.52%, RMSE 56.1025 > 55.2715)
- **G5 (Causal Compliance):** **PASS**
- **G6 (Exact Control Reproduction):** **FAIL / UNVERIFIED** (Reconstructed control MAE 26.4522 / RMSE 55.2715 vs locked reference MAE 26.3668 / RMSE 55.2513 exceeded 1e-3 tolerance)

**Verdict:** **REJECTED ON EVEN.** ODD was not accessed. No rescue variants permitted.

---

## 6. Comprehensive Gate Comparison Matrix

| Gate | Protocol Requirement | Candidate A | Candidate B | Candidate C | Protocol Status |
|---|---|---|---|---|---|
| **G1** | Aggregated ΔMAE ≤ −0.50 W/m² | FAIL (+28.23) | FAIL (−0.3556) | FAIL (+0.6418) | **ALL FAILED** |
| **G2** | Folds improved ≥ 4/5 | FAIL (0/5) | FAIL (2/5) | FAIL (1/5) | **ALL FAILED** |
| **G3** | Max fold degradation ≤ +0.50 W/m² | FAIL (> +20.0) | FAIL (+1.2593) | FAIL (+2.1096) | **ALL FAILED** |
| **G4** | Candidate nMAE & RMSE ≤ Control | FAIL | PASS | FAIL | **A & C FAILED** |
| **G5** | Causal & Data Compliance | PASS | PASS | PASS | **ALL PASSED** |
| **G6** | Exact Control Reproduction | N/A (Failed G1–G4) | Honest Approx | FAIL / UNVERIFIED | **UNRESOLVED / UNNEEDED** |
| **VERDICT** | **All EVEN Gates Pass** | **REJECTED** | **REJECTED** | **REJECTED** | **ALL REJECTED** |

---

## 7. ODD Firewall Audit & Verification

- **ODD Access Audit:** **0 ODD rows accessed across Candidates A, B, and C.**
- **Verification:**
  1. Candidate A loaded data strictly filtered by `split == 'EVEN'`.
  2. Candidate B loaded data strictly filtered by `split == 'EVEN'`.
  3. Candidate C script audit check #11 verified that probe fitting was restricted to `even_probe_df`, and audit check #14 verified `even_df_probe['split'].eq('EVEN').all()`.
- **Conclusion:** The ODD firewall remained 100% intact throughout Phase 10.

---

## 8. Protected Champion Baseline

The official champion remains untouched and preserved as the scientifically reproducible baseline:

- **Champion Model:** Stage 8.1 37-feature HistGradientBoostingRegressor
- **Official ODD Benchmark Metrics:**
  - **MAE:** **36.188657 W/m²**
  - **nMAE:** **28.0688%**
  - **RMSE:** **64.219495 W/m²**
  - **Bias:** **+1.439399 W/m²**
  - **Night MAE:** **0.0000 W/m²**
- **Prediction Artifact:** [`stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/stage7/stage8/stage8_1_700hpa_wind/stage8_1_official_odd_predictions.csv)
- **Prediction Artifact SHA256:** `213a71e132f51ed5673634d42f61d8bf2b26386ccfad358aca8bc3704d18d707`

This champion was **NOT** modified, re-trained, or replaced by Phase 10.

---

## 9. Final Phase 10 Conclusion

**Phase 10 architecture research is formally CLOSED.**

All three candidate architectural paradigms (temporal sequence modeling, shared multi-horizon embeddings, and disagreement-gated residual corrections) failed to satisfy the locked EVEN gate criteria.

### Scientific Finding
No robust architecture-level improvement was demonstrated under the locked Phase 10 protocol. The tree-based tabular champion (Stage 8.1 37-feature HGB) continues to outperform or match all tested neural architecture formulations on this dataset.

### Governance Directives
1. No candidate achieved EVEN gate passage; therefore, **ODD evaluation is NOT authorized for any candidate**.
2. **No rescue variants (A.1, B.1, C.1, etc.) or hyperparameter tuning sweeps are authorized.**
3. The official Stage 8.1 37-feature HGB champion remains the active, protected system champion.

---

## 10. Artifact & Provenance Registry

1. [`PHASE10_FINAL_CLOSURE_CHECKPOINT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/PHASE10_FINAL_CLOSURE_CHECKPOINT.md) — Main closure report (this document)
2. [`PHASE10_FINAL_CLOSURE_CHECKPOINT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/PHASE10_FINAL_CLOSURE_CHECKPOINT.json) — Machine-readable closure record
3. [`PHASE10_CANDIDATE_A_FINAL_REJECTION_CHECKPOINT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/PHASE10_CANDIDATE_A_FINAL_REJECTION_CHECKPOINT.md) — Candidate A rejection record
4. [`PHASE10_CANDIDATE_B_FINAL_REJECTION_CHECKPOINT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/PHASE10_CANDIDATE_B_FINAL_REJECTION_CHECKPOINT.md) — Candidate B rejection record
5. [`PHASE10_CANDIDATE_C_DESIGN_CHECKPOINT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/forecasting/spatial_arome_research/PHASE10_CANDIDATE_C_DESIGN_CHECKPOINT.md) — Candidate C design checkpoint
6. [`PHASE10_CANDIDATE_C_AUDIT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/PHASE10_CANDIDATE_C_AUDIT.json) — Pre-training 15-check audit log
7. [`phase10_candidate_c_train.py`](file:///home/punith-bs/01polaris%20%28Copy%29/phase10_candidate_c_train.py) — Validated Candidate C audit/training script
