# First-Action-Only Forensics Report

## 1. Action Extraction Code Trace

In `scratch/run_8cycle_mpc_test.py` (lines 115–124):

```python
# 4. Extract committed timestep 0 actions (First action only)
p_sol_0 = plan.solar_used[0]
p_wind_0 = plan.wind_used[0]
p_chg_0 = plan.battery_charge[0]
p_dis_0 = plan.battery_discharge[0]
soc_0 = plan.battery_soc[0]
p_dies_0 = plan.diesel_power[0]

# 5. Advance StationState to cycle n+1 (commit timestep 0)
e_next = e_in + eta_ch * p_chg_0 * 1.0 - (1.0 / eta_dis) * p_dis_0 * 1.0
```

---

## 2. Verification of Discarded Steps ($t = 1 \dots 23$)

- At every cycle, actions for timesteps $t \ge 1$ were **NOT** used in the state update.
- Proves receding-horizon commitment vs open-loop execution.

---

## 3. Verdict

```
FIRST_ACTION_INDEX = 0
PLANNED_STEPS_DISCARDED = 1..23
OPEN_LOOP_EXECUTION = NO
FIRST_ACTION_FORENSICS_STATUS = PASS
```
