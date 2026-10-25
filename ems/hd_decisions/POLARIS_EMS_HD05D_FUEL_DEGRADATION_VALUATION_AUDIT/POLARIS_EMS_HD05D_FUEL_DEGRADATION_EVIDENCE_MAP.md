# POLARIS EMS — HD-05D Source Evidence Map

**Audit Target**: Traceability of all parameters, files, equations, and governance artifacts related to fuel and battery degradation valuation.

---

## 1. Traceability Matrix

| Element | File Path | Line Range | Variable / Key Name | Exact Repository Value | Evidence Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Battery Degradation Penalty** | [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11) | L11 | `deg_penalty_per_wh` | `0.00005` ($\$0.00005/\text{Wh}$) | `PROTOTYPE_ASSUMPTION` / `# Cycling penalty` |
| **Battery Degradation Retrieval** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L33) | L33 | `deg_penalty` | `float(bat_cfg.get("deg_penalty_per_wh", 0.00005))` | `IMPLEMENTATION_FACT` |
| **Charge Objective Term** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L109) | L109 | `c[base + 4]` | `deg_penalty * dt * w_t` | `IMPLEMENTATION_FACT` |
| **Discharge Objective Term** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L110) | L110 | `c[base + 5]` | `deg_penalty * dt * w_t` | `IMPLEMENTATION_FACT` |
| **Fuel Price** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L7) | L7 | `fuel_cost_per_l` | `2.50` ($\$2.50/\text{L}$) | `PROTOTYPE_ASSUMPTION` |
| **Marginal Fuel Consumption** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L6) | L6 | `marginal_fuel_consumption_l_per_wh` | `0.00025` ($0.25\text{ L/kWh}$) | `IMPLEMENTATION_FACT` (Technical Generator curve) |
| **Base Fuel Consumption** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L5) | L5 | `base_fuel_consumption_l_per_h` | `5.0` ($5.0\text{ L/h}$) | `IMPLEMENTATION_FACT` (Technical Generator curve) |
| **Generator Startup Cost** | [`system/config/diesel.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/diesel.yaml#L8) | L8 | `startup_cost` | `15.0` ($\$15.0$) | `IMPLEMENTATION_FACT` |
| **Marginal Diesel Objective** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L111) | L111 | `c[base + 7]` | `fuel_cost_per_l * marg_fuel_l_wh * dt * w_t` | `IMPLEMENTATION_FACT` |
| **Base Diesel Objective** | [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L113) | L113 | `c[base + 13]` | `fuel_cost_per_l * base_fuel_l_h * dt * w_t` | `IMPLEMENTATION_FACT` |

---

## 2. Global Evidence Absence Log

The repository was searched for the following concepts. None were found:

- **Battery Replacement Cost**: `ABSENT`
- **Battery Capital Cost / Depreciation**: `ABSENT`
- **Levelized Cost of Storage (LCOS)**: `ABSENT`
- **Manufacturer Warranty / Cycle Limit**: `ABSENT`
- **Station Diesel Procurement Contract**: `ABSENT`
- **Stakeholder Authorization of Fuel Valuation**: `ABSENT`
- **Stakeholder Authorization of $c_{\text{deg}}$**: `ABSENT`
