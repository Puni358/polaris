# POLARIS Stage 8.1 EMS V3 Class F Mechanism Forensic Analysis

**Governance Status**: `V3_MECHANISM_FORENSIC_ANALYSIS_COMPLETE`  
**Execution Reference**: `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv` (SHA256: `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e`)  
**V4 Implementation Status**: `NO V4 IMPLEMENTATION OR EXECUTION OCCURRED`  

---

## 1. Executive Forensic Summary & Primary Result

The frozen empirical POLARIS V3 Class F experiment tested the effect of horizon-weighted MPC objective discounting ($\gamma = 0.95$, $w_t = 0.95^t$) relative to Arm 2 V2 Treatment ($\gamma = 1.0$) and Arm 1 Control ($\gamma = 1.0$) across $N = 173$ paired origins.

### Primary Outcome Summary ($N=173$ Paired Origins)
- **Arm 1 (Control)**: Mean diesel fuel = **27.00 L / origin**
- **Arm 2 (V2 Treatment)**: Mean diesel fuel = **37.27 L / origin**
- **Arm 3 (V3 Class F)**: Mean diesel fuel = **23.99 L / origin**
- **Primary Effect (V3 Class F vs. V2 Treatment)**: Mean Delta = **-13.28 L / origin** (35.6% reduction in diesel fuel), Median Delta = **-13.50 L / origin**, 95% Bootstrap CI = **[-15.11 L, -11.48 L]**, Wilcoxon $W = 32.00, p = 6.22 \times 10^{-21}$.

---

## 2. Mandatory V2 vs. V3 Operational Metrics Comparison

Across all 173 paired origins, operational metrics were calculated directly from step-level telemetry:

| Operational Metric | Arm 1 (Control) | Arm 2 (V2 Treatment) | Arm 3 (V3 Class F) | Paired Delta (V3 - V2) |
|---|---|---|---|---|
| **Total Diesel Fuel (L/origin)** | 27.00 L | 37.27 L | **23.99 L** | **-13.28 L** |
| **Diesel Runtime (h/origin)** | 1.73 h | 2.31 h | **1.35 h** | **-0.97 h** (-41.9%) |
| **Generator Startup Count** | 0.77 | 1.03 | **0.76** | **-0.27** (-26.2%) |
| **Avg Diesel Power when Running** | 23.10 kW | 22.42 kW | **18.30 kW** | **-4.12 kW** |
| **Renewable Curtailment (kWh/origin)** | 177.38 kWh | 56.95 kWh | **17.57 kWh** | **-39.38 kWh** (-69.1%) |
| **Battery Discharge Throughput (kWh)** | 80.04 kWh | 80.04 kWh | **80.04 kWh** | **0.0 kWh** |
| **Unmet Critical Load (kWh)** | 0.0 kWh | 0.0 kWh | **0.0 kWh** | **0.0 kWh** |
| **Constraint Violations** | 0 | 0 | **0** | **0** |

---

## 3. Origin-Level Heterogeneity Breakdown

Evaluating the distribution of primary fuel differences ($V3 - V2$) across all $N=173$ origins reveals clear operational clustering:

```
                  ┌─────────────────────────────────────────┐
                  │ Origin Population Breakdown (N = 173)   │
                  └────────────────────┬────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
│ Group A: Reduced  │        │ Group B: Equal    │        │ Group C: Increased│
│ V3 - V2 < 0       │        │ V3 - V2 = 0       │        │ V3 - V2 > 0       │
│ N = 117 (67.6%)   │        │ N = 54 (31.2%)    │        │ N = 2 (1.2%)      │
│ Mean: -19.76 L    │        │ Mean: 0.00 L      │        │ Mean: +7.02 L     │
│ Median: -23.39 L  │        │ Total: 0.0 L      │        │ Total: +14.0 L    │
└───────────────────┘        └───────────────────┘        └───────────────────┘
```

