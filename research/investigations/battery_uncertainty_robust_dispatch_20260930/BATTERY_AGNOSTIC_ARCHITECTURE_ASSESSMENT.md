# POLARIS — Battery-Agnostic Architecture Assessment

> **RESEARCH SCENARIO / SYNTHETIC UNCERTAINTY ENVELOPE / NOT TARGET-HARDWARE EVIDENCE**

## 1. Architectural Question Statement

> **Can POLARIS accept a battery resource as a parameterized capability rather than requiring a known manufacturer/model?**

---

## 2. Assessment Findings

### Finding 1: Architecture Sufficiency
**YES.** POLARIS's MILP energy management framework (`milp.py`) successfully models battery energy storage as a decoupled, parameterized capability defined by 6 scalar parameters:
$$\{E_{\text{cap}}, P_{\text{max}}, \eta_{\text{rt}}, \text{SOC}_{\text{min}}, \text{SOC}_{\text{max}}, c_{\text{deg}}\}$$
The optimizer does NOT require vendor-specific code, proprietary BMS drivers, or specific battery chemistry equations to achieve 100% solver convergence, energy conservation, and 0.00 kWh unmet load.

---

## 3. Minimum Required Runtime Information

To safely operate with an arbitrary battery system, POLARIS requires the following runtime telemetry and configuration vector:

| Data Element | Type | Requirement | Default if Missing / Invalid |
|---|---|---|---|
| **Usable Capacity ($E_{\text{cap}}$)** | Config Scalar (kWh) | MANDATORY | Must be bounded ≥ 45.0 kWh for 6h survivability |
| **Max Charge/Discharge Power ($P_{\text{max}}$)** | Config Scalar (kW) | MANDATORY | Must be bounded ≥ 15.0 kW |
| **Round-Trip Efficiency ($\eta_{\text{rt}}$)** | Config Scalar (%) | MANDATORY | Default to 84.64% synthetic assumption |
| **SOC Bounds ($\text{SOC}_{\text{min}}, \text{SOC}_{\text{max}}$)** | Config Vector (%) | MANDATORY | Default to [20%, 80%] safety window |
| **Telemetry Freshness Timestamp** | Runtime Stream | MANDATORY | If stale -> Freshness Eligibility = FALSE |
| **Telemetry Validity Flag** | Runtime Stream | MANDATORY | If invalid -> Safety Credit = 0 kW |
| **Degradation Cost Proxy ($c_{\text{deg}}$)** | Config Scalar ($/Wh) | MANDATORY | Default to $0.00005/Wh ($0.05/kWh) |

---

## 4. Parameter State Handling Matrix

POLARIS MILP solver behavior across parameter states:

```
┌─────────────────┬────────────────────────────────────────────────────────────────────────┐
│ Parameter State │ Optimizer Treatment                                                    │
├─────────────────┼────────────────────────────────────────────────────────────────────────┤
│ KNOWN           │ Uses exact parameter value in MILP constraints/objective               │
│ BOUNDED         │ Uses conservative lower/upper bound across uncertainty envelope        │
│ UNKNOWN         │ Uses hardcoded synthetic baseline ($0.05/kWh, 84.64% RTE)               │
│ INVALID         │ Sets battery power capability to 0 kW; switches to non-battery fallback│
└─────────────────┴────────────────────────────────────────────────────────────────────────┘
```
