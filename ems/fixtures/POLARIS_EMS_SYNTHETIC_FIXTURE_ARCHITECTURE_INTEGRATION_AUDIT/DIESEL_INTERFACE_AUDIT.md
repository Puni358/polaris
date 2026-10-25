# DIESEL INTERFACE AUDIT

## 1. DIESEL GENERATOR PARAMETER COMPARISON AUDIT

The audit verified diesel generator parameters across fixture specifications, runtime config (`system/config/diesel.yaml`), and optimization code (`system/optimization/implementations/milp.py`).

| Diesel Parameter | Synthetic Fixture Specification | Runtime Config (`diesel.yaml`) | MILP Implementation (`milp.py`) | ECD Interface (`ecd.py`) | Discrepancy / Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Minimum Power ($P_{\text{min}}$)** | $10.0$ kW ($10,000$ W) | `min_power_w: 10000.0` | `min_diesel_w = 10000.0` | `min_power_w = 10000.0` | **EXACT MATCH** |
| **Maximum Power ($P_{\text{max}}$)** | $60.0$ kW ($60,000$ W) | `max_power_w: 100000.0` | `max_diesel_w = 100000.0` | `max_power_w = 100000.0` | **DISCREPANCY NOTED** ($60$ kW vs $100$ kW config) |
| **Base Fuel Consumption** | $5.0$ L/h | `base_fuel_consumption_l_per_h: 5.0` | `base_fuel_l_h = 5.0` | `base_fuel_consumption_l_per_h = 5.0` | **EXACT MATCH** |
| **Marginal Fuel Consumption**| $0.25$ L/kWh ($0.00025$ L/Wh) | `marginal_fuel_consumption_l_per_wh: 0.00025` | `marg_fuel_l_wh = 0.00025` | `marginal_fuel_consumption_l_per_wh = 0.00025` | **EXACT MATCH** |
| **Physical Startup Fuel** | $0.0$ L | N/A | `startup_cost: 15.0` (\$) | `physical_startup_fuel_l = 0.0` | **EXACT MATCH** |

---

## 2. DISCREPANCY REPORT & ACTION
- **Discrepancy**: The synthetic fixture specifies a diesel generator maximum rating of $60.0$ kW ($60,000$ W). However, runtime config `diesel.yaml` specifies `max_power_w: 100000.0` ($100.0$ kW).
- **Impact**: In SC-01..05, demand never exceeds $45.0$ kW, so generator output remains below $60.0$ kW during fixture scenarios.
- **Governed Action**: Report the discrepancy. Do not modify source code or fixture. Update `diesel.yaml` parameter alignment during future implementation phase.
