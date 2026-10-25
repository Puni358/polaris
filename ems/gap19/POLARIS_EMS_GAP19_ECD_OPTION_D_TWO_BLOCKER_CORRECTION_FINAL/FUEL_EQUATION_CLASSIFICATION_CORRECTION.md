# Fuel Consumption Equation Classification Correction

## Physical Fuel Consumption vs Objective Penalties

The forensic audit of source code (`configs["diesel"].yaml` & `system/optimization/implementations/milp.py`) requires strict separation between physical fuel consumption and MILP objective penalties.

### 1. Objective Startup Penalty vs Physical Fuel:
- In MILP optimization (`milp.py`), startup cost $c_{	ext{start}} 	imes v_{	ext{start}} = \$15$ is an **objective function penalty** ($J3$).
- It represents monetary/maintenance startup penalty, **NOT** physical liters removed from the fuel tank.
- In synthetic config (`configs["diesel"]`), `physical_startup_fuel_l = 0.0 L`.

### 2. Physical Fuel Consumption Model (Future Implementation):
For a 1-hour timestep interval ($\Delta t = 1.0	ext{h}$):

$$\text{fuel\_consumed}_k = \left[ F_{\text{base}} \times \mathbb{I}(P_{\text{diesel},k} > 0) + F_{\text{marg}} \times P_{\text{diesel},k} \right] \times 1.0\text{h}$$

- $F_{\text{base}} = 5.0\text{ L/h}$ (`base_fuel_consumption_l_per_h`)
- $F_{\text{marg}} = 0.00025\text{ L/Wh}$ (`marginal_fuel_consumption_l_per_wh`)
- $P_{\text{diesel},k} = \text{dispatch\_plan.diesel\_power}[0]$ ($W$)

Do **NOT** introduce a nonzero physical startup fuel term or treat the $\$15$ objective penalty as physical fuel liters.
