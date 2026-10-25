# POLARIS EMS — P_CRITICAL PROTOTYPE FIREWALL AUDIT

## 1. Executive Summary

This document performs a strict forensic audit verifying the isolation of synthetic prototype load values from binding station engineering facts.

---

## 2. Prototype Value Classification Matrix

All load values currently existing in `system/config/loads.yaml`, `system/config/station.yaml`, and synthetic test fixtures are explicitly audited below:

| Prototype Value | File Location | Config Status Label | Classification | Production Fact? |
| :--- | :--- | :--- | :--- | :--- |
| **$30,000\text{ W}$ Critical Baseline** | `system/config/loads.yaml:5` | `PROTOTYPE_ASSUMPTION` | `SYNTHETIC_PROTOTYPE_PARAMETER` | **NO** |
| **$10,000\text{ W}$ Water Pumping** | `system/config/loads.yaml:8` | `PROTOTYPE_ASSUMPTION` | `SYNTHETIC_PROTOTYPE_PARAMETER` | **NO** |
| **$5,000\text{ W}$ Secondary Heating** | `system/config/loads.yaml:15` | `PROTOTYPE_ASSUMPTION` | `SYNTHETIC_PROTOTYPE_PARAMETER` | **NO** |
| **$10/\text{Wh}$ Unmet Penalty** | `system/config/loads.yaml:4` | `PROTOTYPE_ASSUMPTION` | `SYNTHETIC_SOLVER_WEIGHT` | **NO** |
| **$200\text{ kWh}$ Battery Capacity** | `system/config/battery.yaml:3` | Prototype Config | `PROTOTYPE_MODEL_PARAMETER` | **NO** |
| **$20\% / 80\% / 95\%$ SOC Limits** | `system/config/battery.yaml:4-5` | Prototype Config | `PROTOTYPE_MODEL_PARAMETER` | **NO** |
| **$10\text{ kW}$ Gen Minimum Load** | `system/config/diesel.yaml:4` | Prototype Config | `PROTOTYPE_MODEL_PARAMETER` | **NO** |
| **$5\text{ L/h}$ Base Fuel Rate** | `system/config/diesel.yaml:6` | Prototype Config | `PROTOTYPE_MODEL_PARAMETER` | **NO** |
| **$0.25\text{ L/kWh}$ Marginal Fuel** | `system/config/diesel.yaml:7` | Prototype Config | `PROTOTYPE_MODEL_PARAMETER` | **NO** |
| **$72\text{h}$ $T_{\text{required}}$ Prototype** | `ECD_CANONICAL_FIXTURE` | Synthetic Fixture | `SYNTHETIC_ENGINEERING_TEST_VALUE_ONLY` | **NO** |
| **$2\text{h}$ $T_{\text{test}}$ Logic Value** | `ECD_CANONICAL_FIXTURE` | Synthetic Fixture | `SYNTHETIC_ECD_LOGIC_VALIDATION_ONLY` | **NO** |

---

## 3. Firewall Confirmation

```yaml
PROTOTYPE_FIREWALL_STATUS: PASS
VERIFICATION: All 11 prototype values are strictly verified as synthetic assumptions. Zero prototype values have been promoted to station engineering facts.
```
