# POLARIS EMS — DEC-004 OPTION D (D1–D6) HUMAN GOVERNANCE DECISION FORM

> [!IMPORTANT]
> **HUMAN GOVERNANCE DECISION FORM**
> This form is open for human governance decisions on Option D sub-questions **D1 through D6**. The AI assistant has prepared technical options, evidence boundaries, and synthetic calculations. The human decision-maker must select and sign each policy choice below.

---

## Governance Decision Summary Register

```text
PACKAGE_ID: POLARIS_EMS_DEC004_UNKNOWN_INVALID_DECISION_PACKAGE
DECISION_ID: DEC-004
OPTION_UNDER_REVIEW: Option D (Protected Critical-Load Fallback)
FINAL_OPTION_D_POLICY_STATUS: NOT_SEALED (Open for Human Input)
```

---

## 1. Decision DEC-004-D1: Exact Protected Critical-Load Definition

**Question**: What scope and categorization constitute the authorized protected critical load ($P_{\text{critical}}$)?
- **Option D1-A**: Static Circuit Inventory in station config (`station_config.yaml`).
- **Option D1-B**: Fixed Static Power Allocation Cap (e.g. $7\text{ kW}$).
- **Option D1-C**: Dynamic Schedule / Thermal Profile ($P_{\text{critical}}(t, T_{\text{amb}})$).

```text
HUMAN DECISION D1: [ D1-A / D1-B / D1-C / OTHER ]
STATUS D1: UNRESOLVED (Awaiting Selection)
```

---

## 2. Decision DEC-004-D2: Battery Behavior during Option D

**Question**: What operational rules govern battery charging and discharging under Option D?
- **Option D2-A**: Charge-Only Mode (Absorb excess generation; prohibit discharge).
- **Option D2-B**: Protected Discharge Support (Allow discharge to cover critical load if $SOC > SOC_{\text{min}}$).
- **Option D2-C**: Complete Battery Lockout ($P_{\text{BD}} = 0, P_{\text{BC}} = 0$).

```text
HUMAN DECISION D2: [ D2-A / D2-B / D2-C / OTHER ]
STATUS D2: UNRESOLVED (Awaiting Selection)
```

---

## 3. Decision DEC-004-D3: Zero Renewables + Diesel Unavailable Fallback

**Question**: What action occurs when renewables are $0\text{ kW}$ and diesel generation is unavailable?
- **Option D3-A**: Zero Automated Supply ($P_{\text{supply}} = 0$) & Await Operator.
- **Option D3-B**: Battery Emergency Discharge (Discharge battery as sole provider until depleted).
- **Option D3-C**: Immediate Terminal Lockout (`CRITICAL_TERMINATION`).

```text
HUMAN DECISION D3: [ D3-A / D3-B / D3-C / OTHER ]
STATUS D3: UNRESOLVED (Awaiting Selection)
```

---

## 4. Decision DEC-004-D4: Critical Load Shortfall Shedding Policy

**Question**: What shedding policy applies when available generation is less than critical load ($P_{\text{supply}} < P_{\text{critical}}$)?
- **Option D4-A**: Ranked Priority Shedding (Shed lowest priority category first).
- **Option D4-B**: Proportional Shedding (Reduce power proportionally across critical circuits).
- **Option D4-C**: Total Critical Trip (Trip all critical load to prevent brownout).

```text
HUMAN DECISION D4: [ D4-A / D4-B / D4-C / OTHER ]
STATUS D4: UNRESOLVED (Awaiting Selection)
```

---

## 5. Decision DEC-004-D5: Maximum Option D Duration / Escalation Watchdog

**Question**: What duration limit or resource margin constraint governs Option D before mandatory escalation?
- **Option D5-A**: Indefinite Await (Remain in Option D until valid input arrives).
- **Option D5-B**: Fixed Watchdog Timer (Escalate after fixed time, e.g. 2 hours).
- **Option D5-C**: Resource-Depletion Limit (Escalate when fuel or battery hits minimum reserve).
- **Option D5-D**: Hybrid Watchdog & Resource Policy (Escalate on timer or resource breach).

```text
HUMAN DECISION D5: [ D5-A / D5-B / D5-C / D5-D / OTHER ]
STATUS D5: UNRESOLVED (Awaiting Selection)
```

---

## 6. Decision DEC-004-D6: Diesel Minimum Output Excess Power Disposition

**Question**: How shall excess generation be disposed when diesel minimum output exceeds remaining critical demand?

```text
HUMAN PROPOSED DIRECTION FOR D6:
  "1. Apply renewable generation to protected critical demand first.
   2. Start/use diesel for remaining critical demand.
   3. If diesel minimum output exceeds remaining critical demand:
      - Use excess generation to charge battery where technically feasible.
      - Curtail remaining excess power only after allowable battery charging is exhausted."

HUMAN DECISION D6: [ SEAL PROPOSED DIRECTION / MODIFY DIRECTION / REJECT ]
STATUS D6: HUMAN_PROPOSED_DIRECTION (Awaiting Formal Seal)
```

---

## Stakeholder Governance Signature Block

*(To be signed by human governance decision-maker upon completion)*

```text
Authorized By (Print Name): ___________________________
Role / Title: ___________________________
Signature: ___________________________
Date: _______________
```

Status: `D1_D6_DECISION_FORM_OPEN`
