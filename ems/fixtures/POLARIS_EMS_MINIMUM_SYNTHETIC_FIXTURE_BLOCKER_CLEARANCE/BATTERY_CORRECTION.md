# BATTERY CORRECTION
## RECONCILED BATTERY SOC MINIMUM FLOOR SPECIFICATION

### 1. SPECIFICATION CORRECTION
The synthetic fixture specification for minimum battery state of charge (SOC) is formally corrected:

$$\text{OLD FIXTURE SPECIFICATION: } SOC_{\text{min}} = 10\% \quad (20\text{ kWh})$$
$$\mathbf{RECONCILED\ FIXTURE\ SPECIFICATION: }\mathbf{SOC_{\text{min}} = 20\%} \quad (40\text{ kWh})$$

### 2. RATIONALE & GOVERNANCE ALIGNMENT
1. Authoritative repository configuration file `system/config/battery.yaml` defines `soc_min = 0.20` ($20\%$ / $40\text{ kWh}$) as the technical cell protection floor (`SOC_min_technical`).
2. Optimization solver scripts (`milp.py`) enforce $E_{\text{batt}}(t) \ge E_{\text{cap}} \cdot SOC_{\text{min\_tech}} = 40\text{ kWh}$ as a hard lower bound.
3. Aligning the synthetic fixture specification to $20\%$ prevents immediate MILP solver constraint infeasibility during closed-loop MPC execution.

### 3. FORMAL PROVENANCE CLASSIFICATION
- **Classification**: `REUSED_EXISTING_PROTOTYPE_PARAMETER`
- **Station Identity**: `NONE`
- **Empirical Status**: `NOT_ESTABLISHED`
- **Scientific Claim Firewall**: The $20\%$ SOC floor ($40\text{ kWh}$) is a synthetic engineering parameter inherited from prototype configuration (`battery.yaml`). It MUST NOT be represented as measured Nuolja battery health or hardware specification.

### 4. RECONCILED BATTERY SPECIFICATION SUMMARY

| Battery Parameter | Reconciled Value | Physical Usable Range | Provenance Tag |
|---|---|---|---|
| Total Nominal Capacity | $200.0\text{ kWh}$ | $0\text{--}200\text{ kWh}$ | `REUSED_EXISTING_PROTOTYPE_PARAMETER` |
| Minimum Technical SOC Floor | **$20.0\%$ ($40.0\text{ kWh}$)** | Lower Bound | `REUSED_EXISTING_PROTOTYPE_PARAMETER` |
| Maximum Technical SOC Ceiling | **$95.0\%$ ($190.0\text{ kWh}$)** | Upper Bound | `REUSED_EXISTING_PROTOTYPE_PARAMETER` |
| Active Usable Storage Window | **$150.0\text{ kWh}$** | $40\text{--}190\text{ kWh}$ | `DERIVED_SYNTHETIC_CAPACITY` |
| Charge / Discharge Max Power | $50.0\text{ kW}$ | $-50\text{ kW} \le P \le +50\text{ kW}$ | `REUSED_EXISTING_PROTOTYPE_PARAMETER` |
| Round-Trip Efficiency | $90.0\%$ ($\eta_c=\eta_d=0.9487$) | Energy Loss Model | `REUSED_EXISTING_PROTOTYPE_PARAMETER` |

`BATTERY_PROVENANCE_STATUS = RECONCILED_AND_CLEARED`.
