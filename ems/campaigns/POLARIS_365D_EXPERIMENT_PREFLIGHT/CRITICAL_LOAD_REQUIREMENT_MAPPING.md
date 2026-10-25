# CRITICAL-LOAD REQUIREMENT MAPPING

## Governance Requirement to Data Source Mapping

```plain
Human Governance Requirement (DEC-004-D1 / D4)
        │
        ├── Essential Heating (P_heating,min) ──────► Data Found: NONE (MISSING)
        ├── Water Treatment (P_water,min) ──────────► Data Found: NONE (MISSING)
        └── Emergency Comms (P_comms,min) ──────────► Data Found: NONE (MISSING)
        │
        ↓
Calculability Status: NOT_REPRODUCIBLE_FROM_AVAILABLE_DATA
```

## Detailed Status Assessment

| Governance Requirement | Required Physical Data | Data Found in Artifacts | Data Missing | Can $P_{i,\text{min}}(t)$ Be Calculated? |
| :--- | :--- | :--- | :--- | :--- |
| **Essential Heating** | Thermal minimum power $[W]$ | `NONE` (Generic Abisko heat pump references only) | Installed heater ratings & $P_{\text{heating,min}}(t)$ formulation | **NO** |
| **Water Treatment** | Potable filtration power $[W]$ | `NONE` | Pump & filter wattage & duty cycle | **NO** |
| **Emergency Comms** | Continuous comms power $[W]$ | Qualitative SITES AWS telemetry mention | Nameplate telemetry power rating | **NO** |
| **Circuit Mapping** | Breaker panel schedule | `NONE` | Single-line electrical diagram | **NO** |
| **Demand Validation** | Empirical station load $[W]$ | Synthetic load generator ($15\text{--}45\text{ kW}$) | Measured continuous station demand | **NO** |

## Conclusion
Because no authoritative numerical power ratings or electrical circuit mappings exist in project artifacts or public technical disclosures, **$P_{\text{critical}}(t) = \sum P_{i,\text{min}}(t)$ cannot be calculated from available station data**.
