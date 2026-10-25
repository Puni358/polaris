# POLARIS EMS — PROTOTYPE VS PRODUCTION BOUNDARY

## 1. Overview

This document establishes a strict, non-negotiable architectural firewall between the **Synthetic Prototype Fixture Domain** and the **Real Station Production Domain**. Under no circumstances may prototype test values or analytical simplifications be promoted to production runtime code.

---

## 2. Boundary Comparison Matrix

| Property | Prototype Fixture Domain | Production Station Domain |
|----------|──────────────────────────|───────────────────────────|
| **Primary Horizon** | $T_{\text{test}} = 2.0\text{ h}$ (Logic Validation) | $T_{\text{required}}$ (Dynamic Operational Input, e.g., $72.0\text{ h}$) |
| **Critical Load** | $P_{\text{crit}} = 30,000\text{ W}$ (Constant Synthetic) | Time-Varying Trajectory $P_{\text{crit}}(t)$ |
| **Battery State** | Synthetic SOC Bands ($80\%, 30\%$) | Real Telemetry `StationState.battery_soc` |
| **Fuel State** | Synthetic Fuel Bands ($50\text{ L}, 12.5\text{ L}, 46.0\text{ L}$) | Real Telemetry `StationState.fuel_remaining_liters` |
| **Renewable Stress** | Zero Solar / Wind | Forecasted Solar & Wind Trajectories |
| **Authority & Freshness** | Static JSON Fixture | Signed Command Payload with TTL & Max-Age Guards |
| **Code Location** | `tests/fixtures/` | `polaris/ems/ecd/` |

---

## 3. Mandatory Firewall Rules

1. **NO Hardcoded Test Horizons**: The runtime ECD code MUST NOT hardcode $2.0\text{ h}$ or $72.0\text{ h}$ as internal logic constants. $T_{\text{target}}$ must be accepted dynamically as a parameter.
2. **NO Hardcoded Test Loads**: The runtime ECD code MUST NOT default to $30,000\text{ W}$.
3. **Fixture Isolation**: Prototype fixture JSON files must reside exclusively in test directories and must never be loaded by production EMS modules.

Status: `VERIFIED`
