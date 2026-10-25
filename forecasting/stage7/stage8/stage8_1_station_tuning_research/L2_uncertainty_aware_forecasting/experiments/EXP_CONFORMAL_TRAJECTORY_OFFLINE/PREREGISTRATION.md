# POLARIS PRE-REGISTRATION: EXP-CONFORMAL-TRAJECTORY-OFFLINE
## Distribution-Free Trajectory-Level Cumulative Solar-Energy Shortfall Validation

**Experiment ID:** `EXP-CONFORMAL-TRAJECTORY-OFFLINE`  
**Target Station:** Mount Nuolja AWS (`ANS_NMS`, 702 m a.s.l., `68.362074° N, 18.738875° E`)  
**Pre-Registration Date:** 2026-10-05T08:07:00+05:30  
**Governance Level:** Research-Only Offline Statistical Validation (Zero EMS, Zero Controller Runs, Zero Production Code Modifications)  
**Status:** **FROZEN PRIOR TO 2025 BLIND EXECUTION**  

---

## 1. Research Question & Objective

Can POLARIS construct a distribution-free, trajectory-level cumulative solar-energy shortfall envelope in Wh that is statistically and physically more defensible than the failed Candidate D V2 AR variance envelope?

### Strict Operational Boundaries:
- NO GAP19 optimizer runs.
- NO closed-loop receding-horizon simulation.
- NO reserve modification or diesel dispatch comparisons.
- NO EBR adjustments.
- The experiment terminates strictly at: `forecast error → cumulative energy uncertainty envelope in Wh`.

---

## 2. Chronological Split Governance & Holdout Honesty

### 2.1 Chronological Split
- **Model Development & Fitting Period (2020–2021, 731 origins):**
  Used to estimate AR(1) persistence $\phi = 0.6435$, intercept $c = 11.7258\text{ W/m}^2$, conditional regime means $\mu(x)$, and innovation clear-sky scale $\sigma(x)$.
- **Conformal Calibration Period (2022, 365 origins):**
  Used exclusively to compute nonconformity scores and calibrate the empirical conformal quantile multiplier $\hat{q}_{cal}(\alpha)$ and empirical quantiles.
- **Primary Blind Evaluation Period (2025, 364 origins):**
  Evaluated strictly out-of-sample with zero parameter tuning.
- **Prior Evidence Reference (2023, 273 origins):**
  Reported solely as historical reference since it was previously exposed during the trajectory requalification audit.

### 2.2 Critical Holdout Honesty Declaration
- 2023 is **NOT** a fresh blind dataset (prior exposure in trajectory requalification).
- 2025 is **NOT** a pristine untouched scientific holdout for the upstream forecasting pipeline, as Stage 8.1 point forecast metrics were previously computed for the freeze document (`FINAL_STAGE8_1_FORECASTING_FREEZE.md`).
- **Narrow Claim Tested:** Whether the pre-specified, distribution-free uncertainty representation calibrated on 2022 transfers to the 2025 evaluation period without any post-hoc tuning or parameter adjustment.

---

## 3. Physical Target & Window Definitions

### 3.1 Physical PV Power Transformation (Exact D3 Model)
All solar quantities are transformed to AC electrical power using the authorized POLARIS D3 microgrid engineering mapping:
$$P_{pv}(t) = \min\left(60000.0, \; 51.0 \times \max(0.0, I(t))\right) \quad [\text{W}]$$
where $51.0 = 300\text{ m}^2 \times 0.20 \times 0.85$, and $60,000\text{ W}$ represents the physical inverter clipping ceiling.

Hourly realized shortfall on the battery side:
$$\Delta P_{pv}(t) = \hat{P}_{pv}(t) - P_{pv}(t) \quad [\text{W}]$$
where $\hat{P}_{pv}(t) = \min(60000.0, 51.0 \times \hat{I}(t))$ and $P_{pv}(t) = \min(60000.0, 51.0 \times I(t))$.

