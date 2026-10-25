# POLARIS EMS — EMERGENCY CONDITION DETECTOR (ECD)
## IMPLEMENTATION AUTHORIZATION CONTRACT & AUDIT REPORT

**Audit Date**: 2026-09-23  
**Audit Status**: IMPLEMENTATION CONTRACT SPECIFICATION COMPLETE  
**Contract Status**: `ECD_IMPLEMENTATION_CONTRACT_STATUS = READY_FOR_IMPLEMENTATION_AUTHORIZATION`  
**Implementation Authorization**: `NOT_GRANTED` (Awaiting human decision)  
**Execution Authorization**: `NOT_GRANTED`  

---

### EXECUTIVE SUMMARY & CONTRACT STATUS REGISTER

This document establishes the authoritative, implementation-ready contract for the Emergency Condition Detector (ECD) in the POLARIS Energy Management System (EMS). This contract is derived directly from closed governance decisions (HD-01, HD-03, HD-04, E3), verified repository source code ([`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml), [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml), [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py)), and the independently audited canonical test fixture package ([`POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/)).

#### Required Status Register
```yaml
ECD_IMPLEMENTATION_CONTRACT_STATUS: READY_FOR_IMPLEMENTATION_AUTHORIZATION
ECD_SPECIFICATION_STATUS: CLOSED
INPUT_CONTRACT: COMPLETE
OUTPUT_CONTRACT: COMPLETE
SCHEMA_IMPACT: IDENTIFIED
ARCHITECTURAL_PLACEMENT: ESTABLISHED
MISSING_INPUT_BEHAVIOR: COMPLETE
AUTHORITY_MODEL: ESTABLISHED
FRESHNESS_MODEL: ESTABLISHED
PROTOTYPE_PRODUCTION_BOUNDARY: VERIFIED
ACCEPTANCE_TEST_CONTRACT: COMPLETE
GOVERNANCE_BLOCKERS:
  - "HD-06: Authorization of production fuel tank capacity and lower reserve thresholds"
  - "HD-03: Cryptographic authentication mechanism for operational T_required override"
  - "HD-03: TTL, maximum-age, and clock-drift numerical threshold authorization"
  - "HD-01: 5-tier critical demand forecast breakdown in ForecastBundle schema"
IMPLEMENTATION_EXECUTED: NO
ECD_EXECUTED: NO
SCHEMA_MODIFIED: NO
RUNTIME_MODIFIED: NO
FIXTURE_MODIFIED: NO
```

---

### 1. ECD CORE RESPONSIBILITY & BOUNDARY

#### Included Responsibilities (What the ECD DOES)
1. **Resource Survivability Assessment**: Evaluates physical endurance horizons ($T_{\text{battery}}, T_{\text{diesel}}$) for battery storage and diesel generation under zero-renewable stress conditions ($P_{\text{solar}}=0, P_{\text{wind}}=0$).
2. **Emergency Mode Classification**: Evaluates time margins ($M_r = T_r - T_{\text{required}}$ or $T_{\text{test}}$) and classifies station operating mode as `NORMAL` or `EMERGENCY`.
3. **E3 Resource Selection**: Identifies `preserved_resource` (larger time margin) and `limiting_resource` (smaller time margin). Outputs `TIE / BOTH` for exact margin ties.
4. **Validation & Fail-Closed Reporting**: Validates input completeness, authority, and freshness. Outputs `FAIL_CLOSED` when $T_{\text{required}}$ is missing, invalid, or unauthorized.

#### Excluded Responsibilities (What the ECD MUST NOT DO)
1. **No Dispatch Optimization**: Does NOT calculate power dispatch setpoints, perform MILP optimization, or solve energy balance constraints.
2. **No Control Actions**: Does NOT start/stop generators, open/close breakers, or shed electrical loads.
3. **No Parameter Ownership**: Does NOT own or invent $T_{\text{required}}$, critical demand, fuel inventory, or component parameters.
4. **No Optimizer Mutation**: Does NOT mutate MILP objective function weights, solver tolerances, or physical constraint bounds.

---

### 2. PRESERVED GOVERNANCE CONSTANTS & HORIZON SEPARATION

1. **Governed Emergency Survivability Baseline**: $T_{\text{required}} = 72.0\text{ hours}$ (`SYNTHETIC_ENGINEERING_TEST_VALUE_PRESERVED_UNCHANGED`, `STATION_MEANING = NONE`).
2. **Synthetic Logic Validation Horizon**: $T_{\text{test}} = 2.0\text{ hours}$ (`SYNTHETIC_ECD_LOGIC_VALIDATION_ONLY`, `STATION_MEANING = NONE`).
3. **Prototype Critical Load**: $P_{\text{crit}} = 30,000\text{ W}$ ($30\text{ kW}$ constant load parameter, `SYNTHETIC_ENGINEERING_TEST_PARAMETER`).
4. **Horizon Separation Rule**: The ECD implementation MUST NOT hardcode $72.0\text{h}$ or $2.0\text{h}$ as immutable internal constants. The required survivability window $T_{\text{target}}$ MUST be consumed dynamically from an authorized input source.

---

### 3. ARCHITECTURAL PLACEMENT & PIPELINE FLOW

```
[Telemetry & Forecast Data]
           │
           ▼
   [ForecastEngine] ──► ForecastBundle (with critical_demand)
           │
           ▼
    [StationState] (with fuel_remaining_liters)
           │
           ▼
┌──────────────────────────────────────────────────────────┐
│              Emergency Condition Detector                │
│  (Evaluates Survivability Margins & E3 Classification)   │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼ EmergencyAssessment
┌──────────────────────────────────────────────────────────┐
│                  EMS Controller / MPC                    │
│   (Consumes Assessment Mode to Set Optimizer Context)    │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
                   [EnergyOptimizer] (MILP) ──► DispatchPlan
```

- **Placement**: ECD sits in `system/control/` or `system/governance/`, executing AFTER state/forecast updates and BEFORE solver execution.
- **Interface**: Consumes `StationState`, `ForecastBundle`, and `battery.yaml`/`diesel.yaml`. Produces `EmergencyAssessment`.

---

### 4. GOVERNANCE BLOCKERS & IMPLEMENTATION READINESS

All technical interfaces, physical equations, test matrices, and error matrices are fully specified. The remaining governance items are explicitly logged in [`POLARIS_EMS_ECD_GOVERNANCE_BLOCKER_REGISTER.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_IMPLEMENTATION_CONTRACT_AUDIT/POLARIS_EMS_ECD_GOVERNANCE_BLOCKER_REGISTER.json).

Upon formal human review of this contract package, implementation may be authorized by granting `IMPLEMENTATION_AUTHORIZATION = GRANTED`.
