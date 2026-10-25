# POLARIS RT-01 INVESTIGATION: RESOURCE PRESERVATION COUNTERFACTUAL REPORT
**Document ID:** RT01-RPT-001  
**Scenario:** `synthetic_168h_endurance_scenario.json` (168 timesteps)  
**Date:** 2026-10-18  
**Investigator:** Antigravity Autonomous Diagnostic Agent  
**Status:** COMPLETE -- HYPOTHESIS CONFIRMED (UNMET LOAD REDUCED TO EXACTLY 0.00 Wh)

---

## 1. Executive Summary & Hypothesis Validation

### 1.1 The Tested Hypothesis
An independent investigation hypothesized that the unresolved **14,974.11 Wh** unmet load at steps 119–121 of the 168-hour endurance scenario is caused by a structural semantic inversion between the Emergency Condition Detector (`system/control/ecd.py`) and the Option D Fallback Solver (`system/optimization/implementations/option_d.py`). 

Specifically:
1. When diesel fuel drops below the endurance required for the 6-hour target horizon ($t_{diesel} < T_{required}$), `ecd.py` evaluates $m_{diesel} < 0$, declaring `OperatingMode.EMERGENCY`.
2. Because the battery still has substantial energy ($m_{battery} > m_{diesel}$), `ecd.py` flags `BATTERY` as the `preserved_resource` (and `DIESEL` as `limiting_resource`).
3. In `option_d.py`, the branch `preserved_resource == ResourceSelection.BATTERY` is coded to **run the diesel generator first** to preserve battery energy.
4. Consequently, `option_d.py` aggressively burns the remaining diesel reserve to protect an already well-charged battery (even at 95.0% SOC), prematurely exhausting the 100 L fuel tank by step 65.
5. With the diesel tank completely empty (0.00 L), the microgrid is left defenseless when renewable generation drops at steps 119–121, forcing the battery to its 20.0% floor and causing 14,974.11 Wh of critical load shedding.

### 1.2 Quantitative Result Summary
This hypothesis was subjected to rigorous, isolated counterfactual testing using a non-invasive wrapper on `runner.option_d_solver.solve` that overrode `preserved_resource` to `ResourceSelection.DIESEL` when battery SOC was safely above the 20.0% minimum floor.

| Performance Metric | Governed Baseline | Counterfactual Intervention | Absolute Delta | Relative Change |
| :--- | :---: | :---: | :---: | :---: |
| **Total 168-Hour Unmet Load (Wh)** | **14,974.11** | **0.00** | **-14,974.11 Wh** | **-100.0% (Eliminated)** |
| **Steps 119–121 Unmet Load (Wh)** | **14,974.11** | **0.00** | **-14,974.11 Wh** | **-100.0% (Eliminated)** |
| - Step 119 Unmet Load (Wh) | 8,919.43 | 0.00 | -8,919.43 Wh | -100.0% |
| - Step 120 Unmet Load (Wh) | 5,105.84 | 0.00 | -5,105.84 Wh | -100.0% |
| - Step 121 Unmet Load (Wh) | 948.84 | 0.00 | -948.84 Wh | -100.0% |
| **Total Diesel Consumed (L)** | **100.00** | **81.72** | **-18.28 L** | **-18.28% (Fuel Saved)** |
| **Final Fuel Remaining (L)** | **0.00** | **18.28** | **+18.28 L** | **Reserve Maintained** |
| **Step of Fuel Exhaustion** | **Step 65** | **Never (>168h)** | **+103+ steps** | **Exhaustion Averted** |
| **Renewable Utilization (%)** | **79.25%** | **79.98%** | **+0.73%** | **Improved** |
| **Renewable Curtailment (%)** | **20.75%** | **20.02%** | **-0.73%** | **Reduced** |
| **System Reliability (%)** | **99.73%** | **100.00%** | **+0.27%** | **Perfect Reliability** |
| **Battery Minimum SOC (%)** | **20.00%** | **20.00%** | **0.00%** | **Within [20%, 95%]** |
| **Battery Maximum SOC (%)** | **95.00%** | **95.00%** | **0.00%** | **Within [20%, 95%]** |

