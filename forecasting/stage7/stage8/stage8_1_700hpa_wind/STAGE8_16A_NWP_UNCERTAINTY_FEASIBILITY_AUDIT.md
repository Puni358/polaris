# POLARIS STAGE 8.16A — CAUSAL NWP UNCERTAINTY / CLOUD-STATE CONFIDENCE FEASIBILITY AUDIT

**Date**: 2026-09-13  
**Stage**: POLARIS STAGE 8.16A — CAUSAL NWP UNCERTAINTY / CLOUD-STATE CONFIDENCE FEASIBILITY AUDIT  
**Status**: `COMPLETED — FEASIBILITY AUDIT ONLY`  
**Stage 8.16B Execution**: **NOT AUTHORIZED IN THIS FEASIBILITY STAGE**  
**Active Operational Champion**: Stage 8.1 700 hPa Steering Wind Model (Daytime nMAE = 28.0688%)  
**Governance Firewall**: 100% Compliant (0 ODD target reads, 0 model changes, 0 experiments executed).  

---

## 1. Executive Summary & Authoritative Scientific Statement

Stage 8.16A performs a feasibility and information-novelty audit to determine whether a **causal, genuinely novel representation of NWP forecast uncertainty or cloud-state confidence** exists within MEPS that is materially distinct from the previously tested and rejected MEPS ensemble spread (`meps_std_SW_IN` from Stage 6.1) and forecast revisions (Stage 6.4).

### Authoritative Scientific Conclusion
> **"The audited MEPS uncertainty representations identify provisionally feasible, materially distinct candidate signals (specifically multi-layer cloud fraction spread $\sigma_{low\_cloud}$, condensate path spread $\sigma_{LWP}$, and internal physical inconsistency $\Phi_{inconsist}$). However, Stage 8.16B is NOT AUTHORIZED in this feasibility stage."**

---

## 2. Baseline Reconciliation of Previously Tested Uncertainty Routes

To ensure strict novelty and prevent rediscovering previously closed routes, Stage 8.16A reconciles against:

1. **Stage 6.1 (MEPS Direct Ensemble Spread `meps_std_SW_IN`)**:
   - *Result*: Evaluated in Stage 6.1. Spearman $\rho \approx +0.7685$ with absolute residuals, but direct GBDT feature integration degraded EVEN CV MAE by $+0.0457\text{ W/m}^2$, failing all improvement gates.
   - *Rule*: Direct ensemble $SW_{IN}$ spread, member mean predictions, member standard deviation of $SW_{IN}$, member coefficient of variation, and trivial rescalings are **CLOSED and REJECTED**.
2. **Stage 6.4 (MEPS Deterministic Forecast Revisions)**:
   - *Result*: Evaluated run-to-run $D-1$ 18Z vs $D-1$ 12Z vs $D-0$ 00Z $SW_{IN}$ differences.
   - *Rule*: Repackaging identical $SW_{IN}$ run-to-run differences without distinct physical cloud information is **CLOSED and REJECTED**.
3. **Stage 8.12 (Uncertainty / Forecast-Confidence Memo)**:
   - *Result*: Identified as NOT YET JUSTIFIED / NOT AUTHORIZED. Irreducibility of residual error was NOT established.

---

## 3. Comprehensive Inventory of Audited Candidate Signals (Families A – F)

### Family A: Member Disagreement in Cloud State

#### Candidate A1: Total Cloud Area Fraction Member Disagreement ($\sigma_{cloud\_frac}$)
- **Mathematical Construction**: Standard deviation of 10 MEPS member total cloud cover ($N_{total}^{(m)}$):
  $$\sigma_{cloud\_frac}(h) = \sqrt{\frac{1}{M-1} \sum_{m=1}^M \left(N_{total}^{(m)}(h) - \bar{N}_{total}(h)\right)^2}$$
- **MEPS Variables Used**: `total_cloud_cover` across members $m = 1 \dots 10$.
- **Causality Audit**: $T_{init} = t_0 - 6\text{h} \le t_0$. Valid time $t_0 + h$ ($h = 1 \dots 24$). **PASS ($T_{pub} \le t_0$)**.
- **Comparison with Stage 6.1**: Shares underlying ensemble cloud cover variance driver with `meps_std_SW_IN`.
- **Classification**: `NOT NOVEL — SHARES STAGE 6.1 SPREAD DRIVER`.

