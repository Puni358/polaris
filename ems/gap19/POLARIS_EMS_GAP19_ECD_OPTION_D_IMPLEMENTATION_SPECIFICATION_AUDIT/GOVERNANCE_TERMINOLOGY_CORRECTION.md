# Governance Terminology & Distinction Corrections Audit

## Mandatory Terminology Corrections
To eliminate ambiguity between established governance contracts and un-implemented runtime software, this audit formally establishes the following distinctions:

### A. J2 / ECD Separation
- **`J2_ECD_GOVERNANCE_SEPARATION = ESTABLISHED`**: Governed policy (Decisions D1 & D3) strictly establishes that J2 represents emergency battery reserve shortfall penalty inside MPC optimization, whereas ECD is the sole Emergency Authority.
- **`J2_ECD_RUNTIME_SEPARATION = NOT_IMPLEMENTED`**: In the current runtime (`system/runtime/runner.py`), ECD is not invoked, so runtime separation layer has not yet been executed in code.

### B. MILP Infeasibility Routing
- **`MILP_INFEASIBILITY_TO_ECD = GOVERNED_TARGET_PATH`**: Governed policy (Decision D4) establishes that solver infeasibility is an input signal to ECD assessment.
- **`MILP_INFEASIBILITY_RUNTIME_ROUTING = NOT_IMPLEMENTED`**: Currently, `runner.py` handles solver infeasibility via historical zero-dispatch fault events (`GOVERNED_ZERO_DISPATCH`).

### C. Option D Emergency Fallback
- **`OPTION_D_GOVERNANCE = SELECTED_AND_SEALED`**: DEC-004 selected Option D Protected Critical-Load Fallback as official policy.
- **`OPTION_D_RUNTIME = NOT_IMPLEMENTED`**: No Option D dispatch solver or heuristic fallback exists in `system/optimization/`.

### D. UNKNOWN_INVALID Handling
- **`UNKNOWN_INVALID = DISTINCT_FROM_EMERGENCY`**: Governed policy and ECD core specify fail-closed safety boundary ($UNKNOWN\_INVALID \ne EMERGENCY$).
- **`UNKNOWN_INVALID_RUNTIME_HANDLING = NOT_ESTABLISHED`**: Current `runner.py` does not check or intercept `UNKNOWN_INVALID` return states.

### E. Synthetic Integration Status
- **`SYNTHETIC_INTEGRATION = TESTABLE_AFTER_IMPLEMENTATION`**: Synthetic integration is 100% testable once the router and Option D adapter are coded.
- **`CURRENT_SYNTHETIC_RUNTIME_INTEGRATION = NOT_IMPLEMENTED`**: Zero runtime integration exists in the current codebase.