> [!IMPORTANT]
> **Conclusion:** The hypothesis is **completely confirmed**. By preventing `option_d.py` from burning diesel when the battery is safely available, 33.28 L of fuel was preserved past step 65. When the renewable deficit arrived at step 119, the preserved fuel allowed the diesel generator to support the microgrid, **reducing unmet load at steps 119–121 to exactly 0.00 Wh** and achieving **100.00% system reliability** across all 168 hours without violating any physical or governance constraint.

---

## 2. Task 1: Verification (Read-Only Code Analysis)

### 2.1 Evaluation of `preserved_resource` in `system/control/ecd.py`
Inspection of `system/control/ecd.py` (lines 282–341) confirms the mathematical logic:

1. **Endurance Calculations (lines 283–295):**
   ```python
   soc_usable_pct = max(0.0, soc_pct - battery_params.min_soc_pct)
   usable_dc_energy_wh = battery_params.capacity_wh * (soc_usable_pct / 100.0)
   usable_ac_energy_wh = usable_dc_energy_wh * battery_params.discharge_efficiency
   t_battery = load_traj.find_time_for_energy_wh(usable_ac_energy_wh)

   available_fuel_l = max(0.0, fuel_remaining_liters - diesel_params.physical_startup_fuel_l)
   t_diesel = load_traj.find_time_for_fuel_liters(
       available_fuel_l,
       diesel_params.base_fuel_consumption_l_per_h,
       diesel_params.marginal_fuel_consumption_l_per_wh
   )
   ```
2. **Margin Evaluation against $T_{target}$ (lines 298–305):**
   ```python
   m_battery = t_battery - t_target
   m_diesel = t_diesel - t_target

   if m_battery >= 0.0 and m_diesel >= 0.0:
       mode = OperatingMode.NORMAL
   else:
       mode = OperatingMode.EMERGENCY
   ```
3. **Preserved Resource Selection (lines 318–328):**
   ```python
   else:  # EMERGENCY
       if is_tie:
           preserved = ResourceSelection.BOTH
           limiting = ResourceSelection.BOTH
       elif m_battery > m_diesel:
           preserved = ResourceSelection.BATTERY
           limiting = ResourceSelection.DIESEL
       else:
           preserved = ResourceSelection.DIESEL
           limiting = ResourceSelection.BATTERY
   ```
**Finding:** In emergency mode, `ecd.py` assigns `preserved_resource` to whichever resource has the **greater endurance margin** ($m_{battery} > m_{diesel}$). When diesel fuel is running low, $t_{diesel}$ falls below $T_{target} = 6.0$ h, driving $m_{diesel} < 0$. If battery SOC is healthy (e.g. 60%), $m_{battery} > 0 > m_{diesel}$, so `ecd.py` designates `BATTERY` as `preserved_resource` and `DIESEL` as `limiting_resource`.

---

### 2.2 Dispatch Branches in `system/optimization/implementations/option_d.py`
Inspection of `system/optimization/implementations/option_d.py` (lines 158–220) maps the exact dispatch execution paths:

1. **Branch `preserved_resource == ResourceSelection.BATTERY` (lines 160–172):**
   ```python
   if assessment.preserved_resource == ResourceSelection.BATTERY:
       # Preserve battery: Run diesel for remaining load first if fuel available
       if available_fuel > 0:
           p_diesel_req = max(min_diesel_w, p_rem_demand)
           p_diesel = min(max_diesel_w, p_diesel_req)
           p_rem_demand_after_diesel = max(0.0, p_rem_demand - p_diesel)
       else:
           p_rem_demand_after_diesel = p_rem_demand

       # Discharge battery for any remaining unmet demand
       if p_rem_demand_after_diesel > 0:
           p_dis = min(max_dis_avail_w, p_rem_demand_after_diesel)
   ```
   *Behavior:* The solver attempts to satisfy the entirety of net critical demand ($P_{rem\_demand}$) using the diesel generator first. Battery discharge is suppressed to 0.0 W unless diesel capacity (50 kW) is exceeded or fuel is zero. Furthermore, per lines 223–228, if $P_{diesel} > P_{rem\_demand}$ (due to the 10 kW generator floor), the excess diesel energy is used to charge the battery.
   
