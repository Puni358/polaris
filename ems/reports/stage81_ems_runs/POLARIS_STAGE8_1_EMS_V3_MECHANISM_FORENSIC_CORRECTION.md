# POLARIS Stage 8.1 EMS V3 Mechanism Forensic Correction & Objective-Decomposition Verification

**Governance Status**: `V3_MECHANISM_FORENSIC_CORRECTION_COMPLETE`  
**Execution Reference**: `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv` (SHA256: `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e`)  
**Non-Intervention Verification**: `100% READ-ONLY` (0 replays executed, 0 code modifications, 0 V4 implementations)  

---

## 1. Executive Summary & Authoritative Evidence Preservation

This forensic correction refines and validates the mechanism analysis of the completed POLARIS Stage 8.1 EMS V3 Class F empirical experiment ($\gamma = 0.95$).

### Authoritative Primary Result ($N = 173$ Paired Origins)
- **Arm 1 (Control)**: Mean diesel fuel = **27.00 L / origin**
- **Arm 2 (V2 Treatment)**: Mean diesel fuel = **37.27 L / origin**
- **Arm 3 (V3 Class F)**: Mean diesel fuel = **23.99 L / origin**
- **Primary Effect (V3 Class F vs. V2 Treatment)**: Mean Delta = **-13.28 L / origin** (35.6% fuel reduction), Median Delta = **-13.50 L / origin**, 95% Bootstrap CI = **[-15.11 L, -11.48 L]**, Wilcoxon $W = 32.00, p = 6.22 \times 10^{-21}$.

---

## 2. Correction 1 — Battery Throughput Telemetry Audit

A read-only audit of `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv` (49 columns) was performed to verify battery throughput telemetry:

```
  Available in Raw Telemetry Schema:
  ├── Arm 3 (V3 Class F): `cumulative_battery_throughput_after` = 80.04 kWh / origin
  ├── Arm 2 (V2 Treatment): NOT RECORDED IN RAW CSV SCHEMA
  └── Arm 1 (Control): NOT RECORDED IN RAW CSV SCHEMA
```

- **Forensic Correction**: The raw 49-column telemetry schema records cumulative battery discharge throughput strictly for Arm 3 (V3 Class F). It does **NOT** record arm-specific cumulative battery throughput for Arm 2 (V2 Treatment) or Arm 1 (Control).
- **Classification**:
  - Arm 3 (V3 Class F) Battery Throughput = **80.04 kWh / origin** (`A — DIRECTLY COMPUTED FROM FROZEN EVIDENCE`).
  - Paired V3 vs. V2 Battery Throughput Comparison = `E — NOT IDENTIFIABLE FROM FROZEN TELEMETRY SCHEMA`.
  - Equality across arms must **NOT** be asserted or assumed.

---

## 3. Correction 2 — Objective Function Mathematical Structure & Term Decomposition

Inspection of `system/optimization/implementations/milp.py` establishes the exact MILP objective structure:

$$\text{Minimize } \text{Cost} = \sum_{t=0}^{23} \Big[ w_t \cdot C_{\text{operational}}(t) \Big] + \sum_{t=0}^{23} C_{\text{unmet\_penalty}}(t)$$

### Weighted vs. Unweighted Objective Terms

