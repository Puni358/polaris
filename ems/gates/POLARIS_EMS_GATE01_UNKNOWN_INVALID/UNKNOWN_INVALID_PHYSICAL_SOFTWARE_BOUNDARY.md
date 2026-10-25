# POLARIS GATE-01 — PHYSICAL VS SOFTWARE BOUNDARY
## SPECIFICATION OF PHYSICAL SAFETY AND SOFTWARE CONTAINMENT BOUNDARIES

---

## 1. PROTECTED-CRITICAL SERVICE INTENT

The human decision mandates:
```yaml
PRESERVE_PROTECTED_CRITICAL_SERVICE: YES
PROTECTED_CRITICAL_SERVICE_POLICY: HUMAN_INTENT_SEALED
PHYSICAL_IMPLEMENTATION: NOT_YET_IMPLEMENTED
```

### Conceptual Protected Load Categories
In accordance with established POLARIS governance, protected-critical service encompasses:
1. **Essential Heating / Life Safety**: Thermal protection required for human survivability in extreme climates.
2. **Essential Water Treatment & Filtration**: Basic water supply and sanitation infrastructure.
3. **Emergency Communications & Telemetry**: Microgrid control room, gateway telemetry, and emergency communication links.

---

## 2. EXPLICIT PHYSICAL NON-INVENTIONS

To maintain strict architectural firewalls, the following physical engineering details are **NOT INVENTED IN THIS GOVERNANCE TASK** and must be specified by station-specific electrical engineering design:

- Generator power setpoints or minimum load thresholds ($P_{\text{diesel, min}}$).
- Battery charge/discharge setpoints or reserve limits ($SOC_{\text{reserve}}$).
- Critical load numerical power requirements ($kW$).
- Hardware interlock specifications or transfer switch topologies.
- Fuel consumption limits or fuel transfer pump setpoints.
- Physical circuit breaker schedules or load-shedding contactors.
- Hardware response timeouts or physical watchdog intervals.

---

## 3. SOFTWARE CONTAINMENT VS. PHYSICAL SAFE STATE

| Dimension | Software Level (runner.py) | Physical Level (Microgrid Hardware) |
| :--- | :--- | :--- |
| **Current Behavior** | Process loop break, `FAILED_TERMINATED` FaultEvent. | Microgrid hardware governors / protection relays. |
| **State Advancement** | `DIGITAL_TWIN_STATE_ADVANCEMENT = NO`. | Physical time advances; assets continue operating. |
| **Governance Status** | `TEMPORARY_SOFTWARE_CONTAINMENT`. | `NOT_ESTABLISHED_BY_SOFTWARE_TERMINATION`. |
| **Implementation Requirement** | Handshake API to signal fallback controller. | Dedicated physical protected-critical fallback hardware. |