2. **Branch `preserved_resource == ResourceSelection.DIESEL` (lines 173–202):**
   ```python
   elif assessment.preserved_resource == ResourceSelection.DIESEL:
       # Preserve diesel: Discharge usable battery energy first
       p_dis = min(max_dis_avail_w, p_rem_demand)
       p_rem_demand_after_bat = max(0.0, p_rem_demand - p_dis)

       # Run diesel only if battery is insufficient and fuel available
       if p_rem_demand_after_bat > 0 and available_fuel > 0:
           p_diesel_req = max(min_diesel_w, p_rem_demand_after_bat)
           p_diesel = min(max_diesel_w, p_diesel_req)
           if p_diesel > p_rem_demand_after_bat:
               p_dis = max(0.0, min(max_dis_avail_w, p_rem_demand - p_diesel))
   ```
   *Behavior:* The solver satisfies net critical demand using the battery first up to available usable energy. Diesel is started only if usable battery energy is zero or insufficient to meet the load.

**The Semantic Inversion:** `ecd.py` conceived of `preserved_resource` as "the resource with superior endurance margin", while `option_d.py` implemented `preserved_resource` as "the resource that must be conserved by burning the OTHER resource". Thus, whenever diesel became critically scarce, the system commanded maximum diesel consumption.

---

### 2.3 Timeline of Baseline Fuel Exhaustion
Tracing the baseline 168-hour execution (`research/rt01_diagnostics/rt01_168h_trace.json`) pinpoints the physical consumption:

1. **Steps 1–45 (NORMAL Mode via `LocalMILPEnergyOptimizer`):**
   - Diesel is dispatched during high demand / low renewable periods at steps 19, 20, 21, and 45.
   - At step 45, diesel runs at 74,062.6 W (charging battery to 59.5% SOC), reducing fuel from 56.80 L to 33.28 L.
2. **Step 46 (First Critical EMERGENCY Transition):**
   - Fuel remaining: 33.28 L $\implies$ Diesel endurance $t_{diesel} = 33.28 / (5.0 + 0.00025 \times 5000) = 5.32$ hours.
   - Target horizon: 6.0 hours $\implies m_{diesel} = 5.32 - 6.0 = -0.68$ hours.
   - Battery SOC: 59.5% $\implies t_{battery} \approx 14.5$ hours $\implies m_{battery} = +8.5$ hours.
   - `ecd.py` evaluates: $m_{diesel} < 0 \implies$ `OperatingMode.EMERGENCY`.
   - `ecd.py` evaluates: $m_{battery} > m_{diesel} \implies$ `preserved_resource = BATTERY`, `limiting_resource = DIESEL`.
3. **Steps 46–49 (Option D Burns 32.01 L of Diesel):**
   - **Step 46:** Net demand = 16,801.5 W. Battery has 72.7 kWh usable energy. Option D dispatches $P_{diesel} = 16,801.5$ W, $P_{dis} = 0.0$ W. Fuel burns: 33.28 L $\to$ 24.08 L.
   - **Step 47:** Net demand = 11,243.5 W. Battery has 72.7 kWh usable energy. Option D dispatches $P_{diesel} = 11,243.5$ W, $P_{dis} = 0.0$ W. Fuel burns: 24.08 L $\to$ 16.27 L.
   - **Step 48:** Net demand = 5,379.5 W. Option D dispatches $P_{diesel} = 10,000.0$ W (floor), $P_{dis} = 0.0$ W. Fuel burns: 16.27 L $\to$ 8.77 L.
   - **Step 49:** Net demand = 1,155.3 W. Option D dispatches $P_{diesel} = 10,000.0$ W (floor), $P_{dis} = 0.0$ W. Fuel burns: 8.77 L $\to$ 1.27 L.
