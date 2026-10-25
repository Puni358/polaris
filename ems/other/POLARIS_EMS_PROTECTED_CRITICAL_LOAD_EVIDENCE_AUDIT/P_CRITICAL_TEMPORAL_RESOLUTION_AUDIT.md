# POLARIS EMS — P_CRITICAL TEMPORAL RESOLUTION AUDIT

## 1. Executive Summary

This document audits the temporal resolution of **$P_{\text{critical}}(t)$** across the existing POLARIS software architecture.

---

## 2. Architecture Resolution Mapping

| Subsystem | File Reference | Native Temporal Resolution | Alignment with $P_{\text{critical}}(t)$ |
| :--- | :--- | :--- | :--- |
| **ForecastBundle Schema** | [`system/schemas/forecast_bundle.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py) | 1-Hour Step (24 Horizon Points) | Aligned for 24-hour energy integrals. |
| **MILP Optimizer** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py) | 1-Hour Step ($H=24$) | Aligned for hourly dispatch planning. |
| **Emergency Detector (ECD)** | [`system/control/ecd.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py) | Continuous per control loop | Consumes 1-hour average power values. |
| **Digital Twin Simulator** | [`system/adapters/h10_runtime_adapter.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/adapters/h10_runtime_adapter.py) | 1-Hour Step | Simulates 1-hour energy balances. |

---

## 3. Sub-Hourly Dynamics Assessment

1. **Hourly Energy Integration**: 1-hour resolution is sufficient to compute total critical energy consumption $E_{\text{critical}} = \sum_{t=1}^6 P_{\text{critical}}(t) \times 1\text{h}$ over the $6\text{-hour}$ $T_{\text{required\_baseline}}$ horizon.
2. **Sub-Hourly Inrush & Startup Spikes**: Sub-hourly power transients (e.g. 5–15 second motor inrush currents during pump or compressor startup) are averaged out over 1-hour timesteps. Inrush peak power is **NOT** represented in 1-hour MPC schemas.
3. **Engineering Gap**: If battery inverter max discharge power ($P_{\text{dis,max}}$) or generator surge capacity must be validated against motor startup inrush, a sub-hourly peak power attribute must be added to equipment specs.

---

## 4. Status Classification

```yaml
P_CRITICAL_TEMPORAL_RESOLUTION_STATUS: 1_HOUR_MPC_RESOLVED_SUB_HOURLY_UNESTABLISHED
RECOMMENDATION: Retain 1-hour resolution for MPC/ECD energy balance; track peak inrush power as an auxiliary engineering parameter.
```
