# Candidate Gate Comparison (`CANDIDATE_GATE_COMPARISON.md`)

**GATE IDENTIFICATION CONTEXT**: POLARIS EMS GAP19 — Post-24H Baseline Next-Gate Identification  
**VERDICT**: `PASS`

---

## Dependency-Based Evaluation of Candidate Areas

The five candidate architectural areas evaluated following the closure of `GAP19_OPTION_B_24H_MPC_BASELINE_TEST` are analyzed below strictly by dependency order, prerequisite status, architectural uncertainty removed, and minimality:

---

## Candidate Evaluation Matrix

| Candidate Area | Description | Prerequisite Status | Uncertainty Removed | Governance Status | Code/Schema Changes | Gate Selection Verdict |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: |
| **1. Multi-Scenario Robustness** | 24-step MPC dispatch across 4 synthetic stress scenarios (`normal`, `renewable_stress`, `demand_stress`, `battery_stress`). | `SATISFIED` (24h baseline CLOSED) | Option B native HiGHS dispatch feasibility under severe generation drops, demand surges, and battery limits. | `CLEAR` (Governed J2 parameters) | `ZERO` | **SELECTED AS NEXT GATE** |
| **2. Longer-Duration MPC (168h Endurance)** | 168-step (7-day) single-scenario endurance run. | `BLOCKED` (Requires multi-scenario stress validation first) | Long-term numerical integration stability across 168 consecutive steps. | `CLEAR` | `ZERO` | **EXCLUDED** (Violates minimality rule: multi-scenario stress must precede long endurance) |
| **3. ECD Runtime Integration** | Live evaluation of `EmergencyConditionDetector` in `PolarisLocalRunner`. | `BLOCKED` (Schema limitation) | Runtime classification of `NORMAL`, `EMERGENCY`, `UNKNOWN_INVALID`. | `CLEAR` (HD-03) | `REQUIRES SCHEMA CHANGE` (Fuel inventory not in `StationState`) | **EXCLUDED** (Blocked by diesel fuel inventory schema representation gap) |
| **4. Option D Runtime Integration** | Live fallback dispatch handling under `UNKNOWN_INVALID` / degraded states. | `BLOCKED` (Governance required) | Operational fallback dispatch policy execution. | `GOVERNANCE_REQUIRED` (DEC-004 parameters OPEN) | `REQUIRES POLICY VALUES` | **EXCLUDED** (Blocked pending human governance decision on DEC-004 parameters) |
| **5. Forecast-Branch Integration (Stage 8.1)** | Coupling ML solar forecast model with Option B optimizer. | `BLOCKED` (Forecast branch governance) | Dispatch stability under real ML forecast error dynamics. | `NOT_ESTABLISHED` (Stage 8.1 reproducibility gate) | `REQUIRES ML ADAPTER` | **EXCLUDED** (Blocked until deterministic stress dispatch is proven) |

---

## Detailed Rationale for Exclusions

### Why Candidate 2 (168h Endurance) is Excluded:
The minimality rule explicitly states: *"Do not recommend a 168h run merely because 24h passed."* A 7-day single-scenario endurance run tests long-term numerical accumulation. However, testing dispatch feasibility across different operational stress regimes (renewable dropouts, peak load surges, battery SOC constraints) is a prior technical necessity. Multi-scenario stress validation must precede long-duration endurance runs.

### Why Candidate 3 (ECD Runtime Integration) is Excluded:
`EmergencyConditionDetector.evaluate()` requires `fuel_remaining_liters` to compute diesel endurance $t_{\text{diesel}}$. The forensic state continuity audit confirmed: `DIESEL_PHYSICAL_INVENTORY_STATE = NOT_REPRESENTED_IN_CURRENT_RUNTIME`. Integrating ECD into runtime before resolving how diesel fuel inventory is represented in `StationState` would corrupt schema contracts.

### Why Candidate 4 (Option D Runtime Integration) is Excluded:
As established in `POLARIS_EMS_DEC004_OPTION_D_FINAL_SELECTION/OPEN_ITEMS_AFTER_DEC004.md`, Option D high-level policy is selected, BUT all concrete operational parameters (Option D watchdog duration $T_{\text{max,degraded}}$, fuel reserve floor $F_{\text{reserve,min}}$, production $T_{\text{required}}$, breaker circuit mapping) remain OPEN governance decisions. Attempting runtime implementation without recorded human governance policy decisions violates the core directive: *"Do not invent production EBR/terminal/Option D values."*

### Why Candidate 5 (Stage 8.1 Forecast Integration) is Excluded:
Introducing stochastic ML forecast prediction errors before proving Option B dispatch robustness under deterministic environmental stress regimes introduces confounding error variables. Deterministic stress validation must precede ML forecast coupling.
