# Authority Escalation Interface Specification

## Governance Requirement (DEC-004)
When `operating_mode == EMERGENCY`, authority escalation is **REQUIRED**.

## Structural Event Payload Specification
Authority escalation is carried via an enriched `FaultEvent` emitted by the router:

```python
class AuthorityEscalationEvent(FaultEvent):
    def __init__(self, timestep: int, assessment: EmergencyAssessment):
        super().__init__(
            timestep=timestep,
            fault_class="EMERGENCY_AUTHORITY_ESCALATION",
            source="EMSControlRouter",
            severity="GOVERNED_EMERGENCY",
            response="OPTION_D_FALLBACK_ACTIVATED",
            state_advanced=True,
            message=(
                f"Emergency mode declared at timestep {timestep}. "
                f"Preserved resource: {assessment.preserved_resource.value}, "
                f"Limiting resource: {assessment.limiting_resource.value}, "
                f"Battery margin: {assessment.battery_margin_hours:.2f}h, "
                f"Diesel margin: {assessment.diesel_margin_hours:.2f}h."
            )
        )
```

---

## Verdict
`AUTHORITY_ESCALATION_INTERFACE = SPECIFIED`. Carried via `FaultEvent` telemetry without network transport assumptions.
