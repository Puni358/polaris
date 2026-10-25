# TEST INVARIANT REGISTER

## Immutable System Invariants

This document establishes the 10 system invariants that MUST be preserved across all implementation and validation steps. Any violation of these invariants constitutes an immediate test failure and invalidates implementation authorization.

---

## The 10 System Invariants

### INVARIANT 1: No Category Priority Bias
No protected critical category receives an unauthorized priority over another under Option D.
$$\alpha_{\text{heating}}(t) = \alpha_{\text{water}}(t) = \alpha_{\text{comms}}(t) = \alpha(t)$$

### INVARIANT 2: Minimum Requirements Basis for D4
D4 proportional allocation uses minimum viable requirements ($P_{i,\text{min}}$), NEVER requested demand ($P_{i,\text{requested}}$).
$$P_{i,\text{served}}(t) = \alpha(t) \cdot P_{i,\text{min}}(t)$$

### INVARIANT 3: Strict Battery Critical-Only Discharge
During Option D, battery discharge CANNOT serve flexible noncritical loads.
$$P_{\text{bat,dis,flex}}(t) = 0 \quad \forall t \text{ in OPTION_D}$$

### INVARIANT 4: Diesel Start Restriction for Battery Charging
Diesel generator CANNOT be started solely to charge the battery.
$$P_{\text{diesel,bat}}(t) \le M \cdot \text{IsCriticalDeficient}(t)$$

### INVARIANT 5: D6 Excess Generation Charging Priority
Diesel excess generation beyond critical load requirements MUST charge the battery before curtailment occurs, up to battery charge capacity.

### INVARIANT 6: Zero Normal Mode Regression
Normal mode dispatch setpoints and objective evaluations are UNCHANGED by the introduction of Option D.

### INVARIANT 7: UNKNOWN_INVALID Provenance Integrity
Untrusted, missing, or stale telemetry inputs MUST NOT be silently treated as valid EMERGENCY data. They MUST route to `OperatingMode.UNKNOWN_INVALID`.

### INVARIANT 8: Truth Firewall Integrity
Future actual ground truth trajectories MUST NOT enter controller decisions at step $t$.

### INVARIANT 9: Synthetic Production Parameter Firewall
Synthetic fixture values ($15, 10, 5, 45, 200, 72$) MUST NOT be promoted to real Nuolja station production values.

### INVARIANT 10: Scalar Objective Boundary
The current scalar MILP objective MUST NOT be represented or described as the final GAP19 lexicographic multi-objective formulation.
