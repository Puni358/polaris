# POLARIS EMS — HD-05 BATTERY DEGRADATION GOVERNANCE GAP REGISTER

**Audit Date**: 2026-09-22  
**Scope**: Open Decisions & Unresolved Governance Items for HD-05 Policy Realization  

---

## 1. Unresolved Governance Decision Items

The following decision items remain unresolved and require human governance authorization before Stage 3 implementation:

| Decision ID | Sub-Decision Title | Status | Evidence & Technical Findings | Unresolved Governance Item | Implementation Impact |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HD-05D** | Numerical Fuel↔Degradation Tradeoff | **OPEN** | $c_{\text{deg}} = \$0.00005/\text{Wh}$ is an engineering constant; fuel is $\$2.50/\text{L}$ | Authorize numerical exchange coefficient $\lambda_{\text{fuel\_deg}}$ or fuel cost $/L | Determines numerical weight between fuel and battery cycling in Stage 3 |
| **HD-05E** | Degradation Formulation Model Choice | **OPEN** | Current model is linear throughput proxy ($c_{\text{deg}} \cdot (p_{\text{chg}}+p_{\text{dis}})$) | Select Option A (Throughput Proxy) vs Option B (Non-linear DoD) vs Option C (Economic) vs Option D (Budget) | Determines mathematical formulation in Stage 3 solver |
| **HD-05F** | Emergency Mode Dynamic Override | **OPEN** | Policy HD-05C requires degradation subordination in emergency | Authorize dynamic suppression rule ($c_{\text{deg}} = 0.0$ when `operating_mode != NORMAL`) | Ensures critical reliability is uninhibited by battery lifetime cost |
| **HD-05G** | Empirical Aging Calibration Data | **OPEN** | Physical aging calibration is `LEVEL 3 — NOT ESTABLISHED` | Determine if empirical battery chemistry & cycle-life testing is required | Governs whether physical aging physics is added |
| **HD-05H** | Schema Extension for Battery Telemetry | **OPEN** | `StationState` schema lacks SOH and temperature fields | Decide if SOH / battery health tracking should be added to schema | Additive schema extension to `StationState` and `DispatchPlan` |

---

## 2. Hard Stop Conditions Verification

- `c_deg` location: Verified at [`battery.yaml:L11`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11) and [`milp.py:L33`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L33).
- Mathematical formulation: Verified as $c_{\text{deg}} \cdot (p_{\text{chg}} + p_{\text{dis}}) \Delta t$.
- Physical aging calibration: Confirmed `BATTERY_AGING_CALIBRATION = NOT_ESTABLISHED`.
- Discrepancy handling: No silent reconciliation performed.
