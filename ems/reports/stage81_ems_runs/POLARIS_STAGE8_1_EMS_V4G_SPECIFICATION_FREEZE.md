# POLARIS Stage 8.1 EMS V4.G Single-Horizon Mechanism Isolation
## Specification & Parameter Freeze Gate
## DESIGN / SPECIFICATION ONLY — NO IMPLEMENTATION — NO EXECUTION

```yaml
GOVERNANCE_STATUS: V4G_SPECIFICATION_FREEZE_COMPLETE
CANDIDATE_ID: V4.G_SINGLE_HORIZON_ISOLATED_DISCOUNTING
CLASSIFICATION: A — SPECIFICATION + PARAMETER FREEZE COMPLETE
V3_MECHANISM_BRANCH: CLOSED
V4_DESIGN_GATE: COMPLETE
V4G_SPECIFICATION: FREEZE_ESTABLISHED
V4G_IMPLEMENTATION: NOT_STARTED
V4G_EXECUTION: NOT_AUTHORIZED
TARGET_HORIZON: h=14
TARGET_DECISION_INDEX: t=13
V4_G_WEIGHT: 0.5133
ALL_OTHER_WEIGHTS: 1.0
V3_RAW_CSV: POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv
V3_RAW_SHA256: a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e
```

---

## 1. Governance State & Executive Summary

This document establishes the official **Specification and Parameter Freeze Gate** for **Candidate V4.G — Single-Horizon Mechanism Isolation** in the POLARIS Energy Management System (EMS).

### Current Governed State:
- **V1 Execution**: `ACCEPTED + FROZEN`
- **V2 Replay Execution**: `ACCEPTED + FROZEN`
- **V3 Class F Execution**: `VALID COMPLETED EXECUTION + FROZEN`
- **V3 Raw Evidence**: `FROZEN` (`POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv`, SHA256: `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e`)
- **V3 Mechanism Evidence**: `ACCEPTED WITH QUALIFICATIONS`
- **V3 Mechanism Branch**: `CLOSED`
- **V4 Design Gate**: `COMPLETE`
- **V4.G Candidate Classification**: `A — SPECIFICATION + PARAMETER FREEZE COMPLETE`
- **V4.G Implementation**: `NOT STARTED`
- **V4.G Execution**: `NOT AUTHORIZED`

> [!IMPORTANT]
> **ABSOLUTE HARD STOP**: This task is strictly a specification and parameter freeze gate. **NO V4.G code implementation or execution has occurred.** No source files were modified, no solver runs were triggered, no pilot executions were performed, and no parameters were tuned against V3 results.

---

## 2. Authoritative V3 Handoff & Scientific Framing

### Governing Scientific Interpretation
> *"V3 mechanism evidence indicates that the Class F improvement is strongly consistent with reduced optimizer sensitivity to later-horizon forecast-dependent operational costs. Individual forecast-horizon contributions were not isolated."*

### Mechanism Classification
- **Classification**: `B — STRONGLY SUPPORTED BUT NOT FULLY ISOLATED`

### Context & Justification for V4.G:
1. **Identified Horizon Error**: In the V3 horizon-level error decomposition, horizon $h=14$ exhibited the highest positive solar forecast bias ($+19.72\text{ W/m}^2$).
2. **V3 Class F Weighting**: In V3 ($\gamma=0.95$), the objective discount weight at timestep $t=13$ (corresponding to horizon $h=14$) was $w_{13} = 0.95^{13} = 0.513342\dots$.
3. **V2 Unweighted Baseline**: In V2 ($\gamma=1.0$), all horizon steps received full weight $w_t = 1.0$.
4. **Core Scientific Question**: V3 applied exponential decay across all 24 forecast horizons simultaneously ($w_t = 0.95^t$). The fact that $h=14$ had the largest observed bias does **NOT** establish that discounting $h=14$ alone was the cause of the V2$\rightarrow$V3 diesel reduction.
5. **Purpose of V4.G**: Candidate V4.G exists specifically to isolate the single-horizon contribution of $h=14$ ($t=13$) by applying the exact V3 weight $w_{13} = 0.5133$ while holding all other horizons at $w_{t \ne 13} = 1.0$.