1. **Group A ($V3 - V2 < 0$, Fuel Reduced)**: $N = 117$ origins (67.6%). Mean Delta = **-19.76 L**, Median Delta = **-23.39 L**. Total fuel saved = **-2,311.5 L**. In these origins, V2 initiated premature or prolonged diesel runs due to late-horizon forecast penalties, whereas Class F avoided or shortened these runs.
2. **Group B ($V3 - V2 = 0$, Fuel Equal)**: $N = 54$ origins (31.2%). Mean Delta = **0.00 L**. These are origins with either zero diesel dispatch required across all arms (e.g., high solar availability) or identical necessary diesel runs during heavy renewable deficits.
3. **Group C ($V3 - V2 > 0$, Fuel Increased)**: $N = 2$ origins (1.2%). Mean Delta = **+7.02 L** (Origin 17: +0.81 L, Origin 161: +13.24 L). In these two origins, late-horizon discounting postponed a diesel dispatch into a subsequent high-demand window.

---

## 4. Objective Coefficient & Mathematical Mechanics Analysis

In MILP optimization, the objective function weights operational costs over the 24-step forecast horizon:
$$\text{Cost} = \sum_{t=0}^{23} w_t \cdot \Big[ C_{\text{diesel}}(P_{d,t}) + C_{\text{start}} \cdot v_t + C_{\text{curtail}}(P_{c,t}) + C_{\text{degrad}}(P_{b,t}) \Big]$$

- **Arm 2 (V2 Treatment)**: $\gamma = 1.0 \Rightarrow w_t = 1.0$ for all $t \in [0 \dots 23]$.
- **Arm 3 (V3 Class F)**: $\gamma = 0.95 \Rightarrow w_t = 0.95^t$ for all $t \in [0 \dots 23]$.

### Horizon Weight Decay Schedule
- $t = 0$: $w_0 = 1.000$ (100.0% weight)
- $t = 5$: $w_5 = 0.774$ (77.4% weight)
- $t = 11$: $w_{11} = 0.569$ (56.9% weight)
- $t = 17$: $w_{17} = 0.418$ (41.8% weight)
- $t = 23$: $w_{23} = 0.307$ (30.7% weight)

### Mathematical Interaction with Stage 8.1 Forecast Errors
Stage 8.1 solar predictions exhibit over-prediction error in distant horizon timesteps ($t \ge 8 \dots 15$).
- Under **$\gamma = 1.0$ (V2 Treatment)**, projected mid/late horizon solar over-predictions create a perceived risk of severe solar curtailment or battery overflow at $t=12\dots 20$. To minimize this projected penalty, the optimizer commits diesel early at $t=0\dots 3$ to cover immediate load while keeping the battery pre-discharged.
- Under **$\gamma = 0.95$ (V3 Class F)**, distant curtailment/overflow penalties at $t=23$ are discounted by $69.3\%$ ($w_{23} = 0.307$), whereas immediate diesel fuel cost at $t=0$ retains $100\%$ weight ($w_0 = 1.000$). The optimizer prioritizes **immediate diesel avoidance** over **distant projected forecast penalties**.
- As actual ground truth unfolds, immediate load is satisfied directly by available renewables and battery without starting the generator.

---

## 5. First-Divergence & Temporal Ordering Analysis

Tracking the first timestep $t$ where V2 Treatment and V3 Class F operational trajectories diverge:

1. **Battery Action & SOC Divergence**: First occurs at **$t = 0$** for 30 origins, $t = 1$ for 19 origins, and $t = 8$ for 42 origins.
2. **Diesel Commitment Divergence**: First occurs at **$t = 2 \dots 3$** for 14 origins, $t = 8$ for 42 origins, and $t = 18 \dots 21$ for 46 origins.
3. **Renewable Curtailment Divergence**: First occurs at **$t = 15$** for 39 origins and $t = 22$ for 21 origins.

### Observed Temporal Sequence
$$\text{Battery/SOC Positioning } (t=0) \;\longrightarrow\; \text{Diesel Commitment } (t=2\dots 8) \;\longrightarrow\; \text{Renewable Curtailment } (t=15\dots 22)$$

---

## 6. Control Context (Control $\rightarrow$ V2 $\rightarrow$ V3)

```
       Control (27.00 L)
               │
               │ +10.27 L (V2 Forecast Over-reaction)
               ▼
     V2 Treatment (37.27 L)
               │
               │ -13.28 L (Class F Objective Weighting)
               ▼
     V3 Class F (23.99 L)
```

