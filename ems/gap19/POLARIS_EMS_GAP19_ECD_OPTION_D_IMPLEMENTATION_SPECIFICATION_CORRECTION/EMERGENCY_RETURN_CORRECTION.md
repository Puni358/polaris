# Emergency → Normal Return Policy Correction

## Correction Details
The previous specification package contained an internal contradiction by claiming `EMERGENCY_RETURN_POLICY = NOT_ESTABLISHED` while simultaneously asserting `EMERGENCY_RETURN_INTERFACE = SPECIFIED`.

## Corrected Classification & Boundary

1. **Policy Status**:
   - `EMERGENCY_RETURN_POLICY = NOT_ESTABLISHED` (`GOVERNANCE_REQUIRED`)
   - `EMERGENCY_RETURN_RUNTIME_BEHAVIOR = NOT_IMPLEMENTED` (`NOT_ESTABLISHED`)
   - `EMERGENCY_RETURN_INTERFACE = BOUNDARY_IDENTIFIED_ONLY` (`ENGINEERING_INTERFACE_ONLY`)

2. **Prohibited Un-Governed Mechanisms**:
   The specification must **NOT** introduce or claim as governed:
   - Hysteresis hours
   - Cooldown timers
   - Debounce logic
   - Recovery SOC/fuel thresholds
   - Automatic recovery windows
   - Minimum emergency durations

3. **Boundary Specification**:
   ECD naturally evaluates survivability margins at each discrete step $k$. However, no automatic `EMERGENCY` $\to$ `NORMAL` return policy is authorized for production or runtime code implementation without explicit governance authorization.