> [!NOTE]
> **EXPERIMENTAL FRAMING STATEMENT**: Candidate V4.G MUST be described strictly as **"SINGLE-HORIZON MECHANISM ISOLATION"**. It is **NOT** a "proven optimal horizon", **NOT** a "fix for V2", and **NOT** declared a priori to be "the cause of V2 diesel consumption". The future V4.G experiment asks: *"Does changing only the objective weighting at h=14 / t=13 materially change the downstream EMS dispatch outcome relative to the V3 Class F reference and V2 baseline?"*

---

## 3. Explicit Index Semantics & Index Mapping

To prevent ambiguity, the indexing conventions across system components are formally specified:

| Concept | Symbol | Valid Range | Definition / Mapping |
|---|---|---|---|
| **MPC Origin Step** | $k$ | $k \in [0 \dots 172]$ | Sequential 1-hour receding horizon evaluation steps across $N=173$ forecast origins. |
| **MILP Decision Timestep** | $t$ | $t \in [0 \dots 23]$ | 0-indexed internal decision timesteps within a single 24-hour MILP optimization window. |
| **Forecast Horizon Hour** | $h$ | $h \in [1 \dots 24]$ | 1-indexed forecast horizon hours ($h = t + 1$). |

### Exact Target Horizon Mapping:
$$\text{Target Horizon: } h = 14 \quad \Longleftrightarrow \quad \text{Target MILP Decision Index: } t = 13$$

---

## 4. Formal Parameter Freeze

The parameters for Candidate V4.G are frozen as follows:

```yaml
TARGET_HORIZON: h=14
TARGET_DECISION_INDEX: t=13
V4_G_WEIGHT: 0.5133
ALL_OTHER_WEIGHTS: 1.0
```

### Horizon Weight Vector Specification $w$:
$$w_t = \begin{cases} 0.5133 & \text{if } t = 13 \quad (h=14) \\ 1.0 & \text{if } t \ne 13 \quad (t \in \{0 \dots 12, 14 \dots 23\}) \end{cases}$$

Explicitly:
- $w_0 = 1.0$
- $w_1 = 1.0$
- $\dots$
- $w_{12} = 1.0$
- **$w_{13} = 0.5133$**
- $w_{14} = 1.0$
- $\dots$
- $w_{23} = 1.0$

> [!IMPORTANT]
> **NO TUNING / NO OPTIMIZATION**: The value $0.5133$ is inherited directly from the already-frozen V3 Class F weighting at $t=13$ ($0.95^{13} = 0.513342\dots$). It is **NOT** an empirically tuned or optimized parameter. No grid search, result-dependent tuning, or parameter optimization against V3 results was or will be performed.

---

## 5. Objective Scope & Structural Invariants

Candidate V4.G preserves the exact mathematical structure of the V3 Class F MILP objective function, altering **ONLY** the weighting coefficient vector $w_t$ applied to operational terms.

### Weighted Operational Objective Terms:
For each timestep $t \in [0 \dots 23]$, the weight $w_t$ modifies only:
1. Diesel marginal fuel cost ($c[\text{fuel\_marg}_t] = \text{fuel\_cost} \cdot \text{marg\_fuel} \cdot dt \cdot w_t$)
2. Diesel base running cost ($c[\text{fuel\_base}_t] = \text{fuel\_cost} \cdot \text{base\_fuel} \cdot dt \cdot w_t$)
3. Diesel generator startup cost ($c[\text{startup}_t] = \text{startup\_cost} \cdot w_t$)
4. Battery degradation cost ($c[\text{deg}_t] = \text{deg\_penalty} \cdot dt \cdot w_t$)
5. Solar curtailment penalty ($c[\text{curt\_sol}_t] = \text{curt\_penalty} \cdot dt \cdot w_t$)
6. Wind curtailment penalty ($c[\text{curt\_wind}_t] = \text{curt\_penalty} \cdot dt \cdot w_t$)

