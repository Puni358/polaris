# POLARIS EMS — HD-05 BATTERY DEGRADATION SOURCE MAP

**Audit Date**: 2026-09-22  
**Scope**: Code & Configuration Evidence Mapping for Battery Degradation Representation  

---

## 1. Primary Source Files & Symbol Inventory

| Artifact / File Path | Symbol / Parameter Name | Exact Line(s) | Value / Type | Code Description / Comment | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| [`system/config/battery.yaml`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11) | `deg_penalty_per_wh` | Line 11 | `0.00005` (float) | `# Cycling penalty` | **IMPLEMENTATION FACT** |
| [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L33) | `deg_penalty` | Line 33 | `float(bat_cfg.get("deg_penalty_per_wh", 0.00005))` | Local optimizer degradation penalty retrieval | **IMPLEMENTATION FACT** |
| [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L109) | `c[base + 4]` | Line 109 | `deg_penalty * dt * w_t` | Objective coefficient for charging power `p_chg` (`$/Wh * W * h`) | **IMPLEMENTATION FACT** |
| [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L110) | `c[base + 5]` | Line 110 | `deg_penalty * dt * w_t` | Objective coefficient for discharging power `p_dis` (`$/Wh * W * h`) | **IMPLEMENTATION FACT** |

---

## 2. Mathematical State Formulation

The degradation penalty term $J_{\text{deg}}$ implemented in [`milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py) is formulated as:

$$ J_{\text{deg}} = \sum_{t=0}^{H-1} c_{\text{deg}} \cdot \Delta t \cdot w_t \cdot \left( p_{\text{chg}}[t] + p_{\text{dis}}[t] \right) $$

where:
- $c_{\text{deg}} = \$0.00005 / \text{Wh} = \$0.05 / \text{kWh}$ (`deg_penalty_per_wh`).
- $p_{\text{chg}}[t]$ is the battery charging power decision variable at timestep $t$ [Watts].
- $p_{\text{dis}}[t]$ is the battery discharging power decision variable at timestep $t$ [Watts].
- $\Delta t = 1.0\text{ hour}$ is the timestep duration.
- $w_t = \gamma^t$ is the horizon discount weight.

---

## 3. Discrepancy & Verification Log

- **scipy.optimize.milp / HiGHS Solver**: **VERIFIED** ([`milp.py:L9`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L9)).
- **Horizon $H=24$**: **VERIFIED** ([`milp.py:L72`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L72)).
- **Coefficient $c_{\text{deg}} = \$0.00005/\text{Wh}$**: **VERIFIED** ([`battery.yaml:L11`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L11)).
- **Capacity $C_{\text{bat}} = 200\text{ kWh}$**: **VERIFIED** ([`battery.yaml:L3`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L3)).
- **Technical Minimum Floor $\text{SOC}_{\text{min\_tech}} = 20\%$**: **VERIFIED** ([`battery.yaml:L4`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L4)).
- **Discharge Efficiency $\eta_{\text{dis}} = 0.92$**: **VERIFIED** ([`battery.yaml:L7`](file:///home/punith-bs/01polaris%20%28Copy%29/system/config/battery.yaml#L7)).
