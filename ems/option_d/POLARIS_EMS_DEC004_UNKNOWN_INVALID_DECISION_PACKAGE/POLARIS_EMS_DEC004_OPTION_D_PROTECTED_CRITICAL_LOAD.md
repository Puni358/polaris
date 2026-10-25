# POLARIS EMS — DEC-004 OPTION D: PROTECTED CRITICAL-LOAD FALLBACK

> [!IMPORTANT]
> **GOVERNANCE CANDIDATE ONLY**
> Option D is a candidate policy concept for human governance review. It is **NOT** approved operational policy, **NOT** authorized for runtime deployment, and **MUST NOT** be implemented or executed without explicit human governance sign-off.

---

## 1. Executive Summary

This document establishes the formal governance specification for **Option D: Protected Critical-Load Fallback** as a fourth candidate operational response for **DEC-004 (Operational Response to ECD UNKNOWN_INVALID)**.

When the Emergency Condition Detector (ECD) returns `UNKNOWN_INVALID` because microgrid survivability cannot be established from valid inputs, Option D places the system into a protected degraded operating concept intended to **preserve only the authorized critical load** while awaiting valid external/operator input to resolve the invalid condition.

---

## 2. Governance Policy Concept & Principles

### 2.1 Core Objectives
1. **Critical Load Protection**: Maintain electrical service exclusively for authorized critical-service loads.
2. **Noncritical Load Suppression**: Do not automatically dispatch noncritical or flexible station loads while survivability state is unknown.
3. **Optimization Suspension**: Do not execute normal long-horizon survivability optimization (`EnergyOptimizer`) while the ECD assessment is `UNKNOWN_INVALID`.
4. **Operator Await Boundary**: Await authorized external or operator input to clear the invalid state and restore normal/emergency MPC execution.

### 2.2 Conceptual Critical-Load Categories
The conceptual load categories under discussion by the human governance process include:
1. **Essential Heating**: Thermal heating required for human survivability in extreme polar/antarctic environments.
2. **Water Treatment & Filtration**: Essential water purification and life-support processing.
3. **Emergency Communications**: Radio, satellite, and telemetry infrastructure.

*Note: These are conceptual categories only. They do NOT represent physical station circuits, power values, equipment IDs, numerical thresholds, or deployment configuration.*

---

## 3. Resource Semantics under Option D

### 3.1 Renewable-First Semantics
- **Candidate Ordering**: Available renewable power (solar PV and wind generation) is directed first toward meeting the authorized critical load demand.
- **Remaining Demand**: If renewable generation is insufficient to cover the critical load, remaining critical demand is supplied by diesel generation when available.
- **Non-Optimization Boundary**: "Renewable-first" represents a candidate dispatch ordering, NOT a new mathematical objective function or optimization target. Zero curtailment or percentage targets are assumed.

### 3.2 Diesel Semantics
- **Critical Load Support**: Diesel generation may be dispatched to cover remaining authorized critical demand when diesel generation is available.
- **Generator Constraint & Operating Boundaries**:
  - *Illustrative Power Balance*: In synthetic calculations, diesel power is modeled at the exact remaining critical demand (e.g., $4\text{ kW}$ to balance $7\text{ kW}$ load $- 3\text{ kW}$ renewables).
  - *Prototype Model Constraint Boundary*: In existing repository configuration (`system/config/diesel.yaml`), `min_power_w = 10000.0` ($10\text{ kW}$). If the physical generator enforces a $10\text{ kW}$ minimum output, operating at $10\text{ kW}$ produces $13\text{ kW}$ total generation ($3\text{ kW}$ renewables $+ 10\text{ kW}$ diesel), resulting in $6\text{ kW}$ excess generation over $7\text{ kW}$ critical load. Treatment of excess generation (charging battery vs. curtailment) is `UNRESOLVED_GOVERNANCE_DECISION`.
  - *Station-Specific Deployment Parameter*: Physical turndown ratios, minimum loading limits, and fuel curves for real station equipment are `ENGINEERING_DEFINITION_REQUIRED`.
- **Unresolved Policy Boundaries**: Option D does NOT authorize fuel reserve thresholds, maximum runtime limits, startup policies, or fuel telemetry freshness rules. If diesel availability itself is unknown/invalid, it is treated as an unresolved engineering case.

### 3.3 Battery Semantics
- **Unresolved Governance State**: Battery behavior under Option D is **NOT ESTABLISHED** and requires an explicit governance decision.
- **No Inferred Policy**: Option D does NOT automatically add battery discharge, nor does it automatically prohibit battery discharge. Zero SOC thresholds, battery reserve percentages, or degradation priorities are created by this document.

---

## 4. Architectural Placement & Boundary Separation

Option D sits strictly in the **EMS Mode Manager / Policy Layer**, completely separate from the ECD Core Evaluator:

```
┌────────────────────────────────────────────────────────┐
│        Emergency Condition Detector (ECD)              │
│                                                        │
│  Evaluates state ──► Returns UNKNOWN_INVALID           │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│           EMS Mode Manager / Policy Layer              │
│                                                        │
│  Option D Policy Execution (If Authorized by Human):   │
│    - Suppress noncritical loads                        │
│    - Order renewable + diesel for critical demand      │
│    - Bypass long-horizon EnergyOptimizer               │
│    - Await operator / valid telemetry input            │
└────────────────────────────────────────────────────────┘
```

The ECD core module (`system/control/ecd.py`) does **NOT** start diesel generators, shed loads, or select setpoints independently.

---

## 5. Summary of Unresolved Governance & Engineering Items

Option D requires the following explicit decisions before any integration implementation could be authorized:
1. **DEC-004-D1**: Exact critical-load definition and circuit inventory.
2. **DEC-004-D2**: Battery dispatch policy under Option D (permitted, prohibited, or reserve-capped).
3. **DEC-004-D3**: Action when renewable generation is zero and diesel is unavailable or invalid.
4. **DEC-004-D4**: Action when the protected critical load itself exceeds total available generation.
5. **DEC-004-D5**: Maximum duration / watchdog timeout for Option D before mandatory escalation.

Status: `CANDIDATE_SPECIFICATION_COMPLETE`
