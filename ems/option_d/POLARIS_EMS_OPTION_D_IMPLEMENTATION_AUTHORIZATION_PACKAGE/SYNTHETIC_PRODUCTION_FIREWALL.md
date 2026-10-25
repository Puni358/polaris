# SYNTHETIC PRODUCTION FIREWALL

## Benchmark Fixture vs Production Data Isolation

This document defines the strict firewall separating synthetic benchmark fixture values from production station engineering parameters.

---

## Fixture Parameter Classification Matrix

| Parameter Category | Synthetic Benchmark Fixture Value | Production Station Parameter Status | Usage Restriction |
| :--- | :--- | :--- | :--- |
| **Heating Critical Load** | $15.0\text{ kW}$ | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Water Critical Load** | $10.0\text{ kW}$ | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Comms Critical Load** | $5.0\text{ kW}$ | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Total Critical Load** | $30.0\text{ kW}$ | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Flexible Noncritical Load** | $15.0\text{ kW}$ | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Total Synthetic Demand** | $45.0\text{ kW}$ | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Fixture Battery Min SOC** | $20.0\%$ (Technical SOC Floor) | `NOT_ESTABLISHED` (Option-D production discharge boundary is open) | Synthetic benchmark test ONLY. |
| **Battery Usable Capacity** | $200.0\text{ kWh}$ ($40\text{--}190\text{ kWh}$) | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Battery Power Rating** | $50.0\text{ kW}$ | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Diesel Power Bounds** | $10.0\text{--}60.0\text{ kW}$ | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Fuel Tank Scenarios** | $500\text{ L}, 20\text{ L}, 10\text{ L}$ | `NOT_ESTABLISHED` | Synthetic test harness ONLY. |
| **Survivability Test Horizon** | $72.0\text{ hours}$ | $T_{\text{required}} = 6.0\text{ hours}$ (Governed Baseline) | $72\text{h}$ synthetic test ONLY. |

---

## Battery Terminology Firewall

The following distinctions must be strictly maintained across all documentation and software representations:

1. **Technical SOC Floor** ($20\%$ in fixture): A physical/model boundary used for synthetic benchmark calculations.
2. **Governed Battery Discharge Boundary**: The production boundary at which Option D stops automated battery support (`NOT_ESTABLISHED`).
3. **Emergency Battery Reserve (EBR)**: GAP19 Stage 2 multi-objective target.
4. **Terminal SOC**: GAP19 multi-step horizon end-state target.

> [!CAUTION]
> The synthetic fixture's 20% SOC floor MUST NOT be written as `20% = EBR` or `20% = Option-D production discharge boundary`.

---

## Firewall Enforcements

1. **Hardcoding Prohibition**: Synthetic fixture numbers ($15, 10, 5, 45, 200, 72, 20\%$) MUST NOT be hardcoded into Python source files (`ecd.py`, `runner.py`, `milp.py`, schemas).
2. **Dynamic Ingestion**: All load values and system capacities must be dynamically ingested from configuration dictionaries or `StationState` fields.
3. **No Production Claims**: Demonstrating successful dispatch on the 45 kW synthetic benchmark fixture does NOT imply station survivability or operational readiness for the real Nuolja station.
