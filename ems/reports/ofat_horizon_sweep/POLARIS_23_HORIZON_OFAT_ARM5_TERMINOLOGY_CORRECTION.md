# POLARIS — ARM-5 TERMINOLOGY CORRECTION REPORT

**DOCUMENT STATUS**: OFFICIAL GOVERNANCE CORRECTION REPORT  
**GOVERNANCE**: FROZEN EVIDENCE — READ-ONLY ANALYSIS  
**TIMESTAMP**: 2026-09-20T09:55:00Z  

---

## 1. TERMINOLOGY CORRECTION SPECIFICATION

A forensic review of the 38-column raw telemetry across all 4,152 timesteps (173 origins $\times$ 24 MPC steps) identified a precise distinction between Arm 5 and other zero-fuel-delta treatment arms:

1. **Exact Telemetry Invariance**:
   - **Arms $j \in \{11, 17, 18, 20, 21, 22, 23\}$** exhibit bitwise, exact 0.000000 identity across all audited telemetry fields (diesel power, commitment, startups, battery charge, battery discharge, SOC, curtailment, and fuel) at every single timestep.

2. **Operational Invariance within Floating-Point Tolerance**:
   - **Arm $j = 5$** exhibits identical diesel power, diesel commitment, startups, battery charge, SOC, curtailment, and fuel across all 4,152 timesteps, but contains a single minor numerical floating-point difference of **0.0009 kW total** across all timesteps in battery discharge power.

### Mandatory Wording Directive
Arm 5 must **NOT** be described as "exact invariant", "exact telemetry match", or "identical".  
Arm 5 is formally classified as **"operationally invariant within the observed floating-point tolerance"**.

---

## 2. MANDATORY STATUS BLOCK

```
FROZEN_EVIDENCE_MODIFIED = NO
MILP_SOLVES_EXECUTED = 0
EXPERIMENT_RERUN = NO
```
