# Fuel State Architectural Decision

## Primary Architectural Question
Is remaining diesel fuel a physical station state variable that must advance through:
`State_k` $\to$ `Dispatch_k` $\to$ `DigitalTwin.step()` $\to$ `State_{k+1}`?

## Architectural Determination: YES

### Rationale:
1. Like battery State-of-Charge ($	ext{SOC}_k$), remaining diesel fuel $F_k$ is a primary physical depletable resource of the microgrid.
2. Evaluating ECD survivability at step $k+1$ using static initial fuel ($F_0 = 100	ext{L}$) while diesel was running at step $k$ violates physical state continuity and truth firewall rules.
3. Therefore, remaining fuel $F_{k+1}$ **MUST** advance physically inside `DigitalTwinSimulator.step()`.

---

## Required Minimum Interface
To support physical fuel state propagation without breaking schema compatibility:
- Add an optional attribute `diesel_fuel_remaining_liters: Optional[float] = None` to `StationState.__init__`.
- If `None` during initialization at $t=0$, default to `configs["diesel"]["initial_fuel_l"]`.
- `DigitalTwinSimulator.step()` calculates fuel consumed at step $k$ and assigns `diesel_fuel_remaining_liters = max(0.0, F_k - F_{\text{consumed},k})` to `State_{k+1}`.