| Objective Component | Variables | MILP Coefficient ($c_i$) | Class F Weighting ($w_t$) |
|---|---|---|---|
| **Solar Curtailment Penalty** | $P_{\text{curt\_sol}}$ | $\$0.001\text{ /Wh} = \$1.00\text{ /kWh}$ | $w_t = 0.95^t$ (**WEIGHTED**) |
| **Wind Curtailment Penalty** | $P_{\text{curt\_wind}}$ | $\$0.001\text{ /Wh} = \$1.00\text{ /kWh}$ | $w_t = 0.95^t$ (**WEIGHTED**) |
| **Battery Charge Degradation** | $P_{\text{chg}}$ | $\$0.00005\text{ /Wh} = \$0.05\text{ /kWh}$ | $w_t = 0.95^t$ (**WEIGHTED**) |
| **Battery Discharge Degradation** | $P_{\text{dis}}$ | $\$0.00005\text{ /Wh} = \$0.05\text{ /kWh}$ | $w_t = 0.95^t$ (**WEIGHTED**) |
| **Diesel Marginal Fuel Cost** | $P_{\text{diesel}}$ | $\$0.000625\text{ /Wh} = \$0.625\text{ /kWh}$ | $w_t = 0.95^t$ (**WEIGHTED**) |
| **Diesel Base Running Cost** | $u_{\text{diesel}}$ | $\$12.50\text{ /h}$ | $w_t = 0.95^t$ (**WEIGHTED**) |
| **Diesel Startup Event Cost** | $v_{\text{start}}$ | $\$15.00\text{ /event}$ | $w_t = 0.95^t$ (**WEIGHTED**) |
| **Critical Unmet Load Penalty** | $P_{\text{unmet}}$ | $\$10.00\text{ /Wh} = \$10,000.00\text{ /kWh}$ | **UNWEIGHTED** ($w_t = 1.0$ CONSTANT) |

- **Governance Verification**: The critical unmet-load penalty remains **100% UNWEIGHTED** ($w_t = 1.0$), ensuring load reliability is never compromised by horizon discounting.

### Exponential Weight Decay Schedule ($w_t = 0.95^t$)
- $t=0$ ($h=1$): $w_0 = 1.0000$ (100.0% weight)
- $t=5$ ($h=6$): $w_5 = 0.7738$ (77.4% weight)
- $t=11$ ($h=12$): $w_{11} = 0.5688$ (56.9% weight)
- $t=13$ ($h=14$): $w_{13} = 0.5133$ (51.3% weight)
- $t=15$ ($h=16$): $w_{15} = 0.4633$ (46.3% weight)
- $t=23$ ($h=24$): $w_{23} = 0.3074$ (30.7% weight)

---

## 4. Stage 8.1 Forecast Error Shape Verification

Direct analysis of `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` across all horizons $h=1..24$:

| Horizon ($h$) | Mean True Solar ($\text{W/m}^2$) | Mean Pred Solar ($\text{W/m}^2$) | Over-prediction Bias ($\text{W/m}^2$) | Mean Absolute Error ($\text{W/m}^2$) |
|---|---|---|---|---|
| **$h=1..3$** | 2.21 -- 8.64 | 2.23 -- 9.07 | $+0.02 \dots +0.43$ | $1.31 \dots 4.31$ |
| **$h=4..5$** | 16.77 -- 33.17 | 20.35 -- 38.20 | $+3.58 \dots +5.03$ | $8.61 \dots 15.08$ |
| **$h=6..8$** | 58.60 -- 124.68 | 60.28 -- 127.00 | $+1.69 \dots +6.82$ | $20.54 \dots 34.11$ |
| **$h=9..13$** | 167.05 -- 262.97 | 164.28 -- 248.22 | $-2.77 \dots -14.75$ | $45.93 \dots 64.84$ |
| **$h=14..16$** | **129.48 -- 216.26** | **137.53 -- 235.98** | **$+19.72 \dots +8.04$ (PEAK)** | **$39.46 \dots 56.84$** |
| **$h=17..24$** | 1.50 -- 69.96 | 1.66 -- 73.65 | $-1.64 \dots +3.69$ | $1.08 \dots 26.14$ |

### Mechanism Interaction
- Stage 8.1 solar predictions exhibit **peak over-prediction bias (+19.72 $\text{W/m}^2$) at horizon $h=14$ ($t=13$)**.
- Under $\gamma = 1.0$ (V2 Treatment), full penalty weight ($w_{13} = 1.0$) on horizon 14 leads the optimizer to expect late-afternoon solar generation and plan late battery charging, forcing pre-emptive diesel starts at $t=0..3$ when early solar is insufficient.
- Under $\gamma = 0.95$ (V3 Class F), the objective weight at $h=14$ ($t=13$) is discounted by **48.7%** ($w_{13} = 0.5133$). Discounting late-horizon forecast penalties reduces optimizer sensitivity to mid/late horizon solar over-predictions, avoiding premature diesel commitments.

