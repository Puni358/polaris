# POLARIS EMS — PROTECTED CRITICAL LOAD MASTER PARAMETER MATRIX

## Executive Statement

This document compiles the complete 19-parameter evidence matrix for **Protected Critical Load ($P_{\text{critical}}(t)$)** and related resource inputs across the POLARIS codebase and configuration files.

---

## Master Parameter Matrix

| Parameter Name | Current Value in Repository | Evidence Status | Source Reference | Production-Ready? |
| :--- | :--- | :--- | :--- | :--- |
| **Protected Equipment Inventory** | `NOT_FOUND` | `NOT_ESTABLISHED` | [`PROTECTED_CRITICAL_EQUIPMENT_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_PROTECTED_CRITICAL_LOAD_EVIDENCE_AUDIT/PROTECTED_CRITICAL_EQUIPMENT_AUDIT.md) | `NO` |
| **Critical Circuit Mapping** | `NOT_FOUND` | `NOT_ESTABLISHED` | [`CRITICAL_CIRCUIT_MAPPING_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_PROTECTED_CRITICAL_LOAD_EVIDENCE_AUDIT/CRITICAL_CIRCUIT_MAPPING_AUDIT.md) | `NO` |
| **$P_{\text{critical}}(t)$ Trajectory** | `30,000 W` (static scalar) | `PROTOTYPE_ONLY` | [`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml) | `NO` |
| **$P_{\text{min,heating}}$** | `UNDEFINED` | `ENGINEERING_REQUIRED` | [`P_CRITICAL_MINIMUM_VIABLE_LEVEL_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_PROTECTED_CRITICAL_LOAD_EVIDENCE_AUDIT/P_CRITICAL_MINIMUM_VIABLE_LEVEL_AUDIT.md) | `NO` |
| **$P_{\text{min,water}}$** | `UNDEFINED` | `ENGINEERING_REQUIRED` | [`P_CRITICAL_MINIMUM_VIABLE_LEVEL_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_PROTECTED_CRITICAL_LOAD_EVIDENCE_AUDIT/P_CRITICAL_MINIMUM_VIABLE_LEVEL_AUDIT.md) | `NO` |
| **$P_{\text{min,comms}}$** | `UNDEFINED` | `ENGINEERING_REQUIRED` | [`P_CRITICAL_MINIMUM_VIABLE_LEVEL_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_PROTECTED_CRITICAL_LOAD_EVIDENCE_AUDIT/P_CRITICAL_MINIMUM_VIABLE_LEVEL_AUDIT.md) | `NO` |
| **Startup / Inrush Peak Power** | `UNDEFINED` | `NOT_ESTABLISHED` | [`P_CRITICAL_TEMPORAL_RESOLUTION_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_PROTECTED_CRITICAL_LOAD_EVIDENCE_AUDIT/P_CRITICAL_TEMPORAL_RESOLUTION_AUDIT.md) | `NO` |
| **Equipment Duty Cycles** | `4h/day` (water pumping) | `PROTOTYPE_ONLY` | [`system/config/loads.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/loads.yaml) | `NO` |
| **Heating Temp Dependency** | `UNDEFINED` | `ENGINEERING_REQUIRED` | [`P_CRITICAL_DYNAMIC_DRIVER_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_PROTECTED_CRITICAL_LOAD_EVIDENCE_AUDIT/P_CRITICAL_DYNAMIC_DRIVER_AUDIT.md) | `NO` |
| **Water Operating Dependency** | `UNDEFINED` | `NOT_ESTABLISHED` | [`P_CRITICAL_DYNAMIC_DRIVER_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_PROTECTED_CRITICAL_LOAD_EVIDENCE_AUDIT/P_CRITICAL_DYNAMIC_DRIVER_AUDIT.md) | `NO` |
| **Comms Duty Dependency** | `UNDEFINED` | `NOT_ESTABLISHED` | [`P_CRITICAL_DYNAMIC_DRIVER_AUDIT.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_PROTECTED_CRITICAL_LOAD_EVIDENCE_AUDIT/P_CRITICAL_DYNAMIC_DRIVER_AUDIT.md) | `NO` |
| **Temporal Resolution** | `1-Hour Step` | `ESTABLISHED_FOR_MPC` | [`system/schemas/forecast_bundle.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py) | `YES` (for 1h MPC) |
| **Usable Battery Energy** | `160 kWh` ($200\text{kWh}, \text{SOC}\in[20\%, 100\%]$) | `PROTOTYPE_ESTABLISHED` | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml) | `PROTOTYPE_ONLY` |
| **Battery SOC Bounds** | `20% / 95%` | `PROTOTYPE_ESTABLISHED` | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml) | `PROTOTYPE_ONLY` |
| **Battery Max Discharge** | `50,000 W` | `PROTOTYPE_ESTABLISHED` | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml) | `PROTOTYPE_ONLY` |
| **Generator Min Power** | `10,000 W` | `PROTOTYPE_ESTABLISHED` | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml) | `PROTOTYPE_ONLY` |
| **Generator Fuel Curve** | `5 + 0.00025 * P` L/h | `PROTOTYPE_ESTABLISHED` | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml) | `PROTOTYPE_ONLY` |
| **Fuel Inventory Telemetry** | `StationState.fuel_remaining_liters` | `INTERFACE_ESTABLISHED` | [`system/schemas/station_state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py) | `YES` (Interface) |
| **Renewable Baseline** | $P_{\text{solar}}=0, P_{\text{wind}}=0$ | `ESTABLISHED_STRESS_BASELINE` | [`POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE/POLARIS_EMS_ECD_CANONICAL_SYNTHETIC_FIXTURE.json) | `YES` (for zero-renewable) |

---

## Matrix Audit Conclusion

Out of 19 required parameters, 16 are currently `PROTOTYPE_ONLY`, `ENGINEERING_REQUIRED`, or `NOT_ESTABLISHED`. No missing values were filled or assumed during this audit.
