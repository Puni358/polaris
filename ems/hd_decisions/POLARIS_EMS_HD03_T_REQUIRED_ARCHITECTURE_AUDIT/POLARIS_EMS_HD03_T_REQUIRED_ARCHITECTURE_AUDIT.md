# POLARIS EMS — HD-03 T_required Architectural Decision-Structure Audit Report

**Audit Status**: COMPLETED (READ-ONLY)  
**Governance Scope**: Human Decision HD-03 Architectural Source Model for $T_{\text{required}}$  
**Target Directory**: [`POLARIS_EMS_HD03_T_REQUIRED_ARCHITECTURE_AUDIT/`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD03_T_REQUIRED_ARCHITECTURE_AUDIT/)  

---

## Executive Summary

The previous HD-03 evidence audit established that the POLARIS repository contains **no authoritative numerical $T_{\text{required}}$** and **no authoritative station resupply/recovery schedule** (`HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`).

This architectural evidence audit evaluates three candidate decision-structures for how $T_{\text{required}}$ should be represented once its value or data source is provided:

- **Option A — Operational-Input Model**: $T_{\text{required}}(t)$ is dynamically provided at runtime by station/mission operations.
- **Option B — Governed Fixed Parameter**: $T_{\text{required}}$ is a single system-wide fixed policy parameter defined in central POLARIS governance.
- **Option C — Governed Configurable Parameter**: $T_{\text{required}}$ is a mandatory deployment/station-specific configuration parameter required prior to station boot.

### Key Audit Findings

1. **Architectural Source Model Selection**: **`HD03_ARCHITECTURAL_SOURCE_MODEL = GOVERNANCE_DECISION_REQUIRED`**. The repository architecture does not declare a single mandatory source model. All three options are technically supportable, but choosing among them requires an explicit stakeholder governance decision.
2. **Prototype vs. Real-Station Dual Compatibility**: A production architecture can support both a **station-configured default** (Option C) and a **dynamic operational override** (Option A) without architectural conflict.
3. **Detector Ownership Boundary**: Across all three options, the Emergency Mode Detector **consumes** $T_{\text{required}}$; it does **not** generate, own, or infer $T_{\text{required}}$.
4. **Missing-Input Behavior**: **`HD03_MISSING_INPUT_BEHAVIOR = GOVERNANCE_REQUIRED`**. Existing governance does not establish whether the system should fail-closed (abort run) or use a fallback if $T_{\text{required}}$ is omitted at startup.
5. **Implementation & Execution Boundary**: Evaluating these architectural options does **NOT** grant authorization to modify schemas (`state.py`), update detector code, or execute solver runs.

---

## 1. Closed Governance Baseline (Preserved)

The following decisions are **FIXED** and strictly preserved:

- **HD-01A**: EBR is a critical-load-based dynamic energy target.
- **HD-01B**: EBR resilience interval **$N = 6\text{ HOURS}$** (fixed, separately governed normal-operation resilience interval).
- **HD-02**: Terminal target derived from EBR at MPC boundary ($E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$); terminal shortfall counted exactly once.
- **HD-04**: Emergency Mode Detector evaluates zero-renewable survivability ($P_{\text{solar}} = 0, P_{\text{wind}} = 0$) through $T_{\text{required}}$ as a detector-local stress scenario. Normal MPC uses causal forecasts.
- **HD-05**: Normal mode: $F_{\text{diesel}} \le 1.05 F^*$; Emergency mode: battery degradation subordinate to critical load.
- **Policy E3**: Emergency mode resource preservation policy (preserve resource with larger survivability margin).

---

## 2. Required Audit Classifications

```plain
HD03_ARCHITECTURAL_SOURCE_MODEL = GOVERNANCE_DECISION_REQUIRED
HD03_OPTION_A_STATUS = SUPPORTED
HD03_OPTION_B_STATUS = SUPPORTED
HD03_OPTION_C_STATUS = SUPPORTED
HD03_MISSING_INPUT_BEHAVIOR = GOVERNANCE_REQUIRED
HD03_DETECTOR_OWNERSHIP = GOVERNANCE_REQUIRED
HD03_RUNTIME_VARIABILITY = GOVERNANCE_REQUIRED
HD03_PROTOTYPE_MODEL = GOVERNANCE_REQUIRED
HD03_NUMERICAL_VALUE = NOT_ESTABLISHED
HD03_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED
HD03_EXECUTION_AUTHORIZATION = NOT_GRANTED
```

