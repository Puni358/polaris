# 365D PRE-REGISTERED EXPERIMENTAL METRICS & REPORTING MATRIX

## Primary Performance Metrics (per Matrix Cell)
1. **Total Diesel Fuel Consumed ($F_{\text{total}}$)**: Total cumulative fuel ($L$) integrated across 8,784 cycles under Scenario Fuel-1.
2. **Absolute Fuel Difference ($\Delta F$)**:
   $$\Delta F = F_{\text{POLARIS}} - F_{\text{Baseline}} \quad [\text{Liters}]$$
3. **Percentage Fuel Difference ($\% \Delta F$)**:
   $$\% \Delta F = \frac{F_{\text{POLARIS}} - F_{\text{Baseline}}}{F_{\text{Baseline}}} \times 100\%$$

> [!IMPORTANT]
> Fuel difference metrics must be computed separately for Mode 1 (Control Isolation) and Mode 2 (Complete System). The term **"Diesel Fuel Saving"** may ONLY be used if $\Delta F < 0$ and all integrity metrics pass.

## Secondary Operational Metrics
- Diesel Generator Runtime Hours ($h$)
- Diesel Generator Starts (off-to-on count)
- Diesel Electrical Energy Generated ($kWh$)
- Solar Energy Generated & Used ($kWh$)
- Wind Energy Generated & Used ($kWh$)
- Renewable Curtailment Energy ($kWh$)
- Battery Charge & Discharge Energy ($kWh$)
- Battery SOC Minimum, Maximum, and Average (%)
- Critical Load Unmet Energy ($kWh$) — MUST BE EXACTLY 0.0 kWh
- Total Unmet Load ($kWh$)
- ECD Emergency Events & Option D Activations (count)
- Governed Constraint Relaxation Events (count)

## Mandatory Integrity Metrics (Quality Gates)
- Future-Truth Access Violation Count (Target: 0)
- State Reset Count (Target: 0)
- Timestamp Monotonicity Violations (Target: 0)
- Bus-Bar Power Balance Conservation Error (Target: $< 10^{-4}\text{ W}$)
- Infeasible Solve Count (Target: 0)
- Invalid Dispatch Count (Target: 0)
- Twin Advancement on Infeasible State Count (Target: 0)
- First-Action-Only Compliance (Target: 100%)
- Bitwise Reproducibility Verification (Target: 100% Identical)
