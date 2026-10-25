# Diesel Dynamics Forensic Audit (`DIESEL_DYNAMICS_FORENSIC_AUDIT.md`)

**FORENSIC AUDIT**: POLARIS EMS GAP19 — Post-8-Cycle Forensic Behavior Audit  
**VERDICT**: `PASS`

---

## 1. Diesel State Progression Table

| Cycle | Diesel Power $P_{\text{diesel}}[0]$ (W) | Diesel Running | Diesel Hours Running | Fuel State Classification |
| :---: | :---: | :---: | :---: | :---: |
| **01** | 44064.27 | `True` | 1.0h | `NOT_ESTABLISHED (Schema Boundary)` |
| **02** | 15000.00 | `True` | 2.0h | `NOT_ESTABLISHED (Schema Boundary)` |
| **03** | 15000.00 | `True` | 3.0h | `NOT_ESTABLISHED (Schema Boundary)` |
| **04** | 15000.00 | `True` | 4.0h | `NOT_ESTABLISHED (Schema Boundary)` |
| **05** | 15000.00 | `True` | 5.0h | `NOT_ESTABLISHED (Schema Boundary)` |
| **06** | 15000.00 | `True` | 6.0h | `NOT_ESTABLISHED (Schema Boundary)` |
| **07** | 15000.00 | `True` | 7.0h | `NOT_ESTABLISHED (Schema Boundary)` |
| **08** | 15000.00 | `True` | 8.0h | `NOT_ESTABLISHED (Schema Boundary)` |

---

## 2. Detailed Findings

- **A-B. Power & Running State**: Generator power bounded in $[10\text{ kW}, 100\text{ kW}]$ when running; `diesel_running` Boolean physically consistent.
- **C-D. Hours Counter**: `diesel_hours_running` incremented continuously from $1.0\text{h}$ to $8.0\text{h}$ with zero reset.
- **E. Objective Integration**: Fuel consumption rate included in $J_3$ objective.
- **F. Fuel Volume Boundary**: `StationState` schema (v1.0.0) tracks operating status and hours, but does not contain remaining fuel volume in liters.

```text
DIESEL_DYNAMICS_STATUS = PASS
FUEL_VOLUME_STATE_CONTINUITY = NOT_ESTABLISHED
```