4. **Step 65 (Literal Exhaustion to 0.00 L):**
   - Battery SOC is **95.0% (completely saturated at 190.0 kWh)**.
   - Net demand after renewables is only **796.37 W**.
   - Option D sees `preserved_resource == BATTERY`. It starts diesel at 10,000 W to serve 796 W while a full 190 kWh battery sits idle.
   - Fuel burns from 1.27 L to **0.0000 L**.
5. **Steps 66–118 (Zero Fuel Reserve):**
   - The station operates with 0.0 L diesel fuel.
6. **Steps 119–121 (The Shortage):**
   - Solar is 0 W, wind generation declines.
   - At step 119, battery discharges its final usable energy (2,074.9 Wh) and reaches the 20.0% floor.
   - Unmet load: Step 119 = 8,919.43 Wh; Step 120 = 5,105.84 Wh; Step 121 = 948.84 Wh. Total = **14,974.11 Wh**.

---

## 3. Task 2: Baseline Establishment

The baseline 168-hour endurance run was executed using standard `PolarisLocalRunner` without code modification:

```
timesteps_executed: 168
execution_status: SUCCESS_CLEAN
total_unmet_load_wh: 14974.11 Wh (14.9741 kWh)
steps_119_121_unmet_wh: 14974.11 Wh
total_diesel_fuel_consumed_l: 100.00 L
fuel_exhaustion_step: Step 65
renewable_utilization_pct: 79.25%
renewable_curtailment_pct: 20.75%
system_reliability_pct: 99.73%
min_soc_pct: 20.00%
max_soc_pct: 95.00%
route_distribution: NORMAL: 32 steps (19.0%), EMERGENCY: 136 steps (81.0%)
```

---

## 4. Task 3 & 4: Isolated Counterfactual Design & Execution

### 4.1 Non-Invasive Interception Methodology
In compliance with the STRICT READ-ONLY boundary, no production file was modified on disk. All experiments were conducted through instance-level method wrapping in `research/rt01_diagnostics/trace_counterfactual_resource_preservation.py`:

```python
orig_solve = runner.option_d_solver.solve

def wrapped_solve(assessment, bundle, current_state, configs):
    # Intercept EmergencyAssessment before Option D solves
    if (
        assessment.preserved_resource == ResourceSelection.BATTERY 
        and current_state.battery_soc_pct > 20.0
    ):
        # Substitute preserved_resource to DIESEL
        assessment = dataclasses.replace(assessment, preserved_resource=ResourceSelection.DIESEL)
    
    return orig_solve(assessment, bundle, current_state, configs)

runner.option_d_solver.solve = wrapped_solve
```

### 4.2 Physical Rationale for Heuristic Condition
1. **Battery Safe Operating Margin:** When battery SOC is strictly above the 20.0% floor, usable electrochemical energy is available.
2. **Elimination of Minimum-Floor Fuel Waste:** Firing the diesel generator consumes a non-negotiable minimum of 5.0 L/h base fuel + 0.00025 L/Wh (7.5 L/h at 10 kW min power). Using the generator to serve a small net demand (e.g. 796 W at step 65) operates at dismal fuel efficiency. Discharging the battery incurs zero base-rate penalty.
3. **Natural Fallback at Battery Depletion:** If battery SOC approaches 20.0%, `curr_e_wh - min_e_wh == 0`, so `p_dis` naturally saturates at 0.0 W and Option D's DIESEL-preservation branch automatically commits diesel to prevent load shedding.

