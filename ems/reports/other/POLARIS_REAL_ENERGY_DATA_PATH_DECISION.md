# POLARIS — REAL ENERGY-DEMAND DATA PATH DECISION RECORD

## 1. Purpose

This document provides neutral decision support for the project team to determine the future direction of real energy-demand data integration in the POLARIS system. 

It presents a factual, evidence-supported analysis of the two currently identified actionable paths:
- **Path A**: Formal Restricted-Data Access
- **Path B**: Explicitly Authorized Hybrid Scenario

This decision record does **NOT** select, recommend, rank, or score either path. It provides neutral documentation so that project governance can make an informed decision.

---

## 2. Authoritative Current State

The current authoritative findings from the closed reconnaissance, acquisition/inspection, and system integration phases are:

- **Real Energy Data Status**: `REAL DATA ACCESS RESTRICTED`
- **Acquisition & Inspection Outcome**: The acquisition and inspection phase did **NOT** establish an openly accessible continuous high-resolution measured polar-station electrical-demand dataset.
- **Inspected Evidence Inventory**:
  - *SITES Nuolja*: Real hourly $SW_{in}$ (shortwave solar irradiance) data exists, but it is **NOT** electrical demand.
  - *AADC Antarctic Station Records*: Monthly energy totals were available, but not the required continuous high-resolution measured demand series.
  - *SANAE IV*: Source documentation/literature describes 1-hour logging, but the raw measured time series was not obtained because access is restricted.
  - *Princess Elisabeth Station*: Source documentation/literature describes operational/load profiles, but raw telemetry was not obtained because access is restricted.
  - *ACEP Arctic Microgrid Sources*: Relevant microgrid/load information exists, but required raw data access is restricted/institutional.
  - *OpenEI / Kaggle Remote-Microgrid Datasets*: Explicitly treated as synthetic/anonymized proxies, **NOT** real polar-station demand.
- **Adapter Implementation Status**: No real-data adapter has been implemented (`NOT IMPLEMENTED / NOT AUTHORIZED`).
- **Synthetic Fixtures**: The synthetic POLARIS station/grid fixtures (`demo_scenario.json`, `synthetic_168h_endurance_scenario.json`, `renewable_stress_scenario.json`, `demand_stress_scenario.json`, `battery_stress_scenario.json`) remain valid, fully preserved, and locked as the active regression test backend.
- **Validated Architecture**: The canonical pipeline remains intact:  
  `DataProvider` → `StationState` → `ForecastEngine` → `ForecastBundle` → `EnergyOptimizer` (MILP) → `DispatchPlan` → `DigitalTwin` → `Evaluation`.
- **Interface & Schema Contracts**: All frozen schemas (`StationState` v1.0, `ForecastBundle` v1.0.0, `DispatchPlan` v1.0), MILP optimization formulations, MPC semantics, and Digital Twin physics remain 100% frozen, protected, and unchanged.

---

## 3. Decision Required

The project team must make an explicit governance decision between the two currently identified actionable paths:

1. **Path A — Formal Restricted-Data Access**: Pursue formal access to a restricted continuous high-resolution measured polar-station demand dataset from an appropriate station or institutional source.
2. **Path B — Explicitly Authorized Hybrid Scenario**: If measured polar-station demand cannot practically be obtained, separately authorize a clearly labelled hybrid scenario combining legitimate measured renewable/weather observations with explicitly modelled demand components.

*Note*: Future evidence may establish additional legitimate paths; Path A and Path B are not treated as permanently exhaustive. Creation of this decision record does **NOT** constitute authorization for either path.

```text
PROJECT DECISION:
PENDING HUMAN AUTHORIZATION
```

---

## 4. Path A — Formal Restricted-Data Access

### A. Objective
Pursue formal institutional authorization to obtain and validate a continuous high-resolution measured polar-station electrical-demand dataset.

### B. Required Inputs
Authorized raw measured electrical demand time-series data from an active or historical polar station.

### C. Required Access / Authorization
Formal institutional data request, data-sharing agreement, credentials, or explicit operator authorization.

