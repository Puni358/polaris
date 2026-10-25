# POLARIS EMS GAP19 — GENERATOR RECOVERY

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_TARGET_STATION_EVIDENCE_RECOVERY`  
**Domain C**: **DIESEL GENERATOR SYSTEMS**  

---

## 1. Generator Recovery Audit Matrix

| Generator Parameter | Target Station Finding | Evidence Classification | Status & Notes |
| :--- | :--- | :--- | :--- |
| **Make / Model** | Un-documented for target station. | `NOT_ESTABLISHED` | Zero manufacturer nameplate data found. |
| **Rated Electrical Power ($P_{\text{D,max}}$)** | $100\text{ kW}$ (Prototype config value). | `SYNTHETIC_ENGINEERING_ASSUMPTION` | Prototype value in `diesel.yaml`. |
| **Minimum Stable Output ($P_{\text{D,min}}$)** | $10\text{ kW}$ (Prototype config value). | `SYNTHETIC_ENGINEERING_ASSUMPTION` | Prototype low-load limit in `diesel.yaml`. |
| **Fuel Consumption Model** | $5.0\text{ L/h} + 0.25\text{ L/kWh}$. | `SYNTHETIC_ENGINEERING_ASSUMPTION` | Linear model; un-verified on engine bench. |
| **Startup Fuel Penalty** | $2.0\text{ Liters}$. | `SYNTHETIC_ENGINEERING_ASSUMPTION` | Un-verified cold-start penalty. |
| **Generator Redundancy** | Single generator assumed. | `NOT_ESTABLISHED` | Zero single-line electrical diagrams found. |

---

## 2. Recovery Outcome & Status

```text
GENERATOR_ENGINEERING_INPUT_STATUS = NOT_ESTABLISHED
```

Generic formulas ($5\text{L/h} + 0.25\text{L/kWh}$) are NOT accepted as station evidence because no certified engine test report for Nuolja station generator hardware exists.
