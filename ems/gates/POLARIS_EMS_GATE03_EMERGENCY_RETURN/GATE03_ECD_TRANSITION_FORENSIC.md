# POLARIS GATE-03 — ECD TRANSITION FORENSIC CLARIFICATION
## READ-ONLY FORENSIC AUDIT OF ECD EVALUATOR, ROUTER, AND RUNNER

---

## 1. FORENSIC CLARIFICATION FINDINGS SUMMARY

| Item # | Forensic Inquiry | Implementation Status | Exact Observed Code Behavior |
| :--- | :--- | :--- | :--- |
| **1** | **Observable ECD Inputs** | **IMPLEMENTED** | `AuthorizedHorizon` ($T_{\text{required}}$), `CriticalLoadTrajectory`, `soc_pct`, `fuel_remaining_liters`, `BatteryParameters`, `DieselParameters`. |
| **2a** | **`NORMAL` Conditions** | **IMPLEMENTED** | $m_{\text{battery}} \ge 0.0$ AND $m_{\text{diesel}} \ge 0.0$ (both battery and fuel endurances $\ge T_{\text{required}}$). |
| **2b** | **`EMERGENCY` Conditions** | **IMPLEMENTED** | $m_{\text{battery}} < 0.0$ OR $m_{\text{diesel}} < 0.0$ under valid telemetry/config inputs. |
| **2c** | **`UNKNOWN_INVALID` Conditions** | **IMPLEMENTED** | Triggered by `_fail_closed()` on invalid/missing/unauthenticated $T_{\text{required}}$, non-finite inputs, or invalid telemetry/config bounds. |
| **3** | **$T_{\text{required}}$ Determination** | **IMPLEMENTED** | Read from static config: `configs.get("ecd", {}).get("t_required_hours", 6.0)`. Wrapped in `AuthorizedHorizon`. |
| **4** | **State Memory / History** | **IMPLEMENTED** | Pure functional evaluator. **Zero historical state or memory**. Operates 100% statelessly per step. |
| **5** | **Emergency Latching** | **NOT_IMPLEMENTED** | Emergency state is **NOT latched** anywhere in `ecd.py`, `router.py`, or `runner.py`. |
| **6** | **Emergency Severity / Depth** | **IMPLEMENTED** (Data) /<br>**NOT_IMPLEMENTED** (Control) | Margins ($m_{\text{batt}}, m_{\text{diesel}}$) & resources (`preserved`, `limiting`) recorded in `EmergencyAssessment`, but **NOT consumed by router/runner**. Route is binary `"EMERGENCY"`. |
| **7** | **Contributing Variables** | **IMPLEMENTED** | **Fuel, SOC, Critical Load**: YES (determine margins). **Renewable Availability (Solar/Wind)**: NO (excluded from survivability math). **Total Demand**: NO (uses critical load). |
| **8** | **Single-Step `EMERGENCY → NORMAL` Return** | **IMPLEMENTED** | **YES**. Step $k$ in `EMERGENCY` followed by step $k+1$ in `NORMAL` immediately switches to Option B (MILP) on step $k+1$ if inputs yield $m \ge 0.0$. |
| **9** | **Emergency Severity Distinction** | **NOT_IMPLEMENTED** | Router does **NOT** distinguish transient vs. sustained vs. severe/depleted emergency. All map to `"EMERGENCY"`. |
| **10** | **`EMERGENCY → NORMAL` Runtime Path** | **IMPLEMENTED** | Step $k$ `EMERGENCY` $\rightarrow$ Step $k+1$ ECD evaluates `NORMAL` $\rightarrow$ `router.py` returns `"NORMAL"` $\rightarrow$ `runner.py` calls Option B MILP $\rightarrow$ `simulator.step()`. |

---

## 2. DETAILED FORENSIC AUDIT BY INQUIRY

