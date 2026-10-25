# UNKNOWN_INVALID Governance Provenance

Review of sealed governance artifacts (DEC-004, Option-D resolution, D1-D6 resolutions):

- **Governance Finding**: Sealed governance established `UNKNOWN_INVALID` as an upstream ECD state triggering a safe-state response, but did not define an explicit numerical penalty or zero-dispatch DispatchPlan schema fallback inside the MILP optimizer class.
- **Classification**: `IMPLEMENTATION_ONLY_NOT_GOVERNED`.
- **Provenances Preserved**:
  - `UNKNOWN_INVALID` state = ESTABLISHED
  - `FaultEvent` = ESTABLISHED
  - `GOVERNED_FAIL_CLOSED` severity = NOT_ESTABLISHED
  - `CONSERVATIVE_SAFE_STATE` = NOT_ESTABLISHED
  - `ECD downstream consumer` = NOT_ESTABLISHED
  - `UNKNOWN_INVALID` operational action = NOT_ESTABLISHED
