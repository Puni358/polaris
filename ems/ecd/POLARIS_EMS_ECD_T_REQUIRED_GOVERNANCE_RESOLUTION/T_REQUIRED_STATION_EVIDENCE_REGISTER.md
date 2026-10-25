# POLARIS EMS — T_REQUIRED STATION EVIDENCE REGISTER

## Executive Statement

This register details the empirical site data and physical documentation required from **Nuolja Station** before production $T_{\text{required}}$ configuration can be validated and unblocked for deployment.

---

## Master Station Evidence Register

| Evidence Item ID | Category | Description | Current Status | Required Empirical Artifact |
| :--- | :--- | :--- | :--- | :--- |
| **EVID-ST-01** | Fuel Storage | Certified fuel tank volume and level transmitter calibration sheet. | `NOT_ESTABLISHED` | Nuolja site tank inspection report. |
| **EVID-ST-02** | Electrical Wiring | As-built single-line diagram mapping critical vs noncritical breaker circuits. | `NOT_ESTABLISHED` | As-built electrical schematic. |
| **EVID-ST-03** | Battery Hardware | Manufacturer battery spec sheet, BMS telemetry map, and temperature derating curves. | `PROTOTYPE_ONLY` | Certified battery & BMS datasheets. |
| **EVID-ST-04** | Diesel Generator | Manufacturer fuel consumption curve, minimum load limit, and cold-start requirements. | `PROTOTYPE_ONLY` | Certified engine bench test report. |
| **EVID-ST-05** | Site Logistics | Official station fuel delivery contract, resupply schedule, and logistics lead time window. | `NOT_ESTABLISHED` | Station logistics operating agreement. |
| **EVID-ST-06** | Meteorology | Nuolja site historical weather anomaly records (maximum blizzard duration distribution). | `NOT_ESTABLISHED` | Site historical weather dataset. |
| **EVID-ST-07** | Operator SLA | Station operator response SLA and site maintenance dispatch protocol. | `NOT_ESTABLISHED` | Station SOP manual. |
| **EVID-ST-08** | Fuel Properties | Diesel fuel grade, arctic pour point, and storage degradation specifications. | `NOT_ESTABLISHED` | Fuel sample lab analysis. |

---

## Deployment Gate Impact

Production deployment of POLARIS EMS remains **BLOCKED** until all eight station evidence items are collected and validated against the 6-hour production baseline ($T_{\text{required\_baseline}} = 6\text{h}$).
