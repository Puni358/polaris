# Itemized Correction Register

| Issue | Previous Ambiguity | Corrected Classification | Governance Rationale |
| :--- | :--- | :--- | :--- |
| Schema Impact | `SCHEMA_IMPACT = NONE_REQUIRED` | `OPTION_B_DIRECT_INTERFACE_SCHEMA_CHANGE = NONE_REQUIRED`<br>`BROADER_GAP19_SCHEMA_EXTENSION = OPEN` | Distinguishes Python optimizer interface compliance from broader governed Option-D/GAP19 schema requirements. |
| Critical Demand | Silent total demand fallback | `CRITICAL_DEMAND_EXPLICIT_INPUT = REQUIRED_FOR_GOVERNED_TEST`<br>`CRITICAL_DEMAND_FALLBACK = IMPLEMENTATION_ONLY`<br>`TOTAL_DEMAND_EQUALS_CRITICAL_DEMAND = NOT_ESTABLISHED` | Prevents runner integration from relying silently on total demand as critical load. |
| Test Terminology | "RUNTIME-TESTED" | `OPTION_B_UNIT_TESTS = PASS`<br>`OPTION_B_INTEGRATED_RUNTIME_TEST = NOT_EXECUTED` | Clarifies that only isolated unit/smoke tests have executed. |
| Selection vs Integration | Equating selection branch to integration | `OPTION_B_SELECTION_PATH = IMPLEMENTED`<br>≠ `ECD_INTEGRATION = IMPLEMENTED` | Adding `"highs_native"` selection branch does not equal full EMS/Option-D integration. |
