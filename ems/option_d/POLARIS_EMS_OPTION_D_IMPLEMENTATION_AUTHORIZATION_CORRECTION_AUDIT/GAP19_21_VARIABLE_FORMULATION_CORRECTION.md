# GAP19 21-VARIABLE FORMULATION CORRECTION

## Correction Summary: Proposed Pre-GAP19 Formulation vs Final EMS Optimizer

This document establishes the formal wording correction for the **21-variable/timestep MILP formulation**.

---

## 1. Identified Wording Issue

Prior package descriptions referred to the 21-variable MILP formulation as `"the final scalar MILP"` or `"the Option D solver"`.

This was incorrect because it implied that the 21-variable formulation represents the final production optimizer or completes GAP19 multi-objective solver architecture.

---

## 2. Corrected Classification & Terminology

The 21-variable/timestep formulation MUST strictly be described as:

```text
GAP19_21_VARIABLE_FORMULATION_STATUS = PROPOSED_PRE_GAP19_OPTION_D_CONSTRAINT_FORMULATION
```

It is:
- An additive pre-GAP19 engineering representation of physical energy balances, D4 proportional allocation, and D6 generator bounds.
- Formulated under the existing single-pass SciPy HiGHS scalar solver wrapper.

It is **NOT**:
- The final EMS optimizer.
- The finalized GAP19 multi-stage lexicographic solver architecture.
- An empirically validated final production MILP.
- A modification of objective governance.

---

## 3. Objective Firewall Boundary

```text
CURRENT_MILP = Existing scalar objective implementation
PROPOSED_PRE_GAP19_FORMULATION = Linear physical & policy constraint extension
GAP19_TARGET = Governed multi-stage sequential lexicographic solver
```

> [!WARNING]
> Pre-GAP19 code MUST NOT add giant penalty weights to simulate lexicographic priority order. The formulation uses existing scalar objective coefficients and enforces Option D strictly via hard linear bounds.
