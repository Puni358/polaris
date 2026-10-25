# Post-Governance Engineering Input Requirements

Once human governance decides policy (Formulation EBR-A..E, TR-A..E), engineering telemetry and configuration data must be provided to populate the formulation:

1. **Battery Asset Limits:** Usable capacity (Wh), nameplate capacity (Wh), C-rate power limits (W), charge/discharge efficiencies.
2. **Protected Critical Load Telemetry:** Station-specific critical load trajectory ($P_{\text{crit}}[t]$) vs total demand.
3. **Generator Fuel Curves:** Minimum operating power (W), base fuel consumption (L/h), marginal fuel consumption (L/Wh), startup fuel (L).
4. **Fuel Inventory Telemetry:** Real-time fuel tank level (L) and telemetry quality index.
5. **ECD Integration Interface:** Operating mode signal ($`NORMAL`$, $`EMERGENCY`$, $`UNKNOWN_INVALID`$).
