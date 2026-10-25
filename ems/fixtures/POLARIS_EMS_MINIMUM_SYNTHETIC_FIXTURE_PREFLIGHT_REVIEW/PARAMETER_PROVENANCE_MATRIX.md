# PARAMETER PROVENANCE MATRIX
## COMPREHENSIVE NUMERICAL PARAMETER CLASSIFICATION MATRIX

### 1. FULL PARAMETER PROVENANCE AUDIT
Every numerical value proposed for the minimum synthetic engineering fixture was audited for provenance classification.

### 2. CLASSIFICATION MATRIX

| Parameter Symbol | Numerical Value | Units | Primary Source / Context | Provenance Classification | Reconciled Preflight Status |
|---|---|---|---|---|---|
| $H_{\text{sim}}$ | 24 | hours | Simulation Duration | `SYNTHETIC_ENGINEERING_ASSUMPTION` | APPROVED |
| $H_{\text{mpc}}$ | 24 | hours | MPC Lookahead Horizon | `SYNTHETIC_ENGINEERING_ASSUMPTION` | APPROVED |
| $\Delta t$ | 1.0 | hours | Simulation & Control Timestep | `SYNTHETIC_ENGINEERING_ASSUMPTION` | APPROVED |
| $P_{\text{critical\_total}}$ | 30.0 | kW | Aggregate Protected Critical Load | `SYNTHETIC_ENGINEERING_ASSUMPTION` | APPROVED |
| $P_{\text{heating}}$ | 15.0 | kW | Critical Heating Component | `SYNTHETIC_ENGINEERING_ASSUMPTION` | APPROVED |
| $P_{\text{water}}$ | 10.0 | kW | Critical Water Treatment Component | `SYNTHETIC_ENGINEERING_ASSUMPTION` | APPROVED |
| $P_{\text{comms}}$ | 5.0 | kW | Critical Communications Component | `SYNTHETIC_ENGINEERING_ASSUMPTION` | APPROVED |
| $P_{\text{flexible}}$ | 15.0 | kW | Noncritical Flexible Demand | `SYNTHETIC_ENGINEERING_ASSUMPTION` | APPROVED |
| $P_{\text{PV\_max}}$ | 50.0 | kW | Peak Solar PV Generation | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $P_{\text{wind\_max}}$ | 20.0 | kW | Peak Wind Generation | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $E_{\text{batt\_cap}}$ | 200.0 | kWh | Total Nominal Storage Capacity | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $P_{\text{batt\_max}}$ | 50.0 | kW | Max Charge / Discharge Power | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $SOC_{\text{min\_tech}}$ | 20.0 | % | Technical Cell Protection Floor | `CURRENT_IMPLEMENTATION_FACT` | **RECONCILED FROM 10%** |
| $SOC_{\text{max\_tech}}$ | 95.0 | % | Technical Maximum Charging Limit | `CURRENT_IMPLEMENTATION_FACT` | APPROVED |
| $\eta_{\text{batt}}$ | 90.0 | % | Battery Round-Trip Efficiency | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $P_{\text{gen\_min}}$ | 10.0 | kW | Diesel Generator Minimum Output | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $P_{\text{gen\_max}}$ | 60.0 | kW | Diesel Generator Maximum Rating | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $F_{\text{base}}$ | 5.0 | L/h | Base Idle Generator Fuel Consumption | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $F_{\text{marginal}}$ | 0.25 | L/kWh | Marginal Generator Fuel Rate | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $V_{\text{fuel,0}}$ | 500.0 | L | Initial Fuel Reserve Volume | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| $T_{\text{required\_baseline}}$ | 6.0 | hours | Sealed ECD Baseline Survivability | `SEALED_HUMAN_GOVERNANCE_DECISION` | APPROVED |
| $\beta_{\text{forecast}}$ | +10.0 | % | Synthetic Forecast Over-Estimation Bias | `SYNTHETIC_ENGINEERING_ASSUMPTION` | APPROVED |

### 3. MANDATORY PROVENANCE SUMMARY
- **Zero parameters** are classified as `REAL_STATION_FACT`.
- **Zero parameters** are authorized for Nuolja production deployment.
- All numerical parameters are strictly isolated within the synthetic engineering boundary.
