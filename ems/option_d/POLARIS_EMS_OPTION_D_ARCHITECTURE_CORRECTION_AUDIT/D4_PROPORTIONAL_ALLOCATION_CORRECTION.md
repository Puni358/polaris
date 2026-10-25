# D4 PROPORTIONAL ALLOCATION CORRECTION

## 1. FORENSIC AUDIT OF D4 SEALED GOVERNANCE Wording
Sealed DEC-004 D4 states:
> "Maintain each protected critical system at or above its engineering-defined minimum viable operating level whenever sufficient power exists. If available power is insufficient: proportionally allocate available power across protected critical systems. Do NOT invent a fixed priority such as heating > water > communications."

---

## 2. MATHEMATICAL FORMULATION ANALYSIS

The audit evaluated candidate mathematical formulations of D4 proportional allocation:

### FORMULATION A: Proportional to Minimum Viable Level ($P_{i,\text{min}}$)
$$P_{i,\text{served}}[t] = \alpha[t] \cdot P_{i,\text{min}}[t] \quad \forall i, \quad \alpha[t] = \frac{P_{\text{avail,crit}}[t]}{\sum_k P_{k,\text{min}}[t]} \in [0, 1)$$
- **Semantics**: Allocates power proportionally to each category's engineering-defined minimum viable operating level.
- **Assumptions**: Assumes all categories degrade proportionally relative to their minimum viable thresholds.

### FORMULATION B: Proportional to Requested Critical Demand ($P_{i,\text{requested}}$)
$$P_{i,\text{served}}[t] = \beta[t] \cdot P_{i,\text{requested}}[t] \quad \forall i, \quad \beta[t] = \frac{P_{\text{avail,crit}}[t]}{\sum_k P_{k,\text{requested}}[t]} \in [0, 1)$$
- **Semantics**: Allocates power proportionally to full requested critical demand.
- **Assumptions**: Assumes load shedding should scale proportionally to full operating request rather than minimum viable floor.

### FORMULATION C: Weighted Human/Station Critical Capacity Ratio
$$P_{i,\text{served}}[t] = \gamma[t] \cdot w_i \cdot P_{i,\text{min}}[t] \quad \forall i$$
- **Semantics**: Incorporates station-specific engineering weight factors $w_i$.

---

## 3. GOVERNANCE AMBIGUITY CLASSIFICATION & SEALED RESOLUTION
- **Previous Finding**: The sealed text ("proportionally allocate available power across protected critical systems") did not uniquely dictate whether proportional allocation must be computed on the basis of minimum viable level $P_{i,\text{min}}$ (Formulation A) or requested critical demand $P_{i,\text{requested}}$ (Formulation B).
- **Sealed Human Governance Decision (2026-09-24)**:
  `D4_ALLOCATION_BASIS = PROPORTIONAL_TO_MINIMUM_VIABLE_CRITICAL_REQUIREMENTS`
  Formulation A ($P_{i,\text{served}}(t) = \alpha(t) \cdot P_{i,\text{min}}(t)$) has been **OFFICIALLY SELECTED AND SEALED**. Formulation B (requested demand basis) has been **FORMALLY REJECTED**.
- **Updated Status**: `D4_FORMULATION_STATUS = GOVERNANCE_SEALED`

