# POLARIS EMS — HD-03 CANDIDATE SOURCE MATRIX

## 1. CANDIDATE SOURCE AUDIT TABLE

The table below lists all potential data sources audited across the workspace for $T_{\text{required}}$ operational schedules:

| Candidate Source | Exact Meaning | Station-Specific? | Audit Status | Evidence Found |
| :--- | :--- | :--- | :--- | :--- |
| **Station Operations Plans** | Station operational procedures and refuel cadences | Yes | `ABSENT` | No official operational plan exists in repo |
| **Logistics Resupply Contracts** | Contractual fuel delivery schedule for remote site | Yes | `ABSENT` | No resupply schedule or contract exists |
| **Station Autonomy Specs** | Mandatory station survival autonomy requirement | Yes | `ABSENT` | No autonomy requirement document exists |
| **Mission Control Overrides** | Telemetry payload containing dynamic survival window | Yes | `ABSENT` | Option A message stream unimplemented |
| **Deployment Configuration** | Static site configuration parameter file | Yes | `ABSENT` | Option C deployment config unimplemented |
| **System Diesel Config (`diesel.yaml`)**| Diesel cost ($2.50/L) and engine constraints | Yes (Generic) | `PRESENT` | Contains fuel price only; zero resupply schedule |
| **MPC Solver Horizon ($H=24\text{h}$)** | 24-hour rolling MILP optimization horizon | No (Algorithmic) | `PRESENT` | Solver horizon only; not $T_{\text{required}}$ |
| **EBR Buffer Horizon ($N=6\text{h}$)** | 6-hour dynamic critical load buffer window | No (Policy) | `PRESENT` | HD-01B normal buffer; not $T_{\text{required}}$ |
| **Decision 08 Resupply Docs ($30\text{d}$)** | Provisional budget allocation example | No (Example) | `PRESENT` | Provisional budget example; not $T_{\text{required}}$ |

---

## 2. SOURCE AUDIT CONCLUSION

No candidate source in the repository provides an authoritative station-specific survival window or resupply schedule.
All existing repository sources are either **absent**, **unimplemented**, or **unrelated solver/resilience parameters**.
