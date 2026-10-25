# Input Specification

## Frozen Input Parameters

1. **Horizon**: 24 hours, 1-hour timesteps ($dt = 1.0$).
2. **Battery Assets**: Capacity = $200,000	ext{ Wh}$, Min SOC = $20\%$, Max SOC = $95\%$, Efficiency = $92\%$, Max Charge/Discharge Power = $50,000	ext{ W}$, Initial Energy = $100,000	ext{ Wh}$.
3. **Diesel Asset**: Min Power = $10,000	ext{ W}$, Max Power = $100,000	ext{ W}$, Base Fuel = $5.0	ext{ L/h}$, Marginal Fuel = $0.00025	ext{ L/Wh}$, Startup Fuel = $2.0	ext{ L}$, Initial Running = `False`.
4. **Explicit Critical Demand Contract**: Explicit $P_{	ext{critical}}[t] = 15,000	ext{ W}$ for all $t=0..23$.
5. **Reserve Targets**: EBR Target = $50,000	ext{ Wh}$, Terminal Target = $100,000	ext{ Wh}$.