### Item 1: Observable Inputs Received by ECD at Each Timestep
Inside `system/control/ecd.py` (`EmergencyConditionDetector.evaluate()`):
1. `horizon_input` (`AuthorizedHorizon`): `t_required_hours` (e.g. 6.0 h), `is_authenticated`, `is_authorized`, `expires_at`, `current_time`.
2. `critical_load` (`CriticalLoadTrajectory`): `ConstantCriticalLoad` or `TimeSeriesCriticalLoad` providing cumulative energy (Wh) and fuel (L) lookup methods.
3. `soc_pct` (`float`): Current battery State of Charge percentage ($0.0 \dots 100.0\%$).
4. `fuel_remaining_liters` (`float`): Current fuel volume in liters ($\ge 0.0$).
5. `battery_params` (`BatteryParameters`): `capacity_wh`, `min_soc_pct`, `max_soc_pct`, `discharge_efficiency`, `max_discharge_power_w`.
6. `diesel_params` (`DieselParameters`): `base_fuel_consumption_l_per_h`, `marginal_fuel_consumption_l_per_wh`, `min_power_w`, `max_power_w`, `physical_startup_fuel_l`.

*Status: **`IMPLEMENTED`***

---

### Item 2: Exact Classification Conditions in ECD (`ecd.py` lines 220–343)

#### A. Condition for `OperatingMode.NORMAL`:
- Telemetry, horizon payload, critical load, and parameters pass validation.
- Battery endurance margin: $m_{\text{battery}} = t_{\text{battery}} - T_{\text{required}} \ge 0.0$.
- Diesel fuel endurance margin: $m_{\text{diesel}} = t_{\text{diesel}} - T_{\text{required}} \ge 0.0$.
- Both margins must be non-negative ($\ge 0.0$).

#### B. Condition for `OperatingMode.EMERGENCY`:
- Telemetry, horizon payload, critical load, and parameters pass validation.
- Either $m_{\text{battery}} < 0.0$ OR $m_{\text{diesel}} < 0.0$.
- Available battery AC energy or diesel fuel cannot sustain the critical load for $T_{\text{required}}$ hours.

#### C. Condition for `OperatingMode.UNKNOWN_INVALID`:
- Input validation failure in `_fail_closed()`:
  - `t_required_hours` is missing, `None`, `NaN`, $\infty$, unauthenticated, unauthorized, expired, or $\le 0.0$.
  - `critical_load` is missing, `NaN`, $\infty$, or $\le 0.0$.
  - `soc_pct` is `NaN`, $\infty$, $< 0\%$, or $> 100\%$.
  - `fuel_remaining_liters` is `NaN`, $\infty$, or $< 0.0$.
  - Battery capacity $\le 0$ or efficiency $\le 0$ or $> 1.0$.
  - Diesel fuel consumption rates $< 0$.

*Status: **`IMPLEMENTED`***

---

### Item 3: Determination of $T_{\text{required}}$
- In `system/control/router.py` (lines 44–53):
  `t_required` is loaded from static configuration: `configs.get("ecd", {}).get("t_required_hours", 6.0)`.
- It is encapsulated into `AuthorizedHorizon(t_required_hours=t_required, is_authenticated=True, is_authorized=True)`.
- No dynamic, state-dependent, or external telemetry calculation of $T_{\text{required}}$ is performed in the current codebase.

*Status: **`IMPLEMENTED`** (Static Configuration Input)*

---

### Item 4: Use of Historical / Persistent State
- `EmergencyConditionDetector.evaluate()` is a **pure functional evaluator**.
- It stores **ZERO historical state**, zero memory of prior steps, zero transition logs, and zero recovery counters.
- Every call to `evaluate()` is completely independent and stateless.

*Status: **`IMPLEMENTED`** (Stateless Single-Step Evaluator)*

---

### Item 5: Emergency State Latching
- **Emergency state is NOT latched anywhere** in `ecd.py`, `router.py`, or `runner.py`.
- When ECD returns `EMERGENCY` on step $k$, no flag or persistent latch is stored in memory.

*Status: **`NOT_IMPLEMENTED`***

---

