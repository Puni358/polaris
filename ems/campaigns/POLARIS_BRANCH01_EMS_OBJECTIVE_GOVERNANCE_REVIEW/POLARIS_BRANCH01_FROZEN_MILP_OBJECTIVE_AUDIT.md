# POLARIS Branch01 Frozen MILP Objective Source Audit Report

**Source File**: `system/optimization/implementations/milp.py`  
**Source SHA256**: `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35`  
**Optimizer Class**: `LocalMILPEnergyOptimizer`  
**Audit Mode**: READ_ONLY_SOURCE_AUDIT  

---

## 1. Verified Objective Function Coefficients

Direct inspection of `system/optimization/implementations/milp.py` lines 93–115 verifies the exact objective construction:

$$\min \sum_{t=0}^{23} \left( c_{\text{curt}} (P_{\text{curt,sol},t} + P_{\text{curt,wind},t}) \cdot w_t + c_{\text{deg}} (P_{\text{chg},t} + P_{\text{dis},t}) \cdot w_t + c_{\text{fuel,marg}} P_{\text{diesel},t} \cdot w_t + c_{\text{unmet}} P_{\text{unmet},t} + c_{\text{fuel,base}} u_{\text{diesel},t} \cdot w_t + c_{\text{start}} v_{\text{start},t} \cdot w_t \right)$$

| Objective Variable | Decision Index | Config Key | Verified Value ($/Wh) | Verified Value ($/kWh) | Weighting ($w_t$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`p_curt_sol`** | `base + 2` | `renewable_curtailment_penalty` | $0.001 | $1.00 | Weighted ($w_t = \gamma^t$) |
| **`p_curt_wind`** | `base + 3` | `renewable_curtailment_penalty` | $0.001 | $1.00 | Weighted ($w_t = \gamma^t$) |
| **`p_chg`** | `base + 4` | `deg_penalty_per_wh` | $0.00005 | $0.05 | Weighted ($w_t = \gamma^t$) |
| **`p_dis`** | `base + 5` | `deg_penalty_per_wh` | $0.00005 | $0.05 | Weighted ($w_t = \gamma^t$) |
| **`p_diesel`** | `base + 7` | `fuel_cost_per_l * marg_fuel_l_wh` | $0.000625 | $0.625 | Weighted ($w_t = \gamma^t$) |
| **`p_unmet`** | `base + 9` | `unmet_penalty_per_wh` | $10.0 | $10,000.00 | **Unweighted** ($w_t = 1.0$) |
| **`u_diesel`** | `base + 13` | `fuel_cost_per_l * base_fuel_l_h` | $12.50 / h | $12.50 / h | Weighted ($w_t = \gamma^t$) |
| **`v_start`** | `base + 14` | `startup_cost` | $15.00 / start | $15.00 / start | Weighted ($w_t = \gamma^t$) |

---

## 2. Mathematical Trade-off Ratios

1. **Unmet Load Penalty to Marginal Diesel Fuel Cost**:
   $$\frac{c_{\text{unmet}}}{c_{\text{fuel,marg}}} = \frac{\$10,000/\text{kWh}}{\$0.625/\text{kWh}} = 16,000.0$$
   *Semantic Meaning*: The optimizer is mathematically willing to spend up to 16,000 kWh of marginal diesel fuel cost ($16,000 \times \$0.625 = \$10,000$) to prevent a single kWh of unmet critical load.

2. **Unmet Load Penalty to Renewable Curtailment Penalty**:
   $$\frac{c_{\text{unmet}}}{c_{\text{curt}}} = \frac{\$10,000/\text{kWh}}{\$1.00/\text{kWh}} = 10,000.0$$

3. **Base Running Cost to Marginal Fuel Cost Equivalent**:
   $$\frac{c_{\text{fuel,base}}}{c_{\text{fuel,marg}}} = \frac{\$12.50/\text{h}}{\$0.625/\text{kWh}} = 20.0\text{ kWh equivalent / hour}$$

---

## 3. Objective Reconciliation Status

`OBJECTIVE_NUMERIC_RECONCILIATION = PASS`

The numeric values reported in previous forensic audits are 100% verified against the frozen source code `system/optimization/implementations/milp.py`.