### D. Engineering Work Required After Authorization
- Inspect and validate raw measurement quality, timestamps, missing values, and physical units ($\text{kW} \to \text{W}$).
- Determine temporal resolution, coverage, and continuity.
- Assess boundary compatibility with `StationState` and `LocalDataProvider`.
- Design, implement, and verify a dedicated `RealDataIngestionAdapter`.
- Execute unit and integration validation suites on adapter output.

### E. Scientific Validity / What It Would Allow Us to Claim
If obtained and validated, it would allow claiming system execution and evaluation against actual measured polar-station electrical demand.

### F. What It Would NOT Allow Us to Claim
- Does **NOT** allow claiming global generalization across all polar stations.
- Does **NOT** allow claiming real-world physical safety guarantees or live operational control validation.
- Does **NOT** allow claiming empirical Stage8.1 → EMS causality unless Stage8.1 is also authorized and connected.

### G. Main Dependencies
- Successful formal access approval from station data owners or institutional repositories.
- Delivery of uncorrupted, continuous, high-resolution demand series.

### H. Main Limitations
- Timelines, approval probabilities, and costs for institutional access: `NOT ESTABLISHED BY CURRENT EVIDENCE.`
- Potential data gaps, confidentiality restrictions, or non-disclosure terms.

### I. Reproducibility Implications
If access is restricted or proprietary, third-party reproduction may require explicit access credentials or data-sharing agreements.

### J. Relationship to Existing Frozen POLARIS Architecture
Integrates strictly upstream of `LocalDataProvider` via a dedicated adapter. Requires zero modifications to frozen EMS, MILP, MPC, or Digital Twin logic.

### K. What Must Happen Before Implementation Can Begin
1. Formal project decision selecting Path A.
2. Formal data request submitted and approved by station operators.
3. Raw measurement dataset delivered and quality audited.
4. Explicit governance authorization to proceed with adapter implementation.

---

## 5. Path B — Explicitly Authorized Hybrid Scenario

### A. Objective
Construct and evaluate an explicitly labelled hybrid scenario combining legitimate measured renewable/weather observations with explicitly modelled demand components.

### B. Required Inputs
- Real measured solar irradiance / weather observations (e.g., SITES Nuolja $SW_{in}$).
- Legitimate measured demand sources where available.
- Explicitly documented synthetic/modelled demand trajectories where measured station demand is unavailable.

### C. Required Access / Authorization
Explicit project governance authorization specifying the hybrid scenario scope, allowed parameter bounds, and mandatory labelling rules.

### D. Engineering Work Required After Authorization
- Define explicit mathematical models or profile generators for polar station demand.
- Implement hybrid data provider / scenario generator.
- Label all outputs explicitly as HYBRID / MODELLED-SYSTEM artifacts.
- Validate dataset integrity through the `DataProvider` → `StationState` pipeline.

### E. Scientific Validity / What It Would Allow Us to Claim
Allows evaluating EMS/MPC optimization performance and control interactions under realistic environmental driving conditions with explicitly controlled demand assumptions.

### F. What It Would NOT Allow Us to Claim
- Must **NOT** be presented as a fully measured polar-station system.
- Must **NOT** be claimed as real-station empirical validation.
- Must **NOT** be claimed as empirical validation of actual station demand.
- Must **NOT** be claimed as a replacement for the missing measured-demand dataset.

### G. Main Dependencies
- Project governance authorization for hybrid scope.
- Validated real renewable/weather time series.

### H. Main Limitations
- Demand profiles rely on synthetic/modelled assumptions rather than empirical telemetry.

### I. Reproducibility Implications
Fully reproducible using open weather datasets and published demand model scripts.

### J. Relationship to Existing Frozen POLARIS Architecture
Fully compatible with `LocalDataProvider` and existing pipeline; requires zero modifications to downstream frozen contracts.

### K. What Must Happen Before Implementation Can Begin
1. Formal project decision selecting Path B.
2. Written governance authorization specifying allowed hybrid parameters and explicit labelling rules.
3. Scenario generator implementation plan approved.

---

## 6. Neutral Comparison

