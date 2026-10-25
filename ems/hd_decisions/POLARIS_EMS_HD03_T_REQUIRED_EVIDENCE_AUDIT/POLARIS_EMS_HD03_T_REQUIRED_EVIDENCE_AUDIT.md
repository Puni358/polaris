# POLARIS EMS — HD-03 T_required Operational Survival Window Evidence Audit Report

**Audit Status**: COMPLETED (READ-ONLY)  
**Governance Scope**: Human Decision HD-03 ($T_{\text{required}}$ Operational Survival Window)  
**Target Directory**: [`POLARIS_EMS_HD03_T_REQUIRED_EVIDENCE_AUDIT/`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_EMS_HD03_T_REQUIRED_EVIDENCE_AUDIT/)  

---

## Executive Summary

This read-only evidence audit determines whether the POLARIS repository contains an authoritative, station-specific definition or numerical value for:

$$T_{\text{required}} = \text{the operational survival window from the current decision point until the next authorized recovery/resupply opportunity}$$

### Key Audit Findings

1. **Existence of Authoritative Numerical $T_{\text{required}}$**: **`ABSENT` / `NOT_ESTABLISHED`**. No numerical value, resupply schedule, fuel delivery cadence, or recovery window exists in any repository code, configuration, schema, or governance document.
2. **Derivability from Existing Data**: **`NOT_POSSIBLE`**. $T_{\text{required}}$ cannot be mathematically derived from existing generator parameters, battery capacity ($200\text{ kWh}$), or load settings without introducing unauthorized engineering assumptions.
3. **Disambiguation of Candidate Numerical Values**:
   - **$24\text{h}$**: MPC decision and forecast horizon $H$ in [`milp.py:L72`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L72). **$T_{\text{required}} \neq 24\text{h}$**.
   - **$6\text{h}$**: HD-01B EBR normal-operation resilience interval $N=6\text{h}$. **$T_{\text{required}} \neq 6\text{h}$**.
   - **$30\text{ days}$**: Provisional resupply-cycle allocation example in Decision 08 docs. **$T_{\text{required}} \neq 30\text{ days}$**.
   - **$2\text{h}$**: Generator minimum run time (`min_up_time_hours: 2` in [`diesel.yaml:L9`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L9)). **$T_{\text{required}} \neq 2\text{h}$**.
   - **$15\text{ minutes}$**: Sub-hourly UPS hold-up autonomy in implementation specs (`INP_03`). **$T_{\text{required}} \neq 15\text{ min}$**.
4. **Impact on HD-04 Emergency Detector**: **`HD-04_IMPLEMENTATION_BLOCKED_BY_HD03 = YES`**. While HD-04 Option A (Zero-Renewable Baseline) is structurally closed, implementing the pre-solve Emergency Mode Detector remains blocked until human governance or station operations provides $T_{\text{required}}$.
5. **Final Verdict**: **`CONCLUSION C` — NO: Required operational data is absent and human policy / station-operations input is required.**

---

## 1. Closed Governance Baseline (Preserved)

The following decisions are **FIXED** and strictly preserved:

- **HD-01A**: EBR is a critical-load-based dynamic energy target.
- **HD-01B**: EBR resilience interval **$N = 6\text{ HOURS}$** (fixed, separately governed normal-operation resilience interval).
- **HD-02**: Terminal target derived from EBR at MPC boundary ($E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$); terminal shortfall counted exactly once.
- **HD-04**: Emergency Mode Detector evaluates zero-renewable survivability ($P_{\text{solar}} = 0, P_{\text{wind}} = 0$) through $T_{\text{required}}$ as a detector-local stress scenario. Normal MPC uses causal forecasts.
- **HD-05**: Normal mode: $F_{\text{diesel}} \le 1.05 F^*$; Emergency mode: battery degradation subordinate to critical load.
- **Policy E3**: Emergency mode resource preservation policy (preserve resource with larger survivability margin).

---

## 2. Audit Question Responses

