# POLARIS STAGE 8.24 — FAITHFUL SCANDES OROGRAPHIC FLOW ROUTE CLOSURE REPORT

> [!CAUTION]
> **GOVERNANCE VERDICT: REJECTED_BY_EVEN_GATES (FAITHFUL IMPLEMENTATION ROUTE CLOSURE)**
> - **Experiment ID:** `POLARIS_STAGE8_24_FAITHFUL_OROGRAPHIC_GOVERNED_EXPERIMENT`
> - **Route Identifier:** `STAGE8.24` (Faithful Scandes Orographic Flow-Regime Expansion)
> - **Operational Champion:** **UNCHANGED (Stage 8.1 37-feature HGB Model preserved)**
> - **Official Benchmark ODD Dataset:** **100% UNTOUCHED (`ODD_RUN = FALSE`)**
> - **ODD Firewall:** **100% MAINTAINED (Zero ODD targets or predictions accessed)**

---

## 1. Governed Route Closure Summary

Following the completion of the pre-registered governed EVEN experiment, **POLARIS Stage 8.24 (Faithful Scandes Orographic Flow-Regime Expansion)** is formally closed as **`REJECTED_BY_EVEN_GATES`**.

The candidate model evaluated the exact pre-registered 2-feature flow representation:
1. **`ctx_u_perp`**: Scandes barrier-normal wind component along $290^\circ$ inflow axis ($U_\perp = -0.9396926 u_{700} + 0.3420201 v_{700}$).
2. **`ctx_mountain_froude`**: Non-dimensional Mountain Froude Number ($Fr = \frac{U_\perp}{N_{\text{layer}} \cdot h}$), derived from the faithful discrete layer-integrated Brunt–Väisälä buoyancy frequency ($N_{\text{layer}}$ over $P_{\text{sfc}} \to 700\text{ hPa}$) and effective relief $h = 828.0\text{ m}$.

No $w_{\text{oro}}$, no hardcoded regime labels, and no unregistered features were added.

---

## 2. Empirical Validation Results Summary

| Metric | Control (Stage 8.1, 37 features) | Candidate (Stage 8.24, 39 features) | Delta | Gate Threshold | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **EVEN MAE** | **37.5529 W/m²** | **37.8072 W/m²** | **+0.2543 W/m²** | $\le -0.50\text{ W/m}²$ | **FAIL (G1)** |
| **EVEN nMAE** | **27.1324%** | **27.3161%** | **+0.1837%** | $\le \text{Control}$ | **FAIL (G4)** |
| **EVEN RMSE** | **76.9839 W/m²** | **77.4707 W/m²** | **+0.4869 W/m²** | $\le \text{Control}$ | **FAIL (G4)** |
| **EVEN Bias** | **+5.6407 W/m²** | **+4.9987 W/m²** | **-0.6420 W/m²** | — | — |
| **Improving Folds** | — | **1 / 5 folds** | — | $\ge 4 / 5\text{ folds}$ | **FAIL (G2)** |
| **Worst Fold Delta** | — | **+0.7186 W/m²** (Fold 3) | — | $\le +0.50\text{ W/m}²$ | **FAIL (G3)** |

---

## 3. Fold-by-Fold Cross-Validation Breakdown

| Fold | Daytime N | Control MAE (W/m²) | Candidate MAE (W/m²) | Delta MAE (W/m²) | Control nMAE (%) | Candidate nMAE (%) | Fold Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fold 1** | 591 | 49.2812 | 49.4249 | +0.1438 | 29.5084% | 29.5945% | Degraded |
| **Fold 2** | 696 | 70.7021 | 70.5377 | **-0.1644** | 36.9894% | 36.9034% | **Improved** |
| **Fold 3** | 648 | 40.3225 | 41.0411 | +0.7186 | 28.1261% | 28.6274% | Degraded (Worst) |
| **Fold 4** | 396 | 25.6368 | 26.1147 | +0.4780 | 36.5408% | 37.2220% | Degraded |
| **Fold 5** | 221 | 1.8218 | 1.9173 | +0.0955 | 50.6984% | 53.3566% | Degraded |

---

## 4. Preservation of $N^2$ Floor Activation Diagnostics

- **Total Sublayers Evaluated:** `21,694`
- **Sublayers $N^2 \le 0$ Floor Activations:** `0` (`0.00%`)
- **Total Origins Evaluated:** `347`
- **Origins Affected by $N^2$ Floor:** `0` (`0.00%`)
- **$N_{\text{layer}}$ Distribution ($\text{s}^{-1}$):**
  - **Mean:** $1.0763 \times 10^{-2}\text{ s}^{-1}$ ($0.010763\text{ s}^{-1}$)
  - **Std Dev:** $2.8495 \times 10^{-4}\text{ s}^{-1}$
  - **Min:** $1.0068 \times 10^{-2}\text{ s}^{-1}$
  - **Median:** $1.0808 \times 10^{-2}\text{ s}^{-1}$
  - **Max:** $1.1451 \times 10^{-2}\text{ s}^{-1}$

---

## 5. Strict Scientific Interpretation Boundary & Governance Directives

> [!IMPORTANT]
> **Scientific Interpretation Boundary:**
> - This empirical result does **NOT** prove that underlying orographic physical processes or Scandes terrain effects are non-existent or irrelevant to atmospheric science.
> - It proves specifically that **THIS pre-registered 2-feature representation (`ctx_u_perp` + `ctx_mountain_froude`)** fails to provide robust incremental predictive value over the Gradient Boosted Tree baseline on top of the Stage 8.1 37-feature control set.
> 
> **Governance Directives Enforced:**
> 1. **Do NOT run ODD evaluation.**
> 2. **Do NOT modify Stage 8.1 champion model or weights.**
> 3. **Do NOT retune candidate features or create variants of $Fr$ or $U_\perp$.**
> 4. **Do NOT add $w_{\text{oro}}$ or hardcoded regime labels.**
> 5. **Do NOT reinterpret results as proof that all orographic physics are useless.**
> 6. **Do NOT automatically promote or open Stage 8.25.**

---

## 6. Route Closure Confirmation

- **Final Classification:** `REJECTED_BY_EVEN_GATES`
- **Operational Champion:** **Stage 8.1 37-feature HGB Model** (`RETAINED`)
- **ODD Benchmark Status:** **100% UNTOUCHED**
- **Route State:** **FORMALLY CLOSED**

*Report generated under POLARIS Stage 8 Governance Protocol on 2026-09-13.*
