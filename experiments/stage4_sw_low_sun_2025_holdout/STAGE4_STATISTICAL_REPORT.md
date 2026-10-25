# POLARIS Stage 4: Statistical Testing & Diesel Gate Report (2025 Holdout)

**Experiment:** `EXP-STAGE4-SW-LOW-SUN-2025-HOLDOUT`  
**Governing Document:** `experiments/EXP_STAGE4_SW_LOW_SUN_PREREGISTRATION.md`  
**Target Population:** 123 origins (2025-05-01 through 2025-08-31)  
**Safety Gate Status:** Candidate S-L (PASS), Candidate SW-L (PASS). Both eligible for diesel gate evaluation.

---

## 1. Preregistered Diesel Gate Criteria

For each candidate against Control B, evaluating origin-paired fuel saving $\Delta_o = \text{Fuel}_{\text{ControlB}}(o) - \text{Fuel}_{\text{candidate}}(o)$ (L):
1. **Two-sided paired Wilcoxon signed-rank test** with Holm correction across the 2 candidate diesel tests:
   - Smaller p-value must satisfy $p < 0.025$.
   - Larger p-value must satisfy $p < 0.05$.
2. **BCa 95% bootstrap confidence interval** on mean paired fuel saving:
   - Lower bound strictly $> 0.00\text{ L/origin}$.
   - Origin-paired resampling, 10,000 resamples, seed 42 (`numpy.random.default_rng(42)`).

---

## 2. Statistical Testing Results

| Candidate | Total Diesel Fuel (L) | Total Saving (L) | Saving (%) | Mean Paired Saving (L/origin) | Median Saving (L/origin) | BCa 95% Bootstrap CI (L/origin) | Lower CI > 0 | Wilcoxon Stat | Raw p-value | Holm-Adjusted p | Holm Sig (α=0.05) | Diesel Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Control B** | 6117.9691 | — | — | — | — | — | — | — | — | — | — | Reference |
| **S-L** | 5334.1331 | 783.8360 | 12.81% | 6.3727 | 5.9488 | [4.1057, 8.5926] | **True** | 1662.0 | 6.9037e-07 | 6.9037e-07 | **True** | **PASS** |
| **SW-L** | 5221.3152 | 896.6539 | 14.66% | 7.2899 | 7.3848 | [4.9970, 9.5583] | **True** | 1564.0 | 2.2831e-08 | 4.5662e-08 | **True** | **PASS** |

---

## 3. Holm Family P-Value Ranking

- **Test 1 (Candidate SW-L):**
  - Raw p-value: $2.2831 \times 10^{-8}$ (rank 1, smaller)
  - Holm threshold: $0.05 / 2 = 0.025$
  - Result: $2.2831 \times 10^{-8} < 0.025 \implies$ **PASS** (Holm-adjusted p = $4.5662 \times 10^{-8}$)
- **Test 2 (Candidate S-L):**
  - Raw p-value: $6.9037 \times 10^{-7}$ (rank 2, larger)
  - Holm threshold: $0.05 / 1 = 0.050$
  - Result: $6.9037 \times 10^{-7} < 0.050 \implies$ **PASS** (Holm-adjusted p = $6.9037 \times 10^{-7}$)

Both tests achieve overwhelming statistical significance with Holm FWER control at $\alpha = 0.05$.

---

## 4. 40% Diesel Reduction Target Status

- **Preregistration Contract (Section 13):**
  - The 40% target is a **benchmark target only**, NOT a gate and NOT an eligibility condition.
- **Observed Savings on 2025 Holdout:**
  - Candidate S-L achieved **12.81%** diesel reduction (783.84 L saved).
  - Candidate SW-L achieved **14.66%** diesel reduction (896.65 L saved).
- **Evaluation:**
  - Neither candidate achieved the 40% target on the 2025 holdout.
  - Per Section 14.3 of the preregistration interpretation matrix:
    *"SW-L passes all gates, saving < 40%, CI > 0 -> Protection costs part of SW's saving. Report trade-off; do not claim the target."*
  - The low-sun stored-energy protection successfully eliminates the reliability deficit of Candidate SW and produces statistically significant diesel savings ($+14.66\%$, $p = 4.57 \times 10^{-8}$), but restoring conservative reserve requirements at low sun reduces the unconstrained 36.50% saving down to 14.66%.
