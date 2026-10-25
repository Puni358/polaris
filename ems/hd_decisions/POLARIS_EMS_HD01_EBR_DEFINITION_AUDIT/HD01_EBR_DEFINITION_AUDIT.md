# POLARIS EMS — HD-01 EBR DEFINITION & TARGET EVIDENCE AUDIT REPORT

**Phase**: Human Governance Decision HD-01 Technical Evidence Audit  
**Audit Date**: 2026-09-22  
**Audit Status**: COMPLETED (READ-ONLY TECHNICAL EVIDENCE AUDIT)  
**Output Package**: `POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT`  

---

## 1. Executive Summary & Required Final Classifications

This report provides the read-only technical evidence audit for **Human Governance Decision HD-01**:
> *"What should the Emergency Battery Reserve (EBR) target mean in POLARIS?"*

All findings in this report are strictly grounded in inspected source code, configuration files, and governed specification artifacts. No code changes, schema modifications, parameter selections, or solver executions were performed.

### Final Governed Classifications

| Metric | Governed Classification | Justification |
| :--- | :--- | :--- |
| **`EBR_DEFINITION_STATUS`** | **`READY_FOR_HUMAN_DECISION`** | Technical evidence for 4 candidate definitions (A/B/C/D) is fully evaluated and ready for human governance selection. |
| **`EBR_CAUSALITY_STATUS`** | **`CAUSALLY_VALID`** | Candidates A, B, C, and pre-solve exogenous Candidate D depend strictly on observed initial state $S(t_0)$ and 24h forecasts from `ForecastBundle`. |
| **`EBR_SCHEMA_STATUS`** | **`ADDITIVE_EXTENSION_REQUIRED`** | Fixed candidates (A/B) require no schema changes; load-adaptive candidates (C/D) require additive critical demand vector (`demand_critical`) in `ForecastBundle`. |
| **`HD01_NUMERICAL_TARGET_STATUS`** | **`DERIVABLE`** | Under Candidate C/D, numerical reserve kWh is dynamically derived from authorized resilience hours $N$ and critical load $D_{\text{critical}}(t)$, avoiding arbitrary static scalar selection. |
| **`HD01_IMPLEMENTATION_AUTHORIZATION`** | **`NOT_GRANTED`** | Read-only evidence audit. Implementation authorization remains strictly **NOT_GRANTED** until human governance authorizes HD-01 choices. |

---

## 2. Governed Context & Boundaries

The following governance decisions are established and preserved without modification:

1. **Stage 1 Priority**: Critical load reliability is Stage 1 and has absolute priority ($p_{\text{unmet,critical}} = 0$).
2. **Stage 2 Placement**: EBR maintenance belongs to Stage 2 (resilience & reserve maintenance).
3. **Soft Reserve Target**: EBR is NOT a hard physical constraint; it may be violated to maintain Stage 1 critical service.
4. **Reserve Preservation**: POLARIS must preserve EBR whenever possible without violating higher-priority reliability.
5. **Shortfall Minimization**: Stage 2 minimizes unavoidable EBR shortfall ($\min \sum \max(0, E_{\text{EBR\_target}}(t) - E(t))$).
6. **Exogenous Detector**: Emergency mode is declared strictly by an external Emergency Mode Detector, NOT self-declared by the optimizer.
7. **Policy E3 Rule**: Emergency operation dynamically preserves whichever resource (battery or diesel) has weaker survivability coverage.
8. **Degradation Priority**: Battery degradation cost is secondary during emergency operation ($c_{\text{deg}} = 0.0$ in emergency mode).
9. **HD-03 Concept**: $T_{\text{required}}$ is the authoritative operational survival window until authorized resupply. The 24h MPC horizon ($H=24$) is NOT a proxy for $T_{\text{required}}$, and fixed 30-day placeholders are NOT authorized.

---

## 3. Battery Model Inspection

The physical battery model was inspected across configuration, schema, and solver implementation files:

