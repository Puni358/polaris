# POLARIS EMS — FUTURE IMPLEMENTATION TEST MATRIX

## 1. Executive Summary

This document specifies the 18-case test matrix required for offline validation if Option D implementation is authorized.

> [!CAUTION]
> **EXECUTION STATUS**: All test cases below are marked **`NOT_EXECUTED`**. No code implementation or test execution occurred during this read-only audit.

---

## 2. 18-Case Testing Matrix

| Test Case ID | Test Description | Target Verification Criteria | Execution Status |
|--------------|------------------|------------------------------|------------------|
| **TC-001** | `UNKNOWN_INVALID` Single Cycle | Verifies runner invokes Option D policy router for a single degraded step. | `NOT_EXECUTED` |
| **TC-002** | Persistent `UNKNOWN_INVALID` | Verifies multi-step state advancement under Option D degraded control. | `NOT_EXECUTED` |
| **TC-003** | `VALID` $\to$ `UNKNOWN_INVALID` Transition | Verifies clean mode transition from normal MPC to Option D critical fallback. | `NOT_EXECUTED` |
| **TC-004** | `UNKNOWN_INVALID` $\to$ `VALID` Recovery | Verifies runner clears load shed relays and resumes normal 24h MILP optimization. | `NOT_EXECUTED` |
| **TC-005** | Renewable-Only Critical Support | Verifies $P_{\text{RE}}$ is applied to $P_{\text{critical}}(t)$ when renewables cover load ($P_{\text{diesel}}=0$). | `NOT_EXECUTED` |
| **TC-006** | Diesel-Assisted Critical Support | Verifies diesel starts and dispatches when renewables are insufficient ($P_{\text{RE}} < P_{\text{critical}}$). | `NOT_EXECUTED` |
| **TC-007** | Battery-Assisted Critical Support | Verifies battery discharges for critical load when renewables + diesel are deficient (D2/D3). | `NOT_EXECUTED` |
| **TC-008** | All-Source Generation Unavailable | Verifies runner handles 0-generation state and awaits operator under D3. | `NOT_EXECUTED` |
| **TC-009** | Proportional Critical Degradation | Verifies MILP proportionally allocates power across critical systems when $P_{\text{supply}} < P_{\text{critical}}$ (D4). | `NOT_EXECUTED` |
| **TC-010** | Diesel Minimum Output Excess | Verifies excess diesel power ($P_{\text{D,min}} - P_{\text{net}}$) charges battery bank under D6. | `NOT_EXECUTED` |
| **TC-011** | Battery Charging Limit Reached | Verifies remaining excess power is curtailed when battery charging limit is hit ($P_{\text{curtail}} > 0$). | `NOT_EXECUTED` |
| **TC-012** | Operator Escalation Time Boundary | Verifies runner logs `FaultEvent` and raises SCADA alarm when $T_{\text{degraded}} \ge T_{\text{max,degraded}}$ (D5). | `NOT_EXECUTED` |
| **TC-013** | Resource-Survivability Boundary | Verifies runner logs `FaultEvent` when fuel or battery hits minimum reserve floor (D5). | `NOT_EXECUTED` |
| **TC-014** | Dynamic $P_{\text{critical}}(t)$ Tracking | Verifies optimizer tracks time-varying critical demand trajectory across horizon steps. | `NOT_EXECUTED` |
| **TC-015** | Noncritical Load Exclusion | Verifies noncritical loads remain 100% shed during Option D execution. | `NOT_EXECUTED` |
| **TC-016** | Critical-Only Battery Discharge | Verifies battery discharge is zero when critical load is 100% powered by generation. | `NOT_EXECUTED` |
| **TC-017** | Diesel-Not-for-Charging Prohibition | Verifies diesel does NOT start when renewables cover critical load ($P_{\text{RE}} \ge P_{\text{critical}}$). | `NOT_EXECUTED` |
| **TC-018** | Deterministic Reproducibility | Verifies identical inputs produce bitwise identical `DispatchPlan` metadata outputs. | `NOT_EXECUTED` |

---

## 3. Test Matrix Summary

```text
TOTAL_TEST_CASES_SPECIFIED   = 18
TEST_CASES_EXECUTED          = 0
TEST_MATRIX_STATUS           = SEALED_NOT_EXECUTED
```

Status: `TEST_MATRIX_SEALED`
