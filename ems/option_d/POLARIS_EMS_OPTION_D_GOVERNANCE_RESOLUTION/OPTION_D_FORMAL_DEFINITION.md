# POLARIS EMS — OPTION D FORMAL GOVERNANCE POLICY DEFINITION

## 1. Trigger Condition
Option D is triggered exclusively when the Emergency Condition Detector (ECD) evaluates system telemetry/forecast inputs and outputs the operational state `UNKNOWN_INVALID`. `UNKNOWN_INVALID` signifies that microgrid survivability endurance cannot be established due to missing, corrupted, expired, or unauthenticated inputs.

---

## 2. Protected Critical-Load Scope
Option D restricts automated energy management to powering ONLY authorized protected critical systems. The conceptual life-safety categories under governance discussion are:
1. **Essential Heating**: Thermal environmental control required for human survivability.
2. **Essential Water Treatment & Filtration**: Potable water purification and life-support processing.
3. **Emergency Communications**: Radio, satellite, and telemetry infrastructure.

*Normative Boundary*: Station policy and site engineering explicitly define the physical equipment and electrical circuits belonging to these categories. Noncritical station loads are not automatically dispatched.

---

## 3. Dynamic Critical-Load Requirement
The protected critical load demand is represented conceptually as a dynamic function:
$$P_{\text{critical}}(t)$$
The required active power of protected systems may vary dynamically with operating conditions (e.g., ambient temperature, heating cycles, filtration flow rates). The optimization algorithm and control layer must **NOT** dynamically redefine or re-classify which equipment is protected; equipment membership is fixed by station engineering configuration.

---

## 4. Renewable Generation Behavior
Immediately available uncurtailed renewable power ($P_{\text{RE}} = P_{\text{solar}} + P_{\text{wind}}$) is directed first toward supplying the dynamic protected critical demand $P_{\text{critical}}(t)$. "Renewable-first" represents a candidate dispatch priority, not an optimization objective target or zero-curtailment guarantee.

---

## 5. Diesel Generation Behavior
Diesel generation ($P_{\text{D}}$) is dispatched to cover remaining protected critical demand when renewable generation is insufficient ($P_{\text{RE}} < P_{\text{critical}}(t)$) and diesel generation is available.
- *Mandatory Restriction*: Diesel generation must **NOT** be started or operated merely to charge the battery bank. Diesel operation is authorized solely when required to maintain protected critical load.

---

## 6. Battery Discharge Behavior
During `UNKNOWN_INVALID`, battery discharge ($P_{\text{BD}} > 0$) is permitted **SOLELY** to supply the authorized dynamic critical load $P_{\text{critical}}(t)$ when renewable and diesel generation are insufficient ($P_{\text{RE}} + P_{\text{D}} < P_{\text{critical}}(t)$).
- *Mandatory Restriction*: Battery discharge must **NOT** be used to supply noncritical loads or serve as a general station energy source during Option D.

---

## 7. Battery Charging Behavior & Unavoidable Excess Power
If diesel is already running because it is required to maintain protected critical load, and the generator's minimum operating output ($P_{\text{D,min}}$) creates unavoidable excess generation ($P_{\text{excess}} = P_{\text{RE}} + P_{\text{D,min}} - P_{\text{critical}}(t) > 0$):
1. Excess generation is directed to charge the battery bank ($P_{\text{BC}}$) up to its allowable technical charging limit.
2. Allowable charging limits include maximum charge power ($P_{\text{BC,max}}$), SOC ceiling ($SOC_{\text{max}}$), charge acceptance, thermal boundaries, and telemetry validity.
3. Remaining excess power beyond allowable charging capacity ($P_{\text{curtail}} = P_{\text{excess}} - P_{\text{BC}}$) is curtailed.

---

