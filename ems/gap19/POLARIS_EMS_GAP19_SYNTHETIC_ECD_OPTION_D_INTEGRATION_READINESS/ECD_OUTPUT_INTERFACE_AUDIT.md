# ECD Output Interface Audit

## Audit of `EmergencyAssessment` Dataclass (`system/control/ecd.py`)

The `EmergencyAssessment` dataclass is the immutable canonical output of ECD evaluation:

```python
@dataclass(frozen=True)
class EmergencyAssessment:
    operating_mode: OperatingMode              # NORMAL / EMERGENCY / UNKNOWN_INVALID
    battery_endurance_hours: float            # t_battery (hours)
    diesel_endurance_hours: float             # t_diesel (hours)
    battery_margin_hours: float               # m_battery = t_battery - t_target
    diesel_margin_hours: float                # m_diesel = t_diesel - t_target
    preserved_resource: ResourceSelection     # BATTERY / DIESEL / BOTH / NONE
    limiting_resource: ResourceSelection      # BATTERY / DIESEL / BOTH / NONE
    tie_status: bool                          # True if abs(m_battery - m_diesel) <= epsilon
    validity_status: ValidityStatus           # VALID / MISSING_T_REQUIRED / INVALID_...
    failure_reason: Optional[str] = None      # Text diagnostic on failure
    target_horizon_hours: Optional[float] = None # t_target (hours)
```

### Classification of Output Fields

| Attribute | Classification | Description & Semantics |
| :--- | :--- | :--- |
| `operating_mode` | `IMPLEMENTED_OUTPUT` | Primary state flag for EMS router (`NORMAL`, `EMERGENCY`, `UNKNOWN_INVALID`). |
| `battery_endurance_hours` | `IMPLEMENTED_OUTPUT` | Physical battery endurance time $t_{\text{battery}}$ based on usable AC Wh. |
| `diesel_endurance_hours` | `IMPLEMENTED_OUTPUT` | Physical diesel generator fuel endurance time $t_{\text{diesel}}$ based on available fuel. |
| `battery_margin_hours` | `IMPLEMENTED_OUTPUT` | Survivability margin $m_{\text{battery}} = t_{\text{battery}} - T_{\text{target}}$. |
| `diesel_margin_hours` | `IMPLEMENTED_OUTPUT` | Survivability margin $m_{\text{diesel}} = t_{\text{diesel}} - T_{\text{target}}$. |
| `preserved_resource` | `IMPLEMENTED_OUTPUT` | E3 resource preservation mandate (`BATTERY` vs `DIESEL`). |
| `limiting_resource` | `IMPLEMENTED_OUTPUT` | Resource identified as limiting microgrid endurance. |
| `tie_status` | `IMPLEMENTED_OUTPUT` | Boolean tie flag when $|m_{\text{battery}} - m_{\text{diesel}}| \le 10^{-6}	ext{h}$. |
| `validity_status` | `IMPLEMENTED_OUTPUT` | Input payload validation status enum. |
| `failure_reason` | `IMPLEMENTED_OUTPUT` | String diagnostic populated when `validity_status != VALID`. |
| `target_horizon_hours` | `IMPLEMENTED_OUTPUT` | Evaluated target horizon $T_{\text{target}}$. |

---

## Verdict
The ECD core output dataclass is fully `IMPLEMENTED_AND_UNIT_TESTED`. It provides all necessary fields for EMS policy routing.
