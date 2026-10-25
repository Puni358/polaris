# D4 OPEN ENGINEERING INPUTS

## 1. OPEN REAL-STATION ENGINEERING INPUTS REGISTER

Sealing governance decision D4 leaves the following physical engineering parameters open for field engineering specification prior to site deployment.

---

## 2. OPEN ENGINEERING PARAMETERS REGISTER

| Parameter ID | Parameter Description | Target Deployment Component | Current Status | Required Action |
| :--- | :--- | :--- | :--- | :--- |
| **ENG-INPUT-01** | Equipment Circuit Mapping for Protected Categories | Site Electrical Schema | `ENGINEERING_REQUIRED` | Map physical site breakers to Heating, Water, Comms |
| **ENG-INPUT-02** | Real Minimum Viable Power Vectors $P_{i,\text{min}}(t)$ | `system/config/loads.yaml` | `ENGINEERING_REQUIRED` | Define physical minimum kW required for human/site survivability |
| **ENG-INPUT-03** | Max Continuous Degraded Duration $T_{\text{max\_degraded}}$ | `system/config/station.yaml` | `ENGINEERING_REQUIRED` | Set maximum hours system can run in degraded D4 mode before escalation |
| **ENG-INPUT-04** | Escalation Fuel Reserve Threshold $V_{\text{escalate}}$ | `system/config/diesel.yaml` | `ENGINEERING_REQUIRED` | Set fuel volume threshold in Liters for operator escalation alarm |
