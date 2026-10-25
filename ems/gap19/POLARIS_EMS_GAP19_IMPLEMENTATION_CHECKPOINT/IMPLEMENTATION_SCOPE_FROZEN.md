# POLARIS GAP19 — Frozen Implementation Scope Specification

This document defines the frozen boundaries of the completed technical implementation.

## 1. Rolling Diesel Fuel State
- **Initialization**: Initial fuel loaded once from `configs["diesel"]["initial_fuel_l"]`.
- **State Propagation**: `StationState.diesel_fuel_remaining_liters` carries rolling fuel state through receding horizon cycles.
- **ECD Input**: `ECD.evaluate(...)` receives current rolling fuel.
- **Consumption Model**: `DigitalTwinSimulator.step()` consumes physical fuel for committed first action $k=0$ (`DispatchPlan.diesel_power[0]`) ONLY:
  $$\text{required\_fuel} = (\text{base\_fuel\_lph} \cdot \mathbf{1}_{p_{\text{diesel}}>0} + \text{marginal\_fuel\_lpwh} \cdot p_{\text{diesel}}[0]) \cdot 1.0\,\text{h}$$
- **Physical Bounds**: `next_fuel = max(0.0, available_fuel - required_fuel)`. Over-consumption is observable and does not trigger automatic emergency policy or start/stop diesel.

## 2. EMS Control Router
- `OperatingMode.NORMAL` → Route to Option B (`GAP19HighsNativeOptimizer`).
- `OperatingMode.EMERGENCY` → Route to Option D (`OptionDFallbackSolver`).
- `OperatingMode.UNKNOWN_INVALID` → Classified as `UNKNOWN_INVALID`; blocks Option B and Option D. Operational response is `NOT_IMPLEMENTED` (`ENGINEERING_INTERFACE_BLOCKER`).

## 3. Option D Protected Critical Fallback
- Conforms strictly to sealed D1–D6 governance:
  - Protects critical load; sheds non-critical load.
  - Direct renewable generation first.
  - Diesel support for remaining load when fuel available.
  - Battery discharge permitted when necessary to maintain protected service, including when battery is limiting resource.
  - Resource margins: larger = preserved; smaller = limiting; equal = TIE/BOTH.
  - Proportional critical load allocation factor $\alpha = P_{\text{crit\_avail}} / \sum P_{i,\min}$ ($0 \le \alpha \le 1$).
  - Excess diesel charges battery ONLY when diesel is running for load. Diesel NEVER started solely to charge battery.
  - `OPTION_D_OBJECTIVE_VALUE = NOT_APPLICABLE / ENGINEERING_INTERFACE_REQUIRED`. Zero arbitrary MILP objective minimization invented.
  - Evaluates single-step $k=0$ emergency decision extended to array of length 24 to satisfy schema. Zero multi-hour MPC optimization performed.

## 4. MILP Infeasibility Containment
- Infeasibility status from Option B (`OPTIMIZATION_INFEASIBLE`) is **NOT** an emergency.
- Digital Twin state advancement: **MUST NOT OCCUR** (`state_advanced = False`).
- Zero fuel decrement, zero automatic Option D routing, zero retry, zero zero-dispatch, zero hold-last-plan, zero shutdown, zero invented runner policy.
- Operational response is `NOT_IMPLEMENTED` (`ENGINEERING_INTERFACE_BLOCKER`).
