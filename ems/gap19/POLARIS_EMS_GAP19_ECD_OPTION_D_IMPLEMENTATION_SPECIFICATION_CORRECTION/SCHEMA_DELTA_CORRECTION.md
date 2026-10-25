# Schema Delta Specification Correction

## Re-Audit of Proposed Schema Extensions

The previous specification proposed extensions to `StationState` and `DispatchPlan`. 

### Mandatory Removal of Policy Override Fields
`ebr_target_wh_override` and `terminal_target_wh_override` (which exist as optional attributes in `StationState`) must **NOT** become runtime policy override mechanisms for Option D or ECD. They are hereby explicitly excluded from the Option D / ECD implementation specification.

### Field-by-Field Re-Evaluation

| Field Name | Target Schema | Why Proposed | Producer | Consumer | Can Existing Data Be Used? | Governance Status | Final Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `operating_mode` | `StationState` | Persist mode | Router | Runner | Already exists (`operating_mode="NORMAL"`) | `IMPLEMENTED_AND_VERIFIED` | `NOT_REQUIRED` (Already exists) |
| `emergency_assessment_json` | `StationState` | Pass telemetry | Router | Telemetry | Can be passed via runtime dict | `GOVERNED_AND_ESTABLISHED` | `PARTIALLY_REQUIRED` (Optional dict) |
| `operating_mode` | `DispatchPlan` | Record mode | Router | Evaluator | Optional parameter in `__init__` | `GOVERNED_AND_ESTABLISHED` | `PARTIALLY_REQUIRED` |
| `option_d_active` | `DispatchPlan` | Track fallback | Router | Evaluator | Derived from `operating_mode` | `GOVERNED_AND_ESTABLISHED` | `NOT_REQUIRED` (Redundant) |

---

## Verdict
`SCHEMA_DELTA = PARTIALLY_REQUIRED`. No new fields are required for `StationState` (`operating_mode` already exists). `DispatchPlan` metadata can be passed cleanly without breaking schema compatibility.
