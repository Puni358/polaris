# POLARIS EMS GATE-07 — DIESEL FUEL ACCOUNTING AUDIT

## 1. Governance Overview & Audit Purpose
This document audits the physical diesel fuel accounting logic enforced within the POLARIS EMS receding-horizon simulation architecture.

## 2. Fuel Consumption Formula Verification

The Digital Twin simulator computes fuel consumption using the frozen physical generator parameters:
$$\text{required\_fuel} = \left(\left(\text{base\_fuel\_lph if } P_{\text{diesel}} > 0 \text{ else } 0.0\right) + \left(\text{marginal\_fuel\_lpwh} \times P_{\text{diesel}}\right)\right) \times 1.0 \text{ hour}$$

Where:
- $\text{base\_fuel\_lph} = 5.0 \text{ L/h}$ (synthetic base overhead)
- $\text{marginal\_fuel\_lpwh} = 0.00025 \text{ L/Wh}$ ($0.25 \text{ L/kWh}$)
- $P_{\text{diesel}}$ is the committed action power in Watts at $k=0$.

## 3. Detailed Audit Findings

### 3.1 Initial Fuel Establishment
- Initial fuel state $F_0$ is set once during initialization from `StationState`.
- Verification Status: **PASS**

### 3.2 Fuel Propagation Continuity
- Fuel is propagated explicitly via `StationState` from cycle $k$ to cycle $k+1$:
  $$F_{k+1} = \max(0.0, F_k - \text{required\_fuel}_k)$$
- Verification Status: **PASS**

### 3.3 Protection Against Silent Resets & Unexplained Replenishment
- Fuel state is strictly non-increasing across cycles: $F_{k+1} \le F_k$.
- Fuel never increases without an explicit replenishment event.
- Verification Status: **PASS**

### 3.4 Protection Against Double Consumption
- Every executed cycle $k$ applies the fuel consumption calculation exactly once inside `DigitalTwinSimulator.step()`.
- Verification Status: **PASS**

### 3.5 Discarded Forecast Actions ($k=1 \dots 23$)
- MPC forecast actions $P_{\text{diesel}}[1 \dots 23]$ are advisory planning steps only.
- Simulator step consumes fuel strictly for $P_{\text{diesel}}[0]$.
- Verification Status: **PASS**

### 3.6 Governed Halt Boundaries (Gate-01 & Gate-02)
- `UNKNOWN_INVALID` mode halts execution prior to simulator step ($0.0 \text{ L}$ consumed, state not advanced).
- `MILP_INFEASIBLE` solver state halts execution prior to simulator step ($0.0 \text{ L}$ consumed, state not advanced).
- Verification Status: **PASS**

## 4. Audit Summary Table

| Audit Criterion | Governed Standard | Observed Behavior | Status |
| :--- | :--- | :--- | :---: |
| Single Initialization | Initial state established once at $k=0$ | Initial state set to $100.0\text{ L}$ | PASS |
| Single-Step Consumption | Exactly 1 step per cycle consumed | Consumed $\text{required\_fuel}_0$ only | PASS |
| Continuous Propagation | $F_{k+1}$ derived from $F_k$ via `StationState` | Bitwise exact state transfer | PASS |
| No Silent Resets | Fuel levels preserved across cycles | Zero reset detected | PASS |
| No Unearned Increases | Non-increasing without replenishment | Monotonically non-increasing | PASS |
| First-Action-Only | $k=0$ action only consumed | $k=1..23$ discarded without consumption | PASS |
| No Double Consumption | Single evaluation per cycle | 1x consumption applied | PASS |
| UNKNOWN_INVALID Halt | No state advancement on invalid state | 0 steps completed, state frozen | PASS |
| MILP Infeasibility Halt | No state advancement on infeasible MILP | 0 steps completed, state frozen | PASS |