---

## 3. Option Comparison Matrix

| Criterion | Option A: Operational Input | Option B: Fixed Governed | Option C: Configurable |
| :--- | :--- | :--- | :--- |
| **Source** | Runtime Station / Mission Ops API | Central POLARIS Policy Config | Station Deployment Manifest |
| **Runtime Variability** | Dynamic (Per timestep or run) | Static (Constant across runs) | Static per deployment |
| **Station Portability** | High (Adapts to resupply updates) | Low (Fixed across all stations) | High (Per-station custom value) |
| **Governance Dependency**| High (Requires ops API interface) | High (Central policy approval) | High (Site manager approval) |
| **Missing-Data Issue** | Must fail-closed or log alert | Fallback in system config | Boot fails if config missing |
| **Reproducibility** | Requires logging provider ID & timestamp | Recorded via config git hash | Recorded in station manifest |
| **Schema Impact** | Requires field in `StationState` | No schema changes | Requires station config field |
| **Detector Integration**| Consumes `state.t_required_hours` | Reads system config parameter | Reads station config parameter |
| **Prototype Suitability** | Low (Requires mock ops provider) | High (Simple static config) | High (Simple deployment config) |
| **Future Station Suitability**| Maximum flexibility for real ops | Restricted for multi-site ops | High for multi-site deployment |

---

## 4. Eighteen-Point Architectural Evaluation

1. **Input Required**: Option A $\to$ Dynamic float; Option B $\to$ System float; Option C $\to$ Deployment float.
2. **Input Location**: Option A $\to$ `StationState`; Option B $\to$ `optimizer.yaml`; Option C $\to$ `station.yaml`.
3. **StationState Schema Sufficiency**: Current `StationState` ([`system/state/state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/state/state.py)) is **INSUFFICIENT** for Option A.
4. **ForecastBundle Involvement**: Not required for $T_{\text{required}}$ unless window varies per timestep.
5. **DispatchPlan Involvement**: No. DispatchPlan receives optimal control outputs, not $T_{\text{required}}$.
6. **Detector Ownership**: Detector **consumes** $T_{\text{required}}$; does not own or generate it.
7. **Time Variability**: Option A $\to$ YES; Option B $\to$ NO; Option C $\to$ NO.
8. **Station Variability**: Option A $\to$ YES; Option B $\to$ NO; Option C $\to$ YES.
9. **Missing-Value Behavior**: `GOVERNANCE_DECISION_REQUIRED` (Fail-closed vs Fallback).
10. **Provenance Requirements**: Provider ID, timestamp, validity window (Option A); Git SHA (Option B/C).
11. **Governance Authority**: Mission Ops (Option A); Governance Committee (Option B); Site Manager (Option C).
12. **Preserves HD-04 Semantics**: **YES** across all options.
13. **Preserves HD-01B ($N=6\text{h}$) Independence**: **YES** ($N=6\text{h}$ normal reserve remains independent).
14. **Preserves HD-02 Independence**: **YES** ($E_{\text{terminal\_target}}$ remains independent).
15. **Works with E3**: **YES** (Detector uses $T_{\text{required}}$ to set mode; E3 handles emergency solve).
16. **Schema Changes**: Option A requires `StationState` schema addition; Option B/C require config additions.
17. **Implementation Complexity**: Option A $\to$ Medium; Option B $\to$ Low; Option C $\to$ Low.
18. **Reproducibility**: Option A requires telemetry logging of dynamic input; Option B/C use static config hashes.

---

## 5. Final Verdict & Hard Stop Block

**Can POLARIS establish the architectural source model for $T_{\text{required}}$ from repository evidence alone?**

> **`HD03_ARCHITECTURAL_SOURCE_MODEL = GOVERNANCE_DECISION_REQUIRED`**.  
> The repository supports Options A, B, and C as valid architectural paradigms. Selecting among them is an open governance decision.

```plain
HD03_NUMERICAL_VALUE=NOT_ESTABLISHED
HD03_IMPLEMENTATION_AUTHORIZATION=NOT_GRANTED
HD03_EXECUTION_AUTHORIZATION=NOT_GRANTED
```