- [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml)
- [`system/schemas/station_state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py) (`StationState`)
- [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py) (`LocalMILPEnergyOptimizer`)

### Battery Model Fact Register

| Property / Parameter | Exact Value / Symbol | File / Location | Semantic Meaning & Units | Classification |
| :--- | :--- | :--- | :--- | :--- |
| **Total Storage Capacity** | `capacity_wh: 200000.0` | [`battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L3) | Nameplate battery energy rating ($200\text{ kWh}$) | **IMPLEMENTATION FACT** |
| **Technical Min SOC Floor** | `min_soc_pct: 20.0` | [`battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L4) | Physical cell protection lower bound ($20\% \text{ SOC} = 40\text{ kWh}$) | **IMPLEMENTATION FACT** |
| **Technical Max SOC Ceiling** | `max_soc_pct: 95.0` | [`battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L5) | Physical cell protection upper bound ($95\% \text{ SOC} = 190\text{ kWh}$) | **IMPLEMENTATION FACT** |
| **Charge Efficiency** | `charge_efficiency: 0.92` | [`battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L6) | Round-trip charging efficiency factor ($\eta_{\text{chg}} = 0.92$) | **IMPLEMENTATION FACT** |
| **Discharge Efficiency** | `discharge_efficiency: 0.92` | [`battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L7) | Round-trip discharging efficiency factor ($\eta_{\text{dis}} = 0.92$) | **IMPLEMENTATION FACT** |
| **Max Charge Power** | `max_charge_power_w: 50000.0` | [`battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L8) | Maximum inverter charge rate ($50\text{ kW}$) | **IMPLEMENTATION FACT** |
| **Max Discharge Power** | `max_discharge_power_w: 50000.0` | [`battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L9) | Maximum inverter discharge rate ($50\text{ kW}$) | **IMPLEMENTATION FACT** |
| **Degradation Cost** | `deg_penalty_per_wh: 0.00005` | [`battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11) | Cycling degradation penalty ($0.00005/\text{Wh} = \$0.05/\text{kWh}$) | **IMPLEMENTATION FACT** |
| **Energy State Variable** | `lb[base+6]=min_e_wh, ub=max_e_wh` | [`milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L121) | Stored cell energy $E(t)$ bounded between $40\text{ kWh}$ and $190\text{ kWh}$ | **IMPLEMENTATION FACT** |
| **State Transition Math** | $E[t+1] - E[t] - \eta_{\text{chg}} p_{\text{chg}} \Delta t + \frac{p_{\text{dis}}}{\eta_{\text{dis}}} \Delta t = 0$ | [`milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L216) | Discrete conservation of energy transition equation | **IMPLEMENTATION FACT** |
| **Reserve Fields in Schemas** | *None* | [`station_state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py) | No fields exist for `EBR_target`, `EBR_floor`, or reserve headroom | **MISSING** |
| **Provisional Reserve Floor** | $\text{SOC}_{\text{EBR\_floor}} = 35\%$ | `OBJECTIVE_SPECIFICATION.md` | Illustrative baseline reserve floor proposal ($35\% \text{ SOC}$) | **ENGINEERING ASSUMPTION** |

---

## 4. Critical-Load Representation

Demand representation was audited across configuration, schema, and optimizer files:

