# POLARIS EMS — HD-02 TERMINAL ENERGY TARGET & EBR RELATIONSHIP AUDIT REPORT

**Phase**: Human Governance Decision HD-02 Technical & Governance Audit  
**Audit Date**: 2026-09-22  
**Audit Status**: COMPLETED (READ-ONLY TECHNICAL AND GOVERNANCE AUDIT)  
**Output Package**: `POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT`  

---

## 1. Executive Summary & Required Final Classifications

This report provides the read-only technical and governance audit for **Human Governance Decision HD-02**:
> *"What should the POLARIS terminal battery-energy target mean, and specifically whether $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$ is technically, mathematically, and architecturally valid?"*

All findings in this report are grounded strictly in inspected source code, solver implementations, and authorized governance artifacts. No code modifications, parameter selections, or solver runs were performed.

### Final Governed Classifications

| Metric | Governed Classification | Justification |
| :--- | :--- | :--- |
| **`HD02_RELATIONSHIP_STATUS`** | **`DEFINED`** | The relationship between rolling intra-horizon EBR and terminal state $E(H)$ is mathematically defined and fully analyzed. |
| **`TERMINAL_TARGET_DERIVATION_STATUS`** | **`TECHNICALLY_VALID`** | Deriving $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$ is mathematically coherent, causally valid, and operationally sound. |
| **`TERMINAL_DOUBLE_COUNTING_RISK`** | **`CONFIRMED`** | Combining $\sum_{t=1}^H \max(0, E_{\text{EBR\_target}}(t) - E(t))$ with a separate term $\max(0, E_{\text{EBR\_target}}(H) - E(H))$ double-counts the $t=H$ shortfall. |
| **`TERMINAL_CAUSALITY_STATUS`** | **`CAUSALLY_VALID`** | Causally valid provided critical load forecast $D_{\text{critical}}$ extends up to $H+N$ steps (or uses static baseline for $k > H$). |
| **`HD02_NUMERICAL_POLICY_STATUS`** | **`NOT_REQUIRED_IF_DERIVED`** | Deriving $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$ eliminates the need for an independent static policy parameter (such as a hardcoded 35% terminal SOC). |
| **`HD02_SCHEMA_STATUS`** | **`ADDITIVE_EXTENSION_REQUIRED`** | Requires extending `demand_critical` forecast array in `ForecastBundle` and logging terminal targets in `DispatchPlan`. |
| **`HD02_IMPLEMENTATION_AUTHORIZATION`** | **`NOT_GRANTED`** | Read-only evidence audit. Implementation authorization remains strictly **NOT_GRANTED** until human governance resolves HD-02 decisions. |

---

## 2. Governed Context & Boundary Constraints

The following governance decisions are established and preserved without modification:

1. **Stage 1 Priority**: Critical load reliability is Stage 1 ($p_{\text{unmet,critical}} = 0$).
2. **Stage 2 Placement**: EBR maintenance belongs to Stage 2.
3. **Soft Reserve Target**: EBR is NOT a hard physical constraint; it may be violated to maintain Stage 1 critical service.
4. **Reserve Preservation**: Optimizer preserves EBR whenever possible without violating Stage 1.
5. **Shortfall Minimization**: Stage 2 minimizes unavoidable EBR shortfall.
6. **HD-01A Decision**: EBR is a CRITICAL-LOAD-BASED dynamic energy target ($E_{\text{EBR\_target}}(t) = E_{\text{min\_tech}} + \frac{\sum_{k=t+1}^{t+N} D_{\text{critical}}(k) \Delta t}{\eta_{\text{dis}}}$).
7. **HD-01B Decision**: EBR uses a SEPARATELY GOVERNED RESILIENCE INTERVAL $N$.
8. **Unresolved $N$**: Numerical value of $N$ is NOT YET DECIDED and must NOT automatically equal $H=24\text{h}$, $T_{\text{required}}$, or a fixed SOC %.
9. **HD-03 Decision**: $T_{\text{required}}$ is the exogenous operational survival window until resupply, evaluated by the Emergency Mode Detector outside the optimizer loop.
10. **Emergency Policy E3**: Dynamically preserve whichever resource has weaker survivability coverage.
11. **Degradation Priority**: Battery degradation cost is secondary during emergency operation ($c_{\text{deg}} = 0.0$).

---

## 3. MILP Horizon Semantics Audit

Inspection of [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py):

