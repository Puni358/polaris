# Diesel State Chain Audit (`DIESEL_STATE_CHAIN_AUDIT.md`)

**GATE CONTEXT**: POLARIS EMS GAP19 — Digital Twin State-Continuity Forensic Review  
**VERDICT**: `PASS`

---

## 1. Diesel State Dynamics in DigitalTwinSimulator

In [`system/simulation/simulator.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/simulation/simulator.py#L54-L55):

```python
diesel_running = p_diesel > 0
diesel_hours = (current_state.diesel_hours_running + 1.0) if diesel_running else 0.0
```

Where `p_diesel` is `dispatch_plan.diesel_power[0]`.

---

## 2. Diesel State Progression Across 8 Cycles

| Cycle | Origin Timestamp | Input Diesel Running | Input Diesel Hours | Committed $P_{\text{diesel}, 0}$ (W) | Output Diesel Running | Output Diesel Hours | Continuity Status |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | `2024-01-01T20:00:00Z` | `False` | 0.0h | 44,064.27 W | `True` | 1.0h | `PASS` |
| 2 | `2024-01-01T21:00:00Z` | `True` | 1.0h | 15,000.00 W | `True` | 2.0h | `PASS` |
| 3 | `2024-01-01T22:00:00Z` | `True` | 2.0h | 15,000.00 W | `True` | 3.0h | `PASS` |
| 4 | `2024-01-01T23:00:00Z` | `True` | 3.0h | 15,000.00 W | `True` | 4.0h | `PASS` |
| 5 | `2024-01-02T00:00:00Z` | `True` | 4.0h | 15,000.00 W | `True` | 5.0h | `PASS` |
| 6 | `2024-01-02T01:00:00Z` | `True` | 5.0h | 15,000.00 W | `True` | 6.0h | `PASS` |
| 7 | `2024-01-02T02:00:00Z` | `True` | 6.0h | 15,000.00 W | `True` | 7.0h | `PASS` |
| 8 | `2024-01-02T03:00:00Z` | `True` | 7.0h | 15,000.00 W | `True` | 8.0h | `PASS` |

---

## 3. Physical Diesel Fuel Inventory Representation

- **Physical Inventory**: Physical fuel volume/mass (liters or kg) is **NOT** represented in the `StationState` schema.
- **Objective Cost vs Physical Fuel**: Objective function J3 diesel cost ($15 startup penalty + proportional fuel cost) is an economic optimization metric; it does NOT mutate physical fuel volume in `StationState`.

Classified:
```text
DIESEL_STATE_CONTINUITY = PASS
DIESEL_PHYSICAL_INVENTORY_STATE = NOT_REPRESENTED_IN_CURRENT_RUNTIME
```