1. **[`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml)**: Contains `critical_load.baseline_power_w: 30000.0` ($30\text{ kW}$ static rating) and `unmet_penalty_per_wh: 10.0` ($\$10,000/\text{kWh}$). Also contains static deferrable (`water_pumping_heat_store`) and curtailable (`secondary_heating`) load structures.
2. **[`system/schemas/forecast_bundle.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py)**: Contains a single `demand` field of type `TimeseriesForecast` (24-point array in Watts). It represents **aggregate station demand** without tier decomposition.
3. **[`system/schemas/station_state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py)**: Contains `last_observed_demand` (float in Watts).
4. **[`system/schemas/dispatch_plan.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/dispatch_plan.py)**: Contains `load_served`, `flexible_load_schedule`, and `unmet_load` vectors.
5. **[`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py)**: Formulates deficit balance $p_{\text{served}} + p_{\text{unmet}} = p_{\text{demand}}$ and applies a single unweighted penalty to $p_{\text{unmet}}$.

### Current System Demand Classification

$$\text{Current System Capability} = \textbf{A. total station demand only}$$

- The system currently provides aggregate station demand timeseries in `ForecastBundle`.
- Five-tier demand vectors ($L_C, L_E, L_D, L_I, L_N$) under Policy D1 are classified as **E. proposed future structure** / **CONCEPTUAL_POLICY_ONLY** requiring additive schema enhancement (`GAP_19`).

---

## 5. Current Stage-2 Formulation Audit

The governed Stage 2 objective is conceptually specified in Objective Specification v2.5.0 (Section 4.3):

$$ J_2 = \sum_{t=1}^{H} \max\left(0, E_{\text{EBR\_target}}(t) - E_{\text{reserve\_available}}(t)\right) + \max\left(0, E_{\text{terminal\_target}} - E(H)\right) $$

### Audit of $E_{\text{reserve\_available}}(t)$

- **Code Implementation**: Stage 2 is NOT currently instantiated in [`milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py). The current prototype solver uses a single composite objective.
- **Governed Semantic Meaning**: $E_{\text{reserve\_available}}(t)$ represents stored battery cell energy $E(t)$ above the physical cell floor $E_{\text{min\_tech}} = 40\text{ kWh}$ ($20\%$).
- **Efficiency Distinction**:
  - Stored cell energy headroom: $E_{\text{usable\_cell}}(t) = E(t) - E_{\text{min\_tech}} \quad [\text{Wh}]$.
  - Delivered AC busbar energy: $E_{\text{usable\_bus}}(t) = (E(t) - E_{\text{min\_tech}}) \times \eta_{\text{dis}} \quad [\text{Wh}]$, where $\eta_{\text{dis}} = 0.92$.
- **Finding**: Evaluated directly against cell energy $E(t)$, $E_{\text{reserve\_available}}(t)$ does NOT account for inverter discharge efficiency $\eta_{\text{dis}}$. To represent actual AC load coverage, $E_{\text{EBR\_target}}(t)$ must be converted to stored cell Wh by dividing by $\eta_{\text{dis}}$.

---

## 6. Neutral Evaluation of Candidate EBR Definitions

Four candidate EBR definitions were evaluated independently:

```
+-------------------------------------------------------------------------------------------------------------------------+
|                                    NEUTRAL EBR CANDIDATE EVALUATION MATRIX                                             |
+------------+-------------------------+------------------+---------------------+-------------------+---------------------+
| Candidate  | Implementation Status   | Load Adaptability| Schema Impact       | Causality Status  | Numerical Auth Req  |
+------------+-------------------------+------------------+---------------------+-------------------+---------------------+
| CAND_A     | Fixed SOC %             | Static           | NO_CHANGE           | CAUSALLY_VALID    | REQUIRED (Static)   |
| CAND_B     | Fixed Energy Wh         | Static           | NO_CHANGE           | CAUSALLY_VALID    | REQUIRED (Static)   |
| CAND_C     | Critical-Load-Based     | Dynamic (Load)   | ADDITIVE_EXTENSION  | CAUSALLY_VALID    | DERIVABLE (from N)  |
| CAND_D     | Dynamic Exogenous       | Dynamic (State)  | ADDITIVE_EXTENSION  | CAUSALLY_VALID*   | NOT_REQUIRED        |
+------------+-------------------------+------------------+---------------------+-------------------+---------------------+
* Valid if generated pre-solve exogenous to optimizer loop.
```

### Candidate A: Fixed SOC EBR ($E_{\text{target}}(t) = C_{\text{bat}} \times \frac{\text{SOC}_{\text{fixed}}}{100\%}$)
- **Technical Feasibility**: YES. Instantiates as constant scalar bound/penalty.
- **Physical Meaning**: Represents constant cell energy percentage ($X\% \times 200\text{ kWh}$). Ignore seasonal load, weather, or resupply state.
- **Numerical Authorization**: REQUIRED. Requires human governance choice of static percentage $X\%$.
- **Technical Minimum Conflict**: If $X\% = 20\%$, it equals $E_{\text{min\_tech}}$ and renders Stage 2 tautological ($\max(0, 40\text{kWh} - E(t)) = 0$ everywhere feasible).
- **Load Adaptability**: NO. Static scalar.

