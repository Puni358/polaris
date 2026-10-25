# Controlled Test Design Specification

## 1. Scope & Purpose

This document designs the controlled static and integration verification test suite for validating the Option-B J2 implementation once implementation authorization is granted.

**Strict Governance Directive**: This test suite is **DESIGNED ONLY** and MUST NOT be executed during this design phase.

---

## 2. Ten Verification Test Cases

### Test Case 1: $J_1$ Highest Priority Verification
- **Purpose**: Verify that Stage 1 ($J_1$, critical load shedding) strictly dominates Stage 2 ($J_2$, reserve maintenance) and Stage 3 ($J_3$, fuel).
- **Test Input (Symbolic)**: Grid outage scenario where solar generation is zero and initial battery energy is $E_{\text{init}} < E_{\text{stage2,target}}[0]$.
- **Expected Outcome**: The optimizer discharges the battery down to $E_{\text{min}}$ (incurring $J_2 > 0$) to keep $J_1 = 0$ (zero critical load shedding).

### Test Case 2: Governed EBR 6-Hour Semantics Verification
- **Purpose**: Verify that $E_{\text{EBR,target}}[t]$ dynamically scales with forward 6-hour critical load forecast $P_{\text{crit}}[k]$.
- **Test Input (Symbolic)**: Critical load step increase at $t = 12$ ($P_{\text{crit}}[12..17] = P_{\text{high}}$).
- **Expected Outcome**: $E_{\text{stage2,target}}[t]$ ramps up starting at $t = 7$ (6 hours prior to peak) and returns to baseline after $t = 17$.

### Test Case 3: Independent Terminal Reserve Representation
- **Purpose**: Verify that Terminal Reserve $E_{\text{term,target}}$ enforces end-of-horizon state viability independently of EBR.
- **Test Input (Symbolic)**: Low critical load at $t=23$ ($E_{\text{EBR,target}}[23] = E_{\text{low}}$) but high terminal policy ($E_{\text{term,target}} = E_{\text{high}}$).
- **Expected Outcome**: $E_{\text{stage2,target}}[23] = E_{\text{high}}$, preserving terminal battery energy for the next cycle.

### Test Case 4: Double-Counting Elimination Verification
- **Purpose**: Verify that a $10\text{ kWh}$ deficit at timestep $t=23$ incurs exactly a single $10 \cdot w_{J2}[23]$ penalty in $J_2$.
- **Test Input (Symbolic)**: Set $E[24] = E_{\text{stage2,target}}[23] - 10\text{ kWh}$.
- **Expected Outcome**: $J_2$ objective value equals exactly $10.0\text{ Wh}$, confirming zero double-counting.

### Test Case 5: 24-Hour Rolling MPC Horizon Semantics
- **Purpose**: Verify that optimization horizon $H = 24$ is maintained across rolling cycles.
- **Test Input (Symbolic)**: Run 24 sequential MPC steps using `PolarisLocalRunner`.
- **Expected Outcome**: Every solve receives a 24-element `ForecastBundle` and outputs a 24-element `DispatchPlan`.

### Test Case 6: No 30-Hour Forecast Request Verification
- **Purpose**: Verify that `ForecastEngine.predict()` is called with `horizon_hours = 24` and returns 24 timestamps.
- **Expected Outcome**: `len(bundle.timestamps) == 24` at every step; zero 30-hour forecast requests.

### Test Case 7: Truth Firewall & Zero Future Leakage
- **Purpose**: Verify that `EnergyOptimizer` and `ForecastEngine` receive ZERO future ground-truth data.
- **Expected Outcome**: `get_runtime_state()` returns strictly past history up to $t_{\text{now}}$.

### Test Case 8: $J_3$ Fuel Liters Verification
- **Purpose**: Verify that Stage 3 ($J_3$) measures diesel fuel consumption in Liters.
- **Expected Outcome**: $J_3 = \text{Fuel}_{\text{total}}$ in Liters, correctly accounting for marginal, base, and startup fuel.

### Test Case 9: $J_4$ Renewable Curtailment Verification
- **Purpose**: Verify that Stage 4 ($J_4$) measures avoidable renewable curtailment in Watt-hours.
- **Expected Outcome**: $J_4 = \sum (P_{\text{curt\_sol}} + P_{\text{curt\_wind}}) \Delta t$ in Wh.

### Test Case 10: `DispatchPlan` Schema Compliance
- **Purpose**: Verify that `DispatchPlan` outputs comply with schema version `1.0.0`.
- **Expected Outcome**: `DispatchPlan.from_dict(plan.to_dict())` passes all non-negativity, finite numerics, and exclusivity checks.

---

## 3. Test Execution Authorization Status

```text
CONTROLLED_TEST_SUITE = DESIGNED_ONLY
TEST_EXECUTION = NOT_EXECUTED
```
