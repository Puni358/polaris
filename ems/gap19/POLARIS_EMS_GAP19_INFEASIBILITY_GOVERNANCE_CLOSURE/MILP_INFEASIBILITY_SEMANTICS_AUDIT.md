# POLARIS EMS GAP19 — MILP INFEASIBILITY SEMANTICS AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Classification**: `GOVERNANCE_REQUIRED`  

---

## 1. Disambiguation of `OPTIMIZATION_INFEASIBLE` Signals

In POLARIS system architecture, the term `OPTIMIZATION_INFEASIBLE` must not be conflated across different engineering layers:

| Layer / Concept | Technical Definition | Example Cause in POLARIS |
| :--- | :--- | :--- |
| **1. Solver Infeasibility** | Numerical status returned by HiGHS (`kInfeasible`) when no solution vector satisfies all matrix rows and variable bounds simultaneously. | $s_{\text{J2}}$ upper bound ($200\text{ kWh}$) exceeded by $E_{\text{EBR\_target}}$ ($380\text{ kWh}$). |
| **2. Physical Infeasibility** | Physical impossibility where total load exceeds maximum combined generation and battery discharge capacity. | Demand = $200\text{ kW}$, but Diesel max = $100\text{ kW}$, Battery max = $50\text{ kW}$. |
| **3. Reserve Infeasibility** | Physical battery energy is insufficient to meet 6-hour EBR or 24-hour terminal reserve target envelope. | High load drains battery below 6-hour survivability threshold. |
| **4. Critical Deficit Infeasibility** | Available generation cannot cover protected critical load ($P_{\text{critical}}$), forcing $J1 > 0$. | Prolonged dark calm (no solar/wind) with empty battery and diesel fuel depletion. |
| **5. Modeling Artifact Infeasibility** | Solver infeasibility caused by un-governed artificial upper bounds on slack variables. | $s_{\text{J2}} \le \text{capacity\_wh}$ ceiling. |
| **6. System Emergency Condition** | High-level operational state requiring transition from NORMAL to EMERGENCY mode or Option D fallback. | ECD detects $T_{\text{required}}$ survivability window breach or sensor fault. |

---

## 2. Established Architecture Signal Relationship

We evaluate four candidate relationships between MILP infeasibility and Emergency Mode:

* **Candidate A**: MILP infeasibility itself defines emergency mode.
* **Candidate B**: ECD independently defines emergency mode; MILP infeasibility is a downstream optimizer condition.
* **Candidate C**: MILP infeasibility and ECD are independent signals.
* **Candidate D**: Not yet governed.

### Audit Finding
In the current sealed codebase (`runner.py`, `gap19_highs_native.py`, `ecd.py`), there is **NO code connecting MILP solver status to ECD or Emergency Mode transitions**. `runner.py` catches `OPTIMIZATION_INFEASIBLE`, logs a `FaultEvent` as `GOVERNED_DEGRADED`, and executes zero dispatch without invoking ECD or changing `StationState.operating_mode`.

Therefore, the architectural relationship is:

`SIGNAL_RELATIONSHIP = Candidate D (Not yet governed)`

---

## 3. Audit Verdict

`MILP_INFEASIBILITY_SEMANTICS = GOVERNANCE_REQUIRED`

Human governance must define whether MILP solver infeasibility should trigger an automatic system transition to EMERGENCY mode and Option D fallback dispatch.
