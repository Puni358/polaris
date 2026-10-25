# POLARIS Branch 01 V2 Objective Function Audit Report

```json
{
  "audit_name": "POLARIS_BRANCH01_V2_OBJECTIVE_AUDIT",
  "status": "PASS",
  "optimizer_class": "LocalMILPEnergyOptimizer",
  "optimizer_sha": "ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35",
  "cost_parameters": {
    "fuel_cost_per_litre_usd": 2.5,
    "marginal_fuel_litres_per_wh": 0.00025,
    "marginal_diesel_cost_per_wh_usd": 0.000625,
    "marginal_diesel_cost_per_kwh_usd": 0.625,
    "base_fuel_litres_per_hour": 5.0,
    "base_diesel_cost_per_hour_usd": 12.5,
    "unmet_load_penalty_per_wh_usd": 10.0,
    "unmet_load_penalty_per_kwh_usd": 10000.0,
    "curtailment_penalty_per_wh_usd": 0.001,
    "curtailment_penalty_per_kwh_usd": 1.0,
    "battery_degradation_penalty_per_wh_usd": 5e-05,
    "battery_degradation_penalty_per_kwh_usd": 0.05,
    "diesel_startup_cost_usd": 15.0
  },
  "tradeoff_ratios": {
    "unmet_load_to_marginal_diesel_cost_ratio": 16000.0,
    "unmet_load_to_curtailment_cost_ratio": 10000.0
  },
  "audit_finding": "The MILP objective places a $10,000/kWh penalty on unmet load vs $0.625/kWh marginal fuel cost (a 16,000x ratio). When Treatment predicts a solar deficit, the optimizer commits diesel generator power to avoid unmet load. This produces +11,350.179 L higher fuel consumption but eliminates 30,543.753 kWh of unmet load, which is mathematically optimal under the frozen objective formulation."
}
```
