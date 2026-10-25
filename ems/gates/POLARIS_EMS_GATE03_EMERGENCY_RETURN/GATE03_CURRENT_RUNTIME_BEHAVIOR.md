# POLARIS GATE-03 — CURRENT RUNTIME BEHAVIOR
## FORENSIC AUDIT OF EMERGENCY ENTRY, EMERGENCY RETURN, AND ROUTER EXECUTION PATHS

---

## 1. DETAILED RUNTIME CONTROL FLOW TRACE

The runtime execution path governing emergency condition evaluation and routing is traced below:

```text
StationState (step k) + ForecastBundle + Configs
                     │
                     ▼
        EMSControlRouter.evaluate_and_route() (router.py)
                     │
                     ▼
      EmergencyConditionDetector.evaluate() (ecd.py)
                     │
      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼
   NORMAL        EMERGENCY    UNKNOWN_INVALID
      │              │              │
      ▼              ▼              ▼
  Option B       Option D      Fail-Closed
  Optimizer      Fallback       Loop Break
 (MILP HiGHS)    Solver      (CRITICAL_TERMINATION)
```

---

## 2. FORENSIC CLASSIFICATION OF RUNTIME STATE TRANSITIONS

| State Transition / Component | Current Implementation Status | Observed Code Behavior in `runner.py` / `router.py` | Governance Status |
| :--- | :--- | :--- | :--- |
| **`NORMAL → EMERGENCY` Entry** | **IMPLEMENTED (Stateless)** | Evaluated at step $k$. If ECD returns `EMERGENCY`, `router.py` routes to `"EMERGENCY"` and calls Option D fallback solver. | **IMPLEMENTED** |
| **`EMERGENCY → NORMAL` Return** | **IMPLEMENTED (Stateless)** | Evaluated at step $k+1$. If ECD returns `NORMAL` on step $k+1$, `router.py` immediately returns `"NORMAL"` and calls Option B (MILP). Zero hysteresis or cooldown. | **GOVERNANCE_REQUIRED** |
| **`UNKNOWN_INVALID` Response** | **IMPLEMENTED (Safety Halt)** | `router.py` outputs `"UNKNOWN_INVALID"`. `runner.py` logs `CRITICAL_TERMINATION` / `FAILED_TERMINATED`, `state_advanced=False`, and breaks loop. | **SEALED (Gate-01 Governed Hybrid)** |
| **`MILP_INFEASIBILITY` Response** | **IMPLEMENTED (Safety Halt)** | `gap19_highs_native.py` returns `OPTIMIZATION_INFEASIBLE`. `runner.py` logs `GOVERNED_DEGRADED`, `state_advanced=False`, and breaks loop. | **SEALED (Gate-02 Option C Relaxation)** |
| **Option D Activation** | **IMPLEMENTED (Emergency Only)** | Invoked strictly when router returns route `"EMERGENCY"`. Executes emergency heuristic dispatch. | **IMPLEMENTED** |
| **Operator Intervention** | **NOT_IMPLEMENTED** | No operator override API, manual control UI, or authorization transfer layer exists in `runner.py`. | **GOVERNANCE_REQUIRED** |
| **Automatic Recovery** | **IMPLEMENTED (Stateless)** | Instantaneous single-step switching without recovery validation, hysteresis, or operator confirmation. | **GOVERNANCE_REQUIRED** |

---

## 3. FORENSIC AUDIT OF EMERGENCY RETURN (`EMERGENCY → NORMAL`)

### Observed Code Mechanics
In `system/runtime/runner.py` (lines 145–150):
- At each timestep $k$, `runner.py` passes `current_state` and `bundle` to `self.router.evaluate_and_route()`.
- If the station was in `EMERGENCY` mode at step $k-1$ (Option D executed), but at step $k$ the battery SOC recovers or fuel is replenished such that `ecd.evaluate()` returns `OperatingMode.NORMAL`:
  - `router.py` returns route `"NORMAL"`.
  - `runner.py` immediately invokes `self.optimizer.optimize()` (Option B / MILP).
  - The Digital Twin advances under Option B dispatch.

### Governance Deficit in Current Code
1. **Zero Hysteresis**: A single transient fluctuation in demand or battery SOC can cause the system to alternate rapidly between Option B and Option D on consecutive timesteps.
2. **Zero Cooldown / Stabilization Window**: No minimum duration in emergency mode or stabilization window is enforced before returning to normal optimization.
3. **Zero Operator Confirmation**: Return to normal mode occurs 100% automatically without requiring operator review or acknowledgment.
4. **Stateless Evaluation**: Neither `router.py` nor `ecd.py` stores historical state transitions; evaluation is 100% memoryless per step.
