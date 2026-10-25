# SIMULATOR CHANGE BOUNDARY AUDIT

## Forensic Source Inspection of `system/simulation/simulator.py`

This document details the forensic inspection of [`system/simulation/simulator.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/simulation/simulator.py) to determine whether changes are mandatory for pre-GAP19 scope.

---

## 1. Static Source Code Evidence

Inspection of [`system/simulation/simulator.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/simulation/simulator.py) (67 lines) reveals:

1. **Battery State Tracking**: Lines 44–52 track battery energy `curr_e_wh` and update `battery_soc_pct` and `battery_energy_wh`.
2. **Generator Status Tracking**: Lines 54–55 track boolean `diesel_running` and `diesel_hours_running`.
3. **Fuel Volume Tracking**: Lines 57–66 construct and return `StationState`. **There is zero fuel tracking code, zero fuel mass-balance logic, and zero fuel volume field in `StationState` or `DigitalTwinSimulator`.**

---

## 2. Static Audit Finding Matrix

```text
SIMULATOR_FUEL_STATE_SUPPORT = NOT_ESTABLISHED
SIMULATOR_FUEL_MASS_BALANCE = NOT_ESTABLISHED
SIMULATOR_FUEL_REMAINING_OUTPUT = NOT_ESTABLISHED
SIMULATOR_MODIFICATION_REQUIRED = YES (If multi-step closed-loop fuel tracking is authorized)
```

---

## 3. Reclassification Decision

Under the governing pre-implementation rules:
> "If source inspection shows a simulator modification is genuinely necessary: classify `SIMULATOR_CHANGE_STATUS = ENGINEERINGALLY_REQUIRED_BUT_NOT_YET_AUTHORIZED` and `system/simulation/simulator.py = MAY_MODIFY_AFTER_SEPARATE_AUTHORIZATION`. Do NOT classify it as `MUST_MODIFY` unless the authorization package has explicit evidence that the change is necessary."

### Classification Outcome:
- **Prior Classification**: `MUST_MODIFY` (Incorrect).
- **Corrected Classification**: `MAY_MODIFY_AFTER_SEPARATE_AUTHORIZATION`.
- **Status**: `SIMULATOR_CHANGE_STATUS = ENGINEERINGALLY_REQUIRED_BUT_NOT_YET_AUTHORIZED`.

> [!CAUTION]
> `system/simulation/simulator.py` is removed from the mandatory implementation list. It may only be modified if closed-loop multi-step synthetic simulation is separately authorized by human decision-makers.
