# GAP19 TARGET OBJECTIVE MAPPING

## Formal Mapping of Stages 1–4 to Native HiGHS Objectives

This document maps the governed GAP19 multi-stage objective hierarchy onto native `highspy` / HiGHS C++ objective structures.

---

## Stage-by-Stage Mapping Specification

### STAGE 1: Critical Reliability ($J_1$)
- **Mathematical Definition**: $J_1 = \sum_{t=0}^{H-1} P_{\text{unmet,critical}}(t) \Delta t$
- **Physical Unit**: Watt-hours ($\text{Wh}$)
- **Target Value**: $J_1^* = 0.0\text{ Wh}$ (when physically feasible)
- **`HighsLinearObjective` Construction**:
  ```python
  obj1 = highspy.HighsLinearObjective()
  # Coefficient vector has 1.0 * dt at p_unmet index for each timestep t
  c1 = np.zeros(num_vars)
  for t in range(H):
      c1[t * K + 9] = 1.0 * dt  # p_unmet
  obj1.coefficients = c1
  obj1.priority = 1
  obj1.weight = 1.0
  obj1.abs_tolerance = 0.0
  obj1.rel_tolerance = 0.0
  ```

### STAGE 2: Emergency Battery Reserve / Terminal Reserve ($J_2$)
- **Mathematical Definition**: $J_2 = \sum_{t=0}^{H-1} s_{\text{EBR}}(t) + s_{\text{term}}$
- **Physical Unit**: Watt-hours ($\text{Wh}$)
- **Target Value**: Minimized reserve shortfall below governed EBR / terminal thresholds.
- **`HighsLinearObjective` Construction**:
  ```python
  obj2 = highspy.HighsLinearObjective()
  # Coefficient vector has 1.0 at slack variable indices s_EBR(t) and s_term
  c2 = np.zeros(num_vars_extended)
  for t in range(H):
      c2[idx_s_ebr[t]] = 1.0
  c2[idx_s_term] = 1.0
  obj2.coefficients = c2
  obj2.priority = 2
  obj2.weight = 1.0
  obj2.abs_tolerance = 0.0
  obj2.rel_tolerance = 0.0
  ```

### STAGE 3: Governed Diesel Fuel Consumption ($J_3$)
- **Mathematical Definition**: $J_3 = \sum_{t=0}^{H-1} \left[ F_{\text{base}} u_{\text{diesel}}(t) + F_{\text{marg}} P_{\text{diesel}}(t) \right] \Delta t + F_{\text{start}} v_{\text{start}}(t)$
- **Physical Unit**: Liters ($\text{L}$)
- **Target Value**: Minimized fuel consumption in Liters.
- **`HighsLinearObjective` Construction**:
  ```python
  obj3 = highspy.HighsLinearObjective()
  c3 = np.zeros(num_vars)
  for t in range(H):
      base = t * K
      c3[base + 7] = marg_fuel_l_wh * dt    # p_diesel (L/Wh * W * h = L)
      c3[base + 13] = base_fuel_l_h * dt     # u_diesel (L/h * h = L)
      c3[base + 14] = start_fuel_l           # v_start (L per start)
  obj3.coefficients = c3
  obj3.priority = 3
  obj3.weight = 1.0
  obj3.abs_tolerance = 0.0
  obj3.rel_tolerance = 0.0
  ```

### STAGE 4: Avoidable Renewable Curtailment ($J_4$)
- **Mathematical Definition**: $J_4 = \sum_{t=0}^{H-1} \left( P_{\text{curt,sol}}(t) + P_{\text{curt,wind}}(t) \right) \Delta t$
- **Physical Unit**: Watt-hours ($\text{Wh}$)
- **Target Value**: Minimized renewable energy curtailment.
- **`HighsLinearObjective` Construction**:
  ```python
  obj4 = highspy.HighsLinearObjective()
  c4 = np.zeros(num_vars)
  for t in range(H):
      base = t * K
      c4[base + 2] = 1.0 * dt  # p_curt_sol (W * h = Wh)
      c4[base + 3] = 1.0 * dt  # p_curt_wind (W * h = Wh)
  obj4.coefficients = c4
  obj4.priority = 4
  obj4.weight = 1.0
  obj4.abs_tolerance = 0.0
  obj4.rel_tolerance = 0.0
  ```
