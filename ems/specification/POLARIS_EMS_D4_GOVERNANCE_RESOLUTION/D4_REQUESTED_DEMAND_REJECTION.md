# D4 REQUESTED DEMAND REJECTION

## 1. FORMAL REJECTION OF REQUESTED-DEMAND PROPORTIONALITY

This document records the formal rejection of the counter-formulation:
$$\text{Proportionality Based on Current Requested Demand } (P_{i,\text{requested}})$$

---

## 2. REJECTED COUNTER-FORMULATION (FORMULATION B)
$$\text{REJECTED: } P_{i,\text{served}}(t) = \beta(t) \cdot P_{i,\text{requested}}(t), \quad \beta(t) = \frac{P_{\text{crit,avail}}(t)}{\sum_k P_{k,\text{requested}}(t)}$$

### REASONING FOR REJECTION
1. **Misalignment with Emergency Survivability Intent**: During severe power deficits, requested demand ($P_{i,\text{requested}}$) may reflect non-essential overhead or transient surges. Allocating power relative to requested demand dilutes power delivered to systems running at their true minimum viable threshold ($P_{i,\text{min}}$).
2. **Governed Intent**: DEC-004 D4 explicitly states: *"Maintain each protected critical system at or above its engineering-defined minimum viable operating level..."* This establishes $P_{i,\text{min}}$ as the authoritative baseline for emergency survivability.

---

## 3. STATUS REGISTER ENTRY
```text
D4_REQUESTED_DEMAND_BASIS = NOT_SELECTED
D4_MINIMUM_VIABLE_REQUIREMENT_BASIS = SELECTED
```
