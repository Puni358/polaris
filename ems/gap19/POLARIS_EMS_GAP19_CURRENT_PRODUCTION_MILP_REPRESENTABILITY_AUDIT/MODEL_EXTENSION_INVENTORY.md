# MODEL EXTENSION INVENTORY

## INVENTORY OF REQUIRED MODEL EXTENSIONS FOR GAP19 GOVERNED TARGET

| Requirement | Existing Variable in `milp.py` | Can Reuse? | New Variable Required? | New Constraint Required? | Extension Status |
|---|---|---|---|---|---|
| **$J_1$ Critical Reliability** | `p_unmet` (total) | Partial | Yes ($P_{\text{unmet,crit}}$) | Yes (Critical demand balance) | `EXTENSION_REQUIRED` |
| **$J_2$ EBR Shortfall** | None | No | Yes ($24 \times s_{\text{EBR}}$) | Yes ($24 \times E + s_{\text{EBR}} \ge E_{\text{target}}$) | `EXTENSION_REQUIRED` |
| **$J_2$ Terminal Shortfall** | None | No | Yes ($1 \times s_{\text{term}}$) | Yes ($1 \times E(23) + s_{\text{term}} \ge E_{\text{term}}$) | `EXTENSION_REQUIRED` |
| **$J_3$ Diesel Fuel** | `p_diesel`, `u_diesel`, `v_start` | Yes | No | No | `FULLY_REPRESENTABLE` |
| **$J_4$ Curtailment** | `p_curt_sol`, `p_curt_wind` | Yes | No | No | `FULLY_REPRESENTABLE` |
| **5-Tier Load Structure** | `p_demand`, `p_flex` | No | Yes ($P_{\text{tier,1..5}}$) | Yes (Tiered demand balances) | `EXTENSION_REQUIRED` |
| **Option D Fallback** | `p_served`, `u_dis` | No | Yes ($\alpha(t)$, $u_{\text{crit\_only}}$) | Yes (Proportional & mode constraints) | `EXTENSION_REQUIRED` |
