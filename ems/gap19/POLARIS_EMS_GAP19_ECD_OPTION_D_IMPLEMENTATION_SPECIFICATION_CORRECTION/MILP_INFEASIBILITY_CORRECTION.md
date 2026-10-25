# MILP Infeasibility Routing Correction

## Correction Details
The previous specification incorrectly asserted that if Option B native HiGHS returns `OPTIMIZATION_INFEASIBLE` while ECD evaluates `operating_mode == NORMAL`, the system executes a "Degraded Normal Fallback" optimizer.

No such "Degraded Normal Fallback" optimizer exists in the codebase or governed policy.

## Corrected Classification & Boundary

1. **Governed Requirement (Decision D4)**:
   - `MILP_INFEASIBILITY = INPUT SIGNAL TO ECD ASSESSMENT` (`GOVERNED_AND_ESTABLISHED`)

2. **Corrected Status Classifications**:
   - `MILP_INFEASIBILITY_ROUTING = GOVERNED_TARGET_PATH` (`GOVERNED_AND_ESTABLISHED`)
   - `NORMAL_AFTER_INFEASIBILITY_ACTION = NOT_ESTABLISHED` (`NOT_ESTABLISHED`)
   - `EMERGENCY_AFTER_INFEASIBILITY = FUTURE_OPTION_D_ROUTING_IF_ECD_DECLARES_EMERGENCY` (`PROPOSED_IMPLEMENTATION`)

3. **Guarantees**:
   - Do **NOT** invent a fallback optimizer.
   - Do **NOT** modify Option B native HiGHS formulation.
   - Historical zero-dispatch blackout (`GOVERNED_ZERO_DISPATCH`) remains explicitly rejected.