- **Horizon Window**: $H = 24$ hours.
- **Terminal Variable**: $E(H) = E(24)$ is stored in decision variable `E_next[23]` (index `23 * K + 6`).
- **Terminal Bounds**: `lb[base + 6] = min_e_wh` ($40,000\text{ Wh} = 20\%$), `ub[base + 6] = max_e_wh` ($190,000\text{ Wh} = 95\%$).
- **Terminal Constraint**: **NONE**. $E(H)$ is unconstrained above the physical cell floor $20\%$.
- **Terminal Objective Cost**: **NONE**. Objective coefficient vector $c$ has cost $0.0$ on `base + 6` for all timesteps.
- **End-of-Horizon Depletion Incentive**: **CONFIRMED**. Because discharging the battery saves diesel fuel in Stage 3 and incurs no end-of-horizon penalty on $E(H)$, a 24h rolling optimizer has a mathematical incentive to aggressively empty the battery down to $20\%$ ($40\text{ kWh}$) at $t=24$. When the next MPC cycle runs at $t=1$, initial energy $E(0)$ is depleted, forcing immediate diesel generator startup.

---

## 4. Reconstructed Battery State Equations

From [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml) and [`milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py):

- **Stored Cell Energy State**: $E(t) \in [40,000\text{ Wh}, 190,000\text{ Wh}] \quad [\text{Wh}]$.
- **Initial Energy**: $E(0) = \text{initial\_e\_wh} = \max(E_{\text{min}}, \min(E_{\text{max}}, \text{station\_state.battery\_energy\_wh}))$.
- **Discharge Efficiency**: $\eta_{\text{dis}} = 0.92$.
- **Charge Efficiency**: $\eta_{\text{chg}} = 0.92$.
- **State Transition Equation**:
  $$ E[t+1] = E[t] + \eta_{\text{chg}} \cdot p_{\text{chg}}[t] \cdot \Delta t - \frac{p_{\text{dis}}[t]}{\eta_{\text{dis}}} \cdot \Delta t $$

### Cell Energy Domain vs AC Busbar Energy Domain
- **Stored Cell Energy ($E(t)$)**: Stored chemical energy inside battery cells $[\text{Wh}]$.
- **AC Busbar Energy ($E_{\text{bus}}$)**: Delivered electrical energy to load after inverter losses $[\text{Wh}]$, where $E_{\text{bus}} = E_{\text{cell}} \cdot \eta_{\text{dis}}$.
- **Domain Conversion**: To deliver AC critical energy $\sum D_{\text{critical}} \Delta t$, the required stored cell energy is $\frac{\sum D_{\text{critical}} \Delta t}{\eta_{\text{dis}}}$.

---

## 5. Reconstructed Mathematical EBR Target

Under decisions HD-01A and HD-01B, the total stored energy target $E_{\text{EBR\_target}}(t)$ is:

$$ E_{\text{EBR\_target}}(t) = \min \left( E_{\text{max\_tech}}, \; E_{\text{min\_tech}} + \frac{\sum_{k=t+1}^{t+N} D_{\text{critical}}(k) \Delta t}{\eta_{\text{dis}}} \right) \quad [\text{Wh}] $$

- Expressed strictly in **Stored Cell Energy** domain ($[\text{Wh}]$).
- Inverter discharge efficiency $\eta_{\text{dis}} = 0.92$ is incorporated in the denominator.
- Physical cell protection floor $E_{\text{min\_tech}} = 40,000\text{ Wh}$ ($20\%$) is added to ensure reserve headroom lies strictly above physical cell floor.
- Upper-bounded by maximum physical storage $E_{\text{max\_tech}} = 190,000\text{ Wh}$ ($95\%$).

---

## 6. Terminal State Analysis at $t=H$

At $t=H$ ($t=24$), evaluating $E_{\text{EBR\_target}}(H)$ yields:

$$ E_{\text{EBR\_target}}(H) = E_{\text{min\_tech}} + \frac{\sum_{k=H+1}^{H+N} D_{\text{critical}}(k) \Delta t}{\eta_{\text{dis}}} $$

- **Semantic Meaning**: The stored battery energy required at the horizon boundary $t=H$ to supply critical load over the $N$ hours *following* the current optimization horizon (timesteps $k = H+1 .. H+N$).
- **Mathematical Coherence**: Comparing $E(H)$ to $E_{\text{EBR\_target}}(H)$ via the soft target term $\max\left(0, E_{\text{EBR\_target}}(H) - E(H)\right)$ is **mathematically valid and coherent**. Both terms are expressed in stored cell Wh.

---

## 7. Horizon Boundary & Double-Counting Analysis

```
                                  DOUBLE-COUNTING AUDIT
                                  
  Formula Scheme 1 (Dual Term):
  J_2 = sum_{t=1}^H max(0, E_EBR(t) - E(t))  +  max(0, E_EBR(H) - E(H))
        |________________________________|     |______________________|
             Includes t=H term!                   Explicit Terminal Term!
                       \________________________/
                                    |
                           CONFIRMED DOUBLE-COUNTING
                           (Shortfall at t=H evaluated twice)

  Formula Scheme 2 (Option A - Single Rolling Sum):
  J_2 = sum_{t=1}^H max(0, E_EBR(t) - E(t))  ---> Evaluates t=H exactly ONCE (Zero Double-Counting)

  Formula Scheme 3 (Option B - Explicitly Split Sum):
  J_2 = sum_{t=1}^{H-1} max(0, E_EBR(t) - E(t)) + max(0, E_EBR(H) - E(H)) ---> Evaluates t=H exactly ONCE
```

### Key Double-Counting Findings

1. **Double-Counting Confirmation**: If Stage 2 includes BOTH $\sum_{t=1}^H \max\left(0, E_{\text{EBR\_target}}(t) - E(t)\right)$ AND a separate terminal term $\max\left(0, E_{\text{terminal\_target}} - E(H)\right)$ with $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$, **the shortfall at $t=H$ is evaluated twice**, double-weighting the penalty on $E(H)$ relative to $E(1)..E(H-1)$.
2. **Resolution Strategies**:
   - **Option A (Single Rolling Sum over $t=1..H$)**: $J_2 = \sum_{t=1}^H \max(0, E_{\text{EBR\_target}}(t) - E(t))$. The $t=H$ term in the sum naturally protects $E(H)$. **Zero double-counting**.
   - **Option B (Split Horizon Sum)**: $J_2 = \sum_{t=1}^{H-1} \max(0, E_{\text{EBR\_target}}(t) - E(t)) + \max(0, E_{\text{EBR\_target}}(H) - E(H))$. Mathematically identical to Option A, but visually isolates boundary reserve. **Zero double-counting**.

---

## 8. Does Terminal Target Need an Independent Policy Number?

$$\text{HD02\_NUMERICAL\_POLICY\_STATUS} = \textbf{NOT\_REQUIRED\_IF\_DERIVED}$$

- If $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$, the terminal target is **dynamically derived** from the EBR formula at $t=H$.
- Introducing a separate static policy scalar (such as a hardcoded 35% terminal SOC) creates competing reserve targets, causes policy friction if $E_{\text{EBR\_target}}(H)$ differs from 35%, and imposes unnecessary governance overhead.

---

## 9. Lexicographic Stage 2 Objective Options

| Option ID | Objective Formulation | Mathematical Behavior | Double-Counting Risk | Boundary Protection | Requires New Policy Parameter? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OPT_A** | $J_2 = \sum_{t=1}^H \max(0, E_{\text{EBR\_target}}(t) - E(t))$ | Single rolling sum covering $t=1..H$ | **NONE** | Full boundary protection via $t=H$ term | **NO** |
| **OPT_B** | $J_2 = \sum_{t=1}^{H-1} \max(0, E_{\text{EBR}}(t) - E(t)) + \max(0, E_{\text{EBR}}(H) - E(H))$ | Explicitly split boundary term | **NONE** | Full boundary protection via terminal term | **NO** |
| **OPT_C** | $J_2 = \sum_{t=1}^H \max(0, E_{\text{EBR}}(t) - E(t)) + \max(0, E_{\text{EBR}}(H) - E(H))$ | Double-weighted penalty on $t=H$ shortfall | **CONFIRMED** | Over-penalizes $t=H$ shortfall | **NO** |
| **OPT_D** | $J_2 = \sum_{t=1}^H \max(0, E_{\text{EBR}}(t) - E(t)) \quad \text{s.t.} \quad E(H) \ge E_{\text{EBR}}(H)$ | Hard constraint at $t=H$ | **NONE** | Hard boundary constraint (may cause infeasibility) | **NO** |

---

## 10. Causality & HD-03 Relationship Audit

- **Causality Status**: $\mathbf{TERMINAL\_CAUSALITY\_STATUS = CAUSALLY\_VALID}$. Evaluating $E_{\text{EBR\_target}}(H)$ requires critical load forecasts for timesteps $k = H+1 .. H+N$. This relies on extending the `demand_critical` forecast array in `ForecastBundle` or using static baseline load for $k > H$, without requiring actual future data or Digital Twin internal state.
- **HD-03 Independence**: $E_{\text{terminal\_target}}$ is an MPC solver boundary condition at $t=H=24\text{h}$. $T_{\text{required}}$ is an exogenous emergency survivability horizon evaluated outside the solver by the Emergency Mode Detector. Equating $H = N = T_{\text{required}}$ is **not authorized** and architecturally invalid.

---

## 11. Schema Impact

| Schema File | Impact Classification | Required Extension / Modification |
| :--- | :--- | :--- |
| [`system/schemas/forecast_bundle.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py) | **ADDITIVE_EXTENSION_REQUIRED** | Extend `demand_critical` forecast vector to $H+N$ timesteps to evaluate $E_{\text{EBR\_target}}(H)$ causally. |
| [`system/schemas/station_state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py) | **NO_CHANGE** | Initial state handling remains unchanged. |
| [`system/schemas/dispatch_plan.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/dispatch_plan.py) | **ADDITIVE_EXTENSION_REQUIRED** | Add `terminal_ebr_target` and `terminal_shortfall` fields for auditability. |

