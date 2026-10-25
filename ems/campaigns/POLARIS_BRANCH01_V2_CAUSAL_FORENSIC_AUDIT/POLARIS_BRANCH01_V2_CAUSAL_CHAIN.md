# POLARIS Branch 01 V2 Causal Chain Analysis

```json
{
  "chain_name": "POLARIS_BRANCH01_V2_CAUSAL_CHAIN",
  "status": "ESTABLISHED",
  "links": [
    {
      "link_index": 1,
      "from": "SOLAR_FORECAST_DIFFERENCE",
      "to": "PERCEIVED_FUTURE_RENEWABLE_AVAILABILITY",
      "classification": "STRONGLY_SUPPORTED",
      "evidence": "Branch01 predicts realistic atmospheric solar attenuation during cloudy periods, whereas Control GHI remains optimistic."
    },
    {
      "link_index": 2,
      "from": "PERCEIVED_FUTURE_RENEWABLE_AVAILABILITY",
      "to": "OPTIMIZER_DISPATCH",
      "classification": "STRONGLY_SUPPORTED",
      "evidence": "When predicted renewable availability is lower than demand, the MILP optimizer solves for diesel commitment to prevent SOC depletion and unmet load."
    },
    {
      "link_index": 3,
      "from": "OPTIMIZER_DISPATCH",
      "to": "BATTERY_RENEWABLE_UTILIZATION",
      "classification": "STRONGLY_SUPPORTED",
      "evidence": "Battery charging increases (+5,810.729 kWh) and discharge increases (+3,746.782 kWh) to smooth generator dispatch."
    },
    {
      "link_index": 4,
      "from": "OPTIMIZER_DISPATCH",
      "to": "DIESEL_COMMITMENT_GENERATION",
      "classification": "DIRECTLY_OBSERVED",
      "evidence": "Treatment diesel ON hours increased from 2,757 h to 4,057 h (+1,300 h) across the 173 trajectories."
    },
    {
      "link_index": 5,
      "from": "DIESEL_COMMITMENT_GENERATION",
      "to": "LOAD_SERVED_UNMET_LOAD",
      "classification": "DIRECTLY_OBSERVED",
      "evidence": "Treatment load served increased by +30,543.753 kWh, reducing unmet load from 40,352.215 kWh in Control to 9,808.462 kWh in Treatment."
    },
    {
      "link_index": 6,
      "from": "DIESEL_GENERATION",
      "to": "FUEL_CONSUMPTION",
      "classification": "DIRECTLY_OBSERVED",
      "evidence": "Fuel consumption increased from 22,486.701 L to 33,836.880 L (+11,350.179 L), matching frozen fuel equation exactly."
    }
  ]
}
```
