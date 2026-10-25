# POLARIS EMS — T_REQUIRED & FUEL RESERVE FLOOR INTERACTION AUDIT

## 1. Purpose

This document audits the mathematical and governance interaction between **ECD Survivability Horizon ($T_{\text{required}}$)** and the **Minimum Volumetric Fuel Reserve Floor ($F_{\text{reserve,min}}$)**.

---

## 2. Mathematical Coupling Analysis

The minimum fuel volume required to sustain protected critical service over the horizon $T_{\text{required}}$ is given by:

$$F_{\text{required}}(T_{\text{required}}) = \int_{0}^{T_{\text{required}}} f_{\text{rate}}(P_{\text{critical}}(t)) \, dt$$

Under prototype constant load $P_{\text{crit}} = 30\text{ kW}$ ($f_{\text{rate}} = 12.5\text{ L/h}$):
$$F_{\text{required}}(T_{\text{required}}) = 12.5 \times T_{\text{required}}\text{ [Liters]}$$

---

## 3. Candidate Policy Coupling Formulations

### Coupling Model 1: Direct Mathematical Derivation
- **Concept**: $F_{\text{reserve,min}}$ is not an independent parameter; it is dynamically calculated as $F_{\text{required}}(T_{\text{required}})$.
- **Behavior**: If remaining diesel fuel $F_{\text{rem}} < F_{\text{required}}(T_{\text{required}})$, the ECD immediately flags diesel endurance failure ($T_{\text{diesel}} < T_{\text{required}}$) and classifies mode as `EMERGENCY`.
- **Governance Requirement**: Requires authorization of $T_{\text{required}}$ and $f_{\text{rate}}(P_{\text{critical}})$.

### Coupling Model 2: Independent Physical Fuel Floor
- **Concept**: $F_{\text{reserve,min}}$ is an independent physical tank safety floor (e.g. minimum fuel height to avoid fuel line unpriming, pump cavitation, or bottom sludge ingestion), completely separate from $T_{\text{required}}$.
- **Behavior**: System enforces $F_{\text{rem}} > F_{\text{reserve,min}}$ as an instantaneous physical guardrail regardless of $T_{\text{required}}$.
- **Governance Requirement**: Requires site engineering tank calibration.

### Coupling Model 3: Dual-Guardrail Policy (Recommended Pattern)
- **Concept**: The system enforces **BOTH** guardrails independently:
  1. Instantaneous Physical Floor: $F_{\text{rem}} > F_{\text{reserve,min}}$ (prevents physical generator starvation).
  2. Survivability Horizon Test: $T_{\text{diesel}} = \frac{F_{\text{rem}} - F_{\text{reserve,min}}}{f_{\text{rate}}(P_{\text{critical}})} \ge T_{\text{required}}$ (ensures usable fuel above floor satisfies time horizon).
- **Behavior**: Provides complete coverage against both physical tank exhaustion and operational time horizon shortfall.

---

## 4. Current Governance Status

The relationship between $T_{\text{required}}$ and $F_{\text{reserve,min}}$ remains **UNRESOLVED**.

```yaml
FUEL_RESERVE_COUPLING_STATUS: GOVERNANCE_DECISION_REQUIRED
F_RESERVE_MIN_NUMERICAL_VALUE: NOT_ESTABLISHED (HD-06 blocker)
T_REQUIRED_NUMERICAL_VALUE: NOT_ESTABLISHED (HD-03 blocker)
```
