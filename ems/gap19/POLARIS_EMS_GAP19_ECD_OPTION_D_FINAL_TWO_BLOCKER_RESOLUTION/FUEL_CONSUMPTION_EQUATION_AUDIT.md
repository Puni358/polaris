# Fuel Consumption Equation Audit

## Physical Fuel Consumption Model (`system/control/ecd.py` & `configs["diesel"]`)

For a 1-hour timestep interval ($\Delta t = 1.0	ext{h}$):

$$\text{fuel\_consumed}_k = \left[ F_{\text{base}} \times \mathbb{I}(\text{diesel\_running}_k) + F_{\text{marg}} \times P_{\text{diesel},k} \right] \times 1.0\text{h} + F_{\text{start}} \times \mathbb{I}(\text{diesel\_startup}_k)$$

### Parameters & Units:
- $F_{\text{base}}$ (`base_fuel_consumption_l_per_h`): Base fuel consumption rate ($L/h$, e.g., $5.0	ext{ L/h}$).
- $F_{\text{marg}}$ (`marginal_fuel_consumption_l_per_wh`): Marginal fuel rate per Wh generated ($L/Wh$, e.g., $0.00025	ext{ L/Wh}$).
- $P_{\text{diesel},k}$: Committed first-action diesel generator power output ($W$, from `dispatch_plan.diesel_power[0]`).
- $\mathbb{I}(\text{diesel\_running}_k)$: Indicator flag ($1$ if $P_{\text{diesel},k} > 0$, else $0$).
- $F_{\text{start}}$ (`physical_startup_fuel_l`): Physical fuel consumed per startup event ($L$, e.g., $0.0	ext{ L}$ synthetic baseline).
- $\mathbb{I}(\text{diesel\_startup}_k)$: Indicator flag ($1$ if $P_{\text{diesel},k} > 0$ and $P_{\text{diesel},k-1} == 0$, else $0$).

---

## Verdict
`FUEL_CONSUMPTION_MODEL = ESTABLISHED`. Uses exact physical parameters already present in `DieselParameters`.