---

## 12. Definitive Human Decision Register (HD-02 Focus)

| Decision Sub-ID | Title | Status | Evidence Summary | Open Human Governance Decision | Implementation Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HD-02A** | Conceptual Distinction | **OPEN** | $E_{\text{terminal\_target}}$ is the $t=H$ instance of rolling EBR | Decide if terminal target is distinct or identical to $E_{\text{EBR}}(H)$ | Defines Stage 2 boundary math |
| **HD-02B** | EBR Derivation Linkage | **OPEN** | Deriving $E_{\text{term}} = E_{\text{EBR}}(H)$ is mathematically valid & clean | Approve $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$ | Eliminates standalone terminal policy knob |
| **HD-02C** | Explicit Objective Term | **OPEN** | Sum $t=1..H$ already covers $t=H$; separate term double-counts | Select Option A (Sum $t=1..H$) or Option B (Split $t=1..H-1$ + Term) | Prevents Stage 2 double-counting bug |
| **HD-02D** | Independent Policy Parameter | **OPEN** | Separate terminal scalar duplicates EBR | Approve `DERIVABLE` classification over static scalar | Prevents competing reserve targets |
| **HD-02E** | Boundary Constraint vs Objective | **OPEN** | Soft objective preserves lexicographic flexibility | Select soft objective vs hard boundary constraint | Avoids solver infeasibility |
| **HD-02F** | Double-Counting Mitigation | **OPEN** | Confirmed double-counting if sum $t=1..H$ + term combined | Approve formulation Option A or B | Ensures mathematically clean Stage 2 solve |

