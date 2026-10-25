# Option D Interface & Priority Logic Audit

## Governance Contract (DEC-004 Resolution)
DEC-004 selected **Option D (Protected Critical-Load Fallback)** as the official emergency fallback policy for POLARIS.

## Conceptual Dispatch Hierarchy for Option D
1. **Protect Critical Systems**: Serve $P_{\text{critical}}(t)$ as highest priority.
2. **Direct Renewable First**: Use available solar $P_{\text{pv}}$ and wind $P_{\text{wind}}$ directly for critical load.
3. **Diesel Generator Support**: Run diesel generator only when renewables are insufficient to cover $P_{\text{critical}}(t)$.
4. **Governed Emergency Battery Usage**: Use battery only under E3 resource preservation rules (`preserved_resource` vs `limiting_resource`).
5. **Exclude Non-Critical Load**: Non-critical load $P_{\text{noncritical}}(t)$ is shed during EMERGENCY mode.
6. **Proportional Allocation**: If total generation < $P_{\text{critical}}(t)$, allocate available power proportionally across protected sub-circuits.
7. **Authority Escalation**: Emit critical alert requesting operator / regional authority intervention.
8. **Excess Diesel Charging Rule**: If diesel is already running to serve critical load and output exceeds demand, excess diesel generation MAY charge the battery.
9. **No Diesel-Only Charging**: Diesel must **NEVER** be started solely to charge the battery in EMERGENCY mode.

---

## Required Option D Inputs & Classification

| Input Field | Source | Required for Synthetic Integration | Schema Availability | Status |
| :--- | :--- | :--- | :--- | :--- |
| `EmergencyAssessment` | ECD Core | Yes | Available via dataclass | `AVAILABLE` |
| `P_critical(t)` | Forecast / Config | Yes | Available in scenario (`actual_demand`) | `AVAILABLE` (Synthetic) |
| `P_renewable(t)` | ForecastBundle | Yes | `bundle.solar_irradiance`, etc. | `AVAILABLE` |
| `StationState` | Runtime Loop | Yes | `StationState` | `AVAILABLE` |
| `Generator Specs` | Config | Yes | `configs["diesel"].yaml` | `AVAILABLE` (Synthetic) |
| `Authority Esc. Channel` | Alert Engine | Optional for synthetic | `FaultEvent` logging | `ADDITIVE_SCHEMA_REQUIRED` |