### Candidate B: Fixed Energy EBR ($E_{\text{target}}(t) = Y \text{ Wh}$)
- **Technical Feasibility**: YES. Instantiates as constant energy scalar.
- **Physical Meaning**: Represents fixed energy quantity $Y \text{ Wh}$. Ignore varying load profiles.
- **Numerical Authorization**: REQUIRED. Requires human governance choice of static energy $Y$.
- **Technical Minimum Conflict**: If $Y = 40,000\text{ Wh}$, duplicates technical minimum floor.
- **Load Adaptability**: NO. Static scalar.

### Candidate C: Critical-Load-Based EBR ($E_{\text{target}}(t) = \frac{\sum_{k=t+1}^{t+N} D_{\text{critical}}(k) \Delta t}{\eta_{\text{dis}}}$)
- **Technical Feasibility**: YES. Sums forecasted critical demand over a governed resilience interval $N$ (hours).
- **Physical Meaning**: HIGH. Directly represents the battery energy required to supply critical load for $N$ hours without diesel generation.
- **Numerical Authorization**: DERIVABLE. Derived dynamically from authorized resilience hours $N$ and forecasted critical load $D_{\text{critical}}(t)$.
- **Technical Minimum Conflict**: NONE. Defined as a distinct energy quantity above technical floor.
- **Schema Requirement**: ADDITIVE EXTENSION REQUIRED. Requires `demand_critical` vector in `ForecastBundle`.

### Candidate D: Dynamic Exogenous EBR ($E_{\text{target}}(t) = f(D_{\text{critical}}, \text{Weather}, \text{Fuel}, \text{Mode})$)
- **Technical Feasibility**: YES, provided target generation occurs in pre-solve phase exogenous to optimization loop.
- **Circularity Risk**: HIGH if generated in-solve using decision variables ($E_{\text{target}} \to \text{Dispatch} \to E(t) \to \text{Mode} \to E_{\text{target}}$). STRICTLY NON-CIRCULAR if generated pre-solve from $S(t_0)$ and `ForecastBundle`.
- **Numerical Authorization**: NOT_REQUIRED_IF_DYNAMIC. Computed at runtime by pre-solve engine.
- **Schema Requirement**: ADDITIVE EXTENSION REQUIRED. Requires `demand_critical` in `ForecastBundle` and `operating_mode` / `fuel_remaining_l` in `StationState`.

---

## 7. EBR vs Emergency Survivability

```
                       POLARIS ARCHITECTURAL SEPARATION
                       
  +-------------------------------------+     +-------------------------------------+
  |     EMERGENCY MODE DETECTOR         |     |        MPC ENERGY OPTIMIZER         |
  |     (Exogenous Pre-Solve Engine)    |     |         (Lexicographic MILP)        |
  +-------------------------------------+     +-------------------------------------+
  | Evaluates: Full Horizon T_required  |     | Evaluates: 24h Horizon H = 24       |
  | Calculates: T_batt, T_fuel          |     | Stage 1: Critical Reliability       |
  | Outputs: operating_mode, limiting   |---->| Stage 2: Min EBR Shortfall J_2      |
  | Scope: Mission Survival Assessment  |     | Scope: Rolling Reserve Headroom     |
  +-------------------------------------+     +-------------------------------------+
```