- **Control $\rightarrow$ V2**: Substituting baseline forecasts with Stage 8.1 predictions degraded performance (+10.27 L/origin) because imperfect mid/late horizon predictions induced false optimization penalties.
- **V2 $\rightarrow$ V3**: Class F ($\gamma = 0.95$) does not merely "reverse" V2 degradation; it fundamentally suppresses over-sensitivity to distant forecast error. V3 Class F consumes **3.01 L/origin less fuel than Arm 1 Control** while maintaining 100% load reliability.

---

## 7. Safety & Reliability Audits

- **Unmet Critical Load**: 0.0 kWh across all 173 origins (100.0% critical load served).
- **Constraint Violations**: 0 solver failures or physical limit breaches.
- **SOC & Battery Bounds**: SOC remained strictly within $[20.0\%, 100.0\%]$ bounds across all timesteps.

---

## 8. Real-World Boundary Statement

> [!IMPORTANT]
> All replays were conducted in the synthetic POLARIS digital twin environment using historical telemetry profiles. These empirical findings demonstrate the mathematical mechanism of MPC horizon discounting within the simulator. No claim of real Nuolja station fuel savings, physical station fuel consumption, or real-world operational robustness is made.

---

## 9. Candidate V4 Intervention Classes

Motivated directly by the observed V3 mechanism, the following candidate V4 intervention classes are identified (*Design Concepts Only — None Implemented or Executed*):

### Candidate V4.A — Asymmetric / Term-Specific Horizon Discounting
- **Targeted Mechanism**: Apply distinct discount factors $\gamma_{\text{diesel}}$ (e.g. 1.0) vs $\gamma_{\text{curtail}}$ (e.g. 0.90) to decouple immediate fuel costs from distant renewable curtailment penalties.
- **Supporting Evidence**: V3 demonstrated that discounting distant curtailment penalties prevents premature diesel start.

### Candidate V4.B — Forecast-Variance-Adaptive SOC Reserve Bounds
- **Targeted Mechanism**: Dynamically adjust minimum SOC reserve bounds $E_{\text{min}}(t)$ as a function of rolling forecast variance $f_{\text{var}}(\hat{y}_{\text{solar}})$.
- **Supporting Evidence**: Maintaining early SOC reserve buffer mitigates diesel dispatch when solar underperforms.

### Candidate V4.C — Minimum-Runtime Diesel Commitment Hysteresis
- **Targeted Mechanism**: Combine Class F horizon weighting with explicit minimum runtime constraints $T_{\text{min,on}}$ to eliminate short diesel cycles.
- **Supporting Evidence**: V3 reduced startup events from 1.03 to 0.76; explicit hysteresis could eliminate remaining short runs.

---

## 10. Mechanism Claim Classifications

| Claim | Classification | Evidence Basis |
|---|---|---|
| **V3 Class F reduces mean diesel fuel by 13.28 L/origin relative to V2.** | `A — DIRECTLY OBSERVED` | Recomputed from raw step telemetry ($N=173$). |
| **V3 Class F reduces diesel runtime by 0.97 h and startups by 0.27/origin.** | `A — DIRECTLY OBSERVED` | Recomputed from raw step telemetry ($N=173$). |
| **V3 Class F reduces renewable curtailment from 56.95 kWh to 17.57 kWh/origin.** | `A — DIRECTLY OBSERVED` | Recomputed from raw step telemetry ($N=173$). |
| **Exponential discount factor $\gamma=0.95$ suppresses sensitivity to late-horizon solar over-predictions.** | `B — STRONGLY SUPPORTED` | Objective coefficient decay ($w_{23}=0.307$) matches forecast error structure. |
| **Primary driver of fuel reduction is the elimination of premature diesel commitments.** | `B — STRONGLY SUPPORTED` | First-divergence timing shows SOC/diesel changes precede curtailment. |
| **Class F will achieve identical fuel savings on the physical Nuolja station.** | `E — NOT IDENTIFIABLE` | Synthetic simulation boundary constraint. |

---

**HARD STOP.**  
*No V4 implementation, execution, or code modifications occurred during this task.*
