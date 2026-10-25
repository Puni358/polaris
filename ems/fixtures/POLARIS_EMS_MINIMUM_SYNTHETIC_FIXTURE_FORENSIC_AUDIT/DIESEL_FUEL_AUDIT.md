# DIESEL FUEL AUDIT
## GENERATOR LINEAR FUEL MODEL VERIFICATION

### 1. LINEAR MODEL AUDIT
Generator fuel consumption rate $F(t)$ is governed by:
$$F(P_{	ext{gen}}) = 5.0 \cdot u_{	ext{gen}}(t) + 0.25 \cdot P_{	ext{gen}}(t) \quad [	ext{L/h}]$$

### 2. OPERATING POINT CALCULATIONS
- $P_{	ext{gen}} = 10.0	ext{ kW} \implies F = 5.0(1) + 0.25(10) = 7.5	ext{ L/h}$
- $P_{	ext{gen}} = 30.0	ext{ kW} \implies F = 5.0(1) + 0.25(30) = 12.5	ext{ L/h}$
- $P_{	ext{gen}} = 60.0	ext{ kW} \implies F = 5.0(1) + 0.25(60) = 20.0	ext{ L/h}$

Flat $12.5	ext{ L/h}$ assumption is confirmed removed; linear model equation verified.

### 3. CONCLUSION
`DIESEL_FUEL_STATUS = PASS`.
Linear fuel consumption model equation is mathematically correct.
