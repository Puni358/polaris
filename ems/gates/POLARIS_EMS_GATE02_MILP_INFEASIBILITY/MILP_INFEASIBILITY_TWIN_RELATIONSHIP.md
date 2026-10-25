# POLARIS GATE-02 — MILP INFEASIBILITY DIGITAL TWIN RELATIONSHIP
## ANALYSIS OF RELATIONSHIP WITH DIGITAL TWIN SIMULATOR

---

## 1. CORE GOVERNANCE QUESTION

```text
               MILP_INFEASIBLE
                     ↓
       DigitalTwinSimulator.step()

             SHOULD THIS OCCUR?
```

### Authoritative Governance Answer
```text
NO. STATE ADVANCEMENT MUST NOT OCCUR.
```

```yaml
DIGITAL_TWIN_STEP_ON_INFEASIBILITY: PROHIBITED
MILP_INFEASIBILITY_STATE_ADVANCEMENT: MUST_NOT_OCCUR
SIMULATOR_MODIFICATION: NONE
```

---

## 2. TECHNICAL & PHYSICAL REASONING

### 1. Violation of First-Action Semantics
Digital Twin first-action semantics mandate that `DigitalTwinSimulator.step(action_k0)` commits the first control vector ($k=0$) of an **authorized, physically feasible dispatch plan**.
When HiGHS returns `MILP_INFEASIBLE`, **no valid control vector $action_{k=0}$ exists**.

### 2. Physical Corruption of Zero-Dispatch Stepping
In pre-existing runner code, `runner.py` passed a dummy zero action ($P_{\text{diesel}}=0$, $P_{\text{battery}}=0$) to `simulator.step()`.
- **Battery Dynamics Corruption**: The simulator applies battery self-discharge and updates SOC down, simulating battery drain while load is completely dropped.
- **Unmet Load Corruption**: The simulator logs 100% unmet load for step $k$, recording a artificial blackout in simulation memory despite physical generators and batteries having fuel and charge available.
- **Fuel Accounting Drift**: Simulated fuel remains unchanged, but physical station hardware (if operating on local fallback governors) may be burning fuel, causing software state and physical reality to diverge irreparably.

### 3. State Inconsistency & Non-Recoverability
If `DigitalTwinSimulator.step()` is invoked on infeasibility:
- The `StationState` advances to $k+1$ under a corrupted state trajectory.
- At timestep $k+1$, the optimizer will attempt to solve from a degraded state (e.g., lower SOC, lost time step), exacerbating infeasibility in subsequent cycles.
- Stopping state advancement at step $k$ preserves the last valid `StationState`, allowing system recovery once governance or operator intervention resolves the blocker.

---

## 3. SUMMARY OF PROHIBITIONS

1. **DO NOT** invoke `DigitalTwinSimulator.step()` when `plan.constraint_status.startswith("OPTIMIZATION_INFEASIBLE")`.
2. **DO NOT** modify `system/simulation/simulator.py` to add automatic fallback handling.
3. **DO NOT** mutate `StationState` variables when the optimizer reports infeasibility.
