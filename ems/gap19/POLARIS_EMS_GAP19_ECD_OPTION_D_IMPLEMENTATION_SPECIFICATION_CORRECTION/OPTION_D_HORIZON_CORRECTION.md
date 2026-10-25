# Option D Execution Horizon Correction

## Correction Details
The previous specification assumed that Option D fallback MUST produce a 24-step / 24-hour `DispatchPlan` schedule merely because Option B MPC does so.

Inspection of DEC-004 and system architecture confirms that no 24-hour horizon for Option D emergency fallback has been established.

## Corrected Classification & Boundary

1. **Status Classifications**:
   - `OPTION_D_HORIZON = NOT_ESTABLISHED` (`NOT_ESTABLISHED`)
   - `OPTION_D_EXECUTION_HORIZON = ENGINEERING_DESIGN_REQUIRED` (`ENGINEERING_INPUT_REQUIRED`)

2. **Engineering Considerations**:
   - Option D is an emergency fallback strategy focused on immediate critical load protection $P_{\text{critical}}(t_k)$.
   - Whether Option D solves a 1-step immediate action, a multi-step horizon, or a 24-step schedule is an open engineering design decision (`ENGINEERING_INPUT_REQUIRED`) that must not be invented by this audit.
