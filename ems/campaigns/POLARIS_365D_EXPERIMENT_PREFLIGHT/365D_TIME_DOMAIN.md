# 365D TIME DOMAIN SPECIFICATION & ARITHMETIC AUDIT

## Time Horizon Specifications
- **Governed Terminology**: `"Full-calendar-year 2024 / 8,784 hourly cycles"`
- **Start Timestamp**: `2024-01-01T00:00:00Z`
- **End Timestamp**: `2024-12-31T23:00:00Z`
- **Timezone**: UTC (Coordinated Universal Time, ISO 8601 `Z` suffix). Zero local offset shifts.
- **Control Timestep ($dt$)**: 1.0 hour (3,600 seconds).
- **Calendar Year Type**: 2024 (Leap Year).
- **Total Days**: 366 days.
- **Total Observations ($N_{obs}$)**: 8,784 hourly timesteps.
- **Total Controller Cycles ($N_{cycles}$)**: 8,784 closed-loop receding-horizon MPC cycles.
- **Forecast Horizon ($H$)**: 24 hours (24 lookahead points per cycle).

## Time Domain Arithmetic Verification
$$N_{obs} = 366 \text{ days} \times 24 \text{ hours/day} = 8,784 \text{ timesteps}$$

> [!NOTE]
> Standard non-leap years contain 8,760 hours ($365 \times 24$). Because calendar year 2024 is a leap year (including February 29, 2024), the full-calendar-year 2024 experiment comprises exactly **8,784 hourly control cycles**.

## Edge Case & Boundary Handling
1. **Leap-Day Handling**: February 29, 2024 (`2024-02-29T00:00:00Z` to `2024-02-29T23:00:00Z`, timesteps 1416–1439) is fully represented in the canonical H1.0 fixture.
2. **Missing / Duplicate Timestamps**: Audited `POLARIS_HYBRID_FIXTURE_H1_0/fixture.csv`. Zero missing timestamps, zero duplicate timestamps. Continuous hourly monotonicity verified.
3. **Year-End Horizon Padding**: For control cycles $k > 8760$, lookahead horizon $k+1 \dots k+24$ extends beyond index 8783. The `H10RuntimeAdapter` applies deterministic terminal value padding (repeating final timestep observations) to maintain a fixed 24-point `ForecastBundle` without out-of-bounds errors.
4. **Initial Cycle Initialization ($k=0$)**: Initialized with `StationState` at `2024-01-01T00:00:00Z`, initial battery SOC = 50.0% (100.0 kWh), initial diesel running state = False, initial cumulative fuel = 0.0 L.
