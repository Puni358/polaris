# POLARIS GATE-02 — MILP INFEASIBILITY SAFETY ANALYSIS
## FORENSIC SAFETY & PHYSICAL RISK ANALYSIS

---

## 1. MATHEMATICAL INFEASIBILITY VS. PHYSICAL STATION SAFETY

A central governance principle established in Gate-02 is the strict operational distinction between:
- **Mathematical Optimizer Infeasibility** (`MILP_INFEASIBLE`), and
- **Physical Station Emergency** (`EMERGENCY`).

```text
+-----------------------------------------------------------------------+
|                       MILP_INFEASIBILITY                              |
|                                                                       |
|  "The current optimization problem has no feasible dispatch solution  |
|   under the supplied model, constraints, state, and forecast inputs." |
+-----------------------------------------------------------------------+
                                   ≠
+-----------------------------------------------------------------------+
|                           EMERGENCY                                   |
|                                                                       |
|  "The microgrid is experiencing physical asset depletion, loss of     |
|   critical load, or an unrecoverable energy balance crisis."           |
+-----------------------------------------------------------------------+
```

### Key Safety Assertions
1. **Does NOT imply emergency**: A solver reporting `MILP_INFEASIBLE` means the algorithm cannot find a 24-hour trajectory that satisfies 100% of constraints simultaneously. It does NOT mean the station is currently out of power or in immediate physical danger.
2. **Does NOT invalidate ECD**: Early Crisis Detection (ECD) evaluates physical state variables (fuel reserve, battery SOC, grid connection). ECD may assess the station as `NORMAL` while the 24-hour MILP is infeasible due to a future constraint conflict (e.g., an over-constrained terminal SOC target at $k=24$).
3. **Does NOT imply Battery / Fuel Survivability Failure**: Survivability failure occurs when total available energy is less than total critical load requirements over the horizon. Infeasibility can occur even when battery and fuel reserves are at 100%, e.g., due to conflicting ramping limits or min-up/down time constraints.
4. **Does NOT authorize Option D**: Option D is an emergency solver. Triggering Option D on model infeasibility incorrectly converts a software model failure into an emergency declaration, bypassing physical ECD safeguards.

---

## 2. CRITICAL-LOAD BOUNDARY & INFEASIBILITY SOURCES

### Hard vs. Soft Constraints in POLARIS MILP
In the POLARIS MILP model (`gap19_highs_native.py` / `milp.py`), critical load served is modeled as a **hard boundary constraint**:
$$P_{\text{diesel}}[k] + P_{\text{discharge}}[k] + P_{\text{renewable}}[k] \ge L_{\text{critical}}[k] \quad \forall k \in \{0, \dots, N-1\}$$

In addition, the model enforces secondary hard constraints:
1. **Terminal SOC Reserve**: $SOC[N] \ge SOC_{\text{target}}$.
2. **Battery Charge/Discharge C-Rate**: $P_{\text{charge}}[k] \le P_{\text{charge, max}}$, $P_{\text{discharge}}[k] \le P_{\text{discharge, max}}$.
3. **Generator Minimum Up/Down Time & Operating Limits**: $P_{\text{min}} \le P_{\text{diesel}}[k] \le P_{\text{max}}$.
4. **Fuel Continuity & Tank Boundaries**: $Fuel[k+1] = Fuel[k] - \text{consumption}(P_{\text{diesel}}[k])$.

### Mechanisms Producing Infeasibility Under Safe Physical Conditions
The optimizer can return `MILP_INFEASIBLE` under physically safe conditions due to over-constrained mathematical boundaries:

```text
Case 1: Over-Constrained Terminal Reserve
  - Station has 80% SOC and ample fuel at k=0.
  - Forecast predicts high demand near end of horizon.
  - Terminal SOC target (SOC[24] >= 50%) cannot be met without violating generator ramp rate.
  - Result: MILP_INFEASIBLE, despite k=0 being 100% safe.

Case 2: Generator Min-Up/Min-Down Conflict
  - Generator was turned off at k=-1.
  - High demand spike at k=1 requires generator, but min-down time constraint prohibits start at k=1.
  - Result: MILP_INFEASIBLE, even though battery could cover k=1 if minor load shedding were permitted.

Case 3: Inaccurate Forecast Spike
  - Solar forecast predicts sudden 90% cloud cover drop in 10 minutes.
  - MILP cannot ramp diesel fast enough in model.
  - Result: MILP_INFEASIBLE, though real solar irradiance may not actually drop.
```

In all three cases, the physical station at step $k=0$ is safe, yet the 24-hour mathematical optimization problem has no valid solution.

---

## 3. PHYSICAL SAFETY IMPLICATIONS OF OPERATIONAL RESPONSES

If the EMS encounters `MILP_INFEASIBLE`:

1. **If zero-dispatch is committed (`GOVERNED_ZERO_DISPATCH`)**:
   - Diesel generator is commanded to 0 kW; battery is commanded to 0 kW.
   - **Physical Risk**: Critical load is immediately dropped at $k=0$, creating an immediate blackout despite available battery and fuel assets. This response is **physically unsafe**.
2. **If Option D is automatically invoked**:
   - Option D sheds non-critical load and operates in emergency mode.
   - **Physical Risk**: Performs un-needed emergency load shedding when normal operation could have continued by adjusting secondary targets.
3. **If execution is blocked (`ENGINEERING_INTERFACE_BLOCKER`)**:
   - EMS issues no new command; station relies on local hardware governors or holds previous setpoints.
   - **Physical Safety**: Prevents software-induced blackout while awaiting authorized operational policy.
