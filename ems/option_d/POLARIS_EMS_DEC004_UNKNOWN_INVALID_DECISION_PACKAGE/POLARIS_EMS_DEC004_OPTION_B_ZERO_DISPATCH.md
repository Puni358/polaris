# POLARIS EMS — DEC-004 OPTION B: ZERO-DISPATCH FAIL-CLOSED CONTROL

## 1. Executive Summary

This document provides a factual, evidence-based forensic analysis of **Option B: Zero-Dispatch Fail-Closed Control** as an operational response to ECD `UNKNOWN_INVALID`.

---

## 2. Concept & Operational Mechanism

- **Concept**: If the ECD returns `UNKNOWN_INVALID` at timestep $k$, the system enforces zero controllable generation:
  $$P_{\text{battery,charge}} = 0, \quad P_{\text{battery,discharge}} = 0, \quad P_{\text{diesel}} = 0$$
- **Runtime Interpretation**: Reuses the zero-power physics mechanism defined in `POLARIS_SYSTEM_D4C0_FAILURE_CONTRACT.md` for MILP infeasibility.

---

## 3. Benefits & Technical Rationale

1. **Energy Safety**: Completely prevents battery over-discharge, thermal runaway risk, and uncontrolled fuel burn during corrupted/unverified operational states.
2. **Predictable Physics**: Zero-power state advancement is natively implemented and validated in `DigitalTwinSimulator`.

---

## 4. Operational Hazards & Load Implications

1. **Critical Load Interruption**: Enforcing $P_{\text{diesel}} = 0$ and $P_{\text{dis}} = 0$ forces all station electrical demand to become unmet load ($P_{\text{unmet}} = P_{\text{demand}}$), unless uncurtailed solar/wind directly powers loads.
2. **Blackout Risk**: Creates immediate power disruption for life-safety, communications, and emergency services.

---

## 5. Implementation & Engineering Dependencies

- **Contract Extension**: Requires extending the D4-C0 failure contract from MILP infeasibility to cover ECD input failures (`UNKNOWN_INVALID`).
- **Telemetry Severity**: Logs `FaultEvent(fault_class="INVALID_SURVIVABILITY_ASSESSMENT", severity="GOVERNED_DEGRADED", response="GOVERNED_ZERO_DISPATCH")`.

Status: `ANALYSIS_COMPLETE`
