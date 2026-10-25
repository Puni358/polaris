# POLARIS GATE-02 — MILP INFEASIBILITY ECD RELATIONSHIP
## ANALYSIS OF RELATIONSHIP WITH EARLY CRISIS DETECTION (ECD)

---

## 1. FROZEN GOVERNANCE RULE

The authoritative rule governing the relationship between MILP infeasibility and Early Crisis Detection (ECD) is:

```text
DO NOT automatically rerun ECD merely because the optimizer failed.
```

```yaml
ECD_RELATIONSHIP: DEFINED
NO_AUTOMATIC_ECD_RERUN: AUTHORIZED
NO_AUTOMATIC_OPTION_D_ROUTING: AUTHORIZED
```

---

## 2. FUNCTIONAL SEPARATION: PHYSICAL EVALUATION VS. OPTIMIZATION

```text
+------------------------------------+       +------------------------------------+
|   EARLY CRISIS DETECTION (ECD)     |       |     ENERGY OPTIMIZER (MILP)        |
|                                    |       |                                    |
| - Domain: Physical Reality         |       | - Domain: Mathematical Horizon     |
| - Inputs: Current Telemetry        |       | - Inputs: Forecasts & Constraints  |
| - Evaluates: Asset Degradation,    |  -->  | - Evaluates: 24-Hour Economic      |
|   Fuel Reserves, Hardware Faults   |       |   & Operational Trajectory         |
| - Outputs: NORMAL / UNKNOWN /      |       | - Outputs: Optimal DispatchPlan    |
|   EMERGENCY                        |       |   or MILP_INFEASIBLE               |
+------------------------------------+       +------------------------------------+
```

### Key Differences
1. **Physical Telemetry vs. Forecast Trajectory**:
   - ECD evaluates measured physical telemetry at timestep $k$ (e.g., fuel level, battery voltage, grid presence).
   - MILP evaluates a 24-hour lookahead trajectory combining physical telemetry with weather forecasts, load demand predictions, and mathematical boundary constraints.
2. **Direction of Dependency**:
   - Information flows from ECD to Optimizer: ECD assessment determines whether Option B (for `NORMAL`) or Option D (for `EMERGENCY`) is selected.
   - Information does NOT flow backward from Optimizer to ECD: A mathematical solver failure during 24-hour optimization does NOT retroactively alter physical telemetry measured at $k=0$.

---

## 3. GOVERNANCE ANALYSIS OF RERUNNING ECD ON INFEASIBILITY

### Scenario A: Rerunning ECD on Existing Telemetry
- If `gap19_highs_native.py` returns `MILP_INFEASIBLE`, rerunning ECD on the exact same telemetry will produce the exact same assessment (`NORMAL`).
- Rerunning ECD provides zero new information and does not resolve solver infeasibility.

### Scenario B: Forcing ECD to Return `EMERGENCY` on Infeasibility
- Overriding ECD to output `EMERGENCY` whenever `MILP_INFEASIBLE` occurs would corrupt ECD's core physical domain integrity.
- ECD would no longer represent physical station health, but would instead act as a synthetic error flag for optimization solver failures.

---

## 4. FUTURE POLICY CONDITIONS FOR ECD RE-EVALUATION

Any future proposal seeking to couple solver infeasibility with ECD re-evaluation must satisfy all of the following governance preconditions:

1. **New Telemetry Arrival**: ECD re-evaluation is authorized only if fresh physical telemetry has been ingested since the start of the optimization solve.
2. **Forecast Invalidation Protocol**: A formal mechanism must exist to declare forecast input corruption prior to re-evaluating ECD.
3. **Strict Domain Preservation**: ECD must never output `EMERGENCY` unless physical asset thresholds (fuel, battery, grid, hardware fault) are breached. Solver status must remain isolated from physical state assessment.

---

## 5. CONCLUSION

Under Gate-02, **ECD is not re-invoked upon MILP infeasibility**. The ECD assessment recorded at the beginning of the control cycle remains authoritative for that cycle.