### 4.3 Governance & Boundary Verification
- **SHA-256 Immutability Check:** Pre- and post-run SHA-256 hashes of all protected files matched byte-for-byte:
  - `system/control/ecd.py`: `091358c08b9460e0e9a802ff149c2b54ce1d8036bc2d6eed0f4c1fd9e41c96db`
  - `system/optimization/implementations/option_d.py`: `022cc6a0aef4e61772a7274ef3b0e772abacf16fab373feb3273d6af0f653771`
  - `system/control/router.py`: `b2a46bc5bd8c619b5eca9b020daa3dd1b4571214bab47cfe17587bc9074e90f3`
  - `system/runtime/runner.py`: `6d1671b6efbf6ac1f422e26a039bb0dae158cb99c2075ea5680d062f8dc53b10`
  - `system/simulation/simulator.py`: `8c44f757058e4bdc83e4b9988258d69198d85a766b25fcaeed4204c74b3c5e5f`
  - `system/optimization/implementations/gap19_highs_native.py`: `fd1afe10a60c6e9caf415d648701a33655a76e5e9f558c49c0f39bc118a2e737`
- **Physical Hard Constraints:**
  - Total fuel consumed: **81.72 L $\le$ 100.0 L** (PASSED, 18.28 L safety headroom).
  - Minimum SOC: **20.00% $\ge$ 20.00%** (PASSED, zero floor violation).
  - Maximum SOC: **95.00% $\le$ 95.00%** (PASSED, zero overcharge).
  - Renewable utilization: **79.98% $\ge$ 75.00%** (PASSED, +4.98% margin above requirement).
- **Security & Authorization:** The project's fail-closed authorization behavior remained intact.

---

## 5. Task 5: Detailed Results & Critical Window Telemetry

### 5.1 Pre-Shortage Window (Steps 44–52, 63–67) Comparison

| Step | Mode | Base Fuel (L) | Base Dies (W) | Base Dis (W) | CF Fuel (L) | CF Dies (W) | CF Dis (W) | CF SOC (%) | Counterfactual Action & Effect |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **44** | NORMAL | 56.80 $\to$ 56.80 | 0.0 | 24,941.9 | 56.80 $\to$ 56.80 | 0.0 | 24,941.9 | 50.0% | Identical baseline MILP solve. |
| **45** | NORMAL | 56.80 $\to$ 33.28 | 74,062.6 | 0.0 | 56.80 $\to$ 33.28 | 74,062.6 | 0.0 | 36.5% $\to$ 59.5% | Identical baseline MILP solve (diesel charges battery). |
| **46** | EMERG | 33.28 $\to$ 24.08 | 16,801.5 | 0.0 | **33.28 $\to$ 33.28** | **0.0** | **16,801.5** | 59.5% $\to$ 50.3% | **Preserved 9.20 L fuel**; battery meets load. |
| **47** | EMERG | 24.08 $\to$ 16.27 | 11,243.5 | 0.0 | **33.28 $\to$ 33.28** | **0.0** | **11,243.5** | 50.3% $\to$ 44.2% | **Preserved 7.81 L fuel**; battery meets load. |
| **48** | EMERG | 16.27 $\to$ 8.77 | 10,000.0 | 0.0 | **33.28 $\to$ 33.28** | **0.0** | **5,379.5** | 44.2% $\to$ 41.3% | **Preserved 7.50 L fuel**; battery meets load. |
| **49** | EMERG | 8.77 $\to$ 1.27 | 10,000.0 | 0.0 | **33.28 $\to$ 33.28** | **0.0** | **1,155.3** | 41.3% $\to$ 40.7% | **Preserved 7.50 L fuel**; battery meets load. |
| **50** | EMERG | 1.27 $\to$ 1.27 | 0.0 | 0.0 | 33.28 $\to$ 33.28 | 0.0 | 0.0 | 40.7% $\to$ 42.5% | Solar charges battery in both runs. |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |
| **64** | EMERG | 1.27 $\to$ 1.27 | 0.0 | 0.0 | 33.28 $\to$ 33.28 | 0.0 | 0.0 | 95.0% | Both batteries reach 95.0% ceiling. |
| **65** | EMERG | 1.27 $\to$ **0.00** | **10,000.0** | **0.0** | **33.28 $\to$ 33.28** | **0.0** | **796.4** | 95.0% $\to$ 94.6% | **Averted fuel exhaustion**; 796 W served by battery. |
| **66** | EMERG | 0.00 $\to$ 0.00 | 0.0 | 10,616.9 | 33.28 $\to$ 33.28 | 0.0 | 10,616.9 | 94.6% $\to$ 88.8% | Battery discharges in both; CF has 33.28 L fuel reserve. |

