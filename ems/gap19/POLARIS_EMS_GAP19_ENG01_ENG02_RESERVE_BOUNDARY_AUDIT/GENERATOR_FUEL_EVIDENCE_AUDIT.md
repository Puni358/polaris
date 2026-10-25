# POLARIS EMS GAP19 — GENERATOR / FUEL EVIDENCE AUDIT

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_ENG01_ENG02_RESERVE_BOUNDARY_AUDIT`  
**Focus**: **DIESEL GENERATOR & FUEL INVENTORY PARAMETER PROVENANCE**  

---

## 1. Audit of Diesel Generator & Fuel Inputs

| Diesel Parameter | Value in `system/config/diesel.yaml` | Evidence Classification | Production Status |
| :--- | :--- | :--- | :---: |
| **Maximum Power Rating ($P_{\text{D,max}}$)** | $100,000.0\text{ W}$ ($100\text{ kW}$) | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **NOT_ESTABLISHED** for real site |
| **Minimum Stable Output ($P_{\text{D,min}}$)** | $10,000.0\text{ W}$ ($10\text{ kW}$) | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **NOT_ESTABLISHED** for real site |
| **Base Fuel Consumption** | $5.0\text{ L/h}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **NOT_ESTABLISHED** for real site |
| **Marginal Fuel Consumption** | $0.00025\text{ L/Wh}$ ($0.25\text{ L/kWh}$) | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **NOT_ESTABLISHED** for real site |
| **Startup Fuel Penalty** | $2.0\text{ Liters}$ | `SYNTHETIC_ENGINEERING_ASSUMPTION` | **NOT_ESTABLISHED** for real site |
| **Real Station Fuel Inventory** | Unspecified ($100\text{L}$ test default) | `NOT_ESTABLISHED` | **NOT_ESTABLISHED** |
| **Total Tank Capacity** | Unspecified ($500\text{L}$ test default) | `NOT_ESTABLISHED` | **NOT_ESTABLISHED** |
| **Resupply Schedule / SLA** | Unspecified | `NOT_ESTABLISHED` | **NOT_ESTABLISHED** |

---

## 2. Critical Fuel Inventory Preservation Rule

```text
REAL STATION FUEL INVENTORY = NOT_ESTABLISHED
```

* **Test Values Discarded**: Historical test scripts used $500\text{L}$, $100\text{L}$, $50\text{L}$, $20\text{L}$, and $12.5\text{L}$ fuel levels.
* **Audit Finding**: All such values are **`SYNTHETIC_ENGINEERING_ASSUMPTION`** parameters.
* **Firewall Rule**: Zero real fuel tank calibration sheets or inventory telemetry records exist in the repository (Item **EVID-ST-01**). Synthetic test fuel numbers MUST NOT be cited as station capacity.
