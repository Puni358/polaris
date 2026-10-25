# POLARIS EMS — HD-03 NUMERICAL CANDIDATE PROVENANCE MATRIX

## 1. NUMERICAL PROVENANCE TABLE

The table below classifies every numerical candidate value observed in the repository by its exact original meaning and authority class:

| Candidate Value | Value | Original Meaning in Code / Governance | Authority Class | $T_{\text{required}}$ Eligible? |
| :--- | :--- | :--- | :--- | :--- |
| **MPC Horizon ($H$)** | $24\text{h}$ | Rolling optimization window for MILP solver foresight | `HISTORICAL_IMPLEMENTATION_VALUE` / `UNRELATED_VALUE` | **NO** (Conflates solver window with resupply window) |
| **EBR Interval ($N$)** | $6\text{h}$ | HD-01B fixed normal-operation critical load battery buffer | `PROJECT_ENGINEERING_ASSUMPTION` / `HISTORICAL_IMPLEMENTATION_VALUE` | **NO** (Conflates normal buffer with emergency survival) |
| **Resupply Budget Example** | $30\text{d}$ | Decision 08 provisional long-term fuel budget allocation example | `PROVISIONAL_EXAMPLE` | **NO** (Long-term financial budget example, not operational guarantee) |
| **Generator Min Runtime** | $2\text{h}$ | Diesel engine thermal minimum run constraint | `UNRELATED_VALUE` | **NO** (Engine thermal constraint, not station survival) |
| **UPS Hold-Up Time** | $15\text{m}$ | Electrical ATS/UPS hold-up interval during transfer | `UNRELATED_VALUE` | **NO** (Hold-up time, not EMS survival window) |
| **Crude Cell Discharge** | $6.67\text{h}$ | Physical calculation ($100\text{ kWh} / 15\text{ kW}$ load) | `DERIVED_PHYSICAL_QUANTITY` | **NO** (Cell discharge estimate; violates non-derivation directive) |

---

## 2. PROVENANCE AUDIT SUMMARY

Only values classified as **`AUTHORITATIVE_OPERATIONAL_REQUIREMENT`** (Class A) or **`AUTHORITATIVE_STATION_DATA`** (Class B) are eligible to establish $T_{\text{required}}$. 

No Class A or Class B values exist in the POLARIS repository. Classes C through G **MUST NOT** be promoted to $T_{\text{required}}$ policy merely because a numerical value exists.
