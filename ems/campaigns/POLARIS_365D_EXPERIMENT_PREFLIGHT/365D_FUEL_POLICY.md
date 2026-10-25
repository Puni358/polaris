# 365D DIESEL FUEL EXPERIMENT SCENARIOS & RESUPPLY POLICY

## Experimental Fuel Scenarios

### Scenario Fuel-1: Infinite-Reservoir / Cumulative Accounting (PRIMARY)
- **Design Intent**: Isolates controller fuel consumption performance from arbitrary physical tank size and resupply logistics assumptions.
- **Consumption Model**: $F_{\text{step}} = (5.0\text{ L/h} \cdot \mathbb{I}(P_{\text{diesel}} > 0) + 0.00025\text{ L/Wh} \cdot P_{\text{diesel}}) \cdot 1.0\text{ h}$.
- **Accounting Semantics**: Diesel fuel availability does NOT constrain generator dispatch. Cumulative diesel fuel consumed ($L$) is integrated continuously over all 8,784 cycles:
  $$F_{\text{cumulative}}(k+1) = F_{\text{cumulative}}(k) + F_{\text{step}}(k)$$
- **Fuel Clipping**: Zero artificial fuel clipping at 0.0 L. Tank depletion never interrupts controller dispatch.
- **Classification**: **PRIMARY ANNUAL DIESEL-CONSUMPTION EXPERIMENT**.

### Scenario Fuel-2: Synthetic Finite-Resupply Experiment (SECONDARY SENSITIVITY)
- **Design Intent**: Evaluates controller sensitivity under finite storage and resupply logistics.
- **Required Frozen Parameters**: Synthetic tank capacity ($L$), initial fuel inventory ($L$), refill trigger threshold ($L$), refill quantity ($L$), refill timing rule (before/after step).
- **Governance Status**: `GOVERNANCE/PARAMETER BLOCKED`. Parameters are NOT established in current codebase and must be formally frozen by human authorization before execution.
- **Disclaimer**: Strictly a synthetic sensitivity scenario; must NOT be claimed as real Nuolja station logistics.

### Scenario Fuel-3: Physical Station Logistics Model (FUTURE WORK)
- **Governance Status**: `PHYSICAL_STATION_RESUPPLY_MODEL = NOT_ESTABLISHED`.
- **Reasoning**: Real Nuolja station tank capacity, initial inventory, delivery batch sizes, and physical supply chain logistics are NOT ESTABLISHED. Preserved as future work.
