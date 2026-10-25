# POLARIS GAP19 — Canonical Remaining Blockers Register

This register documents all unresolved governance, engineering, station-specific, and validation blockers. No operational actions have been invented for these unresolved items.

---

## Category A: Governance Decisions Required

### A.1 UNKNOWN_INVALID Operational Action
- **Status**: `NOT_IMPLEMENTED` | `ENGINEERING_INTERFACE_BLOCKER`
- **Description**: Concrete operational response when ECD evaluates `OperatingMode.UNKNOWN_INVALID` remains unresolved.
- **Firewall Rule**: Must **NOT** invent hold-last-plan, zero-dispatch, shutdown, generator start, load shedding, operator trip, new FaultEvent severity, or automatic Option D routing.

### A.2 MILP Infeasibility Operational Response
- **Status**: `NOT_IMPLEMENTED` | `ENGINEERING_INTERFACE_BLOCKER`
- **Description**: Operational response when Option B returns `OPTIMIZATION_INFEASIBLE` remains unresolved.
- **Frozen Rule**: **NO STATE ADVANCEMENT** (`state_advanced = False`). Digital Twin state must not advance. Must **NOT** invent retry, zero-dispatch, hold-last-plan, or silent termination.

### A.3 Emergency Return Policy
- **Status**: `NOT_IMPLEMENTED` | `UNRESOLVED`
- **Description**: Automatic recovery/transition from `EMERGENCY` back to `NORMAL` mode remains unresolved.
- **Firewall Rule**: Zero hysteresis, cooldown, debounce, minimum emergency duration, or recovery thresholds authorized or implemented.

### A.4 $T_{\text{required}}$ / ECD Deployment Policy
- **Status**: `GOVERNED_BASELINE`
- **Governed Baseline**: `T_REQUIRED_BASELINE = 6 HOURS`
- **Semantics**: Protected critical service survivability duration.
- **Configuration**: Hybrid (Automated MFA cryptographic authority gate).
- **Test Value Distinction**: 72-hour survivability values are synthetic prototype test fixtures only. 72h must **NOT** be converted into station policy.

---

## Category B: Engineering Interface Definitions Required

### B.1 Production Telemetry Freshness
- **Status**: `UNRESOLVED`
- **Missing Interfaces**:
  - SCADA telemetry maximum allowable age;
  - Timestamp validity and clock-drift handling;
  - Stale fuel telemetry response;
  - Stale battery telemetry response;
  - Stale critical-load telemetry response.
- **Firewall Rule**: Zero numerical TTL values invented.

### B.2 Authentication & Authority Mechanisms
- **Status**: `UNRESOLVED`
- **Missing Interfaces**:
  - Cryptographic signature mechanism;
  - Key management and distribution;
  - Authentication transport protocol;
  - Authorization roles and RBAC schema;
  - MFA mechanism for authority override;
  - Credential rotation policy;
  - Replay protection.
- **Firewall Rule**: Zero authentication protocols invented.

---

## Category C: Station-Specific Engineering Inputs Required

### C.1 Protected Critical-Load Engineering (Real Station)
- **Status**: `NOT_ESTABLISHED`
- **Missing Station Inputs**:
  - Actual physical equipment inventory for critical systems;
  - Electrical circuit mapping and breaker topology;
  - Dynamic $P_{\text{critical}}(t)$ profile for actual station;
  - Minimum viable power thresholds for individual subsystems:
    - Heating system power curve;
    - Water treatment / filtration power curve;
    - Emergency communications equipment power curve;
  - Diesel generator minimum operating power boundary;
  - Actual diesel generator fuel consumption curve;
  - Battery charge acceptance rate under thermal constraints;
  - SOC and cell temperature operating boundaries.
- **Firewall Rule**: Synthetic prototype fixture values must **NOT** be converted into station facts.

---

## Category D: Validation & Testing Requirements

### D.1 Controlled Environment Validation Gates
- **Status**: `PENDING_FUTURE_AUTHORIZATION`
- **Required Gates**: Controlled integration readiness review, synthetic closed-loop replay, truth firewall validation, fuel state rolling continuity validation.

---

## Category E: Production Deployment Requirements

### E.1 Production Deployment Authorization
- **Status**: `NOT_AUTHORIZED`
- **Requirements**: Real-station engineering inputs, SCADA transport interfaces, cryptographic auth gates, physical deployment safety signoff.
