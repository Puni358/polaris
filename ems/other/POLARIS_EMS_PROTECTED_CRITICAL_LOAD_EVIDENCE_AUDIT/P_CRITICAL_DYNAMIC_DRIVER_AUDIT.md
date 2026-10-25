# POLARIS EMS — P_CRITICAL(t) DYNAMIC DRIVER AUDIT

## 1. Executive Summary

This document audits potential physical and environmental drivers that cause variation in **Protected Critical Load ($P_{\text{critical}}(t)$)** over time.

---

## 2. Dynamic Driver Audit Register

| Dynamic Driver Candidate | Physical Mechanism | Current Repository Evidence Status | Classification |
| :--- | :--- | :--- | :--- |
| **Ambient Temperature** | Outdoor temperature drives heating energy required to sustain indoor survivability threshold. | Zero thermal building model exists in codebase. `loads.yaml` uses static $30\text{kW}$ baseline. | `ENGINEERING_REQUIRED` / `NOT_ESTABLISHED` |
| **Water Filtration Cycle** | Intermittent pumping and backwashing cycles for water treatment. | `loads.yaml` contains synthetic 4-hour window (08:00–18:00). No physical flow model. | `PROTOTYPE_ONLY` / `NOT_ESTABLISHED` |
| **Comms Duty Cycle** | Peak power during high-power telemetry transmissions vs low-power idle standby. | No comms power profile exists in repository. | `NOT_ESTABLISHED` |
| **Equipment Startup / Inrush** | Motor start-up current spikes for pumps and compressors. | No sub-hourly inrush model exists in schema or code. | `NOT_ESTABLISHED` |
| **Redundancy Switching** | Failover from primary to backup critical equipment. | No redundancy switching logic exists in code. | `NOT_ESTABLISHED` |

---

## 3. Findings & Model Readiness

Current repository models treat critical demand as a static constant ($30,000\text{ W}$ in `loads.yaml`). No dynamic thermal or operational driver models exist in Python runtime.

```yaml
P_CRITICAL_DYNAMIC_MODEL_STATUS: NOT_ESTABLISHED
REASON: Requires building thermal modeling, pump duty cycle data, and site environmental telemetry.
```
