# Synthetic Test Harness Specification

## Test Suite Specification (TEST-A through TEST-I)

| Test ID | Scenario Name | Test Setup & Fixture | Expected Router Mode | Expected Optimizer / Policy | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TEST-A** | Nominal MPC | `demo_scenario.json` | `NORMAL` | Option B Native HiGHS | `SUCCESS_CLEAN`, $s_{J2}=0$ |
| **TEST-B** | Battery Emergency | Synthetic $15\%$ SOC | `EMERGENCY` | Option D Fallback | Battery preserved, diesel runs |
| **TEST-C** | Diesel Emergency | Synthetic $5	ext{L}$ fuel | `EMERGENCY` | Option D Fallback | Diesel preserved, battery discharges |
| **TEST-D** | Dual Depletion | Low SOC & low fuel | `EMERGENCY` | Option D Fallback | Proportional critical load shedding |
| **TEST-E** | Resource Tie | Margin diff $< 10^{-6}	ext{h}$ | `EMERGENCY` | Option D Fallback | `preserved_resource = BOTH` |
| **TEST-F** | UNKNOWN_INVALID | Expired auth horizon | `UNKNOWN_INVALID` | Fail-Closed | MPC halted, `CRITICAL_TERMINATION` |
| **TEST-G** | MILP Infeasibility | `demand_stress_scenario.json` | `NORMAL` $	o$ `EMERGENCY` | Passed to ECD $	o$ Option D | Zero dispatch blackout prevented |
| **TEST-H** | Transition N $	o$ E | Closed-loop 24h run | Dynamic transition | Option B $	o$ Option D | Smooth mode handover |
| **TEST-I** | Transition E $	o$ N | Recovery sequence | Dynamic transition | Option D $	o$ Option B | Mode return evaluated per-step |

---

## Verdict
`SYNTHETIC_TEST_HARNESS = SPECIFIED`. Complete 9-test harness contract defined.