### Item 6: Representation of Emergency Severity / Depth
- **Data Representation**: `EmergencyAssessment` records quantitative margin hours (`battery_margin_hours`, `diesel_margin_hours`) and resource classifications (`preserved_resource`, `limiting_resource`).
- **Control Decision Representation**: In `router.py` (lines 102–103), these quantitative margins are **NOT** consumed. The router converts any negative margin into a binary route string `"EMERGENCY"`. Neither `router.py` nor `runner.py` scales control or selects fallback algorithms based on emergency depth.

*Status: **`IMPLEMENTED`** (Data Fields) / **`NOT_IMPLEMENTED`** (Control Logic)*

---

### Item 7: Contribution of Fuel, SOC, Critical Load, Renewables, and Demand

| Variable | Contributes to ECD Classification? | How Contributed in Code |
| :--- | :--- | :--- |
| **Fuel Remaining** | **YES** | Determines diesel endurance hours $t_{\text{diesel}}$ via critical load fuel lookup. |
| **Battery SOC** | **YES** | Determines usable AC battery energy $E_{\text{usable\_ac}}$ and endurance hours $t_{\text{battery}}$. |
| **Critical Load** | **YES** | Determines cumulative energy and fuel consumption rates over $T_{\text{required}}$. |
| **Renewable Availability (Solar/Wind)** | **NO** | Excluded from ECD. ECD calculates survivability assuming zero solar and zero wind. |
| **Total Station Demand** | **NO** | ECD evaluates against *critical load*, not total demand. (Router uses scalar demand as critical load fixture). |

*Status: **`IMPLEMENTED`***

---

### Item 8: Single-Step Return from `EMERGENCY` to `NORMAL`
- **YES**. Because `ecd.py` and `router.py` operate statelessly:
  - If step $k$ has $m_{\text{diesel}} < 0.0$, ECD returns `EMERGENCY` $\rightarrow$ router outputs `"EMERGENCY"` $\rightarrow$ Option D runs.
  - If step $k+1$ receives higher fuel or SOC (or lower critical load) such that $m_{\text{battery}} \ge 0.0$ and $m_{\text{diesel}} \ge 0.0$, ECD returns `NORMAL` $\rightarrow$ router outputs `"NORMAL"` $\rightarrow$ Option B (MILP) runs on step $k+1$.
- Transition from `EMERGENCY` back to `NORMAL` occurs instantaneously on the very next step without cooldown or verification.

*Status: **`IMPLEMENTED`** (Stateless Single-Step Transition)*

---

### Item 9: Router Distinction Between Emergency Regimes
- The current `EMSControlRouter` has **NO distinction** between:
  - Transient emergency,
  - Sustained emergency,
  - Severe / depleted emergency.
- All negative margin conditions map to the single string route `"EMERGENCY"`.

*Status: **`NOT_IMPLEMENTED`***

---

### Item 10: Step-by-Step Runtime Trace of `EMERGENCY → NORMAL` Path

```text
Step k (EMERGENCY Mode):
  1. runner.py calls router.evaluate_and_route(state_k, bundle_k, configs).
  2. ecd.evaluate() calculates m_diesel < 0.0. Returns assessment(operating_mode=EMERGENCY).
  3. router.py returns (assessment, "EMERGENCY").
  4. runner.py executes Option D solver: option_d_solver.solve(...).
  5. simulator.step() advances state to state_{k+1}.

Step k+1 (Return to NORMAL):
  1. runner.py calls router.evaluate_and_route(state_{k+1}, bundle_{k+1}, configs).
  2. ecd.evaluate() receives state_{k+1}. Calculates m_battery >= 0.0 AND m_diesel >= 0.0.
  3. ecd.evaluate() returns assessment(operating_mode=NORMAL).
  4. router.py line 101 returns (assessment, "NORMAL").
  5. runner.py line 147 sees route == "NORMAL", calls optimizer.optimize(...) (Option B / MILP HiGHS).
  6. If plan is valid, simulator.step() advances state_{k+1} to state_{k+2} under Option B dispatch.
```

*Status: **`IMPLEMENTED`** (Stateless Single-Step Transition)*
