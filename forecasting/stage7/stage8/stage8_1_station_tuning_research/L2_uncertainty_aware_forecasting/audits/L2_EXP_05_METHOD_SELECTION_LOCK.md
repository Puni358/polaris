# POLARIS L2-EXP-05 — Method-Selection Lock (Blind-Set Firewall)

**Experiment ID**: `L2-EXP-05`  
**Workspace**: `stage7/stage8/stage8_1_station_tuning_research/L2_uncertainty_aware_forecasting/`  
**Target Station**: Mount Nuolja Middle Station AWS (`ANS_NMS`, 702 m a.s.l., `68.36207412° N, 18.73875158° E`)  
**Date Locked**: October 4, 2026 11:20:00 UTC  
**Lock Purpose**: Establish strict pre-registration of candidate envelope formulations, historical development/validation partitions, and evaluation criteria prior to any external evaluation on 2023 data.

---

## 1. Governance Rules & Scientific Discipline

1. **Blind Set Firewall**:
   - The 2023 blind dataset (Jan–Sep 2023, $N=3,673$ daytime observations) is strictly locked.
   - 2023 observations MUST NOT be used to:
     - select an envelope formulation,
     - estimate or optimize any numeric threshold,
     - fit empirical bins or quantiles,
     - perform comparative model or envelope selection.
   - Any access to 2023 is restricted to a read-only post-lock external confirmation check of the independently selected formulation.
2. **2024 Quarantine**:
   - Year 2024 remains 100% quarantined (0 rows accessed).
3. **No Numerical Optimization**:
   - No grid search, no parameter tuning, no searching for the "optimal floor".
   - 80 W/m² is recorded strictly as the research ablation baseline from L2-EXP-04 and is NOT considered an established physical constant.
4. **No Production Promotion**:
   - Stage 8.1 F, Candidate F, GAP19, optimizer, and production code remain 100% untouched.

---

## 2. Authorized Partitions & Data Splits

| Partition | Time Range | Sample Size (Daytime $\theta_{\text{elev}} > 0$) | Authorized Research Usage |
|---|---|---|---|
| **Development** | 2020-01-01 to 2021-12-31 | 8,137 rows | Primary envelope characterization, empirical percentiles, clear-sky ratio analysis |
| **Validation** | 2022-01-01 to 2022-12-31 | 4,069 rows | Independent out-of-sample formulation testing and inter-annual robustness check |
| **Blind Holdout** | 2023-01-01 to 2023-09-30 | 3,673 rows | Locked. Single-use external validation check only after formulation lock |
| **Quarantined** | 2024-01-01 to 2024-12-31 | 0 rows | Strictly prohibited from all access |

---

## 3. Pre-Registered Candidate Envelope Formulations

The research evaluates four structural formulations:

### Formulation A: Multiplicative Clear-Sky Bound
$$U_A = k \times \text{clearsky\_ghi}$$
- **Reference**: $k = 1.25$ (existing baseline from Stage 8.1 / Candidate L).
- **Physical Hypothesis**: Assumes observed irradiance is strictly proportional to direct geometric clear-sky GHI, with headroom ($k > 1$) allowing for cloud-edge enhancement.
- **Pre-Identified Failure Mode**: As $\theta_{\text{elev}} \to 0^\circ$, $\text{clearsky\_ghi} \to 0$, forcing $U_A \to 0$, conflicting with positive atmospheric diffuse scattering and twilight irradiance.

### Formulation B: Clear-Sky + Positive Diffuse Floor
$$U_B = \max(k \times \text{clearsky\_ghi}, F)$$
- **Reference**: $k = 1.25$, $F = 80\text{ W/m}^2$ (L2-EXP-04 research ablation reference only).
- **Physical Hypothesis**: Decouples the mid-day direct beam geometric regime ($k \times \text{cs}$) from the low-sun atmospheric diffuse/scattered background radiation envelope ($F$).
- **Pre-Identified Properties**: Eliminates low-sun clipping; simple and causally computable; has discontinuous derivative at transition.

### Formulation C: Elevation-Aware Continuous Envelope
$$U_C = g(\theta_{\text{elev}}, \text{clearsky\_ghi})$$
- **Physical Hypothesis**: Atmospheric diffuse irradiance varies continuously with path length and solar zenith angle; envelope smoothly blends from a twilight diffuse envelope at $\theta_{\text{elev}} \approx 0^\circ$ into the geometric clear-sky regime at higher elevations.
- **Pre-Identified Properties**: Physically smooth; however, without direct/diffuse radiation separation at `ANS_NMS`, functional parameters cannot be uniquely identified from first principles.

### Formulation D: Empirical Historical Regime Envelope
$$U_D = Q_p(\text{actual} \mid \text{regime})$$
- **Physical Hypothesis**: Envelope is defined directly as the high empirical quantile (e.g. 99th percentile) of historical observations within observable meteorological bins.
- **Pre-Identified Properties**: High empirical coverage on training data by construction; lacks physical elegance; subject to sampling noise in sparse bins.

---

## 4. Formulation Selection & Evaluation Criteria

The scientific selection of a defensible formulation is governed strictly by the following pre-registered criteria applied to Development (2020–2021) and Validation (2022) data:

1. **Asymptotic Horizon Validity**: Does the bound remain valid as $\theta_{\text{elev}} \to 0^\circ$, or does it force an unphysical zero upper bound that actual observations routinely violate?
2. **Empirical Robustness Across Years**: Is the behavior of the envelope consistent between 2020, 2021, and 2022?
3. **Causal Computability at Forecast Time**: Does the formulation depend solely on variables known at forecast issuance (astronomical solar elevation, NWP clear-sky GHI, origin context)?
4. **Physical Separability**: Can the physical justification be clearly categorized into `VERIFIED`, `INFERRED`, or `UNKNOWN` without fabricating unmeasured direct/diffuse components?
5. **Separation of Formulation vs. Numeric Threshold**: Can a general formulation be endorsed on physical grounds while recognizing that exact numeric production thresholds remain unresolved without dedicated diffuse sensor measurements?

---

## 5. Decision Lock Declaration

- **Primary Selection Data**: 2020–2021 Development + 2022 Validation.
- **External Confirmation Only**: 2023 Blind Test.
- **Forbidden Action**: Any retrospective modification of formulations or tuning of constants based on 2023 metrics.
