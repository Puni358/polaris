# POLARIS EMS — HD-05 BATTERY DEGRADATION UNIT & DIMENSIONAL AUDIT

**Audit Date**: 2026-09-22  
**Scope**: Dimensional Consistency & Stage 3 Objective Combining Audit  

---

## 1. Dimensional Analysis of Implementation Terms

### A. Current Degradation Penalty Term
- Decision Variables: $p_{\text{chg}}[t], p_{\text{dis}}[t]$ in Watts [$\text{W}$].
- Timestep: $\Delta t = 1.0\text{ hour}$ [$\text{h}$].
- Degradation Coefficient: $c_{\text{deg}} = 0.00005$ [$\$/\text{Wh}$] ($\$0.05/\text{kWh}$).
- Unit Evaluation:
  $$ \text{Units}\left(J_{\text{deg}}\right) = \left( \frac{\$}{\text{Wh}} \right) \cdot \left( \text{W} \right) \cdot \left( \text{h} \right) = \$ \quad [\text{Currency Dollars}] $$

### B. Stage 3 Diesel Fuel Objective
- Decision Variable: $p_{\text{diesel}}[t]$ in Watts [$\text{W}$], $u_{\text{diesel}}[t], v_{\text{start}}[t]$ binary flags.
- Fuel Rate Coefficients: $F_{\text{base}} = 5.0\text{ L/h}$, $F_{\text{marg}} = 0.00025\text{ L/Wh}$, $F_{\text{start}} = 6.0\text{ L}$.
- Unit Evaluation:
  $$ \text{Units}\left(J_{\text{fuel}}\right) = \text{Liters of Diesel} \quad [\text{L}] $$

---

## 2. Direct Addition Compatibility Check

$$\text{Direct Addition Check}: \qquad J_{\text{Stage3}} = J_{\text{fuel}} + J_{\text{deg}} = [\text{Liters}] + [\text{Dollars}]$$

- **Result**: **DIMENSIONALLY INVALID**. Liters of fuel $[\text{L}]$ cannot be directly added to monetary currency $[\$]$ or energy throughput $[\text{Wh}]$ without a conversion parameter.
- **Resolution Requirement**: Combining fuel consumption and battery cycling in Stage 3 requires a governed conversion parameter:
  - Monetary conversion: $\text{fuel\_cost\_per\_l} = \$2.50/\text{L}$ (converts fuel Liters to Dollars $[\$]$), OR
  - Physical exchange factor: $\lambda_{\text{fuel\_deg}}$ $[\text{L}/\text{Wh}]$ (converts battery throughput Wh to equivalent fuel Liters $[\text{L}]$).

```
UNIT_CONVERSION_REQUIREMENT = REQUIRED
```