- **Classification**: $\textbf{B. Related but distinct concepts}$.
- **EBR (Stage 2)**: Rolling intra-horizon operational resilience target ($E_{\text{EBR\_target}}(t)$) evaluated inside the MPC optimizer loop across $H=24\text{h}$. Its purpose is to maintain near-term reserve headroom to absorb short-term solar drops or forecast errors.
- **Emergency Survivability ($T_{\text{batt}}, T_{\text{fuel}}$)**: Exogenous forward endurance calculation evaluated outside the MPC optimizer loop across the full survival window ($T_{\text{required}}$). Its purpose is to assess multi-day mission survival and trigger emergency mode transitions.
- **Double-Counting Risk**: High if $T_{\text{required}}$ (e.g. 72h) is forced into the 24h Stage 2 optimizer objective. Kept distinct by evaluating $T_{\text{required}}$ strictly in the pre-solve detector and evaluating EBR within $H=24\text{h}$ in Stage 2.

---

## 8. EBR vs Technical Minimum SOC

- **Technical Minimum ($E_{\text{min\_tech}} = 20\% = 40\text{ kWh}$)**: Hard physical cell protection bound. Enforced in Stage 0/1 as $E(t) \ge 40\text{ kWh}$. Dropping below 20% causes cell damage.
- **Emergency Battery Reserve ($E_{\text{EBR\_target}}(t)$)**: Soft resilience headroom target ($E_{\text{EBR\_target}}(t) > 40\text{ kWh}$) optimized in Stage 2. Shortfall is penalized in Stage 2, but may be accepted to maintain Stage 1 critical service.
- **Distinctness**: Conceptually distinct. Setting $E_{\text{EBR\_target}} = E_{\text{min\_tech}}$ eliminates Stage 2 optimization by rendering $\max(0, 40\text{kWh} - E(t)) = 0$ identically for all feasible points.

---

## 9. EBR vs Terminal Energy Target

- **Temporal Scope**: $E_{\text{EBR\_target}}(t)$ applies across all timesteps $t \in \{1..H\}$ (intra-horizon reserve). $E_{\text{terminal\_target}}$ applies specifically at timestep $t=H$ (inter-horizon boundary condition).
- **Derivability**: $E_{\text{terminal\_target}}$ is derivable directly from $E_{\text{EBR\_target}}(H)$ ($E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$). Linking them eliminates a standalone arbitrary terminal SOC parameter while ensuring inter-horizon boundary continuity across consecutive MPC solve windows.

---

## 10. Causality & Future-Truth Audit

- **Causally Valid**: Candidates A, B, C, and pre-solve Candidate D rely exclusively on observed state $S(t_0)$ and 24h forecasted quantities from `ForecastBundle`.
- **Causally Invalid / Blocked**: Any candidate requiring actual future demand, actual future solar/wind, actual future SOC, or Digital Twin internal state. In-solve feedback loops between Stage 2 dispatch and detector mode are strictly blocked.

---

## 11. Schema Impact

| Candidate Definition | `ForecastBundle` Impact | `StationState` Impact | `DispatchPlan` Impact | Overall Classification |
| :--- | :--- | :--- | :--- | :--- |
| **CAND_A (Fixed SOC)** | NO_CHANGE | NO_CHANGE | NO_CHANGE | **NO_CHANGE** |
| **CAND_B (Fixed Energy)** | NO_CHANGE | NO_CHANGE | NO_CHANGE | **NO_CHANGE** |
| **CAND_C (Critical-Load-Based)** | ADDITIVE_EXTENSION_REQUIRED (`demand_critical`) | NO_CHANGE | ADDITIVE_EXTENSION_REQUIRED (`ebr_target`) | **ADDITIVE_EXTENSION_REQUIRED** |
| **CAND_D (Dynamic Exogenous)** | ADDITIVE_EXTENSION_REQUIRED (`demand_critical`) | ADDITIVE_EXTENSION_REQUIRED (`operating_mode`, `fuel_rem`) | ADDITIVE_EXTENSION_REQUIRED (`ebr_target`) | **ADDITIVE_EXTENSION_REQUIRED** |

---

## 12. Numerical Target Authorization Analysis

$$\text{HD01\_NUMERICAL\_TARGET\_STATUS} = \textbf{DERIVABLE}$$

