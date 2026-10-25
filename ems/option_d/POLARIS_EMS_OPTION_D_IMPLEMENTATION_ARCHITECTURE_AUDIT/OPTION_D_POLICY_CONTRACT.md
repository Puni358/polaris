# OPTION D POLICY CONTRACT

## 1. OPTION D POLICY LAYER INTERFACE SPECIFICATION

The `OptionDPolicyLayer` is the central policy preprocessor component in the proposed architecture.

```python
# Conceptual Dataclass for Policy Output Constraint Set
@dataclass(frozen=True)
class ModeConstraintSet:
    mode_directive: str                     # "NORMAL", "OPTION_D_EMERGENCY", "UNKNOWN_INVALID_SAFE_STATE"
    allow_noncritical_load_service: bool    # True in NORMAL, False in OPTION_D
    battery_discharge_max_power_w: List[float] # Bound vector [H=24] for battery discharge
    force_diesel_excess_charging: bool      # Enforces D6 diesel excess battery charging
    enable_proportional_allocation: bool   # Enforces D4 proportional allocation across critical
    curtailment_allowed: bool              # True
    provenance_hash: str
```

---

## 2. POLICY CONTRACT INPUTS, OUTPUTS, AND INVARIANTS

### INPUTS
- `assessment`: `EmergencyAssessment` from ECD.
- `station_state`: `StationState` at origin $t0$.
- `forecast_bundle`: `ForecastBundle` for 24h horizon.
- `config`: Governed load configuration (`system/config/loads.yaml`).

### OUTPUTS
- `mode_constraint_set`: `ModeConstraintSet` object containing hourly upper/lower bounds and boolean policy flags for `EnergyOptimizer`.

### INVARIANTS
1. **Normal Mode Preservation**: In `NORMAL` mode, `allow_noncritical_load_service = True`, `battery_discharge_max_power_w = 50000.0` for all $t$. Normal EMS optimization is 100% preserved.
2. **Emergency Noncritical Isolation**: In `OPTION_D_EMERGENCY` or `UNKNOWN_INVALID_SAFE_STATE`, noncritical load service is prohibited (`allow_noncritical_load_service = False`), and battery discharge is bounded by hourly critical demand: $P_{\text{dis,max}}(t) = P_{\text{critical}}(t)$.
3. **Fail-Closed Routing**: If `assessment.validity_status != ValidityStatus.VALID`, `mode_directive` MUST BE set to `UNKNOWN_INVALID_SAFE_STATE`.

---

## 3. PROVENANCE & FORENSIC AUDIT TRAIL
`ModeConstraintSet` embeds a cryptographic SHA-256 hash of the input `EmergencyAssessment` and `StationState` to ensure 100% end-to-end traceability of policy enforcement.
