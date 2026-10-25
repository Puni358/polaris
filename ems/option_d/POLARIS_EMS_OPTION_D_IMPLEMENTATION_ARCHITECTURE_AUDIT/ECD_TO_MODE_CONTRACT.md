# ECD TO MODE CONTRACT

## 1. ECD OUTPUT TO OPERATING MODE TRANSFORMATION

The audit evaluated how `EmergencyAssessment` ([ecd.py:L183](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py#L183)) produced by `ECD.evaluate()` should be transformed into a governed runtime operating mode.

```python
@dataclass(frozen=True)
class EmergencyAssessment:
    operating_mode: OperatingMode           # NORMAL, EMERGENCY, UNKNOWN_INVALID
    battery_endurance_hours: float
    diesel_endurance_hours: float
    battery_margin_hours: float
    diesel_margin_hours: float
    preserved_resource: ResourceSelection    # BATTERY, DIESEL, TIE / BOTH, N/A
    limiting_resource: ResourceSelection     # BATTERY, DIESEL, TIE / BOTH, N/A
    tie_status: bool
    validity_status: ValidityStatus          # VALID, MISSING_T_REQUIRED, EXPIRED_T_REQUIRED, etc.
    failure_reason: Optional[str] = None
    target_horizon_hours: Optional[float] = None
```

---

## 2. SEPARATION OF ASSESSMENT EVIDENCE AND MODE DIRECTIVE

- **Rule 1**: The raw `EmergencyAssessment` MUST BE PRESERVED intact for audit logging, telemetry capture, and provenance verification.
- **Rule 2**: The Policy Layer inspects BOTH `operating_mode` AND `validity_status` to determine the active mode directive:

```text
IF validity_status != ValidityStatus.VALID:
    ModeDirective = UNKNOWN_INVALID_SAFE_STATE
ELSE IF operating_mode == OperatingMode.NORMAL:
    ModeDirective = NORMAL_EMS_OPERATION
ELSE IF operating_mode == OperatingMode.EMERGENCY:
    ModeDirective = OPTION_D_PROTECTED_FALLBACK
```

---

## 3. REQUIRED INFORMATION FLOW TO POLICY LAYER

The `OptionDPolicyLayer` requires the following fields from `EmergencyAssessment`:
1. `operating_mode` (`NORMAL`, `EMERGENCY`, `UNKNOWN_INVALID`).
2. `validity_status` (`VALID`, `MISSING_T_REQUIRED`, `INVALID_TELEMETRY`, etc.).
3. `limiting_resource` (`BATTERY`, `DIESEL`, `TIE / BOTH`, `N/A`).
4. `preserved_resource` (`BATTERY`, `DIESEL`, `TIE / BOTH`, `N/A`).
5. `target_horizon_hours` ($T_{\text{required}} = 6.0$h).

This contract preserves full forensic evidence while giving the Policy Layer exact, structured directives for constraint generation.
