# Field-by-Field State Continuity Forensics Report

## 1. Field-by-Field Continuity Classification Matrix

| StationState Field | Cycle $n$ Output $\to$ Cycle $n+1$ Input | Classification | Continuity Status |
| :--- | :--- | :--- | :---: |
| `timestamp` | Advanced by $+1.0\text{ hour}$ ISO-8601 | `DERIVED_FROM_PREVIOUS_STATE` | **EXACTLY_PROPAGATED** |
| `battery_energy_wh` | $E_{\text{next}} = E_{\text{in}} + \eta_{\text{ch}} P_{\text{chg}, 0} - \frac{1}{\eta_{\text{dis}}} P_{\text{dis}, 0}$ | `DERIVED_FROM_PREVIOUS_STATE` | **EXACTLY_PROPAGATED** |
| `battery_soc_pct` | $(E_{\text{next}} / 200,000) \times 100\%$ | `DERIVED_FROM_PREVIOUS_STATE` | **EXACTLY_PROPAGATED** |
| `diesel_running` | `True` if $P_{\text{diesel}, 0} > 0$ else `False` | `DERIVED_FROM_PREVIOUS_STATE` | **EXACTLY_PROPAGATED** |
| `diesel_hours_running` | Increment by $+1.0\text{ h}$ if running else $0.0\text{ h}$ | `DERIVED_FROM_PREVIOUS_STATE` | **EXACTLY_PROPAGATED** |
| `operating_mode` | Constant `"NORMAL"` | `EXACTLY_PROPAGATED` | **EXACTLY_PROPAGATED** |
| `terminal_target_wh_override` | Constant $100,000.0\text{ Wh}$ | `EXACTLY_PROPAGATED` | **EXACTLY_PROPAGATED** |

---

## 2. Accidental Re-initialization Audit

- Zero fields were re-initialized to initial values ($80\%$ SOC / $160\text{ kWh}$) between cycles.
- Battery energy propagated smoothly: $160,000\text{ Wh}$ (Cycle 1 in) $\to 186,739.13\text{ Wh}$ (Cycle 1 out / Cycle 2 in) $\to \dots \to 186,739.13\text{ Wh}$ (Cycle 8 out).

---

## 3. Verdict

```
ACCIDENTAL_REINITIALIZATIONS = NONE (0)
ALL_FIELDS_PROPAGATED = YES
STATE_CONTINUITY_FORENSICS_STATUS = PASS
```
