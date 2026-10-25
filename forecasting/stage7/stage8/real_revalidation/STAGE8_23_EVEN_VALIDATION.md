# POLARIS STAGE 8.23 — EVEN-ONLY VALIDATION REPORT

**Execution Timestamp:** `2026-09-13T11:00:49.548570+00:00`  
**Control Baseline:** Frozen Stage 8.1 37-feature HGB Operational Champion  
**Target Station:** SITES Nuolja (68.362074°N, 18.738752°E)  

---

## 1. EVEN 5-Fold Cross-Validation Metric Summary

| Model / Candidate | Feature Count | EVEN Daytime MAE (W/m²) | Delta MAE vs Control (W/m²) | EVEN Daytime nMAE (%) | Delta nMAE (%) | EVEN Daytime RMSE (W/m²) | Improving Folds (out of 5) | Worst Fold Degradation (W/m²) | Gates Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Control (Stage 8.1)** | **37** | `37.6201` | `0.0000` | `29.2063%` | `0.0000%` | `60.1606` | N/A | N/A | **CONTROL** |
| **Candidate A (LOCAL_STATE)** | **41** | `37.4891` | `-0.1310` | `29.1046%` | `-0.1017%` | `60.0560` | `2 / 5` | `+0.6208` | **FAIL** |
| **Candidate B (CONTRAST)** | **38** | `37.8235` | `+0.2035` | `29.3642%` | `+0.1580%` | `60.3566` | `2 / 5` | `+0.7938` | **FAIL** |
| **Candidate C (COMBINED)** | **42** | `37.7859` | `+0.1659` | `29.3350%` | `+0.1288%` | `60.4381` | `2 / 5` | `+0.9242` | **FAIL** |

---

## 2. Fold-by-Fold Breakdown

| Fold | Control MAE | Candidate A MAE (Delta) | Candidate B MAE (Delta) | Candidate C MAE (Delta) |
| :--- | :--- | :--- | :--- | :--- |
| Fold 1 | `49.3114` | `49.5079` (`+0.1965`) | `49.5323` (`+0.2209`) | `49.8000` (`+0.4886`) |
| Fold 2 | `70.5688` | `68.6986` (`-1.8702`) | `70.1946` (`-0.3742`) | `69.5452` (`-1.0236`) |
| Fold 3 | `40.3456` | `40.9664` (`+0.6208`) | `40.7380` (`+0.3924`) | `41.2698` (`+0.9242`) |
| Fold 4 | `25.7704` | `26.1943` (`+0.4238`) | `26.5642` (`+0.7938`) | `26.2640` (`+0.4936`) |
| Fold 5 | `2.1041` | `2.0783` (`-0.0258`) | `2.0884` (`-0.0156`) | `2.0505` (`-0.0536`) |

---

## 3. Pre-Registered Acceptance Gate Evaluations

### Candidate A (LOCAL_STATE): **FAIL**
- **G1 (MAE Improvement <= -0.50 W/m²):** **FAIL** (`-0.1310 W/m²`)
- **G2 (Fold Consistency >= 4/5 folds):** **FAIL** (`2 / 5 folds improved`)
- **G3 (Worst Fold Degradation <= +0.50 W/m²):** **FAIL** (`+0.6208 W/m²` in Fold 3)
- **G4 (nMAE & RMSE Non-Degradation):** PASS
- **G5 (Causal Integrity):** PASS
- **G6 (Exact Control Reproduction):** PASS

### Candidate B (MOUNTAIN_VALLEY_CONTRAST): **FAIL**
- **G1 (MAE Improvement <= -0.50 W/m²):** **FAIL** (`+0.2035 W/m²`)
- **G2 (Fold Consistency >= 4/5 folds):** **FAIL** (`2 / 5 folds improved`)
- **G3 (Worst Fold Degradation <= +0.50 W/m²):** **FAIL** (`+0.7938 W/m²` in Fold 4)
- **G4 (nMAE & RMSE Non-Degradation):** **FAIL** (`nMAE & RMSE degraded`)
- **G5 (Causal Integrity):** PASS
- **G6 (Exact Control Reproduction):** PASS

### Candidate C (COMBINED): **FAIL**
- **G1 (MAE Improvement <= -0.50 W/m²):** **FAIL** (`+0.1659 W/m²`)
- **G2 (Fold Consistency >= 4/5 folds):** **FAIL** (`2 / 5 folds improved`)
- **G3 (Worst Fold Degradation <= +0.50 W/m²):** **FAIL** (`+0.9242 W/m²` in Fold 3)
- **G4 (nMAE & RMSE Non-Degradation):** **FAIL** (`nMAE & RMSE degraded`)
- **G5 (Causal Integrity):** PASS
- **G6 (Exact Control Reproduction):** PASS

---

## 4. Governance Firewall & Protocol Decision

> [!WARNING]
> **ZERO CANDIDATES PASSED EVEN VALIDATION GATES.**
>
> In accordance with strict pre-registered governance rules:
> 1. **Protocol Halted:** Execution stops immediately (`ODD_RUN = FALSE`).
> 2. **ODD Target Firewall:** ODD target values remain completely uninspected (`ODD_TARGET_ACCESS = FALSE`).
> 3. **Classification:** **`REJECTED_ON_EVEN`**
> 4. **Operational Champion:** Stage 8.1 37-feature HGB model remains the operational champion.
