# EMS Control Router Minimal Interface Design

## 1. Responsibilities & Non-Responsibilities

### Responsibilities:
1. Consume `EmergencyAssessment` output from `EmergencyConditionDetector`.
2. Determine which existing control path is eligible based strictly on `operating_mode`.
3. Route `OperatingMode.NORMAL` toward Option B native HiGHS optimizer.
4. Route `OperatingMode.EMERGENCY` toward Option D fallback solver.
5. Intercept `OperatingMode.UNKNOWN_INVALID` and prevent silent solver execution.

### Non-Responsibilities (PROHIBITED):
- Does **NOT** calculate survivability.
- Does **NOT** alter ECD assessment results.
- Does **NOT** optimize energy dispatch.
- Does **NOT** modify $J1 	o J2 	o J3 	o J4$ objective priorities.
- Does **NOT** decide emergency state.
- Does **NOT** declare emergency from $s_{J2} > 0$.
- Does **NOT** declare normal mode from solver success.
- Does **NOT** decide emergency return policy.

---

## 2. Minimal State Routing Table

| ECD Mode | Validity Status | Router Action | Target Path | Output Object | Final Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `NORMAL` | `VALID` | Invoke Option B HiGHS | `gap19_highs_native.py` | `DispatchPlan` (Option B) | `PROPOSED_DESIGN` |
| `EMERGENCY` | `VALID` | Invoke Option D Fallback | `option_d.py` | `DispatchPlan` (Option D) | `PROPOSED_DESIGN` |
| `UNKNOWN_INVALID` | `INVALID_*` | Intercept Path | `UNKNOWN_INVALID_ROUTE` | None (Action `NOT_ESTABLISHED`) | `NOT_ESTABLISHED` |