---

## 13. Artifact Package Summary

The completed evidence package contains 12 artifacts in [`POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/):

1. [`01_TERMINAL_STATE_ANALYSIS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/01_TERMINAL_STATE_ANALYSIS.csv)
2. [`02_EBR_TERMINAL_RELATIONSHIP.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/02_EBR_TERMINAL_RELATIONSHIP.csv)
3. [`03_HORIZON_BOUNDARY_ANALYSIS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/03_HORIZON_BOUNDARY_ANALYSIS.csv)
4. [`04_DOUBLE_COUNTING_ANALYSIS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/04_DOUBLE_COUNTING_ANALYSIS.csv)
5. [`05_STAGE2_OBJECTIVE_OPTIONS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/05_STAGE2_OBJECTIVE_OPTIONS.csv)
6. [`06_TERMINAL_CAUSALITY_ANALYSIS.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/06_TERMINAL_CAUSALITY_ANALYSIS.csv)
7. [`07_HD03_RELATIONSHIP.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/07_HD03_RELATIONSHIP.csv)
8. [`08_SCHEMA_IMPACT.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/08_SCHEMA_IMPACT.csv)
9. [`09_HD02_HUMAN_DECISION_REGISTER.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/09_HD02_HUMAN_DECISION_REGISTER.csv)
10. [`10_PROVENANCE.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/10_PROVENANCE.csv)
11. [`HD02_TERMINAL_TARGET_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/HD02_TERMINAL_TARGET_AUDIT.md)
12. [`HD02_TERMINAL_TARGET_AUDIT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD02_TERMINAL_TARGET_AUDIT/HD02_TERMINAL_TARGET_AUDIT.json)

---

## 14. Final Required Return Declarations

```
HD02_RELATIONSHIP_STATUS = DEFINED
TERMINAL_TARGET_DERIVATION_STATUS = TECHNICALLY_VALID
TERMINAL_DOUBLE_COUNTING_RISK = CONFIRMED
TERMINAL_CAUSALITY_STATUS = CAUSALLY_VALID
HD02_NUMERICAL_POLICY_STATUS = NOT_REQUIRED_IF_DERIVED
HD02_SCHEMA_STATUS = ADDITIVE_EXTENSION_REQUIRED
HD02_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED
```