- Under load-adaptive formulations (Candidate C/D), numerical reserve kWh is dynamically derived from authorized resilience hours $N$ and critical load forecast $D_{\text{critical}}(t)$.
- If human governance selects a static scalar formulation (Candidate A/B), numerical authorization status shifts to **REQUIRED**, demanding explicit human selection of static percentage $X\%$ or energy $Y\text{ kWh}$.

---

## 13. Definitive Human Decision Register (HD-01 Focus)

| Decision ID | Sub-Decision Title | Status | Evidence Summary | Remaining Human Governance Decision | Implementation Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HD-01A** | EBR Semantic Definition | **OPEN** | Candidates A/B/C/D evaluated in evidence matrix | Select semantic formulation (A, B, C, or D) | Defines Stage 2 objective structure |
| **HD-01B** | Fixed vs Dynamic Target | **OPEN** | Candidates C/D adapt to load; A/B are static | Choose static scalar vs dynamic load-derived target | Determines if pre-solve target generation pipeline is needed |
| **HD-01C** | Resilience Interval ($N$) | **OPEN** | Interval $N$ is independent of MPC $H=24\text{h}$ and $T_{\text{required}}$ | Select resilience hours $N$ (e.g., $N \le 24\text{h}$) | Sets summation window for critical-load EBR |
| **HD-01D** | Numerical Target Auth | **OPEN** | Derivable for C/D; Required for A/B | Authorize static scalar $X\%/Y\text{ kWh}$ if A/B selected | Sets static target parameter in optimizer config |
| **HD-01E** | EBR vs Tech Min | **OPEN** | Tech min = 20% ($40\text{ kWh}$); EBR floor $> 20\%$ | Confirm EBR target is strictly above $20\%$ cell floor | Prevents Stage 2 tautological objective bug |
| **HD-01F** | EBR vs Terminal Target | **OPEN** | $E_{\text{terminal\_target}}$ derivable as $E_{\text{EBR\_target}}(H)$ | Approve $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$ linkage | Eliminates standalone terminal SOC parameter |

---

## 14. Artifact Package Summary

The completed evidence package contains the following 11 artifacts in [`POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/):

1. [`01_EBR_DEFINITION_MATRIX.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/01_EBR_DEFINITION_MATRIX.csv): Neutral evaluation matrix across candidates A/B/C/D.
2. [`02_CRITICAL_LOAD_EVIDENCE.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/02_CRITICAL_LOAD_EVIDENCE.csv): Evidence audit of current demand representation in POLARIS.
3. [`03_STAGE2_FORMULATION_AUDIT.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/03_STAGE2_FORMULATION_AUDIT.csv): Audit of Stage 2 objective and $E_{\text{reserve\_available}}$ semantics.
4. [`04_EBR_SURVIVABILITY_RELATIONSHIP.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/04_EBR_SURVIVABILITY_RELATIONSHIP.csv): Separation of rolling EBR target vs exogenous survivability assessment.
5. [`05_EBR_TERMINAL_RELATIONSHIP.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/05_EBR_TERMINAL_RELATIONSHIP.csv): Audit of intra-horizon EBR vs terminal SOC target.
6. [`06_EBR_CAUSALITY_AUDIT.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/06_EBR_CAUSALITY_AUDIT.csv): Causality & future-truth audit across all candidates.
7. [`07_EBR_SCHEMA_IMPACT.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/07_EBR_SCHEMA_IMPACT.csv): Detailed schema impact on `ForecastBundle`, `StationState`, `DispatchPlan`.
8. [`08_HD01_HUMAN_DECISION_REGISTER.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/08_HD01_HUMAN_DECISION_REGISTER.csv): Focused decision register for HD-01A through HD-01F.
9. [`09_PROVENANCE.csv`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/09_PROVENANCE.csv): Provenance metadata and final classification records.
10. [`HD01_EBR_DEFINITION_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/HD01_EBR_DEFINITION_AUDIT.md): Comprehensive markdown audit report.
11. [`HD01_EBR_DEFINITION_AUDIT.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD01_EBR_DEFINITION_AUDIT/HD01_EBR_DEFINITION_AUDIT.json): Machine-readable audit data package.
