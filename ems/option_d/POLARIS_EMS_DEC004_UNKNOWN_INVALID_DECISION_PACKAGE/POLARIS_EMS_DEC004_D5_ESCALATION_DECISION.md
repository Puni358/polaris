# POLARIS EMS — DEC-004-D5: OPTION D MAXIMUM DURATION & ESCALATION WATCHDOG

> [!IMPORTANT]
> **GOVERNANCE DECISION PREPARATION**
> This document prepares decision **DEC-004-D5** for human governance review. It analyzes watchdog timers, resource thresholds, and escalation pathways. It does **NOT** select or approve a policy.

---

## 1. Exact Governance Question

**DEC-004-D5**: *What maximum duration limit, step threshold, or resource margin constraint shall govern Option D execution before mandatory escalation to terminal lockout (`CRITICAL_TERMINATION`)?*

---

## 2. Authoritative Evidence & Technical Boundaries

### 2.1 Established Evidence
- **Degraded Operation**: Option D is a temporary degraded concept intended to protect critical load while awaiting valid external/operator input.
- **No Inherent Timeout**: The repository currently defines no automated timeout mechanism for degraded policy execution.

### 2.2 Unestablished Items (Requires Definition)
- **Watchdog Boundary**: Unresolved whether a fixed time limit (e.g. $N$ hours or $M$ timesteps) should force escalation.
- **Resource Boundary**: Unresolved whether fuel depletion or battery SOC limits trigger escalation.

---

## 3. Policy Candidate Options for Human Review

- **Option D5-A (Indefinite Await)**: Maintain Option D indefinitely until valid telemetry or operator manual input is received.
- **Option D5-B (Fixed Watchdog Timer)**: Enforce a strict time limit (e.g. 2 hours / 4 timesteps). If `UNKNOWN_INVALID` persists beyond the limit, escalate to `CRITICAL_TERMINATION`.
- **Option D5-C (Resource-Depletion Escalation)**: Maintain Option D until diesel fuel drops below emergency threshold (e.g. $10\text{ L}$) or battery drops below $SOC_{\text{min}}$, then escalate.
- **Option D5-D (Hybrid Watchdog & Resource Policy)**: Escalate upon whichever event occurs first: time limit expiry OR critical resource margin breach.

---

## 4. Synthetic Illustrative Numerical Example

> [!CAUTION]
> **SYNTHETIC ILLUSTRATIVE EXAMPLE ONLY**
> The values below are **NOT STATION DATA**, **NOT DEPLOYMENT PARAMETERS**, and **NOT GOVERNANCE VALUES**.

### Scenario Timeline under Hypothetical 2-Hour Watchdog:
- **12:00**: ECD returns `UNKNOWN_INVALID`. Option D activates. Noncritical load shed ($23\text{ kW}$); critical load served ($7\text{ kW}$).
- **13:00** ($t+1\text{h}$): Telemetry remains `UNKNOWN_INVALID`. Option D continues execution.
- **14:00** ($t+2\text{h}$): Watchdog timer expires ($2.0\text{h}$). System escalates to `CRITICAL_TERMINATION` (Option C), halting automated MPC and raising critical SCADA alarm.

```text
12:00 ──► UNKNOWN_INVALID detected ──► Option D Starts (7 kW Critical Served)
13:00 ──► 1 Hour Elapsed ───────────► Option D Continues
14:00 ──► 2 Hours Elapsed (Limit) ──► ESCALATION: CRITICAL_TERMINATION
```

---

## 5. Cross-Decision Interactions & Dependencies

- **Interaction with D2 (Battery)**: Battery SOC reserve floor interacts with D5 resource-depletion escalation.
- **Interaction with D3/D4**: Zero-supply or critical shortfall conditions may trigger accelerated D5 escalation.

---

## 6. Required Engineering Definitions

1. Maximum allowable time limit ($T_{\text{max,degraded}}$) for unattended degraded operation.
2. Minimum fuel reserve threshold ($F_{\text{reserve,min}}$) triggering terminal escalation.

---

## 7. Human Decision Form (DEC-004-D5)

```text
DECISION ID: DEC-004-D5
QUESTION: What duration/resource limit governs Option D before mandatory escalation?

SELECTED POLICY OPTION: [ D5-A (Indefinite) / D5-B (Fixed Watchdog) / D5-C (Resource Depletion) / D5-D (Hybrid) / OTHER ]

HUMAN DECISION STATUS: UNRESOLVED (Awaiting Human Selection)
AUTHORIZED BY: ___________________________
DATE: _______________
```

Status: `D5_DECISION_PREPARATION_COMPLETE`