| Audit Question | Repository Evidence Finding | Classification |
| :--- | :--- | :--- |
| **1. Authoritative $T_{\text{required}}$ Value?** | No numerical $T_{\text{required}}$ defined | `ABSENT` |
| **2. Authoritative Refueling Schedule?** | No fuel delivery dates or intervals | `ABSENT` |
| **3. Authoritative Station Logistics Schedule?** | Decision 08 structure approved; schedule `STATION_DATA_REQUIRED` | `ABSENT` |
| **4. Authoritative Recovery Opportunity?** | No recovery time or event specified | `ABSENT` |
| **5. Station Assistance Time Specification?** | No external rescue or assistance lead time defined | `ABSENT` |
| **6. Mission Plan Recovery Window?** | No mission timeline or endpoint defined | `ABSENT` |
| **7. Station Autonomous Operation Spec?** | UPS hold-up ($15\text{ min}$) only; no hourly autonomy spec | `ABSENT` |
| **8. Authoritative Fuel Delivery Cadence?** | No delivery cadence or protected reserve period defined | `ABSENT` |
| **9. Mission-End / Guaranteed Recovery Time?** | No mission-end timestamp in repository | `ABSENT` |
| **10. Misleading Numerical Values?** | Found $24\text{h}$ (MPC), $6\text{h}$ (EBR), $30\text{d}$ (Budget), $2\text{h}$ (Gen), $15\text{m}$ (UPS) | `DISAMBIGUATED` |

---

## 3. Required Audit Classifications

```plain
HD03_AUTHORITATIVE_VALUE = ABSENT
HD03_AUTHORITATIVE_SOURCE = ABSENT
HD03_RESUPPLY_SCHEDULE = ABSENT
HD03_RECOVERY_WINDOW = ABSENT
HD03_STATION_AUTONOMY_REQUIREMENT = ABSENT
HD03_MISSION_CONSTRAINT = ABSENT
HD03_NUMERICAL_DERIVATION = NOT_POSSIBLE
HD03_NUMERICAL_VALUE = NOT_ESTABLISHED
HD03_POLICY_STATUS = GOVERNANCE_DECISION_REQUIRED
HD03_IMPLEMENTATION_AUTHORIZATION = NOT_GRANTED
HD03_EXECUTION_AUTHORIZATION = NOT_GRANTED

HD-04_IMPLEMENTATION_BLOCKED_BY_HD03 = YES
```

---

## 4. Cross-Policy Compatibility Audit

1. **HD-04 Compatibility**: The HD-04 policy statement ("Emergency Mode Detector evaluates zero-renewable survivability through $T_{\text{required}}$") is structurally valid and mathematically complete. However, code execution is blocked (`HD-04_IMPLEMENTATION_BLOCKED_BY_HD03 = YES`) until $T_{\text{required}}$ is specified.
2. **HD-01B ($N=6\text{h}$) Independence**: **$N = 6\text{h} \neq T_{\text{required}}$**. $N=6\text{h}$ is a normal-mode rolling resilience target inside the MPC loop. $T_{\text{required}}$ is the full-horizon operational survival window outside the MPC loop.
3. **HD-02 Compatibility**: Terminal target $E_{\text{terminal\_target}} = E_{\text{EBR\_target}}(H)$ is evaluated at timestep $H$ over steps $H+1 \dots H+6$. It is completely independent of $T_{\text{required}}$.

---

## 5. Final Verdict & Hard Stop Block

**Can POLARIS currently determine an authoritative numerical $T_{\text{required}}$ from repository evidence alone?**

> **CONCLUSION C**: **NO — Required operational data is absent and human policy / station-operations input is required.**

Exact missing operational input: **Authoritative station resupply schedule, fuel logistics delivery contract, or station-specific operational recovery window.**

```plain
HD03_NUMERICAL_VALUE=NOT_ESTABLISHED
HD03_IMPLEMENTATION_AUTHORIZATION=NOT_GRANTED
HD03_EXECUTION_AUTHORIZATION=NOT_GRANTED
```
