# CLAIM FIREWALL SPECIFICATION
## SCIENTIFIC & EMPIRICAL CLAIM BOUNDARIES

### 1. SCIENTIFIC BOUNDARY MANDATE
The completed empirical and external evidence recovery audits established:
- `DIRECT_NUOLJA_EVIDENCE = 0`
- `P_CRITICAL_EXTERNAL_EVIDENCE = NOT_ESTABLISHED`
- `REAL_NUOLJA_DATA = FALSE`

Therefore, all values in `POLARIS_EMS_MINIMUM_SYNTHETIC_ENGINEERING_FIXTURE` are strictly synthetic engineering assumptions or reused prototype parameters.

### 2. MANDATORY PROVENANCE TAGGING
Every dataset, row, and parameter in this package carries the binding provenance block:
```yaml
provenance:
  source_type: SYNTHETIC_ENGINEERING_ASSUMPTION # or REUSED_EXISTING_PROTOTYPE_PARAMETER
  station_identity: NONE
  empirical_status: NOT_ESTABLISHED
  deployment_status: NOT_AUTHORIZED
  real_nuolja_data: FALSE
```

### 3. CLAIM BOUNDARY REGISTER

| Result / Data Point | Scientifically Permissible Claim | STRICTLY PROHIBITED CLAIM |
|---|---|---|
| **$30\text{ kW}$ Critical Load** | Synthetic load vector used for Option D proportional allocation software testing. | "Nuolja station protected critical load is $30\text{ kW}$." |
| **$200\text{ kWh}$ Battery Capacity** | Reused prototype storage parameter for MILP SOC constraint testing. | "Nuolja station has a $200\text{ kWh}$ battery storage system." |
| **$20\%$ Minimum SOC Floor** | Technical cell degradation protection floor enforced in `battery.yaml`. | "Nuolja battery minimum operational reserve is $20\%$." |
| **$12.5\text{ L/h}$ @ $30\text{ kW}$ Fuel Rate** | Derived fuel rate from synthetic linear model $F = 5.0\cdot u + 0.25\cdot P$. | "Nuolja generator fuel consumption is $12.5\text{ L/h}$." |
| **$50\text{ kW}$ Solar / $20\text{ kW}$ Wind** | Synthetic renewable trajectories used to test dual-renewable dispatch. | "Nuolja station renewable generation is $50\text{ kW}$ solar and $20\text{ kW}$ wind." |
| **Simulation Output Metrics** | Software execution log proving MPC closed-loop mathematical convergence. | "POLARIS EMS achieves $X\%$ fuel savings or $Y$ hours survivability at Nuolja." |

### 4. CONCLUSION
`CLAIM_FIREWALL_STATUS = ENFORCED`.
Zero synthetic data points or simulation outcomes from this package may be promoted to real Nuolja station facts or performance claims.
