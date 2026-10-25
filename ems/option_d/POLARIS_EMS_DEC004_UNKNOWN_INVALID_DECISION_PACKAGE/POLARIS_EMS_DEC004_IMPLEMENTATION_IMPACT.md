# POLARIS EMS — DEC-004 IMPLEMENTATION IMPACT ANALYSIS

## 1. Overview

This document specifies the required software modifications, schema updates, state handlers, and testing layers required if Candidate Option A, B, C, or D is selected by the human governance decision-maker.

---

## 2. Option-by-Option Implementation Requirements

> [!NOTE]
> All schema modifications, runtime additions, and test cases below are **PROPOSED FUTURE IMPLEMENTATION** items. None are approved, authorized, or implemented. Implementation requires prior human governance decision selecting the option and explicit engineering authorization.

### 2.1 Requirements for OPTION A (Hold Last Valid Dispatch) [PROPOSED FUTURE IMPLEMENTATION]
- **Runtime Changes**: [Proposed] Modify `PolarisLocalRunner.run_pipeline()` to cache `last_valid_dispatch_plan`. When `ecd.evaluate()` returns `UNKNOWN_INVALID`, substitute `last_valid_dispatch_plan` for current step.
- **Schema Changes**: [Proposed Proposal] Add `plan_hold_count: int` to `DispatchPlan` metadata — *REQUIRES GOVERNANCE/ENGINEERING AUTHORIZATION*.
- **State Handling**: [Proposed] Implement a timeout watchdog (e.g. max 3 steps hold) after which execution escalates to `CRITICAL_TERMINATION`.
- **Testing**: [Proposed] Add integration test `test_ecd_unknown_invalid_hold_plan()` verifying plan reuse.

### 2.2 Requirements for OPTION B (Zero-Dispatch / Fail-Closed Control) [PROPOSED FUTURE IMPLEMENTATION]
- **Runtime Changes**: [Proposed] Modify `PolarisLocalRunner.run_pipeline()` to generate a `GOVERNED_ZERO_DISPATCH` plan when ECD returns `UNKNOWN_INVALID`.
- **Schema Changes**: [Proposed Proposal] Extend D4-C0 `FaultEvent` logging to record `fault_class="INVALID_SURVIVABILITY_ASSESSMENT"`, `severity="GOVERNED_DEGRADED"` — *REQUIRES GOVERNANCE/ENGINEERING AUTHORIZATION*.
- **State Handling**: [Proposed] Advance state via 0-power simulator physics ($P_{\text{chg}}=0, P_{\text{dis}}=0, P_{\text{diesel}}=0$).
- **Testing**: [Proposed] Add integration test `test_ecd_unknown_invalid_zero_dispatch()` verifying zero power.

### 2.3 Requirements for OPTION C (Operator / Manual Intervention) [PROPOSED FUTURE IMPLEMENTATION]
- **Runtime Changes**: [Proposed] Modify `PolarisLocalRunner.run_pipeline()` to raise a fatal fault event when ECD returns `UNKNOWN_INVALID`.
- **Schema Changes**: [Proposed Proposal] Record `FaultEvent(fault_class="INVALID_SURVIVABILITY_ASSESSMENT", severity="CRITICAL_TERMINATION", response="FAILED_TERMINATED")` — *REQUIRES GOVERNANCE/ENGINEERING AUTHORIZATION*.
- **State Handling**: [Proposed] Immediately break MPC loop and lock `execution_status = "FAILED_TERMINATED"`.
- **Testing**: [Proposed] Add integration test `test_ecd_unknown_invalid_operator_trip()` verifying pipeline halt.

### 2.4 Requirements for OPTION D (Protected Critical-Load Fallback) [PROPOSED FUTURE IMPLEMENTATION]
- **Runtime Changes**: [Proposed] Add a Critical Load Shedder / Policy Router module in `PolarisLocalRunner`. When ECD returns `UNKNOWN_INVALID`, suppress noncritical load dispatch, route renewable generation to authorized critical load, and dispatch diesel to cover remaining critical load.
- **Schema Changes**: [Proposed Proposal] Add `protected_critical_load_w: Optional[float]` and `shed_noncritical_load_w: Optional[float]` to `DispatchPlan` metadata — *REQUIRES GOVERNANCE/ENGINEERING AUTHORIZATION*.
- **State Handling**: [Proposed] Advance state via simulator applying renewable + diesel power to critical load ONLY.
- **Testing**: [Proposed] Add integration test `test_ecd_unknown_invalid_protected_critical_fallback()` verifying load shedding and critical load protection.

Status: `IMPACT_ANALYSIS_COMPLETE`