---

### 5.2 Shortage Window (Steps 117–121) Telemetry

| Step | Base Fuel | Base Dies | Base Dis | Base Unmet | CF Fuel | CF Dies | CF Dis | CF SOC | CF Unmet | Outcome Analysis |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **117** | 0.00 | 0.0 | 19,292.0 | 0.0 | 33.28 | 0.0 | 19,292.0 | 41.2% $\to$ 30.7% | Identical battery discharge; CF fuel intact. |
| **118** | 0.00 | 0.0 | 17,575.3 | 0.0 | 33.28 | 0.0 | 17,575.3 | 30.7% $\to$ 21.1% | Battery approaches 20% floor. |
| **119** | 0.00 | 0.0 | 2,074.9 | **8,919.43** | **33.28 $\to$ 25.78** | **10,000.0** | **994.4** | 21.1% $\to$ 20.6% | **0.00 Wh** | Diesel runs, covering shortfall; unmet = 0.00. |
| **120** | 0.00 | 0.0 | 0.0 | **5,105.84** | **25.78 $\to$ 18.28** | **10,000.0** | **0.0** | 20.6% $\to$ 22.8% | **0.00 Wh** | Diesel runs at floor, excess charges battery; unmet = 0.00. |
| **121** | 0.00 | 0.0 | 0.0 | **948.84** | **18.28 $\to$ 18.28** | **0.0** | **948.8** | 22.8% $\to$ 22.3% | **0.00 Wh** | Surcharge from step 120 covers remainder; unmet = 0.00. |

---

## 6. Side Effects & System Impact Analysis

1. **Zero Shift in Unmet Load:** Unmet load was not merely shifted to later timesteps. Total unmet load across the entire 168-hour horizon was **0.00 Wh** (down from 14,974.11 Wh).
2. **Improved Renewable Utilization:** Renewable utilization increased from **79.25% to 79.98%**. Because the battery was discharged during steps 46–49 instead of held artificially full by diesel generation, the battery had greater absorption headroom when solar generation peaked between steps 50 and 64. Renewable curtailment dropped from 1,422.89 kWh to 1,372.41 kWh.
3. **Substantial Fuel Conservation:** Diesel fuel consumption dropped from 100.00 L to **81.72 L**, leaving **18.28 L** of reserve fuel at the end of the 168-hour scenario.
4. **Reliability:** Reliability reached **100.00%**.

---

## 7. Architectural Recommendation for Permanent Remediation

When an authorized change window opens for protected files, the recommended structural resolution is:

1. **Option D Logic Realignment:**
   In `system/optimization/implementations/option_d.py`, modify line 160:
   The battery should **always** be dispatched first whenever usable energy exists above the safety floor ($SOC > min\_soc\_pct$). Firing diesel while usable battery energy exists should only occur if net demand exceeds battery inverter discharge capacity ($P_{rem\_demand} > P_{dis\_max}$) or if battery SOC has reached the minimum floor.
2. **ECD Preservation Semantics Clarity:**
   Ensure documentation in `system/control/ecd.py` clarifies that `preserved_resource` denotes the *survivability anchor* (the stronger resource that enables the microgrid to survive), not an operational command to immediately consume the scarcer resource.

---
*Report generated and validated autonomously against the POLARIS microgrid architecture.*
