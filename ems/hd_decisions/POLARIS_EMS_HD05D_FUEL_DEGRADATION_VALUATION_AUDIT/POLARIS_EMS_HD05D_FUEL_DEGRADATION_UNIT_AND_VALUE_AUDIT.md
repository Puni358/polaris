# POLARIS EMS — HD-05D Unit and Valuation Audit

**Audit Objective**: Inspect dimensional consistency and valuation metrics of fuel and battery degradation in POLARIS.

---

## 1. Dimensional Unit Analysis

### 1.1 Physical Units
- **Battery Charging / Discharging Power**: $P_{\text{chg}}[t], P_{\text{dis}}[t] \ [\text{W}]$
- **Timestep**: $\Delta t = 1.0 \ [\text{h}]$
- **Battery Energy Throughput**: $(P_{\text{chg}}[t] + P_{\text{dis}}[t]) \Delta t \ [\text{Wh}]$
- **Diesel Output Power**: $P_{\text{diesel}}[t] \ [\text{W}]$
- **Diesel Operating Commitment**: $u_{\text{diesel}}[t] \in \{0, 1\}$
- **Diesel Fuel Consumption**: 
  $$\text{Fuel}[t] = \left( \text{base\_fuel\_l\_h} \cdot u_{\text{diesel}}[t] + \text{marg\_fuel\_l\_wh} \cdot P_{\text{diesel}}[t] \right) \Delta t \ [\text{L}]$$

### 1.2 Objective Term Dimensionality in Current Prototype (`milp.py`)
- **Degradation Term ($J_{\text{deg}}$)**:
  $$J_{\text{deg}} = c_{\text{deg}} \cdot (P_{\text{chg}} + P_{\text{dis}}) \Delta t = \left[ \frac{\$}{\text{Wh}} \right] \cdot [\text{W}] \cdot [\text{h}] = [\$]$$
- **Fuel Term ($J_{\text{fuel}}$)**:
  $$J_{\text{fuel}} = \text{fuel\_cost\_per\_l} \cdot \text{Fuel}[t] = \left[ \frac{\$}{\text{L}} \right] \cdot [\text{L}] = [\$]$$

### 1.3 Dimensional Conclusion
The scalar MILP objective in `milp.py` achieves dimensional consistency **only by converting both fuel and battery throughput into dollars ($)** using prototype parameters:
- Fuel conversion factor: $\$2.50/\text{L}$
- Battery throughput conversion factor: $\$0.00005/\text{Wh}$

Direct physical addition of fuel liters and battery energy throughput:
$$J_{\text{physical}} = \text{Fuel} \ [\text{L}] + \text{Throughput} \ [\text{Wh}]$$
is **dimensionally invalid** without an explicit physical exchange coefficient $\lambda_{\text{deg}} \ [\text{L/\text{Wh}}]$.

---

## 2. Numerical Tradeoff Implied by Current Implementation

If the current MILP solver decides whether to supply $1 \ \text{kWh}$ of energy from marginal diesel generation versus cycling $1 \ \text{kWh}$ through the battery:

- **Marginal Diesel Cost**:
  $$c_{\text{diesel\_marginal}} = \$2.50/\text{L} \times 0.00025 \ \text{L}/\text{Wh} = \$0.000625/\text{Wh} = \$0.625/\text{kWh}$$
- **Battery Cycling Cost**:
  $$c_{\text{deg}} = \$0.00005/\text{Wh} = \$0.05/\text{kWh}$$
- **Implied Exchange Ratio**:
  $$\frac{c_{\text{diesel\_marginal}}}{c_{\text{deg}}} = \frac{0.000625}{0.00005} = 12.5$$

This implies that in the current implementation, **$1\text{ kWh}$ of marginal diesel power is penalized $12.5 \times$ more heavily than $1\text{ kWh}$ of battery throughput**.

However, because both $\$2.50/\text{L}$ and $\$0.00005/\text{Wh}$ are labeled `PROTOTYPE_ASSUMPTION` in the configuration files, **this $12.5\times$ numerical weighting has no scientific or governance standing**.
