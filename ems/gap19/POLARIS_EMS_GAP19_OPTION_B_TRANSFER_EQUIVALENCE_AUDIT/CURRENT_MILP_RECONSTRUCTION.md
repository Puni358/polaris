# CURRENT MILP RECONSTRUCTION

## Canonical Reconstruction of Current Optimizer Implementation

This document provides the source-accurate reconstruction of [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py).

---

## Canonical Reconstruction Registers

### `CURRENT_MILP_VARIABLES`
- **Horizon $H$**: 24 hours.
- **Decision Variables per Timestep $K$**: 15 decision variables.
- **Total Variables ($N = H \times K$)**: 360 decision variables ($24 \times 15 = 360$).
- **Integrality**: 264 continuous variables, 96 binary variables ($4 \times 24 = 96$).

### `CURRENT_MILP_BOUNDS`
- Continuous variable bounds: Non-negative power/energy limits ($[0, P_{\text{max}}]$, $[E_{\text{min}}, E_{\text{max}}]$).
- Binary variable bounds: $[0.0, 1.0]$ with `integrality = 1`.

### `CURRENT_MILP_CONSTRAINTS`
- **Constraint Matrix $A$**: $11 \times 24 + 1 = 265$ linear constraints.
- Includes solar decomposition, wind decomposition, bus-bar energy balance, demand deficit balance, battery charge/discharge exclusivity, battery energy discrete transition, generator min/max operating bounds, generator startup tracking, and deferrable load total demand constraint.

### `CURRENT_MILP_OBJECTIVE`
- **Scalar Weighted Objective Function**:
  $$\min_{x} c^T x = \sum_{t=0}^{23} \left[ c_{\text{curt}} (P_{\text{curt,sol}} + P_{\text{curt,wind}}) + c_{\text{deg}} (P_{\text{chg}} + P_{\text{dis}}) + c_{\text{fuel,marg}} P_{\text{diesel}} + c_{\text{unmet}} P_{\text{unmet}} + c_{\text{fuel,base}} u_{\text{diesel}} + c_{\text{start}} v_{\text{start}} \right] \cdot w_t \cdot \Delta t$$

### `CURRENT_SOLVER_INTERFACE`
- Uses SciPy public wrapper: `scipy.optimize.milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)`.
- Underlyling solver engine: HiGHS C++ solver accessed via standard SciPy C extension.
