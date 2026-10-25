# TEST ARCHITECTURE

## 1. PRE-IMPLEMENTATION TEST SUITE SPECIFICATION (TEST-A THROUGH TEST-M)

The audit specified 13 targeted tests to validate Option D implementation BEFORE code execution is authorized.

| Test ID | Test Name | Target Module | Objective & Assertion |
| :--- | :--- | :--- | :--- |
| **TEST-A** | Schema Compatibility | `system/schemas/` | Verify additive fields serialize/deserialize without breaking v1.0.0 JSON |
| **TEST-B** | Fixture Adapter | `SyntheticFixtureProvider`| Verify parsing of all 120 fixture rows, 5 scenarios, kW->W scaling |
| **TEST-C** | ECD Input Mapping | `system/control/ecd.py` | Verify ECD evaluation against fixture scenarios SC-01..05 |
| **TEST-D** | Mode Routing | `OptionDPolicyLayer` | Verify transformation of `EmergencyAssessment` into `ModeConstraintSet` |
| **TEST-E** | Option D Constraint Gen | `system/optimization/` | Verify linear constraint matrix dimensions ($456$ vars) |
| **TEST-F** | Critical-Only Battery | `milp.py` | Assert $P_{\text{dis}}[t] \le P_{\text{critical}}[t]$ and zero battery to flex load in emergency |
| **TEST-G** | Renewable-First Critical | `milp.py` | Assert available renewables allocated to critical load before diesel |
| **TEST-H** | Diesel Excess Charging | `milp.py` | Assert D6 diesel excess charges battery up to limit before curtailment |
| **TEST-I** | Proportional Allocation | `milp.py` | Assert equal ratio $\alpha$ across critical categories when power insufficient |
| **TEST-J** | UNKNOWN_INVALID Routing | `SafeStateFallbackRouter`| Assert fail-closed safe-state zero-dispatch fallback on telemetry error |
| **TEST-K** | Truth Firewall | `runner.py` | Assert zero future actuals ($t+1..t+24$) passed to controller |
| **TEST-L** | Normal-Mode Regression | `runner.py` | Assert 100% numerical identity of normal mode dispatch vs baseline |
| **TEST-M** | GAP19 Objective Alignment| `system/optimization/` | Assert `ModeConstraintSet` compatibility with 4-stage lexicographic interface |

---

## 2. EXECUTION RULE
- **DO NOT EXECUTE NOW**.
- This test architecture is defined for future implementation verification.
