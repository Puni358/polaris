# RENEWABLE MINIMALITY REVIEW
## DUAL RENEWABLE COVERAGE RATIONALE (SOLAR 0-50 kW & WIND 0-20 kW)

### 1. FORENSIC AUDIT OF RENEWABLE INPUTS
The proposed minimum fixture specifies dual renewable generation sources:
- **Solar PV Generation**: Bimodal daytime curve peaking at $50\text{ kW}$ ($0\text{--}50\text{ kW}$).
- **Wind Generation**: Synthetic fluctuating curve peaking at $20\text{ kW}$ ($0\text{--}20\text{ kW}$).

This audit evaluated whether both solar and wind are strictly required, or if a single renewable source (e.g. solar only) would be minimum-sufficient.

### 2. ARCHITECTURAL COVERAGE JUSTIFICATION
- **Single Renewable (Solar Only)**:
  - Demonstrates daytime renewable availability and nighttime zero-generation periods.
  - *Deficiency*: Leaves the POLARIS EMS wind forecasting, wind dispatch variables, and wind actuals data pathways unexercised.
- **Dual Renewable (Solar + Wind)**:
  - Exercises complete multi-source renewable integration in the MILP optimizer:
    $$P_{\text{renewable}}(t) = P_{\text{PV}}(t) + P_{\text{wind}}(t)$$
  - Demonstrates complementary renewable dispatch (e.g., wind generation during nighttime when solar is zero).
  - Tests Option D excess generation charging and curtailment when $P_{\text{PV}}(t) + P_{\text{wind}}(t) > P_{\text{critical}}(t) + P_{\text{batt,charge\_max}}$.

### 3. MINIMALITY EVALUATION OF TRAJECTORY COMPLEXITY
- The synthetic solar curve uses a deterministic bell-shaped bimodal profile ($0\text{ kW}$ hours 0–6, rising to $50\text{ kW}$ at hour 12, falling to $0\text{ kW}$ by hour 18).
- The synthetic wind curve uses a deterministic stepped profile ($10\text{ kW}$ hours 0–8, $20\text{ kW}$ hours 8–16, $5\text{ kW}$ hours 16–24).
- Neither trajectory requires stochastic noise or complex micro-meteorological simulation. Simple deterministic step/sinusoidal curves are minimum-sufficient to test all control code paths.

### 4. PROVENANCE & CLAIM BOUNDARIES
Both trajectories are classified:
`solar_provenance: REUSED_SYNTHETIC_ENGINEERING_PARAMETER`
`wind_provenance: REUSED_SYNTHETIC_ENGINEERING_PARAMETER`
`empirical_status: NOT_ESTABLISHED`

They MUST NOT be cited as measured Nuolja solar irradiance or wind speeds.

### 5. CONCLUSION & RECOMMENDATION
`RENEWABLE_MINIMALITY_STATUS = MINIMUM_REQUIRED`.
Retain both Solar ($0\text{--}50\text{ kW}$) and Wind ($0\text{--}20\text{ kW}$) in the minimum synthetic fixture to maintain 100% test coverage of POLARIS EMS dual-renewable dispatch software architecture.
