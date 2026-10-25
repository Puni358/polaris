# POLARIS EMS — P_CRITICAL MASTER DATA GAP REGISTER

## Executive Summary

This register details all unresolved station engineering gaps, missing physical datasheets, and unestablished schema extensions blocking construction of a production **$P_{\text{critical}}(t)$** trajectory.

---

## Master Data Gap Register

| Gap ID | Category | Missing Parameter / Input | Current Status | Impact on $P_{\text{critical}}(t)$ Construction | Required Engineering Step |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GAP-PC-01** | Equipment | Protected Equipment Inventory | `NOT_ESTABLISHED` | Blocks identification of physical loads comprising $P_{\text{critical}}$. | Site equipment nameplate audit. |
| **GAP-PC-02** | Electrical | Critical Breaker / Circuit Mapping | `NOT_ESTABLISHED` | Blocks load actuator control & breaker shedding logic. | As-built electrical drawing audit. |
| **GAP-PC-03** | Thermal | Building Thermal / Heating Model | `ENGINEERING_REQUIRED` | Blocks calculation of ambient temperature-driven heating $P_{\text{heating}}(t)$. | Building thermal loss modeling. |
| **GAP-PC-04** | Pumping | Water Filtration Operating Profile | `NOT_ESTABLISHED` | Blocks dynamic water pumping power profile $P_{\text{water}}(t)$. | Water system pump spec sheet review. |
| **GAP-PC-05** | Comms | Emergency Comms Power Profile | `NOT_ESTABLISHED` | Blocks comms & telemetry power profile $P_{\text{comms}}(t)$. | SCADA & radio rack power measurement. |
| **GAP-PC-06** | Shortfall | Minimum Viable Operating Levels | `ENGINEERING_REQUIRED` | Blocks calculation of $P_{\text{min,critical}}$ for Rule D4 shortfall allocation. | Equipment minimum operational specs. |
| **GAP-PC-07** | Shortfall | Proportional Allocation Weights | `ENGINEERING_REQUIRED` | Blocks numerical power rationing under Option D Rule D4. | Formulate allocation weighting vector. |
| **GAP-PC-08** | Transient | Sub-Hourly Inrush Power Spikes | `NOT_ESTABLISHED` | Blocks inverter surge capacity validation during motor startup. | Motor locked-rotor current audit. |
| **GAP-PC-09** | Schema | Additive `critical_demand` Schema Field | `SCHEMA_IMPACT_IDENTIFIED` | Blocks transmission of critical load vector in `ForecastBundle`. | Define `ForecastBundle` schema v1.1.0. |
| **GAP-PC-10** | Data | Nuolja Station Real Demand Dataset | `DATA_BLOCKED` | Blocks empirical validation of site load profile. | Real energy data access authorization. |

---

## Construction Readiness Conclusion

```yaml
P_CRITICAL_T_CONSTRUCTION_STATUS: NOT_READY
REASON: 10 critical engineering and data gaps block the construction of an empirical P_critical(t) trajectory.
FIREWALL_RULE: No synthetic replacement trajectory will be created or promoted to production status.
```
