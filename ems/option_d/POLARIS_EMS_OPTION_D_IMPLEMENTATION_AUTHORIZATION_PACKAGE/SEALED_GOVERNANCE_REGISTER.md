# SEALED GOVERNANCE REGISTER

## Governance Authority Statement

All decisions contained within this register represent **FROZEN HUMAN GOVERNANCE AUTHORITY**. They have been formally sealed in prior governance iterations and **MUST NOT BE REOPENED OR MUTATED** by engineering teams, mathematical optimization formulations, or software implementations.

---

## Immutable Governance Decisions

### DEC-004: Option D — Protected Critical Load Fallback
- **Selected Architecture**: Option D.
- **Title**: Protected Critical Load Fallback.
- **Core Principle**: When energy resources are severely constrained or survivability is threatened, the EMS shifts operation to strictly protect station-defined critical equipment, shedding noncritical flexible loads while managing available power proportionally across critical categories.

### D1: Protected Critical Equipment Definition
- **Definition**: Protected critical equipment is station-defined.
- **Dynamic Requirement**: Protected critical power requirement may vary dynamically over time: $P_{i,\text{min}}(t)$.
- **Optimizer Boundary**: Critical equipment identity is defined by station engineering and governance; it is **never** dynamically redefined or recategorized by the optimizer.
- **Conceptual Categories**:
  1. Essential heating required for human survivability.
  2. Essential water treatment and filtration.
  3. Emergency communications.

### D2: Battery Discharge Restriction
- **Boundary**: During Option D, battery discharge is permitted **only** to serve protected critical loads.
- **Restriction**: Battery energy must **not** support noncritical flexible loads under Option D dispatch.

### D3: Resource Exhaustion Sequence & Battery Discharge Boundary
- **Sequence**: If combined renewable generation and diesel generation are insufficient to supply protected critical load, remaining battery capability is used to maintain protected critical systems while awaiting operator decision.
- **Termination Criteria**: Continues until either:
  1. The operator resolves the condition, OR
  2. The governed battery discharge boundary is reached.
- **Production Status**: The actual production Option-D battery discharge boundary is `NOT_ESTABLISHED` and remains an open engineering/governance input.
- **Synthetic Fixture Distinction**: The synthetic benchmark fixture uses $\text{SOC}_{\text{min}} = 20\%$. This is a `SYNTHETIC_ENGINEERING_FIXTURE_VALUE`. It is **NOT** the production Option-D battery discharge boundary, NOT a real Nuolja station requirement, NOT an authorized production emergency reserve, and NOT a universal POLARIS battery policy.

### D4: Critical Load Allocation Basis (HUMAN SEALED)
- **Selected Basis**: `PROPORTIONAL_TO_MINIMUM_VIABLE_CRITICAL_REQUIREMENTS`.
- **Sufficient Power Case**: When available protected-critical power $\ge \sum_i P_{i,\text{min}}(t)$, maintain each protected critical system at or above its minimum viable operating level ($P_{i,\text{served}}(t) \ge P_{i,\text{min}}(t)$).
- **Insufficient Power Case**: When available protected-critical power $P_{\text{critical,available}}(t) < \sum_i P_{i,\text{min}}(t)$, allocate available power proportionally according to minimum viable requirements:
  $$P_{i,\text{served}}(t) = \alpha(t) \cdot P_{i,\text{min}}(t)$$
  $$\text{where } \alpha(t) = \frac{P_{\text{critical,available}}(t)}{\sum_i P_{i,\text{min}}(t)}, \quad 0 \le \alpha(t) \le 1$$
- **Priority Rule**: No critical category receives an authorized priority over another. Requested-demand proportionality ($P_{i,\text{requested}}$) is explicitly **NOT** selected.

### D5: Operator Escalation Triggers
- **Trigger Criteria**: Dual escalation boundary — `TIME_BOUNDARY` OR `RESOURCE_SURVIVABILITY_BOUNDARY`, whichever occurs first.
- **Status**: Structural rule sealed. `D5_TIME_BOUNDARY` remains open; `D5_RESOURCE_SURVIVABILITY_DEFINITION` requires station engineering models (usable fuel, critical load profile, battery capability, generator curves, resupply relationship). A fixed fuel-volume threshold (`D5_FIXED_FUEL_VOLUME_THRESHOLD`) is `NOT_AUTHORIZED`.

### D6: Diesel Excess Generation Management
- **Rule**: If diesel generation is required to maintain protected critical load, and minimum generator operating output ($P_{\text{diesel,min}}$) produces excess energy beyond immediate critical demand:
  1. Diesel excess is routed to battery charging.
  2. Excess energy is curtailed only after the battery cannot accept more.
- **Restriction**: Diesel generation must **NEVER** be started solely for the purpose of charging the battery.

---

## Sealed $T_{\text{required}}$ Governance

| Attribute | Sealed Governance Value |
| :--- | :--- |
| **Baseline Duration** | $T_{\text{required}} = 6.0\text{ hours}$ |
| **Operational Semantics** | `PROTECTED_CRITICAL_SERVICE_SURVIVABILITY_DURATION` |
| **Configuration Mode** | `HYBRID` |
| **Override Authority** | `AUTOMATED_MFA_CRYPTOGRAPHIC_AUTHORITY_GATE` |
| **Fuel Relationship** | `INDIRECTLY_COUPLED` |
| **Synthetic Fixture Note** | 72 hours is a **synthetic engineering test value only** and must never replace 6.0h in production governance. |