### 3.2 Target Windows
For every eligible origin $t$:
- Window start hour: $s \in \{06, 07, \dots, 18\}$ UTC.
- Window duration: $w \in \{1, 2, 3, 4, 5, 6\}$ hours.
- Feasibility constraint: $s + w - 1 \le 18$ (ensuring all hours in the forward window are observed across historical and 2025 datasets).
- Exactly **63 valid window instances** per origin:
  - $w=1$: $s \in [6..18]$ (13 windows)
  - $w=2$: $s \in [6..17]$ (12 windows)
  - $w=3$: $s \in [6..16]$ (11 windows)
  - $w=4$: $s \in [6..15]$ (10 windows)
  - $w=5$: $s \in [6..14]$ (9 windows)
  - $w=6$: $s \in [6..13]$ (8 windows)

Cumulative battery-side shortfall over window $(s, w)$ with $\Delta t = 1.0\text{ h}$:
$$C(s, w) = \sum_{\tau=s}^{s+w-1} \Delta P_{pv}(\tau) \cdot \Delta t \quad [\text{Wh}]$$

---

## 4. Candidate Uncertainty Representations

All three methods evaluate the exact same origins, window starts, window lengths, and target definitions:

### Method A: V2 AR Variance Propagation (Comparison Baseline Only)
- **Status:** Unvalidated comparison baseline.
- **Predicted Mean Shortfall:**
  $$\hat{C}_{AR}(s, w) = \sum_{\tau=s}^{s+w-1} 51.0 \times \Delta t \times \hat{e}_I(\tau)$$
  where $\hat{e}_I(\tau) = \mu(x_\tau) \cdot (1 - \phi^{\tau + 1})$, $\phi = 0.6435$, and $\mu(x_\tau) \in \{+22.1, +5.1, -13.3\}\text{ W/m}^2$.
- **Variance Scale:**
  $$S_{AR}(s, w) = 51.0 \times \Delta t \times \sqrt{\sum_{\tau=s}^{s+w-1} \left( \sum_{l=\tau}^{s+w-1} \phi^{l-\tau} \right)^2 \sigma_{innov}^2(x_\tau)}$$
  where $\sigma_{innov}(x_\tau) = 24.03 + 0.1464 \cdot \text{clearsky\_ghi}[\tau]$.
- **Envelope:**
  $$U_A(s, w; \alpha) = \hat{C}_{AR}(s, w) + z_{1-\alpha} \times S_{AR}(s, w)$$
  where $z_{0.90} = 1.28155$ and $z_{0.95} = 1.64485$.

### Method B: Empirical Cumulative-Error Quantile
- **Status:** Non-parametric empirical benchmark.
- **Envelope:** For each start $s$ and length $w$, compute the empirical $(1-\alpha)$ quantile of realized cumulative shortfall across the calibration set $\mathcal{D}_{cal}$ (2022):
  $$U_B(s, w; \alpha) = \text{Quantile}_{1-\alpha}\left( \{ C_i(s, w) \}_{i \in \mathcal{D}_{cal}} \right) \quad [\text{Wh}]$$

### Method C: Trajectory-Level Split-Conformal Cumulative-Energy Envelope
- **Status:** Proposed distribution-free method.
- **Nonconformity Score:** One-sided, studentized / clear-sky-normalized residual score:
  $$r_i(s, w) = \frac{C_i(s, w) - \hat{C}_{AR, i}(s, w)}{\max(S_{AR, i}(s, w), \; \sigma_0)}$$
  where $\sigma_0 = 1.0\text{ Wh}$ (regularization for zero clear-sky).
- **Trajectory Score:** Worst-case nonconformity across all 63 windows of origin $i$:
  $$R_i = \max_{(s, w)} r_i(s, w)$$
- **Finite-Sample Calibration on $\mathcal{D}_{cal}$ ($N_{cal} = 365$):**
  $$k = \left\lceil (N_{cal} + 1)(1 - \alpha) \right\rceil$$
  - $\alpha = 0.10 \implies k = \lceil 366 \times 0.90 \rceil = 330 \implies \hat{q}_{cal}(0.10) = R_{(330)}$
  - $\alpha = 0.05 \implies k = \lceil 366 \times 0.95 \rceil = 348 \implies \hat{q}_{cal}(0.05) = R_{(348)}$
