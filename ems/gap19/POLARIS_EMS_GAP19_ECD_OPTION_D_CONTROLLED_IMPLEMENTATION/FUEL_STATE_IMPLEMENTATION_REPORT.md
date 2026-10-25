# POLARIS EMS GAP19 — Fuel State Implementation Report

## Technical Design & Execution

### 1. Conceptual Chain
```
initial configuration fuel (configs["diesel"]["initial_fuel_l"])
        ↓
StationState_0.diesel_fuel_remaining_liters
        ↓
committed DispatchPlan[k=0].diesel_power[0]
        ↓
DigitalTwinSimulator.step()
        ↓
physical fuel consumption (required_fuel = base_lph + marginal_lpwh * p_diesel[0])
        ↓
StationState_{k+1}.diesel_fuel_remaining_liters
        ↓
next ECD.evaluate(..., fuel_remaining_liters=...)
```

### 2. Physical Consumption Equation
For each committed 1h action ($k=0$):
$$\text{required\_fuel} = (\text{base\_fuel\_consumption\_l\_per\_h} \cdot \mathbf{1}_{\text{p\_diesel}>0} + \text{marginal\_fuel\_consumption\_l\_per\_wh} \cdot \text{p\_diesel}[0]) \cdot 1.0\,\text{h}$$

### 3. Fuel Bounds & Over-Consumption Observability
- Physical fuel non-negativity enforced via $\text{next\_fuel} = \max(0.0, \text{AVAILABLE\_FUEL} - \text{REQUIRED\_FUEL})$.
- Fuel clipping to $0.0$ is observable. Fuel shortage does not invent emergency responses or start/stop diesel automatically.
- $100\%$ compliant with Sections 5, 7, 8, 9 of governance specification.
