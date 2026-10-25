# Battery-Agnostic Parameter Envelope & Source Classification

```yaml
PHASE_ID: battery_agnostic_portability_20260930
RESEARCH_TYPE: BATTERY_AGNOSTIC_PORTABILITY_STUDY
PRODUCTION_PROMOTION: NOT_AUTHORIZED
DISCLAIMER: RESEARCH SCENARIO - NOT TARGET-HARDWARE EVIDENCE
```

## 1. Bounded Research Parameter Envelope

The parameter envelope defines lower, reference, and upper bounds across five key battery configuration dimensions for offline research testing:

| Parameter Dimension | Unit | Lower Bound | Reference (C0) | Upper Bound | Source Classification | Safety Relevance |
| :--- | :---: | ---: | ---: | ---: | :--- | :--- |
| **Nominal Energy Capacity** | kWh | 100.0 | 200.0 | 400.0 | Engineering Scenario Envelope | Performance / Dispatch |
| **Max Charge / Discharge Power**| kW | 25.0 | 50.0 | 100.0 | Engineering Scenario Envelope | **Safety-Critical Hardware Limit** |
| **Round-Trip Efficiency ($\eta_{\text{rt}}$)** | fraction | 0.8100 | 0.8464 | 0.9025 | Literature-Derived Envelope | Performance / Economic |
| **Minimum SOC Limit** | % | 10.0% | 20.0% | 30.0% | Safety-Critical Constraint | **Safety-Critical Reserve** |
| **Maximum SOC Limit** | % | 80.0% | 95.0% | 100.0% | Safety-Critical Constraint | **Safety-Critical Protection** |

---

## 2. Explicit Parameter Source Classifications

```text
Layer 1: Target-Specific Evidence         -> ABSENT for Nuolja BESS
Layer 2: External Evidence                -> Tier C Peer-Reviewed Literature (Wang, Schmalstieg, NREL)
Layer 3: Literature-Derived Parameters    -> Efficiency range (81% to 90.25%), LFP degradation exponents
Layer 4: Engineering Scenario Parameters  -> Capacity (100-400 kWh), Power (25-100 kW), SOC bounds (10-95%)
Layer 5: Synthetic Engineering Assumptions -> 200 kWh / 50 kW Fixture Proxy (real_nuolja_data: false)
```

No parameter in Layers 3, 4, or 5 is represented as target site hardware evidence.
