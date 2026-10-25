# POLARIS EMS — DEC-004 OPTION A: HOLD LAST VALID DISPATCH

## 1. Executive Summary

This document provides a factual, evidence-based forensic analysis of **Option A: Hold Last Valid Dispatch** as an operational response to ECD `UNKNOWN_INVALID`.

---

## 2. Concept & Operational Mechanism

- **Concept**: If the ECD returns `UNKNOWN_INVALID` at timestep $k$, the EMS bypasses re-optimization and continues executing the dispatch setpoints or schedule from the most recent valid `DispatchPlan` generated at timestep $t_{k-1}$.
- **Runtime Interpretation**: Re-applies step 1 setpoints ($P_{\text{chg}}, P_{\text{dis}}, P_{\text{diesel}}$) or step $j$ setpoints from the cached plan.

---

## 3. Benefits & Technical Rationale

1. **Automation Continuity**: Prevents abrupt microgrid blackouts or unnecessary generator shutdowns during brief telemetry dropouts or temporary operational command delays.
2. **Smooth Dispatch**: Maintains continuous battery charging/discharging and generator power levels according to previously validated physics.

---

## 4. Operational Hazards & Failure Modes

1. **Horizon Expiration Hazard**: A 24-hour `DispatchPlan` contains finite steps. If `UNKNOWN_INVALID` persists longer than the plan horizon, the plan exhausts and cannot be executed further.
2. **State & Energy Drift Hazard**: Physical solar irradiance or demand may diverge significantly from the $t_{k-1}$ forecast. Holding fixed setpoints under adverse cloud cover can deplete the battery below $20\%\text{ SOC}$, triggering a terminal `FAILED_STATE_VIOLATION` in `DigitalTwinSimulator`.
3. **Critical Service Risk**: If critical demand surges above the held generator power level, the fixed setpoint cannot adapt, risking power loss to life-safety loads.

---

## 5. Implementation & Engineering Dependencies

- **Plan Memory Cache**: Requires adding a `last_valid_dispatch_plan` field to `PolarisLocalRunner`.
- **Expiration Watchdog**: Requires specifying a maximum allowed plan-hold duration (e.g. 1 to 3 steps) after which control must escalate to Option B or C.

Status: `ANALYSIS_COMPLETE`
