# POLARIS EMS — DEC-004-D3: ZERO RENEWABLE + DIESEL UNAVAILABLE FALLBACK

> [!IMPORTANT]
> **GOVERNANCE DECISION PREPARATION**
> This document prepares decision **DEC-004-D3** for human governance review. It analyzes operational response when generation resources fail while ECD outputs `UNKNOWN_INVALID`. It does **NOT** select or approve a policy.

---

## 1. Exact Governance Question

**DEC-004-D3**: *What operational action shall the system take when operating under Option D (`UNKNOWN_INVALID`), renewable generation is zero ($P_{\text{RE}} = 0$), diesel generation is physically unavailable or faulted, and protected critical load demand exists ($P_{\text{critical}} > 0$)?*

---

## 2. Authoritative Evidence & Technical Boundaries

### 2.1 Established Evidence
- **Resource Shortfall**: When $P_{\text{RE}} = 0$ and diesel is unavailable, automated active generation capacity is zero ($0\text{ kW}$).
- **State Distinction**: This scenario is **NOT** equivalent to `ECD = EMERGENCY`. `EMERGENCY` requires valid inputs and a calculated endurance failure. `UNKNOWN_INVALID + RESOURCE_FAILURE` means inputs are invalid AND active generation is zero.

### 2.2 Unestablished Items (Requires Definition)
- **Automatic Generator Retry**: Unresolved whether the system may attempt automated restart of a faulted/unavailable generator.
- **Battery Fallback**: Unresolved whether battery energy may be dispatched as sole provider under D3 if battery discharge is authorized under D2.

---

## 3. Policy Candidate Options for Human Review

- **Option D3-A (Zero Automated Supply & Await Operator)**: Enforce $P_{\text{supply}} = 0\text{ kW}$, allow critical load to be shed or handled by local hardware protection relays, and await human operator intervention.
- **Option D3-B (Battery Emergency Discharge)**: If authorized under D2 and battery SOC is valid ($SOC > SOC_{\text{min}}$), discharge battery to supply critical load until depleted or operator arrives.
- **Option D3-C (Immediate Terminal Lockout)**: Immediately escalate state from Option D to `CRITICAL_TERMINATION` (Option C), halting the MPC pipeline and raising a high-priority SCADA alarm.

---

## 4. Synthetic Illustrative Numerical Example

> [!CAUTION]
> **SYNTHETIC ILLUSTRATIVE EXAMPLE ONLY**
> The values below are **NOT STATION DATA**, **NOT DEPLOYMENT PARAMETERS**, and **NOT GOVERNANCE VALUES**.

### Scenario Setup:
- **Protected Critical Load**: $7\text{ kW}$
- **Solar Generation**: $0\text{ kW}$ (Nighttime)
- **Wind Generation**: $0\text{ kW}$ (Calm winds)
- **Diesel Generator**: Unavailable / Faulted ($0\text{ kW}$)
- **Available Generation Supply**: $0 + 0 + 0 = 0\text{ kW}$
- **Unmet Critical Load**: $\max(0, 7 - 0) = 7\text{ kW}$

```text
Generation: 0 kW (Solar 0 + Wind 0 + Diesel 0)
Critical Demand: 7 kW
 └── Unmet Critical Demand = 7 kW ──► BLACKOUT / UNPOWERED
```

---

## 5. Cross-Decision Interactions & Dependencies

- **Interaction with D2 (Battery)**: Option D3-B directly requires D2 to authorize battery discharge under degraded conditions.
- **Interaction with D5 (Escalation)**: Immediate zero-supply condition under D3 may trigger early D5 escalation.

---

## 6. Required Engineering Definitions

1. Telemetry criteria determining "Diesel Unavailable" (e.g. breaker open, low fuel pressure, fault code).
2. Local station UPS / DC control power endurance during zero-generation blackout.

---

## 7. Human Decision Form (DEC-004-D3)

```text
DECISION ID: DEC-004-D3
QUESTION: What action occurs when renewables are 0 and diesel is unavailable under Option D?

SELECTED POLICY OPTION: [ D3-A (Zero Supply) / D3-B (Battery Discharge) / D3-C (Terminal Lockout) / OTHER ]

HUMAN DECISION STATUS: UNRESOLVED (Awaiting Human Selection)
AUTHORIZED BY: ___________________________
DATE: _______________
```

Status: `D3_DECISION_PREPARATION_COMPLETE`