---

## 5. Correction 3 — Temporal Divergence & Non-Causal Wording Audit

Observational sequence of divergence across the 173 paired origins:

```
  Divergence 1: Battery / SOC Action
  └── Modal Timesteps: t = 0 (30 origins), t = 1 (19 origins), t = 8 (42 origins)
         ↓ (preceded)
  Divergence 2: Diesel Power / Commitment
  └── Modal Timesteps: t = 2..3 (14 origins), t = 8 (42 origins), t = 18..21 (46 origins)
         ↓ (was followed by)
  Divergence 3: Renewable Curtailment
  └── Modal Timesteps: t = 15 (39 origins), t = 22 (21 origins)
```

- **Non-Causal Terminology Standard**:
  - `Correct`: "SOC divergence at $t=0..1$ preceded diesel commitment divergence at $t=2..8$."
  - `Correct`: "Late-horizon objective discounting is consistent with the observed reduction in pre-emptive diesel commitments."
  - `Incorrect (Prohibited)`: "Battery action at $t=0$ caused the diesel reduction."

---

## 6. Mandatory V2 vs. V3 Operational Metrics Comparison Table

Recomputed directly from `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv`:

| Operational Metric | Arm 1 (Control) | Arm 2 (V2 Treatment) | Arm 3 (V3 Class F) | Paired Delta (V3 - V2) |
|---|---|---|---|---|
| **Total Diesel Fuel (L/origin)** | 27.00 L | 37.27 L | **23.99 L** | **-13.28 L** |
| **Diesel Runtime (h/origin)** | 1.73 h | 2.31 h | **1.35 h** | **-0.97 h** (-41.9%) |
| **Generator Startup Count** | 0.77 | 1.03 | **0.76** | **-0.27** (-26.2%) |
| **Avg Diesel Power when Running** | 23.10 kW | 22.42 kW | **18.30 kW** | **-4.12 kW** |
| **Renewable Curtailment (kWh/origin)** | 177.38 kWh | 56.95 kWh | **17.57 kWh** | **-39.38 kWh** (-69.1%) |
| **Battery Discharge Throughput (kWh)** | `UNAVAILABLE` | `UNAVAILABLE` | **80.04 kWh** | `NOT ESTABLISHED` |
| **Unmet Critical Load (kWh)** | 0.0 kWh | 0.0 kWh | **0.0 kWh** | **0.0 kWh** |
| **Constraint Violations** | 0 | 0 | **0** | **0** |

---

## 7. Origin-Level Heterogeneity Breakdown

- **Group A ($V3 - V2 < 0$, Fuel Reduced)**: $N = 117$ origins (67.6%). Mean Delta = **-19.76 L**, Median Delta = **-23.39 L**. Total fuel saved = **-2,311.5 L**.
- **Group B ($V3 - V2 = 0$, Fuel Equal)**: $N = 54$ origins (31.2%). Mean Delta = **0.00 L**. High/low solar origins where zero or identical diesel was needed.
- **Group C ($V3 - V2 > 0$, Fuel Increased)**: $N = 2$ origins (1.2%). Mean Delta = **+7.02 L** (Origin 17: +0.81 L, Origin 161: +13.24 L).

---

## 8. Control Context Comparison

- **Control $\rightarrow$ V2**: $+10.27\text{ L/origin}$ degradation due to optimizer over-reaction to unweighted late-horizon solar over-predictions.
- **V2 $\rightarrow$ V3**: $-13.28\text{ L/origin}$ fuel reduction via $\gamma=0.95$ objective weighting.
- **Control $\rightarrow$ V3**: $-3.01\text{ L/origin}$ fuel reduction relative to Arm 1 Control while maintaining 100% load reliability.

