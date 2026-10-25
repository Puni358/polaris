# State Propagation Provenance Forensics

## 1. Resolution of Secondary Audit Question

> **"What exactly generated the next StationState after each executed first action?"**

Code inspection of `scratch/run_8cycle_mpc_test.py` proves:

```python
# Battery state update equation:
eta_ch = 0.92
eta_dis = 0.92
e_in = current_state.battery_energy_wh
e_next = e_in + eta_ch * p_chg_0 * 1.0 - (1.0 / eta_dis) * p_dis_0 * 1.0
e_next = round(e_next, 4)
soc_next = round((e_next / 200000.0) * 100.0, 4)

next_dt = curr_dt + timedelta(hours=1)
next_iso = next_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
diesel_running_next = (p_dies_0 > 0.0)
diesel_hours_next = (current_state.diesel_hours_running + 1.0) if diesel_running_next else 0.0

current_state = StationState(...)
```

---

## 2. Classification

The state propagation mechanism is classified as **CASE B**:

```text
STATE_PROPAGATION = SYNTHETIC_STATE_TRANSITION
```

An explicit synthetic deterministic state-transition function evaluating the exact physical battery energy dynamics $E_{\text{next}} = E_{\text{in}} + \eta_{\text{ch}} P_{\text{chg}} \Delta t - \frac{1}{\eta_{\text{dis}}} P_{\text{dis}} \Delta t$ was used to update `StationState` between cycles.

---

## 3. Verdict

```
STATE_PROPAGATION_CLASSIFICATION = SYNTHETIC_STATE_TRANSITION
DIGITAL_TWIN_SIMULATOR_CALLED = NO
MANUAL_ARBITRARY_ASSIGNMENT = NO
STATE_PROPAGATION_FORENSICS_STATUS = PASS
```