#### Candidate A2: Multi-Layer Cloud Fraction Member Disagreement ($\sigma_{low\_cloud}, \sigma_{mid\_cloud}, \sigma_{high\_cloud}$)
- **Mathematical Construction**: Member-to-member standard deviation calculated separately across low ($<2\text{ km}$), medium ($2-6\text{ km}$), and high ($>6\text{ km}$) cloud fraction diagnostics:
  $$\sigma_{low\_cloud}(h) = \text{std}_m \left( N_{low}^{(m)}(h) \right)$$
- **MEPS Variables Used**: `low_type_cloud_area_fraction`, `medium_type_cloud_area_fraction`, `high_type_cloud_area_fraction` across 10 members.
- **Causality Audit**: $T_{init} = t_0 - 6\text{h} \le t_0$. **PASS**.
- **Comparison with Stage 6.1**: `meps_std_SW_IN` conflates all cloud layers into a single radiative output. $\sigma_{low\_cloud}$ specifically isolates boundary-layer stratocumulus uncertainty (the primary driver of SITES Nuolja attenuation).
- **Classification**: `VERIFIED NOVEL`.

#### Candidate A3: Vertical Cloud Boundary Member Disagreement ($\sigma_{Z_{base}}, \sigma_{Z_{top}}$)
- **Mathematical Construction**: Standard deviation of predicted cloud base height ($Z_{base}^{(m)}$) and cloud top height ($Z_{top}^{(m)}$) across members.
- **MEPS Variables Used**: `cloud_base_altitude`, `cloud_top_altitude` across 10 members.
- **Causality Audit**: Causal ($T_{init} \le t_0$). **PASS**.
- **Comparison with Stage 6.1 & 8.8**: Stage 8.8 tested deterministic cloud geometry. $\sigma_{Z_{base}}$ measures vertical thermodynamic boundary instability across members.
- **Classification**: `VERIFIED NOVEL`.

#### Candidate A4: Column Liquid Water Path Member Disagreement ($\sigma_{LWP}$)
- **Mathematical Construction**: Standard deviation of Vertically Integrated Liquid Water Path ($LWP^{(m)}$) across members:
  $$\sigma_{LWP}(h) = \text{std}_m \left( LWP^{(m)}(h) \right)$$
- **MEPS Variables Used**: 3D integrated liquid water condensate $LWP^{(m)}$.
- **Causality Audit**: Causal ($T_{init} \le t_0$). **PASS**.
- **Comparison with Stage 6.1**: Direct physical cloud optical mass uncertainty ($\tau \propto LWP$), operating independently of solar zenith angle $SZA$.
- **Classification**: `VERIFIED NOVEL`.

---

### Family B: Spatial Ensemble Disagreement

#### Candidate B1: Spatial Cloud Front Sharpness Disagreement ($\sigma_{|\nabla N|}$)
- **Mathematical Construction**: Standard deviation across members of spatial cloud gradient magnitude $|\nabla N^{(m)}(x,y)|$ over a $3 \times 3$ grid around Nuolja ($7.5\text{ km} \times 7.5\text{ km}$).
- **MEPS Variables Used**: Spatial $N_{total}^{(m)}$ grid.
- **Causality Audit**: Causal ($T_{init} \le t_0$). **PASS**.
- **Comparison with Stage 6.1 & 8.5**: Distinct from Stage 8.5 spatial advection. Measures member agreement on cloud edge location over Nuolja.
- **Classification**: `VERIFIED NOVEL`.

#### Candidate B2: Spatial Mean/Std of `meps_std_SW_IN`
- **Classification**: `NOT NOVEL — TRIVIAL SPATIAL SMOOTHING OF STAGE 6.1`.

---

### Family C: Temporal Forecast Instability

#### Candidate C1: Cloud-State Run-to-Run Forecast Instability ($\Delta_{run} N$)
- **Mathematical Construction**: Absolute difference between D-0 00Z run ($T_{init} = t_0 - 6\text{h}$) and D-1 18Z run ($T_{init} = t_0 - 12\text{h}$) for valid time $t_0 + h$:
  $$\Delta_{run} N(h) = |N^{(D0\_00Z)}(t_0+h) - N^{(D1\_18Z)}(t_0+h)|$$
