# Option D Minimal Interface Design

## Class Specification: `OptionDFallbackSolver` (`system/optimization/implementations/option_d.py`)

Signature: `OptionDFallbackSolver.solve(assessment: EmergencyAssessment, bundle: ForecastBundle, current_state: StationState, configs: Dict[str, Any]) -> DispatchPlan`

## Exact DEC-004 Priority Logic Implementation
1. **Serve Protected Critical Load First**: $P_{\text{critical}}(t)$ served as highest priority.
2. **Direct Renewable First**: Use available solar $P_{\text{pv}}(t)$ and wind $P_{\text{wind}}(t)$ directly for critical load.
3. **Diesel Generator Support**: Run diesel generator only when renewables < $P_{\text{critical}}(t)$.
4. **Governed Emergency Battery Rules**:
   - `preserved_resource == BATTERY`: Minimize battery discharge; rely primarily on diesel.
   - `preserved_resource == DIESEL`: Discharge usable battery energy to minimize diesel runtime.
5. **Exclude Non-Critical Load**: Shed non-critical loads ($P_{\text{noncritical}} = 0$).
6. **Proportional Allocation**: If total generation < $P_{\text{critical}}(t)$, allocate available power proportionally across protected circuits.
7. **Excess Diesel Battery Charging**: Charge battery only when diesel is already required for critical load and output > load. Diesel is NEVER started solely to charge battery.

---

## Verdict
`OPTION_D_RUNTIME_INTERFACE = PROPOSED_IMPLEMENTATION`. Follows DEC-004 rules cleanly.
