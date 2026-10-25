# TRUTH FIREWALL

## Controller Causality & Non-Anticipative Isolation

This document defines the strict **Truth Firewall** separating controller-permissible information from future ground truth.

---

## Causal Information Scope

```mermaid
graph TD
    subgraph "Controller Permissible Information (Step t)"
        A["Current State SOC(t), V_fuel(t)"]
        B["Causal Telemetry History t' <= t"]
        C["Governed Forecast Bundle Forecast(t:t+H)"]
        D["Governed Baseline T_required = 6.0h"]
    end
    
    subgraph "Future Actual Truth (FORBIDDEN to Controller)"
        E["Future Actual Solar Generation P_solar(t+k)"]
        F["Future Actual Wind Generation P_wind(t+k)"]
        G["Future Actual Load Realizations Demand(t+k)"]
    end
    
    A --> H["EnergyOptimizer & ECD"]
    B --> H
    C --> H
    D --> H
    
    E -- FORBIDDEN --> H
    F -- FORBIDDEN --> H
    G -- FORBIDDEN --> H
    
    E --> I["Digital Twin Evaluation Only"]
    F --> I
    G --> I
```

---

## Enforced Firewall Rules

1. **Non-Anticipative Control**: `EnergyCrisisDetector`, `OptionDPolicyLayer`, and `EnergyOptimizer` MUST make decisions based strictly on state at step $t$ and forecasted quantities over horizon $H$.
2. **Evaluation Separation**: Future ground truth trajectories (actual solar, actual wind, actual demand) are consumed **only** by `system/simulation/simulator.py` to evaluate closed-loop dispatch performance.
3. **No Clairvoyance**: Optimization models must NOT inspect future environment steps to retroactively adjust $t=0$ dispatch setpoints.
