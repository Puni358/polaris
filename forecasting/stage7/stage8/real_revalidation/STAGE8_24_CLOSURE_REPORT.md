# POLARIS STAGE 8.24 — FORMAL CLOSURE & CHECKPOINT REPORT

> [!CAUTION]
> **GOVERNANCE VERDICT: REJECTED ON EVEN**
> - **Experiment ID:** `POLARIS_STAGE8_24_GOVERNED_EXPERIMENT`
> - **Route Name:** Stage 8.24 Orographic Flow Regime (`ctx_u_perp` + `ctx_mountain_froude`)
> - **Operational Champion:** **UNCHANGED (Stage 8.1 37-feature HGB)**
> - **Official ODD Daytime nMAE:** **28.0688% (UNTOUCHED)**

---

## 1. Governed Experiment Identification & Protocol

- **Experiment Name:** Stage 8.24 — Orographic Flow Regime Expansion
- **Candidate Features:** `ctx_u_perp` (Scandes barrier-normal wind) + `ctx_mountain_froude` (mountain Froude number)
- **Protocol:** 5-fold forward-chaining EVEN-only validation on 173 locked EVEN forecast origins.
- **ODD Access:** **NOT ACCESSED (`ODD_RUN = FALSE`)**

---

## 2. Empirical Validation Results

| Metric | Control (Stage 8.1, 37 features) | Candidate (39 features) | Delta |
| :--- | :---: | :---: | :---: |
| **MAE** | **37.6308 W/m²** | **38.0280 W/m²** | **+0.3972 W/m²** |
| **nMAE** | **29.2146%** | **29.5228%** | **+0.3082%** |
| **RMSE** | **60.0974 W/m²** | **60.4400 W/m²** | **+0.3426 W/m²** |
| **Improving Folds** | — | **1 / 5 folds** | — |
| **Worst Fold Delta** | — | **+1.1857 W/m²** (Fold 3) | — |

---

## 3. Gate Audit Matrix

| Gate ID | Description | Required Threshold | Empirical Result | Gate Status |
| :--- | :--- | :--- | :---: | :---: |
| **G1** | MAE Margin | $\Delta \text{MAE} \le -0.50\text{ W/m}²$ | `+0.3972 W/m²` | **FAIL** |
| **G2** | Fold Consistency | $\ge 4 / 5\text{ folds improve}$ | `1 / 5 folds` | **FAIL** |
| **G3** | Worst Fold Tolerance | Worst fold $\le +0.50\text{ W/m}²$ | `+1.1857 W/m²` | **FAIL** |
| **G4** | nMAE & RMSE Non-Degradation | $\text{nMAE} \le \text{ctrl} \land \text{RMSE} \le \text{ctrl}$ | nMAE: `29.5228%`, RMSE: `60.4400` | **FAIL** |
| **G5** | Causal Integrity | 100% causal features ($t_0 = 00:00\text{ UTC}$) | 100% causal (173/173 origins) | **PASS** |
| **G6** | Control Reproduction | Exact Stage 8.1 control match | `37.6308 W/m²` exact match | **PASS** |

---

## 4. Scientific Conclusion & Interpretation

The barrier-normal wind (`ctx_u_perp`) and mountain Froude number (`ctx_mountain_froude`) representation did **not** provide robust incremental predictive value beyond the existing Stage 8.1 37-feature set under the locked EVEN protocol.

> [!IMPORTANT]
> **Scientific Interpretation Boundary:**
> - This result does **NOT** imply that underlying mountain-flow physics or orographic processes are unimportant for solar irradiance forecasting.
> - It does **NOT** imply that orographic cloud blocking, lee-side clearing, or terrain-forced uplift do not exist over Nuolja.
> - The experiment empirically proves only that these specific scalar surface-to-700hPa flow representations do **not** add net predictive skill to the Gradient Boosted Tree model on top of the 37 features already present in Stage 8.1 (which already implicitly encode atmospheric stability, humidity, and 3D MEPS winds).

---

## 5. Research Space Reduction

With the formal closure of Stage 8.24, POLARIS has systematically evaluated and closed multiple candidate axes:

1. **Local Meteorological Observations & Tendencies** (Stage 8.23: TA/RH/Dewpoint/Lapse Rate) — *REJECTED ON EVEN*
2. **2D & 3D NWP State Summaries** (Stage 8.21A: Slant-path 3D condensate) — *REJECTED ON EVEN*
3. **NWP Uncertainty & Spread** (Stage 8.16B: Multi-model / ensemble spread) — *REJECTED ON EVEN*
4. **Orographic Flow Regime Indicators** (Stage 8.24: Barrier-normal wind & Mountain Froude) — *REJECTED ON EVEN*

> [!NOTE]
> **Strategic Research Focus Moving Forward:**
> POLARIS is deliberately compressing its research space away from further tuning of static scalar features or generic meteorological state representations. Future research must target **genuinely independent cloud-evolution information** (e.g. satellite-derived NRT cloud motion/displacement vectors or direct high-frequency observational tracking) that provides orthogonal physical signal not available within MEPS NWP initialization or local ground-station telemetry.

---

## 6. Project Governance & Status Confirmation

- **Verdict:** `REJECTED_ON_EVEN`
- **ODD Benchmark Dataset:** **100% UNTOUCHED**
- **Operational Champion:** **Stage 8.1 37-feature HGB Model**
- **Official Benchmark ODD Daytime nMAE:** **28.0688%**
- **Master Handoff & Route Registry:** **UNTOUCHED**

---

*Report generated automatically under POLARIS Stage 8 Governance Guidelines on 2026-09-13.*
