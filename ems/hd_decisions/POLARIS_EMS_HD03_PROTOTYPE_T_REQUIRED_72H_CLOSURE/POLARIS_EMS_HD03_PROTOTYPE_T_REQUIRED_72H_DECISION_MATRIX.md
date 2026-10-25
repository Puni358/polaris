# POLARIS EMS — HD-03 TIME HORIZONS DECISION MATRIX

## 1. COMPACT TIME HORIZONS DECISION MATRIX

The table below contrasts the three distinct time horizons in POLARIS EMS, demonstrating zero conflation between them:

| Horizon Name | Value | Subsystem Scope | Governed Purpose | Authority Basis |
| :--- | :--- | :--- | :--- | :--- |
| **Normal EBR Interval ($N$)** | $6\text{ HOURS}$ | Dynamic EBR Target (HD-01B) | Normal-operation critical load battery buffer | Human Governance Policy (HD-01B) |
| **MPC Optimization Horizon ($H$)** | $24\text{ HOURS}$ | Rolling MILP Solver | Computational foresight & forecast horizon | Mathematical MILP Specification |
| **Prototype Survivability ($T_{\text{req}}$)** | $72\text{ HOURS}$ | Emergency Detector Prototype | Synthetic multi-day survivability test parameter | Human Governance Policy (HD-03 Prototype) |

---

## 2. PROHIBITED CONFLATIONS & DERIVATIONS

The 72-hour prototype value **MUST NOT** be described as being derived from:
1. The 24-hour MPC horizon ($H=24\text{h}$).
2. The 6-hour EBR resilience interval ($N=6\text{h}$).
3. Battery capacity or state of charge calculations.
4. Fuel tank volume or diesel burn rates.
5. Historical station autonomy data.
6. Station operations or logistics resupply schedules.