### Strict Unweighted Invariant:
- **Unmet Critical Load Penalty**: Remains **UNWEIGHTED** ($w_{\text{unmet}, t} = 1.0$ for all $t$).
  $$c[\text{unmet}_t] = \text{unmet\_penalty} \cdot dt \quad (\text{independent of } w_t)$$

### Immutable System Components:
- **Physical Constraints**: Bus-bar balance, battery power/SOC bounds, diesel minimum/maximum power bounds, charge/discharge exclusivity rules remain 100% identical.
- **Simulator Physics**: `DigitalTwinSimulator` closed-loop state transitions strictly immutable.
- **Forecast Engine & Data**: `Stage81ForecastEngine` and ground truth datasets strictly immutable.
- **Data Contracts**: `ForecastBundle`, `DispatchPlan`, `StationState` schema version `1.0.0` strictly immutable.

---

## 6. Required Source Code Inspection & Insertion Audit

A static audit of the codebase was conducted to confirm exact insertion points for future implementation without making any code edits.

| Source File | Component / Line Range | Current Logic | Intended V4.G Insertion / Modification |
|---|---|---|---|
| [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py) | `LocalMILPEnergyOptimizer.optimize()`, Lines 95–97 | `gamma = float(config.get("optimizer", {}).get("horizon_discount_factor_gamma", 1.0))` <br> `w_t = gamma ** t` | Replace line 97 with V4.G vector logic: <br> `if config.get("optimizer", {}).get("v4g_single_horizon_mode", False):` <br> `    t_target = int(config.get("optimizer", {}).get("v4g_target_index", 13))` <br> `    w_t = float(config.get("optimizer", {}).get("v4g_weight", 0.5133)) if t == t_target else 1.0` |
| [`system/runtime/runner.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/runtime/runner.py) | `PolarisLocalRunner.__init__()`, Lines 74–79 | Loads `optimizer.yaml` into `self.configs["optimizer"]` | Passes V4.G configuration parameters when `v4g` mode is selected. |

### Confirmation of Audit Verification Checklist:
- [x] Exact objective coefficient locations verified (`milp.py` lines 99–106).
- [x] Exact $t=13$ mapping verified.
- [x] Exact $h=14$ mapping verified ($h = t + 1$).
- [x] Class F objective structure verified.
- [x] Unmet-load penalty verified as unweighted (`c[base + 9] = unmet_penalty_per_wh * dt`).
- [x] Zero physical constraints affected.
- [x] Zero forecast inputs modified.
- [x] Zero simulator behaviors modified.
- [x] Zero schema changes required.
- [x] Intervention mechanically isolated from V3 Class F.

---

## 7. Future 3-Arm Experimental Protocol & Endpoints

When V4.G execution is eventually authorized, the evaluation MUST be conducted as a **3-Arm Paired Replay** over $N=173$ forecast origins:

```
                              ┌───────────────────────────────────────────┐
                              │ N = 173 Governed Forecast Origins        │
                              └─────────────────────┬─────────────────────┘
                                                    │
                 ┌──────────────────────────────────┼──────────────────────────────────┐
                 ▼                                  ▼                                  ▼
   ┌───────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
   │ Arm 1: CONTROL            │      │ Arm 2: V3 REFERENCE       │      │ Arm 3: V4.G CANDIDATE     │
   │ LocalBaselineForecast Engine│      │ Stage81ForecastEngine     │      │ Stage81ForecastEngine     │
   │ gamma = 1.0 (Unweighted)  │      │ gamma = 0.95 (Class F)    │      │ w_13 = 0.5133, w_other=1.0│
   └─────────────┬─────────────┘      └─────────────┬─────────────┘      └─────────────┬─────────────┘
                 │                                  │                                  │
                 └──────────────────────────────────┼──────────────────────────────────┘
                                                    ▼
                              ┌───────────────────────────────────────────┐
                              │ Paired Origin-Level Statistical Analysis  │
                              │ Primary Endpoint: Diesel Fuel (L/origin)  │
                              └───────────────────────────────────────────┘
```

### Arm Specifications:
- **Arm 1 (Control)**: `LocalBaselineForecastEngine`, $\gamma = 1.0$ (unweighted baseline).
- **Arm 2 (V3 Reference)**: `Stage81ForecastEngine`, $\gamma = 0.95$ ($w_t = 0.95^t$).
- **Arm 3 (V4.G Candidate)**: `Stage81ForecastEngine`, single-horizon discount ($w_{13} = 0.5133, w_{t \ne 13} = 1.0$).

### Primary & Secondary Endpoints:
- **Primary Endpoint**: Total diesel fuel consumption per 24h origin ($\text{L/origin}$).
- **Secondary Endpoints**:
  - Diesel Runtime ($\text{h/origin}$)
  - Generator Startup Count ($\text{count/origin}$)
  - Diesel Energy ($\text{kWh/origin}$)
  - Renewable Energy Used ($\text{kWh/origin}$)
  - Renewable Curtailment ($\text{kWh/origin}$)
  - Battery Metrics (Discharge throughput kWh, SOC min/max — ONLY where telemetry supports)
  - Unmet Critical Load ($\text{kWh/origin}$)
  - Constraint Violations ($\text{count}$)

---

## 8. Mechanism-Specific Analysis Plan & Hypothesized Outcomes

The future statistical analysis will compare **Arm 3 (V4.G)** against **Arm 2 (V3 Reference)** and **Arm 1 (Control)** to evaluate whether discounting $h=14 / t=13$ alone reproduces the V3 dispatch behavior.

### Possible Analytical Outcome Classifications (For Future Execution):
- **Outcome Category A**: V4.G produces a clear operational change strongly matching the V3 Class F trajectory, confirming that $h=14 / t=13$ is the primary mechanism driver.
- **Outcome Category B**: V4.G produces partial fuel savings, demonstrating that $h=14 / t=13$ contributes materially but multi-horizon cumulative decay ($t=8\dots 23$) is also required.
- **Outcome Category C**: V4.G produces little or no operational change relative to Arm 1 Control, weakening the hypothesis that $h=14 / t=13$ is a dominant contributor.
- **Outcome Category D**: V4.G produces an unexpected dispatch or safety degradation, refuting the candidate mechanism.

> [!NOTE]
> V4.G is NOT required to "beat" V3 to be scientifically informative. Any of the above outcome categories provides direct, valuable scientific evidence regarding horizon error causality.

---

## 9. Governance Classification & Verification

### Candidate Classification:
- **Classification**: `A — SPECIFICATION + PARAMETER FREEZE COMPLETE`
- **Justification**: The exact intervention, mathematical formula, parameter values ($w_{13}=0.5133$), index mapping ($t=13 \leftrightarrow h=14$), objective scope, code insertion point (`milp.py`), and 3-Arm comparison protocol are fully specified and demonstrable from current source code inspection.

### Integrity Verification Checklist:
- [x] `V1` unchanged
- [x] `V2` unchanged
- [x] `V3` unchanged
- [x] `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv` unchanged (SHA256: `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e`)
- [x] Stage 8.1 forecast artifacts unchanged
- [x] All schemas (`ForecastBundle`, `StationState`, `DispatchPlan`) unchanged
- [x] All core logic (`milp.py`, `runner.py`, `simulator.py`) unchanged
- [x] Zero V4.G code written
- [x] Zero V4.G execution performed
- [x] Zero parameter tuning performed

---

## 10. Final Governance State & Absolute Hard Stop

```yaml
V3_MECHANISM_BRANCH: CLOSED
V4_DESIGN_GATE: COMPLETE
V4G_SPECIFICATION: FREEZE_ESTABLISHED
V4G_IMPLEMENTATION: NOT_STARTED
V4G_EXECUTION: NOT_AUTHORIZED
```

---
**ABSOLUTE HARD STOP.**  
*No implementation, execution, pilot, or smoke test occurred during this task. The next governed task will be a separate V4.G implementation authorization and static implementation audit gate.*
