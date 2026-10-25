# POLARIS EMS — GATE-05 FIXTURE SPECIFICATION

> [!IMPORTANT]
> **ENGINEERING VALIDATION FIXTURE ONLY**
> This fixture is a controlled synthetic engineering validation environment constructed strictly to exercise existing EMS architecture and sealed governance boundaries.
> - **MUST NOT** be described as validation on a real polar station.
> - **MUST NOT** establish real station demand, wind generation, or hardware safety.
> - **MUST NOT** silently invent numerical policy thresholds.

---

## 1. Governance Context & Purpose

The purpose of Gate-05 is to assemble and validate a controlled synthetic end-to-end integration fixture that exercises all five operational pathways across the sealed governance boundaries established in Gates 01–04:

1. **Gate-01**: `GOVERNED_HYBRID` response to `UNKNOWN_INVALID` states (halt automatic optimization, preserve critical service, require authorized human operator intervention).
2. **Gate-02**: `OPTION_C_GOVERNED_CONSTRAINT_RELAXATION` hierarchy for MILP infeasibility (critical load is HARD and compulsory, noncritical loads follow governed relaxation; infeasible solve MUST NOT advance Digital Twin state).
3. **Gate-03**: `AUTOMATIC_RETURN_WITH_OPERATOR_NOTIFICATION_AND_OVERRIDE` for emergency return (automatic return from `EMERGENCY` to `NORMAL` upon ECD evaluating `NORMAL`, with operator notification event and operator override authority).
4. **Gate-04**: Engineering Interfaces and Contracts compatibility audit.

---

## 2. Tested Operational Pathways

| Path Index | Operating Path Name | Triggering Input Condition | Expected System Route | Governed Handling Strategy | Target Result Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Path 1** | `NORMAL` Pathway | Autonomy $> T_{\text{required}}$, valid telemetry | `NORMAL` Route | Option B (Native HiGHS Lexicographic MILP) $\rightarrow$ DispatchPlan $\rightarrow$ Digital Twin step $\rightarrow$ Next StationState | **PASS** |
| **Path 2** | `EMERGENCY` Pathway | Reserve Autonomy $< T_{\text{required}}$ (e.g., fuel $\le 5$L) | `EMERGENCY` Route | Option D Fallback Solver $\rightarrow$ Governed Emergency DispatchPlan $\rightarrow$ Digital Twin step $\rightarrow$ Next StationState | **PASS** |
| **Path 3** | `UNKNOWN_INVALID` Pathway | Missing / Malformed $T_{\text{required}}$ payload | `UNKNOWN_INVALID` Route | Gate-01 GOVERNED_HYBRID: Stop automatic optimization, zero simulator steps, state_advanced = False | **PASS** |
| **Path 4** | `MILP_INFEASIBILITY` Pathway | Solver status `OPTIMIZATION_INFEASIBLE` | `NORMAL` Route $\rightarrow$ Infeasible | Gate-02 Option-C Safety Invariant: Hard critical load, zero simulator steps, state_advanced = False, halt pipeline | **PASS** |
| **Path 5** | `EMERGENCY_RETURN` Pathway | Step $k$: `EMERGENCY` $\rightarrow$ Step $k+1$: ECD evaluates `NORMAL` | `EMERGENCY` $\rightarrow$ `NORMAL` | Gate-03 Policy: Automatic return to `NORMAL`, Operator Notification Event generated, Operator Override interface represented | **PASS** |

---

## 3. Truth Firewall Specification

To preserve controller isolation and prevent future leakage:
1. **Controller Isolation**: The control pipeline (`ForecastEngine`, `ECD`, `EMSControlRouter`, `Option B / Option D`) receives ONLY forecasts and current telemetry `StationState`.
2. **Simulation Boundary**: The `DigitalTwinSimulator` receives actual ground truth measurements strictly at step execution time ($t=k+1$).
3. **No Future Leakage**: No future actual ground truth trajectory data is accessible to or used by any optimizer or decision evaluator.

---

## 4. Frozen & Protected Component Boundaries

- **Forecast Artifacts**: Untouched and frozen.
- **MILP / HiGHS Implementation**: Untouched and frozen.
- **Digital Twin Simulator**: Untouched and frozen.
- **Source Code Modifications**: `SOURCE_MODIFICATIONS = 0` across all files in `system/`.

---

## 5. Verification Fixture Implementation

The synthetic integration test fixture is implemented and executable at:
[`tests/test_gate05_synthetic_fixture.py`](file:///home/punith-bs/01polaris%20%28Copy%29/tests/test_gate05_synthetic_fixture.py)