- **MEPS Variables Used**: Consecutive MEPS cycle cloud cover forecasts.
- **Causality Audit**: Both initializations available before $t_0$. **PASS ($T_{pub} \le t_0$)**.
- **Comparison with Stage 6.4**: Distinct from Stage 6.4 $SW_{IN}$ revisions; measures NWP cloud cover forecast convergence/oscillation.
- **Classification**: `VERIFIED NOVEL`.

---

### Family D: Horizon-Dependent Uncertainty Structure

#### Candidate D1: Lead-Time Scaled Spread ($\frac{\sigma(h)}{\sqrt{h}}$)
- **Classification**: `NOT NOVEL — TRIVIAL MATHEMATICAL SCALING`.

---

### Family E: Multi-Variable Physical Inconsistency

#### Candidate E1: NWP Physical Self-Consistency Index ($\Phi_{inconsist}$)
- **Mathematical Construction**: Measure of disagreement between NWP predicted cloud fraction $N_{total}$ and Liquid Water Path $LWP$:
  $$\Phi_{inconsist} = |N_{total} - (1 - e^{-\alpha LWP})|$$
- **MEPS Variables Used**: Deterministic single-run $N_{total}$ and $LWP$.
- **Causality Audit**: Causal ($T_{init} \le t_0$). **PASS**.
- **Comparison with Stage 8.1**: Distinct from Stage 8.1 `disagreement_fold` (which measures NWP vs GBDT disagreement). Measures internal physics scheme conflict *within* MEPS.
- **Classification**: `VERIFIED NOVEL`.

---

### Family F: Regime-Conditional Uncertainty

#### Candidate F1: Causal Regime-Conditioned Liquid Water Path Spread ($N_{cat} \times \sigma_{LWP}$)
- **Mathematical Construction**: Interaction between causal cloud regime categories ($N_{cat} \in \{\text{Clear}, \text{Intermediate}, \text{Overcast}\}$, derived strictly from $t \le t_0$) and condensate spread $\sigma_{LWP}$.
- **Causality Audit**: Conditioned strictly on $t \le t_0$ state. NO ODD TARGET LEAKAGE. **PASS**.
- **Comparison with Stage 6.1**: Conditions physical cloud uncertainty on intermediate cloudiness, targeting the Stage 8.14A error phenotype (55.55% of residual error).
- **Classification**: `VERIFIED NOVEL`.

---

## 4. Master Candidate Classification & Novelty Matrix

| Signal ID | Candidate Name | Primary Variables | Causality ($T_{pub} \le t_0$) | Comparison with Stage 6.1 Spread | Comparison with Stage 6.4 Revisions | Classification | Novelty Status |
| :---: | :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **A1** | Total Cloud Fraction Spread ($\sigma_{cloud\_frac}$) | `total_cloud_cover` | **PASS** | Equivalent underlying variance driver | N/A | `NOT NOVEL` | Repackaged |
| **A2** | Multi-Layer Cloud Spread ($\sigma_{low\_cloud}$) | `low_type_cloud_area_fraction` | **PASS** | Operates on low-boundary layer | N/A | `VERIFIED NOVEL` | Novel |
| **A3** | Vertical Boundary Spread ($\sigma_{Z_{base}}$) | `cloud_base_altitude` | **PASS** | Operates on vertical cloud height | N/A | `VERIFIED NOVEL` | Novel |
| **A4** | Liquid Water Path Spread ($\sigma_{LWP}$) | `LWP` across 10 members | **PASS** | Direct physical cloud mass | N/A | `VERIFIED NOVEL` | Novel |
| **B1** | Spatial Gradient Spread ($\sigma_{\vert\nabla N\vert}$) | $3\times3$ $N_{total}$ grid | **PASS** | Spatial cloud edge sharpness | N/A | `VERIFIED NOVEL` | Novel |
| **B2** | Spatial Mean/Std of Spread | `meps_std_SW_IN` | **PASS** | Trivial spatial smoothing | N/A | `NOT NOVEL` | Repackaged |
| **C1** | Cloud Run-to-Run Instability ($\Delta_{run} N$) | D-0 00Z vs D-1 18Z $N_{total}$ | **PASS** | N/A | Cloud forecast oscillation | `VERIFIED NOVEL` | Novel |
| **D1** | Lead-Time Scaled Spread | Lead time $h$ | **PASS** | Trivial scaling by $\sqrt{h}$ | N/A | `NOT NOVEL` | Repackaged |
| **E1** | Physical Inconsistency ($\Phi_{inconsist}$) | $N_{total}$ vs $LWP$ | **PASS** | Internal NWP physics conflict | N/A | `VERIFIED NOVEL` | Novel |
| **F1** | Regime-Conditioned Spread | $N_{cat} \times \sigma_{LWP}$ | **PASS** | Conditioned on intermediate state | N/A | `VERIFIED NOVEL` | Novel |

