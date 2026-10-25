# POLARIS EMS — MINIMUM FIXTURE BATTERY MODEL

## 1. Executive Summary

This document specifies the minimum synthetic battery model for BESS simulation and control.

---

## 2. Battery Model Parameters

- **Total Capacity ($C_{\text{bat}}$)**: $200,000\text{ Wh}$ ($200\text{ kWh}$).
- **Usable SOC Range**: $[20.0\%, 95.0\%]$ ($40\text{ kWh}$ floor, $190\text{ kWh}$ ceiling).
- **Charge / Discharge Efficiency ($\eta_{\text{chg}}, \eta_{\text{dis}}$)**: $0.92$ ($92\%$).
- **Max Power Limits ($P_{\text{chg,max}}, P_{\text{dis,max}}$)**: $50,000\text{ W}$ ($50\text{ kW}$).
- **Degradation Cost Penalty**: $\$0.00005/\text{Wh}$ throughput.

---

## 3. Provenance & Claim Boundary

```yaml
BATTERY_MODEL_CLASSIFICATION: REUSED_SYNTHETIC_ENGINEERING_PARAMETER
SOURCE: system/config/battery.yaml
STATION_IDENTITY: NONE
CLAIM_FIREWALL: Reused prototype values for BESS control demonstration. Must NOT be cited as Nuolja battery capacity.
```
