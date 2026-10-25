# POLARIS — Objective Term Contribution Audit

> **RESEARCH SCENARIO / SYNTHETIC BATTERY BOUNDARY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Annual Objective Value Breakdown

This audit quantifies the annual contribution of each objective function term in POLARIS C0 Control vs Diagnostic Counterfactuals across the 8,784-hour annual trajectory.

```yaml
OBJECTIVE_WEIGHTS:
  c_fuel_per_L: 1.00 # Standardized fuel weighting ($/L)
  c_deg_per_kWh: 0.05 # $0.05/kWh synthetic penalty
  c_start_per_event: 2.50 # Diesel start penalty ($/start)
  c_curt_per_kWh: 0.001 # Minimal curtailment penalty
```

---

## 2. Objective Function Term Contribution Table

| Objective Term | Description | C0 Control ($) | Exp A ($) | Exp B ($) | Exp D ($) |
|---|---|---:|---:|---:|---:|
| **Diesel Fuel Cost** | $1.00 \times \text{Fuel (L)}$ | $93,465.63 | $82,150.00 | $77,150.00 | $77,022.60 |
| **Battery Degradation Cost** | $0.05 \times \text{Discharge (kWh)}$ | **$40.44** | **$0.00** | **$0.00** | **$0.00** |
| **Generator Startup Cost** | $2.50 \times \text{Starts (412 vs 326)}$ | $1,030.00 | $820.00 | $815.00 | $815.00 |
| **Curtailment Penalty** | $0.001 \times \text{Curtailment (kWh)}$ | $66.19 | $34.94 | $21.47 | $21.46 |
| **TOTAL OBJECTIVE VALUE** | Combined objective cost | **$94,602.26** | **$83,004.94** | **$77,986.47** | **$77,859.06** |

---

## 3. Structural Question & Answer

> **Does the current objective encode the desired battery-vs-diesel tradeoff?**

- **Answer**: **NO.** Under the current objective formulation, the linear degradation cost term ($0.05/kWh) acts as a strict penalty on battery throughput. While $40.44 total annual degradation cost appears small, its *marginal* application at every timestep prevents the optimizer from incurring $0.05/kWh of battery wear to save $0.07–$0.10/kWh of diesel fuel during partial-load hours.
- Consequently, the current objective structurally penalizes battery dispatch, prioritizing generator runtime over battery wear.
