# POLARIS EMS GAP19 — OPTION D DATA-BLOCKED BOUNDARY

**Gate ID**: `GAP19_OPTION_B_MULTI_SCENARIO_STRESS_TEST`  
**Package ID**: `POLARIS_EMS_GAP19_DATA_BLOCKED_OPERATIONAL_ARCHITECTURE`  

---

## 1. Option D Sealed Policy Baseline

Option D (**Protected Critical-Load Fallback**, DEC-004) is human-selected and sealed:
- **Decision Status**: `SELECTED_AND_SEALED`
- **Core Directive**: When ECD declares `EMERGENCY` or `UNKNOWN_INVALID`, non-critical loads are shed, and available power (diesel + renewables + battery) is allocated strictly to protected critical load ($P_{\text{critical}}(t)$).
- **Proportional Allocation (D4)**: Under power deficit, power is shared proportionally based on minimum viable requirements ($P_{i,\min}$).
- **Diesel Charging Rule (D6)**: Diesel charges battery ONLY when diesel is already running to support critical load and excess minimum generation exists; diesel is never started solely to charge battery.

---

## 2. Open Engineering Requirements Before Runtime Implementation

Option D **MUST NOT** be implemented in codebase files until the following data-blocked requirements are provided:

1. **Sub-Circuit Load Data ($P_{\text{critical}}(t)$)**: Measured critical load series for Nuolja site.
2. **Critical Circuit Mapping**: As-built electrical single-line diagrams mapping physical breakers.
3. **Proportional Ratios ($P_{i,\min}$)**: Numerical minimum viable operating levels per protected sub-system.
4. **Implementation Authorization**: Explicit human governance authorization for code edits.
