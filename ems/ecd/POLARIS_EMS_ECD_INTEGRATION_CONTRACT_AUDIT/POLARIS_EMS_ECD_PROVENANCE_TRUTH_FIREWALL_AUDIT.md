# POLARIS EMS — ECD PROVENANCE & TRUTH FIREWALL AUDIT

## 1. Executive Summary

This document audits the data provenance and truth firewall mechanisms governing the Emergency Condition Detector (ECD) during integrated operation.

---

## 2. Truth Firewall Leakage Analysis

To prevent future ground-truth contamination:
1. **Critical Load Trajectory Leakage Check**: The ECD consumes `critical_demand_w` produced by `ForecastEngine` at origin $t_0$. Future actual demand values from `data_provider.get_future_ground_truth()` are strictly isolated to `DigitalTwinSimulator` and **MUST NEVER** be accessible to `EmergencyConditionDetector`.
2. **Fuel & Battery Telemetry Leakage Check**: Telemetry inputs (`soc_pct`, `fuel_remaining_liters`) are read strictly from `StationState` at step origin $t_0$. No future simulation state changes may be read ahead.
3. **Causal Time Ordering**: All ECD evaluation timestamps satisfy $t_{\text{eval}} = t_0$.

---

## 3. Provenance Chain

Every `EmergencyAssessment` output record contains a provenance metadata block:
- `t0_timestamp`: Step origin ISO-8601 UTC string.
- `forecast_bundle_id`: Hash digest of input `ForecastBundle`.
- `station_state_hash`: Hash digest of input `StationState`.
- `target_horizon_source`: Operational override payload identity or baseline config origin.

Status: `VERIFIED`