- **Envelope in Wh:**
  $$U_C(s, w; \alpha) = \hat{C}_{AR}(s, w) + \hat{q}_{cal}(\alpha) \times \max(S_{AR}(s, w), \sigma_0) \quad [\text{Wh}]$$

---

## 5. Coverage, Width, and Evaluation Metrics

### 5.1 Coverage Definitions
1. **Marginal Coverage (per window length $w$):**
   $$\text{Cov}(w) = \frac{1}{N_{eval} \times N_{starts}(w)} \sum_{i} \sum_{s} \mathbb{I}\left( C_i(s, w) \le U(s, w) \right)$$
2. **Simultaneous Trajectory Coverage (per origin):**
   Origin $i$ passes if and only if **all 63 required windows** satisfy the bound:
   $$\text{TrajCov} = \frac{1}{N_{eval}} \sum_{i=1}^{N_{eval}} \prod_{(s, w)} \mathbb{I}\left( C_i(s, w) \le U_i(s, w) \right)$$

### 5.2 Envelope Width Metrics
Envelope width $W(s, w) = U(s, w) - 0$ (reported in Wh):
- Mean width
- Median width
- 90th percentile width

### 5.3 Subgroup Stratification (Minimum $n = 30$)
- **Year:** 2020, 2021, 2022, 2023, 2025.
- **Season:** DJF, MAM, JJA, SON.
- **Cloud Regime (mean cloud cover hours 6..18):** Clear ($<20\%$), Partial ($20\text{--}80\%$), Overcast ($>80\%$).
- **Solar Elevation Regime (mean elevation hours 6..18):** Low ($<15^\circ$), Mid ($15\text{--}30^\circ$), High ($\ge 30^\circ$).
- Subgroups with $n < 30$ are reported descriptively and excluded from PASS/FAIL decisions.

---

## 6. Pre-Registered Decision Criteria (PASS / FAIL / INCONCLUSIVE)

To prevent post-hoc rationalization, decision thresholds are frozen before blind evaluation:

- **PASS:**
  1. Primary blind 2025 simultaneous trajectory coverage meets or exceeds nominal target within finite-sample margin:
     - $\alpha = 0.10$: $\text{TrajCov}_{2025} \ge 87.0\%$ (nominal 90%).
     - $\alpha = 0.05$: $\text{TrajCov}_{2025} \ge 92.5\%$ (nominal 95%).
  2. No major regime collapse for subgroups with $n \ge 30$ (coverage does not drop $>10\%$ below nominal in any eligible regime).
  3. Mean envelope width is not materially more conservative than Method B ($< 2.0\times$ empirical benchmark width).
- **FAIL:**
  1. Simultaneous trajectory coverage on 2025 collapses materially below nominal ($< 85.0\%$ for $\alpha=0.10$ or $< 90.0\%$ for $\alpha=0.05$).
  2. Severe subgroup collapse occurs (e.g. Summer JJA or Overcast coverage $< 75.0\%$).
  3. Method requires post-hoc parameter adjustments on 2025.
- **INCONCLUSIVE:**
  Coverage targets are achieved, but envelope width is excessively conservative ($> 2.5\times$ empirical width), indicating coverage was achieved solely through severe over-buffering.

---

## 7. Frozen Input Manifest

```json
{
  "historical_dataset": {
    "path": "candidate_L_research/CANDIDATE_F_HISTORICAL_RESIDUAL_DATASET_2020_2023.csv",
    "sha256": "1337a56896ba1ea2d3ff40ad2513e02c7f662bbfc3c71ffb717c22542ee2dbab"
  },
  "blind_2025_predictions": {
    "path": "stage7/stage8/stage8_1_corrected_2025/stage8_1_CORRECTED_2025_blind_predictions.csv",
    "sha256": "65e0a0acf2d7196bfa557b319419f0c340b63f1d01d69d5b20c93217742e9500"
  },
  "blind_2025_features": {
    "path": "stage7/stage8/stage8_1_corrected_2025/stage8_1_full_37_feature_matrix_2025_CORRECTED.csv",
    "sha256": "9fe6b9f8b46b89e28315606b365ab6cf6055292240980f211304d379143d2087"
  }
}
```
