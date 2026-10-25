# Critical Legacy Mode Static Audit

## 1. Questions A–I Resolution Matrix

| Question | Audit Findings & Code Evidence | Verdict |
| :--- | :--- | :--- |
| **A. Where is `UNGOVERNED_LEGACY` defined?** | It is **NOT** defined in any source file in `system/`. Search for `LEGACY` returns 0 occurrences across the codebase. | **NOT_DEFINED_IN_CODE** |
| **B. Who can select it?** | No component can select it, as it is not a valid enum or state value. | **NONE** |
| **C. Is it the default?** | No. Default `operating_mode` in `StationState` is `"NORMAL"`. | **NO** |
| **D. Can `PolarisLocalRunner` select it accidentally?** | No. `PolarisLocalRunner` uses `StationState` which defaults to `"NORMAL"`. | **NO** |
| **E. Can a normal governed Option-B call enter it?** | No. Governed calls run strictly under `"NORMAL"` or `"EMERGENCY"`. | **NO** |
| **F. Can external configuration select it?** | No. External config passed via YAML parses `"NORMAL"` or `"EMERGENCY"`. | **NO** |
| **G. Can missing inputs cause automatic transition into it?** | No. Missing governed inputs raise explicit `ValueError("MISSING_GOVERNED_INPUT...")`. | **NO** |
| **H. Does it bypass the numerical firewall?** | No legacy mode exists to bypass the numerical firewall. | **NO** |
| **I. Does it violate "Do not repurpose `demand.point`"?** | No. `demand.point` is strictly used for total station demand. | **NO** |

---

## 2. Isolation Classification

Because `UNGOVERNED_LEGACY` is not implemented in the production codebase and missing governed inputs result in explicit hard failure rather than legacy fallback:

```
LEGACY_COMPATIBILITY_ISOLATED = YES
LEGACY_MODE_AUDIT_STATUS = PASS
```
