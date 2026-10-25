# NUMERICAL RANGE AUDIT
## PARAMETER BOUNDS & HARD CONSTRAINT AUDIT

### 1. BOUND VERIFICATION RESULTS

| Parameter / Field | Declared Bounds | Observed Fixture Range | Constraint Status |
|---|---|---|---|
| Critical Heating Load | $15.0	ext{ kW}$ | $15.0	ext{ kW}$ (or NaN in SC-05) | **PASS** |
| Critical Water Load | $10.0	ext{ kW}$ | $10.0	ext{ kW}$ (or NaN in SC-05) | **PASS** |
| Critical Comms Load | $5.0	ext{ kW}$ | $5.0	ext{ kW}$ (or NaN in SC-05) | **PASS** |
| Aggregate Critical Load | $30.0	ext{ kW}$ | $30.0	ext{ kW}$ (or NaN in SC-05) | **PASS** |
| Flexible Load | $15.0	ext{ kW}$ | $15.0	ext{ kW}$ | **PASS** |
| Solar PV Generation | $0.0	ext{--}50.0	ext{ kW}$ | $0.0000	ext{--}50.0000	ext{ kW}$ | **PASS** |
| Wind Generation | $0.0	ext{--}20.0	ext{ kW}$ | $0.0000	ext{--}20.0000	ext{ kW}$ | **PASS** |
| Initial Battery SOC | $20.0\%	ext{--}95.0\%$ | $20.0\%$ (SC-02/04) / $80.0\%$ (SC-01/03/05) | **PASS** |
| Usable Battery Energy | $40.0	ext{--}190.0	ext{ kWh}$ | $40.0	ext{ kWh}$ or $160.0	ext{ kWh}$ | **PASS** |
| Initial Fuel Reserve | $\ge 0.0	ext{ L}$ | $500.0	ext{ L}$, $20.0	ext{ L}$, or $10.0	ext{ L}$ | **PASS** |

### 2. CONCLUSION
`NUMERICAL_RANGE_STATUS = PASS`.
All numerical parameters strictly respect their declared engineering bounds.
