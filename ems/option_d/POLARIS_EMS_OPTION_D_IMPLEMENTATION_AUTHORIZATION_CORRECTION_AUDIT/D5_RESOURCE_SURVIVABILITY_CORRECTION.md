# D5 RESOURCE SURVIVABILITY CORRECTION

## Correction Summary: Resource-Survivability Boundary vs Fixed Fuel Volume

This document establishes the formal correction for **Governance Decision D5 (Operator Escalation Triggers)**.

---

## 1. Identified Issue in Prior Package Draft

Prior drafts referred to an open governance item as a `"fixed fuel-volume threshold"` or `"50 L escalation threshold"`.

This was imprecise and risked converting a dynamic engineering survivability assessment into a raw fixed-liter rule.

---

## 2. Corrected D5 Governance Semantics

Sealed D5 governance specifies dual escalation boundaries:

$$\text{Escalation Trigger} = \text{Time Boundary} \quad \mathbf{OR} \quad \text{Resource-Survivability Boundary} \quad (\text{whichever occurs first})$$

```text
D5_TIME_BOUNDARY = OPEN
D5_RESOURCE_SURVIVABILITY_DEFINITION = ENGINEERING_GOVERNANCE_REQUIRED
D5_FIXED_FUEL_VOLUME_THRESHOLD = NOT_AUTHORIZED
```

---

## 3. Engineering Dependencies of Resource Survivability

Resource survivability MUST NOT be collapsed into a raw fuel volume number. Conceptually, fuel resource survivability depends on dynamic station engineering models, including:
- Usable fuel volume remaining ($V_{\text{fuel}}(t)$).
- Protected critical load minimum power profile ($P_{\text{crit,min}}(t)$).
- Generator fuel consumption rate curve ($F_{\text{rate}}(P_{\text{gen}})$).
- Generator minimum operating constraints ($P_{\text{diesel,min}}$).
- Renewable availability assumptions used by survivability assessment.
- Station resupply / refill timeline.
- Required survivability duration ($T_{\text{required}} = 6.0\text{h}$).

---

## 4. Multi-Resource Scope (Fuel + Battery)

D5 resource survivability encompasses both **fuel survivability** AND **battery survivability**:
- **Battery Survivability Deficit**: Battery SOC dropping below level required to sustain critical load for remaining $T_{\text{required}}$ horizon.
- **Fuel Survivability Deficit**: Fuel volume dropping below level required to sustain generator output for critical load over $T_{\text{required}}$.

Either deficit establishes emergency conditions in ECD and triggers operator escalation monitoring.
