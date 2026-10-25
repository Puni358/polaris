# CRITICAL LOAD SEMANTICS CORRECTION

## 1. DISTINCTION BETWEEN CRITICAL LOAD POWER QUANTITIES

The audit clarified the distinct physical definitions of load quantities to prevent conflation in solver equations:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ P_i,nominal(t)   : Nameplate / Rated Maximum Electrical Power Rating        │
├─────────────────────────────────────────────────────────────────────────────┤
│ P_i,requested(t) : Operational Requested Power Demand for Category i        │
├─────────────────────────────────────────────────────────────────────────────┤
│ P_i,min(t)       : Engineering-Defined Minimum Viable Operating Level        │
├─────────────────────────────────────────────────────────────────────────────┤
│ P_i,served(t)    : Actual Dispatched Electrical Power Delivered by EMS      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. CONFLATION CORRECTION
- **Previous Blueprint Gap**: Earlier documents occasionally used $P_{\text{critical}}(t)$ without distinguishing whether it represented full requested demand $P_{\text{req}}(t)$ or minimum viable operating level $P_{\text{min}}(t)$.
- **Correction**:
  - `P_critical_requested`: Total requested critical demand forecast array in `ForecastBundle.critical_demand`.
  - `P_critical_min`: Vector of minimum viable power levels $P_{i,\text{min}}(t)$ configured in engineering inputs (`system/config/loads.yaml`).
  - `P_served_crit`: Decision variable vector in `EnergyOptimizer` representing actual power delivered to protected critical loads.
