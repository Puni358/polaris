# J3 CANONICAL FORMULATION

## DIESEL FUEL CONSUMPTION OBJECTIVE ($J_3$)

- **Priority**: 3
- **Mathematical Form**:
  $$\min J_3(x) = \sum_{t=0}^{23} \left( F_{\text{marg}} \cdot P_{\text{diesel}}(t) + F_{\text{base}} \cdot u_{\text{diesel}}(t) + F_{\text{start}} \cdot v_{\text{start}}(t) \right) \cdot \Delta t$$
- **Units**: Liters of diesel fuel ($\text{L}$).
- **Coefficients**:
  - $F_{\text{marg}}$: Marginal fuel consumption rate ($\text{L/Wh}$).
  - $F_{\text{base}}$: Base idling fuel consumption rate ($\text{L/h}$).
  - $F_{\text{start}}$: Startup fuel consumption equivalent ($\text{L/event}$).

`J3_CANONICAL_FORMULATION` = `ESTABLISHED`