## 8. Insufficient-Power & Shortfall Behavior
The system shall attempt to maintain ALL protected critical systems at their engineering-defined minimum viable operating levels.
- If available generation/discharge power ($P_{\text{supply}}$) is insufficient to satisfy all minimum viable operating levels ($P_{\text{supply}} < \sum P_{\text{min,viable}}$):
  1. Available power is **proportionally allocated** across the protected critical systems.
  2. The system shall **NOT** impose an arbitrary category priority (e.g. heating > water > comms) unless separately authorized by governance.
  3. The system shall immediately escalate the condition to the authorized operator while continuing whatever critical service is physically possible.

---

## 9. Operator Escalation
Mandatory operator escalation occurs upon reaching the first applicable degraded boundary:
1. Reaching the governed time-duration boundary ($T_{\text{max,degraded}}$), **OR**
2. Reaching the governed resource-survivability boundary ($SOC_{\text{min}}$ or $F_{\text{reserve,min}}$),
whichever occurs first. Escalation alerts the operator via SCADA alarms and logs a governed `FaultEvent`.

---

## 10. Time and Resource Boundaries
The numerical thresholds for degraded duration ($T_{\text{max,degraded}}$), minimum battery reserve ($SOC_{\text{min}}$), and minimum fuel reserve ($F_{\text{reserve,min}}$) are **ENGINEERING AND GOVERNANCE DEFINITIONS**. They are NOT established numerical policy values at this stage.

---

## 11. Recovery to Normal Operation
Option D remains active until:
1. Telemetry/forecast inputs become valid, allowing ECD to evaluate survivability and transition the system back to `NORMAL` or `EMERGENCY` under governed rules, **OR**
2. An authorized human operator issues a manual override command to clear `UNKNOWN_INVALID`.

---

## 12. Prohibited Behaviors
The following operational actions are strictly prohibited under Option D:
- No battery discharge to supply noncritical loads.
- No starting or running diesel generators solely to charge the battery.
- No dynamic redefinition of protected critical equipment by optimization algorithms.
- No imposition of unapproved category priorities (e.g. heating > water > comms).
- No automatic station shutdown solely because operator escalation occurs.
- No treatment of synthetic prototype parameters as real station policy.
- No autonomous 24-hour MILP optimization of noncritical loads during `UNKNOWN_INVALID`.

---

## 13. Engineering Parameters Not Yet Established
The following items remain `ENGINEERING_DEFINITION_REQUIRED`:
- Physical circuit breaker mapping for critical equipment.
- Dynamic critical load calculation formulas $P_{\text{critical}}(t)$.
- Minimum viable operating levels ($P_{\text{min,viable}}$) for each critical system.
- Maximum battery charge power ($P_{\text{BC,max}}$), charge acceptance, and thermal cutoffs.
- Station generator turndown ratios, minimum output ratings, and fuel curves.

---

## 14. Governance Parameters Not Yet Established
The following items remain `GOVERNANCE_DECISION_REQUIRED`:
- Degraded mode maximum duration watchdog limit ($T_{\text{max,degraded}}$).
- Minimum battery SOC reserve threshold ($SOC_{\text{min}}$).
- Minimum diesel fuel reserve threshold ($F_{\text{reserve,min}}$).
- Final selection of DEC-004 operational response across Options A, B, C, and D.

---

## 15. Prototype-Only Values
The following parameters in the repository are explicitly classified as `SYNTHETIC_PROTOTYPE_TEST_VALUE` and are **NOT** deployment policy:
- $72.0\text{ h}$ $T_{\text{required}}$ reference value.
- $2.0\text{ h}$ $T_{\text{test}}$ offline validation value.
- $30,000\text{ W}$ constant prototype load value.
- $80\% / 30\%$ high/low SOC test bands.
- $50\text{ L} / 12.5\text{ L}$ high/low fuel test bands.
- $10\text{ kW}$ prototype generator minimum output parameter.

---

## 16. Implementation Boundary
This formal policy definition establishes governance specifications **ONLY**. Implementation authorization is **NOT GRANTED**. No runtime code, schema, optimizer, or control module has been modified or executed.

Status: `FORMAL_DEFINITION_SEALED`
