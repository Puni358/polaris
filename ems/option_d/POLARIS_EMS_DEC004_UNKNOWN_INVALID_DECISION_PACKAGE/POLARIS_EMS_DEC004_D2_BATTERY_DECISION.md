# POLARIS EMS — DEC-004-D2: BATTERY BEHAVIOR DURING OPTION D

> [!IMPORTANT]
> **GOVERNANCE DECISION PREPARATION**
> This document prepares decision **DEC-004-D2** for human governance review. It analyzes battery charging, discharging, safety boundaries, and engineering requirements. It does **NOT** select or approve a policy.

---

## 1. Exact Governance Question

**DEC-004-D2**: *What operational rules govern battery charging and battery discharging when the system is operating under Option D (`UNKNOWN_INVALID`)?*

---

## 2. Authoritative Evidence & Technical Boundaries

### 2.1 Established Evidence
- **Candidate Option D Concept**: Renewable generation is ordered first; diesel generation covers remaining critical demand.
- **Human Proposed Direction for D6**: Excess diesel generation above critical demand should be used to charge the battery where technically feasible.

### 2.2 Unestablished Items (Requires Definition)
- **Battery Discharge Authorization**: Unresolved whether battery discharge ($P_{\text{BD}} > 0$) is authorized to serve critical load when renewables/diesel are unavailable or insufficient.
- **Battery Charging from Excess Renewables**: Unresolved whether excess renewable power beyond $P_{\text{critical}}$ may charge the battery during `UNKNOWN_INVALID`.
- **Reserve Preservation**: Unresolved whether a minimum SOC threshold (e.g. $20\%$ or $30\%$) locks out battery discharge.
- **Telemetry Validity**: Unresolved whether battery charging/discharging is permitted if battery telemetry (SOC, voltage, temperature) is unverified or stale.

---

## 3. Five Sub-Dimensions of Battery Policy

1. **A. Diesel Excess Charging ($P_{\text{BC,diesel}}$)**: Charging battery using excess output when diesel minimum power exceeds remaining critical load (addressed in D6).
2. **B. Renewable Excess Charging ($P_{\text{BC,renew}}$)**: Charging battery using surplus renewable power when $P_{\text{RE}} > P_{\text{critical}}$.
3. **C. Critical Load Discharge Support ($P_{\text{BD}}$)**: Discharging battery to cover critical load shortfall when $P_{\text{RE}} + P_{\text{D}} < P_{\text{critical}}$.
4. **D. Reserve Floor Protection ($SOC_{\text{min}}$)**: Setting a hard stop on discharge to preserve emergency reserve.
5. **E. Degradation & Thermal Constraints**: Enforcing maximum charge/discharge C-rates and temperature limits.

---

## 4. Policy Options for Human Review

- **Option D2-A (Charge-Only Mode)**: Permit battery charging from excess generation (renewables + diesel), but strictly **PROHIBIT** battery discharge ($P_{\text{BD}} = 0$).
- **Option D2-B (Protected Discharge Support)**: Permit battery discharge to serve critical load, provided $SOC > SOC_{\text{reserve}}$ (e.g. $20\%$).
- **Option D2-C (Complete Battery Lockout)**: Disconnect battery entirely ($P_{\text{BD}} = 0, P_{\text{BC}} = 0$) while telemetry is `UNKNOWN_INVALID`.

---

## 5. Synthetic Illustrative Numerical Examples

> [!CAUTION]
> **SYNTHETIC ILLUSTRATIVE EXAMPLE ONLY**
> The values below are **NOT STATION DATA**, **NOT DEPLOYMENT PARAMETERS**, and **NOT GOVERNANCE VALUES**.

### Example 1: Excess Generation Charging ($P_{\text{RE}} = 3\text{ kW}, P_{\text{D,min}} = 10\text{ kW}, P_{\text{critical}} = 7\text{ kW}$)
- Total Generation: $3 + 10 = 13\text{ kW}$
- Critical Demand: $7\text{ kW}$
- Excess Power Available: $13 - 7 = 6\text{ kW}$
- **Outcome**: $6\text{ kW}$ directed to battery charging ($P_{\text{BC}} = 6\text{ kW}$), subject to battery acceptance limits.

### Example 2: Zero Renewables Diesel Excess ($P_{\text{RE}} = 0\text{ kW}, P_{\text{D,min}} = 10\text{ kW}, P_{\text{critical}} = 7\text{ kW}$)
- Total Generation: $10\text{ kW}$
- Critical Demand: $7\text{ kW}$
- Excess Power Available: $10 - 7 = 3\text{ kW}$
- **Outcome**: $3\text{ kW}$ directed to battery charging ($P_{\text{BC}} = 3\text{ kW}$).

---

## 6. Required Battery Engineering Definitions

1. Maximum allowable charge power ($P_{\text{BC,max}}$) during degraded operation.
2. Minimum SOC reserve limit ($SOC_{\text{min}}$).
3. Telemetry validity rules: Can battery operate if SOC signal is missing or invalid?
4. Thermal safety cutoffs for unattended charging.

---

## 7. Human Decision Form (DEC-004-D2)

```text
DECISION ID: DEC-004-D2
QUESTION: What battery behavior is authorized during Option D?

SELECTED POLICY OPTION: [ D2-A (Charge Only) / D2-B (Discharge Support) / D2-C (Lockout) / OTHER ]

HUMAN DECISION STATUS: UNRESOLVED (Awaiting Human Selection)
AUTHORIZED BY: ___________________________
DATE: _______________
```

Status: `D2_DECISION_PREPARATION_COMPLETE`
