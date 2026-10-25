# POLARIS EMS — ECD OPTIMIZER BOUNDARY AUDIT

## 1. Executive Summary

This document specifies the interface boundary and strict firewall between the Emergency Condition Detector (ECD) and the MILP / Rule-Based `EnergyOptimizer`.

---

## 2. Strict Optimizer Firewall Rules

1. **ZERO Direct Optimizer Access**: The ECD **MUST NOT** import, instantiate, or call `EnergyOptimizer`, `LocalMILPEnergyOptimizer`, or solver libraries (e.g., Highs, CBC, SciPy).
2. **ZERO Coefficient Manipulation**: The ECD **MUST NOT** alter cost weights, degradation penalties, or slack penalties inside MILP matrices.
3. **ZERO Constraint Alteration**: The ECD **MUST NOT** modify battery capacity, charge/discharge power limits, or generator min/max generation bounds inside `EnergyOptimizer`.
4. **Clean Parameter Pass-Through**: The EMS Mode Manager / Policy Layer passes an explicit `operating_mode` context to `EnergyOptimizer.optimize(bundle, state, configs, mode_context=...)`.

---

## 3. Boundary Architectural Diagram

```
┌────────────────────────────────────────────────────────┐
│        Emergency Condition Detector (ECD)              │
└──────────────────────────┬─────────────────────────────┘
                           │ Outputs: EmergencyAssessment
                           ▼
┌────────────────────────────────────────────────────────┐
│           EMS Mode Manager / Policy Layer              │
│                                                        │
│  Selects dispatch policy based on EmergencyAssessment: │
│    - NORMAL: Minimize operational fuel & degradation   │
│    - EMERGENCY: Maximize fuel/battery preservation     │
└──────────────────────────┬─────────────────────────────┘
                           │ Configures mode context
                           ▼
┌────────────────────────────────────────────────────────┐
│             EnergyOptimizer (MILP / Rule-Based)         │
│                                                        │
│  Solves dispatch plan according to configured mode     │
└────────────────────────────────────────────────────────┘
```

Status: `ESTABLISHED`
