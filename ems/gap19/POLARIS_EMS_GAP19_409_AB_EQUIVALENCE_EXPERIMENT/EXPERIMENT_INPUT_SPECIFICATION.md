# Experiment Input Specification

The experiment evaluated 3 distinct operational regimes to thoroughly cover the solution space:

1. `RENEWABLE_SURPLUS`: Solar 2000 W, Wind 1000 W, Demand 1500 W, Initial SOC 50%.
2. `DIESEL_REQUIRED`: Solar 200 W, Wind 100 W, Demand 25000 W, Initial SOC 20%.
3. `HIGH_CURTAILMENT`: Solar 60000 W, Wind 40000 W, Demand 5000 W, Initial SOC 90%.

## Explicit Input Contracts
- `critical_demand_w`: `[1000.0] * 24` W
- `ebr_target_wh`: `60000.0` Wh
- `terminal_target_wh`: Initial SOC Energy Wh
