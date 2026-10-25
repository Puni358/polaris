# POLARIS EMS GATE-11 — OPTION D (D1-D6) SPECIFICATION

## 1. Executive Summary & Audited Implementation Identity
This document specifies the operational rules, heuristic logic, resource allocation priority, and charge/discharge exclusivity for Option D protected critical fallback solver (`OptionDFallbackSolver`).

- **Implementation File**: `system/optimization/implementations/option_d.py`
- **Audited Option D SHA256**: `78630c19a3c4be8d634f05a47a2c7eacf0f4083c988b97f64bb7ca98f3d60f12`
- **Operational Mode Trigger**: `EMERGENCY` evaluated by `EmergencyConditionDetector`.

## 2. Sealed D1-D6 Governance Semantics

### D1 — Protected Critical Load Priority
- Protected critical load $P_{\text{crit}}(t)$ is served at the highest priority. Non-critical load demand is shed during emergency mode.

### D2 — Battery Protection & Limits
- Usable battery capacity supports protected critical load only down to minimum SOC bound ($20.0\%$).
- Battery discharge power is bounded by physical limit $P_{\text{dis\_max}} = 50,000 \text{ W}$.

### D3 — Resource Depletion Fallback
- When solar and wind generation are zero or depleted, battery energy is deployed. If battery energy is insufficient, diesel generation is engaged.

### D4 — Proportional Critical Allocation
- When total available power $P_{\text{total}}(t) < P_{\text{crit}}(t)$, allocation factor $\alpha(t) = \frac{P_{\text{total}}(t)}{P_{\text{crit}}(t)}$ is applied to allocate available power proportionally across critical loads.
- If $P_{\text{crit}}(t) = 0$, $\alpha(t) = 1.0$ (safe zero-denominator protection).

### D5 — Time/Resource Boundary
- Resource endurance $t_{\text{battery}}$ and $t_{\text{diesel}}$ evaluated by ECD define emergency boundary without invented numerical thresholds.

### D6 — Diesel Excess Handling & Exclusivity
- Excess diesel generation beyond immediate critical load charges the battery up to max charge power ($50,000 \text{ W}$) only while diesel is running for load.
- Diesel generator is NEVER started solely to charge the battery.
- Charge/discharge exclusivity is enforced (`if p_diesel > 0: p_dis = 0`).
