# Fuel State Boundary Audit (`FUEL_STATE_BOUNDARY.md`)

**FORENSIC AUDIT**: POLARIS EMS GAP19 — Cycle-Chain State Reconciliation Audit  
**VERDICT**: `FUEL_VOLUME_STATE_CONTINUITY = NOT_ESTABLISHED`

---

## 1. Schema & Telemetry Findings

- **`StationState` Schema**: Version `1.0.0` tracks `diesel_running` (`bool`) and `diesel_hours_running` (`float`). Fuel mass/volume remaining (e.g. liters) is **NOT** a field in `StationState`.
- **`diesel_hours_running` Continuity**: Incremented continuously across Cycles 1-8 ($1.0\text{h} \to 8.0\text{h}$).
- **Fuel Volume Representation**: Fuel consumption rate ($L/h$) is computed in solver telemetry, but remaining fuel volume is not tracked as a physical state variable.

---

## 2. Authoritative Boundary Classification

Fuel volume state continuity cannot be claimed because fuel remaining is not present in the physical state schema.

```text
FUEL_HOURS_CONTINUITY = PASS
FUEL_VOLUME_STATE_CONTINUITY = NOT_ESTABLISHED
```
