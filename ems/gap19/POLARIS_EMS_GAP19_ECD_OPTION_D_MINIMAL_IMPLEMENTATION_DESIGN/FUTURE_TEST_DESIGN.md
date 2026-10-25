# Future Test Suite Design

## Test Harness Design (TEST-A through TEST-H)

| Test ID | Test Target | Test Inputs | Expected Router State | Expected Dispatch Path |
| :--- | :--- | :--- | :--- | :--- |
| **TEST-A** | Nominal MPC | Nominal scenario | `NORMAL` | Option B HiGHS Native |
| **TEST-B** | Battery Emergency | Synthetic $15\%$ SOC | `EMERGENCY` | Option D Fallback |
| **TEST-C** | Diesel Emergency | Synthetic $5	ext{L}$ fuel | `EMERGENCY` | Option D Fallback |
| **TEST-D** | Resource Tie | Margin diff $< 10^{-6}	ext{h}$ | `EMERGENCY` | Option D (`preserved=BOTH`) |
| **TEST-E** | UNKNOWN_INVALID | Expired horizon payload | `UNKNOWN_INVALID` | Intercepted (No silent solver) |
| **TEST-F** | MILP Infeasibility | `demand_stress_scenario.json` | Status passed to ECD | Option D if EMERGENCY |
| **TEST-G** | State Propagation | 1-step execution | State advanced | `DigitalTwinSimulator.step` |
| **TEST-H** | Option B Protection | `gap19_highs_native.py` | Unchanged math | HiGHS objective hierarchy |

No tests were executed during this design audit.