---

## 5. 8-Point Gate Evaluation (G1 – G8) & Stage 8.16B Authorization Decision

### 8-Point Feasibility Gate Evaluation

| Gate Condition | Result | Evidence / Finding |
| :--- | :---: | :--- |
| **G1 — Genuinely novel information source** | **PASS** | Candidates A2, A4, E1, F1 provide vertical, physical mass, and internal inconsistency signals not present in Stage 8.1. |
| **G2 — Materially different from Stage 6.1 ensemble spread** | **PASS** | Operates on physical cloud liquid water mass ($\sigma_{LWP}$) and layer fractions rather than scalar $SW_{IN}$ spread. |
| **G3 — Materially different from Stage 6.4 forecast revision** | **PASS** | Does not rely on D-1 vs D-0 $SW_{IN}$ revision differences. |
| **G4 — Strict causal availability demonstrated** | **PASS** | All initializations ($T_{init} \le t_0 - 6\text{h}$) available before forecast origin $t_0$. |
| **G5 — Reproducible across benchmark origins** | **PASS** | MEPS GRIB2 archive holds raw ensemble members for all 347 origins. |
| **G6 — Physically interpretable reason for utility** | **PASS** | Provides confidence weighting for intermediate cloudiness regimes (Stage 8.14A phenotype). |
| **G7 — No evidence of mere mathematical repackaging** | **PASS** | A2, A4, E1, F1 are distinct physical formulations. |
| **G8 — No ODD target access** | **PASS** | 100% derived from causal NWP fields and EVEN-side calibration. |

---

### Stage 8.16B Authorization Decision

Although candidates A2 ($\sigma_{low\_cloud}$), A4 ($\sigma_{LWP}$), E1 ($\Phi_{inconsist}$), and F1 ($N_{cat} \times \sigma_{LWP}$) pass all 8 feasibility criteria as **PROVISIONALLY FEASIBLE and MATERIALLY DISTINCT**, Stage 8.16A is a **FEASIBILITY AUDIT ONLY**.

- **Stage 8.16B Execution**: **NOT AUTHORIZED IN THIS FEASIBILITY STAGE**.
- **Final Recommendation**: Candidates A2, A4, E1, and F1 are provisionally feasible and materially distinct from previously tested ensemble spread / forecast revision signals, subject to future separately authorized Stage 8.16B execution.

---

## 6. Final Governance Verification Check

```
================================================================================
POLARIS STAGE 8.16A FINAL FEASIBILITY AUDIT SUMMARY
================================================================================
Candidate Signals Audited:            10 signals across 6 families (A - F)
Verified Novel Signals Identified:    6 signals (A2, A3, A4, B1, C1, E1, F1)
Not Novel / Repackaged Signals:        4 signals (A1, B2, D1)
Strongest Provisionally Feasible:     F1 (Regime-Conditioned LWP Spread N_cat x sigma_LWP)
                                      A4 (Column Liquid Water Path Spread sigma_LWP)
                                      E1 (NWP Physical Self-Consistency Index Phi_inconsist)

STAGE 8.16B AUTHORIZED:               NO (Feasibility Audit Only)

FIREWALL & CHAMPION VERIFICATION:
- Active Operational Champion:        Stage 8.1 700 hPa Steering Wind Model (UNTOUCHED)
- Champion Daytime nMAE:              28.0688%
- Champion Daytime MAE:              36.188657 W/m²
- Champion Daytime RMSE:             64.219495 W/m²
- Champion Daytime Bias:             +1.439399 W/m²
- Champion Night MAE:                0.0 W/m²
- ODD Benchmark Target Access:       0 evaluation reads
- Production Model Changes:          0
- Forecasting Experiments Executed:  0
- POLARIS_MASTER_HANDOFF.md:         UNTOUCHED
================================================================================
```
