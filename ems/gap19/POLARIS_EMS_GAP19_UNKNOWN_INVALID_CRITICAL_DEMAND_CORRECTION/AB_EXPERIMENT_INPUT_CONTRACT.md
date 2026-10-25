# A/B Experiment Input Contract

To eliminate any ambiguity arising from silent fallbacks during the Option A vs Option B equivalence experiment, the experimental test harness MUST explicitly supply:

1. `operating_mode = "NORMAL"`
2. `critical_demand_w`: Explicit 24-hour critical demand trajectory (e.g. `[1000.0] * 24` or derived explicitly from fixture).
3. `ForecastBundle`: Identical timestamps, solar, wind, and demand.
4. `StationState`: Identical initial SOC, battery energy, and diesel status.
5. `config`: Identical battery capacity, min/max SOC, charge/discharge efficiency, diesel power, fuel consumption rates, EBR target, and terminal target.

`A_B_INPUT_CONTRACT = COMPLETE`