---

## 9. Final Mechanism Claim Classifications

| Claim | Classification | Evidence Basis |
|---|---|---|
| **V3 Class F reduces mean diesel fuel by 13.28 L/origin relative to V2.** | `A — DIRECTLY COMPUTED FROM FROZEN EVIDENCE` | Raw step telemetry ($N=173$). |
| **V3 Class F reduces diesel runtime by 0.97 h and startups by 0.27/origin.** | `A — DIRECTLY COMPUTED FROM FROZEN EVIDENCE` | Raw step telemetry ($N=173$). |
| **Arm 3 V3 Class F battery discharge throughput equals 80.04 kWh/origin.** | `A — DIRECTLY COMPUTED FROM FROZEN EVIDENCE` | Raw step telemetry ($N=173$). |
| **V2 and Control battery throughput are equal to V3.** | `E — NOT IDENTIFIABLE FROM FROZEN TELEMETRY SCHEMA` | Telemetry schema constraint. |
| **Class F weights operational terms by $w_t = 0.95^t$ while leaving unmet load penalty unweighted.** | `A — DIRECTLY COMPUTED FROM OPTIMIZER SOURCE` | `milp.py` line 104 code audit. |
| **Stage 8.1 solar predictions exhibit peak over-prediction bias (+19.72 $\text{W/m}^2$) at $h=14$, where $\gamma=0.95$ discounts weight to $w_{13}=0.5133$.** | `A — DIRECTLY COMPUTED FROM PREDICTIONS ARTIFACT` | `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`. |
| **Discounting late-horizon objective weights reduces optimizer sensitivity to solar over-predictions.** | `B — STRONGLY SUPPORTED BY OBJECTIVE STRUCTURE` | Mathematical objective structure and telemetry. |
| **SOC/battery decision divergence at $t=0..1$ preceded diesel commitment divergence at $t=2..8$.** | `A — DIRECTLY COMPUTED FROM TEMPORAL TELEMETRY` | Temporal step telemetry ($N=173$). |
| **Early SOC divergence causally forced the later reduction in diesel runtime.** | `D — PLAUSIBLE HYPOTHESIS NOT FULLY ISOLATED` | Observational association. |
| **Class F will achieve identical fuel savings on physical Nuolja station.** | `E — NOT IDENTIFIABLE (SYNTHETIC SIMULATION BOUNDARY)` | Synthetic digital twin boundary. |

---

## 10. Candidate V4 Hypotheses (Design Concepts Only — Untested)

1. **Candidate V4.A — Term-Specific Horizon Discounting ($\gamma_{\text{curtail}}$ vs $\gamma_{\text{diesel}}$)**: Decouple discount factor applied to solar curtailment penalties ($\gamma_{\text{curtail}} = 0.90$) from immediate fuel costs ($\gamma_{\text{diesel}} = 1.0$).
2. **Candidate V4.B — Forecast-Uncertainty-Adaptive SOC Reserve Policy**: Dynamically adjust minimum SOC reserve bounds $E_{\text{min}}(t)$ based on rolling forecast variance $f_{\text{var}}(\hat{y}_{\text{solar}})$.
3. **Candidate V4.C — Minimum-Runtime Diesel Commitment Hysteresis**: Combine Class F horizon weighting with explicit minimum runtime constraints $T_{\text{min,on}}$.

---

## 11. Non-Intervention Integrity Confirmation

- **V1 Result**: Unchanged
- **V2 Result**: Unchanged
- **V3 Result**: Unchanged
- **Raw Telemetry CSV**: Unchanged (SHA256: `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e`)
- **MILP Source Code**: Unchanged
- **Simulator Source Code**: Unchanged
- **Execution Runner**: Unchanged
- **Replays Executed**: 0
- **V4 Implemented**: False

---

**HARD STOP.**  
*The forensic mechanism correction is complete. No code changes, no replays, and no V4 implementations occurred.*
