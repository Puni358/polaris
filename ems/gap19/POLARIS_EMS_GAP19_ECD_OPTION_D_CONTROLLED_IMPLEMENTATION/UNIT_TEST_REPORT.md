# POLARIS EMS GAP19 — Unit & Component Test Report

## Execution Summary

| Test Suite | Total Executed | Passed | Failed | Errors | Duration |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `tests/test_gap19_ecd_option_d.py` | 18 | 18 | 0 | 0 | 0.004 s |
| `tests/test_isolated_components.py` | 4 | 4 | 0 | 0 | 0.002 s |
| **Total** | **22** | **22** | **0** | **0** | **0.006 s** |

## Section 25 Test Results (Items A through R)

| Test ID | Description | Result |
| :--- | :--- | :---: |
| `test_A_initial_fuel_initialization` | Initial fuel loaded from config | **PASS** |
| `test_B_one_step_fuel_consumption` | 1h physical fuel consumption calculated | **PASS** |
| `test_C_fuel_first_action_only_semantics` | Consumption uses committed $k=0$ ONLY | **PASS** |
| `test_D_zero_negative_fuel_boundary` | Fuel non-negative clipping & over-consumption observable | **PASS** |
| `test_E_fuel_state_continuity_across_two_cycles` | Multi-cycle fuel continuity verified | **PASS** |
| `test_F_ecd_receives_current_fuel_not_initial` | ECD receives rolling current fuel | **PASS** |
| `test_G_normal_option_b_routing` | NORMAL mode routed to Option B | **PASS** |
| `test_H_emergency_option_d_routing` | EMERGENCY mode routed to Option D | **PASS** |
| `test_I_unknown_invalid_not_silently_routed` | UNKNOWN_INVALID blocked from Option B/D | **PASS** |
| `test_J_milp_infeasibility_does_not_declare_emergency` | Infeasibility status does not mutate ECD | **PASS** |
| `test_K_milp_infeasibility_does_not_advance_digital_twin_state` | Infeasibility state advancement = False | **PASS** |
| `test_L_option_d_proportional_critical_load_allocation` | Proportional allocation $\alpha$ calculated | **PASS** |
| `test_M_renewable_first_behavior` | Renewable used first for protected load | **PASS** |
| `test_N_diesel_support_behavior` | Diesel generator supports remaining load | **PASS** |
| `test_O_excess_diesel_charges_battery` | Permissible excess diesel charges battery | **PASS** |
| `test_P_diesel_not_started_solely_for_battery_charging` | Zero diesel start solely for battery charging | **PASS** |
| `test_Q_digital_twin_receives_only_first_action` | Simulator receives committed $k=0$ action | **PASS** |
| `test_R_option_b_protected_behavior_remains_unchanged` | SHA-256 baseline hashes of protected files match | **PASS** |

## Isolated Component Tests
- `test_isolated_router_normal`: **PASS**
- `test_isolated_router_emergency`: **PASS**
- `test_isolated_option_d_solver_generation`: **PASS**
- `test_isolated_simulator_step`: **PASS**
