# Emergency Battery Reserve (EBR) Semantics Analysis

This analysis examines potential operational interpretations of the Emergency Battery Reserve (EBR) to assist human stakeholders in defining reserve policy.

## Candidate Operational Interpretations

### Interpretation 1: Minimum Stored Energy Floor (Fixed Wh or SOC %)
- **Physical Meaning:** Absolute lower boundary on battery stored energy across all operational timesteps.
- **Relationship to $T_{\text{REQUIRED}}$:** Decoupled from dynamic load trajectories; acts as a static buffer.
- **Operational Consequence:** Simple to enforce, but may restrict battery usage when critical load is low or solar is imminent.
- **E3 Compatibility:** Compatible with basic minimum SOC, but does not adapt to dynamic resource survivability margins.

### Interpretation 2: Critical-Load Survivability Reserve ($T_{\text{REQUIRED}} = 6\text{h}$)
- **Physical Meaning:** Stored energy required to sustain protected critical load for a governed duration ($T_{\text{REQUIRED}} = 6\text{h}$).
- **Relationship to $T_{\text{REQUIRED}}$:** Directly coupled to $T_{\text{REQUIRED}}$ and forward critical demand trajectory $P_{\text{crit}}[t]$.
- **Operational Consequence:** Dynamically scales with critical load forecasts. Prevents unnecessary battery locking during low-load periods.
- **E3 Compatibility:** Fully aligned with E3 survivability margin semantics.

### Interpretation 3: Dynamic ECD-Derived Reserve
- **Physical Meaning:** Reserve target dynamically updated based on ECD state evaluation and relative diesel fuel availability.
- **Relationship to $T_{\text{REQUIRED}}$:** Coupled to ECD survivability assessment.
- **Operational Consequence:** Adapts when diesel fuel is low or generator is faulted.
- **E3 Compatibility:** Maximizes microgrid survivability by balancing battery and diesel availability.

```text
EBR_SEMANTICS = GOVERNANCE_DECISION_REQUIRED
EBR_PHYSICAL_UNIT = GOVERNANCE_DECISION_REQUIRED
```
