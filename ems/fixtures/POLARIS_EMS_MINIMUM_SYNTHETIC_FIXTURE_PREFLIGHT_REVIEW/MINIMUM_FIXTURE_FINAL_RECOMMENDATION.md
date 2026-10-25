# MINIMUM FIXTURE FINAL RECOMMENDATION
## FROZEN SYNTHETIC FIXTURE SPECIFICATION FOR SEPARATE GENERATION TASK

### 1. FROZEN FIXTURE SPECIFICATION OVERVIEW
Once the blockers in `PRE_GENERATION_BLOCKER_REGISTER.md` are formally signed off by human review, a separate future fixture-generation task can use this frozen specification to generate the synthetic CSV input files.

### 2. FROZEN FIXTURE SPECIFICATION SUMMARY
- **Simulation Duration**: 24 Hours ($t = 0, 1, 2, \dots, 23$).
- **Timestep**: $\Delta t = 1.0\text{ Hour}$.
- **Lookahead Horizon**: $H = 24\text{ Hours}$ ($N = 24$ decision steps per cycle).
- **Number of Scenarios**: 5 Deterministic Scenarios (SC-01 through SC-05).
- **Load Model**: 2-Tier Load Structure:
  - $P_{\text{critical}}(t) = 30\text{ kW}$ (Heating 15 kW, Water 10 kW, Comms 5 kW).
  - $P_{\text{flexible}}(t) = 15\text{ kW}$ (Noncritical, shed under Emergency / Option D).
- **Renewable Trajectories**:
  - Solar: Bimodal daytime curve $0\text{--}50\text{ kW}$.
  - Wind: Stepped curve $0\text{--}20\text{ kW}$.
- **Battery Storage Specification**:
  - Total Nominal Capacity: $200\text{ kWh}$.
  - Usable SOC Range: **$20\%$ to $95\%$** ($40\text{ kWh}$ to $190\text{ kWh}$).
  - Charge/Discharge Power: Max $50\text{ kW}$.
  - Efficiency: $90\%$ Round-Trip.
- **Diesel Generator Specification**:
  - Operating Bounds: Min $10\text{ kW}$, Max $60\text{ kW}$.
  - Linear Fuel Curve: $F(t) = 5.0 \cdot u_{\text{gen}}(t) + 0.25 \cdot P_{\text{gen}}(t)\text{ L/h}$.
- **Fuel Reserve Specification**:
  - Initial Fuel: $500\text{ L}$ (SC-01, SC-02, SC-05); $20\text{ L}$ (SC-03); $10\text{ L}$ (SC-04).
  - Resupply: $0\text{ L/h}$.
- **Forecast Generation**:
  - $\hat{P}_{\text{PV}}(t+k|t) = 1.10 \times P_{\text{PV,actual}}(t+k)$.
  - Controller receives `ForecastBundle` lookahead vectors; Digital Twin receives actuals.
- **Provenance Tagging**: Every output CSV header MUST contain the `SYNTHETIC_ENGINEERING_ASSUMPTION` provenance block.

### 3. MANDATORY IMPLEMENTATION FIREWALL
DO NOT write CSV files or code until `FIXTURE_GENERATION_READY` moves to `YES` upon human approval.