| Category | Path A: Formal Restricted-Data Access | Path B: Explicitly Authorized Hybrid Scenario |
| :--- | :--- | :--- |
| **Primary Data Source** | Real measured polar station demand time series | Measured weather/renewable data + modelled demand |
| **Access Requirement** | Formal institutional access request / agreement | Project governance authorization |
| **Empirical Validity** | Measured station demand trajectory | Synthetic/modelled demand trajectory |
| **Third-Party Reproducibility** | Subject to data access restrictions | 100% reproducible with open code/weather data |
| **Timeline / Access Likelihood**| `NOT ESTABLISHED BY CURRENT EVIDENCE` | Immediate upon project authorization |
| **Downstream Architecture Impact**| Zero change to frozen EMS/contracts | Zero change to frozen EMS/contracts |
| **Primary Claim Boundary** | Validated on actual station demand | Validated on hybrid weather/modelled demand |

---

## 7. Scientific Claim Boundaries

Neither Path A nor Path B, by itself, automatically establishes:
- Real-station operational validation;
- Generalization across polar stations;
- Global EMS robustness guarantees;
- Real-world physical safety guarantees;
- Empirical Stage8.1 → EMS causality;
- Universal forecasting-to-operations benefit.

---

## 8. Architectural Compatibility

Preserve the established architectural finding:

> *"No frozen-contract incompatibility was identified during reconnaissance/inspection; adapter feasibility appears possible, subject to obtaining and validating the required high-resolution measurements."*

This finding confirms architectural boundary feasibility, but does **NOT** imply that:
- The adapter is validated;
- The adapter is ready;
- Real-data integration is complete;
- Real-data compatibility is 100% proven;
- The real-data path has been experimentally demonstrated.

The target downstream execution pipeline remains:  
`Real measured demand` → `authorized provider/adapter` → `StationState` → `existing ForecastEngine boundary` → `ForecastBundle v1.0` → `frozen EMS / MILP / MPC` → `DispatchPlan` → `DigitalTwin` → `Evaluation`.

---

## 9. Dependencies and Preconditions

- **Path A Preconditions**:  
  Project decision → Formal data request submitted → Access granted → Dataset received → Measurement quality audited → Adapter implementation authorized.

- **Path B Preconditions**:  
  Project decision → Hybrid scenario scope defined → Labelling rules established → Governance authorization granted → Scenario generator implementation authorized.

---

## 10. Synthetic Fixture Preservation

Synthetic fixtures (`demo_scenario.json`, `synthetic_168h_endurance_scenario.json`, `renewable_stress_scenario.json`, `demand_stress_scenario.json`, `battery_stress_scenario.json`) remain locked and preserved. 

They serve as the validated engineering and regression test backend and must **NOT** be deleted, modified, or reinterpreted as measured station demand.

---

## 11. Stage8.1 and D5 Status

- **Stage8.1 Status**: `STAGE8.1: FROZEN / NOT CONNECTED / NOT AUTHORIZED`.
- **D5 Status**: `D5: CLOSED / UNTOUCHED / NOT RERUN`.

---

## 12. Decision Authority

The current evidence establishes that real measured high-resolution demand access is restricted.

The project team must decide whether to:
1. Pursue formal restricted-data access (Path A), **OR**
2. Separately authorize a clearly labelled hybrid scenario (Path B).

No implementation should begin until that decision is explicitly authorized.  
Creation of this decision record does **NOT** constitute authorization for either path.

```text
PROJECT DECISION:
PENDING HUMAN AUTHORIZATION
```

---

## 13. Required Next Action After Human Decision

Once the project team renders a formal decision:
- If Path A is selected: Initiate formal data request process to target station operators.
- If Path B is selected: Draft hybrid scenario specification document for governance sign-off.
- No software implementation, data ingestion, or experiment shall be initiated prior to explicit authorization.

---

## 14. Final Status

```text
REAL ENERGY-DEMAND PATH:
DECISION PENDING HUMAN AUTHORIZATION

ACCESS STATUS:
REAL DATA ACCESS RESTRICTED

ADAPTER STATUS:
NOT IMPLEMENTED / NOT AUTHORIZED

HYBRID SCENARIO:
NOT AUTHORIZED

STAGE8.1:
FROZEN / NOT CONNECTED / NOT AUTHORIZED

D5:
CLOSED / UNTOUCHED / NOT RERUN

SYNTHETIC FIXTURES:
PRESERVED

ARCHITECTURAL COMPATIBILITY:
NO FROZEN-CONTRACT INCOMPATIBILITY IDENTIFIED DURING RECONNAISSANCE/INSPECTION
```
