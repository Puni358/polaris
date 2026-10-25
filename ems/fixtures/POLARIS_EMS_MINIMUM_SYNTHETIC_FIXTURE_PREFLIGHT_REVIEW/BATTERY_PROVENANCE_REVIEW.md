# BATTERY PROVENANCE REVIEW
## AUDIT OF STORAGE PARAMETERS & 10% VS 20% SOC FLOOR DISCREPANCY

### 1. FORENSIC AUDIT OF BATTERY PARAMETERS
The proposed minimum synthetic fixture specified the following battery parameters:
- **Usable Energy Capacity**: $200\text{ kWh}$
- **Maximum Charge / Discharge Power**: $50\text{ kW}$
- **Round-Trip Efficiency**: $90\%$ ($\eta_c = \eta_d = 0.9487$)
- **Minimum State of Charge (SOC)**: $10\%$ ($20\text{ kWh}$)

This preflight audit cross-referenced these parameters against the authoritative repository codebase and configuration files.

### 2. DISCREPANCY IDENTIFICATION: 10% VS 20% MINIMUM SOC
A major provenance discrepancy was discovered between the proposed fixture audit and the underlying system configuration:

| Source | Specified Minimum SOC | Equivalent Usable Floor | Provenance / Role |
|---|---|---|---|
| Proposed Fixture Audit | $10\%$ ($0.10$) | $20\text{ kWh}$ | `NEW_SYNTHETIC_ENGINEERING_TEST_VALUE` |
| Authoritative System Config (`system/config/battery.yaml`) | $20\%$ ($0.20$) | $40\text{ kWh}$ | `CURRENT_IMPLEMENTATION_FACT` (`SOC_min_technical`) |
| Objective Specification (Decision 11 Traceability) | $20\%$ ($0.20$) | $40\text{ kWh}$ | Hardware Protection Floor (`SOC_min_tech`) |

### 3. IMPACT ANALYSIS OF THE SOC DISCREPANCY
1. `system/config/battery.yaml` defines `soc_min = 0.20` as the **technical minimum cell degradation protection floor**.
2. Optimization solver formulations in `milp.py` enforce $E_{\text{batt}}(t) \ge E_{\text{cap}} \cdot SOC_{\text{min\_tech}} = 40\text{ kWh}$.
3. If the synthetic fixture is generated with an initial or minimum SOC assumption of $10\%$, executing the solver against `battery.yaml` will immediately trigger a hard constraint violation or force infeasibility.
4. Using $10\%$ in the fixture creates an unnecessary discrepancy with established project configuration.

### 4. RECONCILIATION REQUIREMENT
Before fixture generation:
- The minimum fixture battery SOC floor MUST be reconciled from $10\%$ to **$20\%$** ($40\text{ kWh}$).
- The usable energy range for the $200\text{ kWh}$ battery is strictly $20\%\text{--}95\%$ ($40\text{ kWh}$ to $190\text{ kWh}$), providing $150\text{ kWh}$ of active storage capacity.

### 5. PARAMETER PROVENANCE TABLE

| Battery Parameter | Value | Source | Provenance Status | Reconciliation Action |
|---|---|---|---|---|
| Total Nominal Capacity | $200\text{ kWh}$ | `system/config/battery.yaml` | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| Max Charge Power | $50\text{ kW}$ | `system/config/battery.yaml` | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| Max Discharge Power | $50\text{ kW}$ | `system/config/battery.yaml` | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| Charge/Discharge Efficiency | $90\%$ RTT | `system/config/battery.yaml` | `REUSED_SYNTHETIC_ENGINEERING_PARAMETER` | APPROVED |
| Minimum Technical SOC | $20\%$ ($40\text{ kWh}$) | `system/config/battery.yaml` | `CURRENT_IMPLEMENTATION_FACT` | **RECONCILED FROM 10% TO 20%** |
| Maximum Technical SOC | $95\%$ ($190\text{ kWh}$) | `system/config/battery.yaml` | `CURRENT_IMPLEMENTATION_FACT` | APPROVED |

### 6. CONCLUSION & RECOMMENDATION
`BATTERY_PROVENANCE_STATUS = DISCREPANCY_IDENTIFIED`.
The $10\%$ SOC floor proposal is REJECTED. The synthetic fixture generator MUST use $SOC_{\text{min}} = 20\%$ ($40\text{ kWh}$) to maintain strict consistency with `battery.yaml` and MILP solver constraints.
