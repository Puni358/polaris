# FAILURE MODE MATRIX

## 1. COMPREHENSIVE FAILURE MODE & EXCEPTION MATRIX

The audit cataloged 15 potential failure conditions across data ingestion, ECD evaluation, policy generation, optimization, and state update.

| Input / Failure Condition | Expected Architectural Response | Implementation Location | Currently Implemented? | Governance Dependency |
| :--- | :--- | :--- | :--- | :--- |
| **1. Critical load missing** | Raise `ValueError` in provider | `SyntheticFixtureProvider` | NO | None |
| **2. Critical load invalid/NaN** | Fail-closed to `UNKNOWN_INVALID` | `ECD._fail_closed()` | **YES** ([ecd.py:L329](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py#L329)) | None |
| **3. Fuel state missing** | Fallback to initial default; log warning | `StationState` factory | NO | None |
| **4. Fuel state stale** | Flag `INVALID_TELEMETRY` in ECD | `ECD.evaluate()` | **YES** ([ecd.py:L257](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py#L257)) | None |
| **5. Battery SOC invalid/NaN** | Fail-closed to `UNKNOWN_INVALID` | `ECD._fail_closed()` | **YES** ([ecd.py:L256](file:///home/punith-bs/01polaris%20%28Copy%29/system/control/ecd.py#L256)) | None |
| **6. ECD returns UNKNOWN_INVALID** | Invoke `SafeStateFallbackRouter` | `runner.py` / Fallback | NO | DEC-004 D2 |
| **7. Diesel unavailable/fault** | Set $P_{\text{diesel,max}} = 0$ in bounds | `ModeConstraintSet` | NO | None |
| **8. Renewable unavailable ($0$ W)** | Busbar balance covered by battery/diesel | `milp.py` | **YES** ([milp.py:L172](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L172)) | None |
| **9. Battery at min SOC floor ($20\%$)** | Set $P_{\text{dis,max}} = 0$ in bounds | `milp.py` | **YES** ([milp.py:L35](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L35)) | None |
| **10. All resources insufficient** | D4 Proportional allocation across critical | `milp.py` | NO | DEC-004 D4 |
| **11. Generator min > critical** | D6 Diesel excess charges battery/curtails | `milp.py` | NO | DEC-004 D6 |
| **12. Battery cannot accept excess** | Curtail remaining excess generation | `milp.py` | **YES** ([milp.py:L157](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L157)) | DEC-004 D6 |
| **13. Operator escalation reached** | Emit `FaultEvent`, log UI alarm | `RuntimeSupervisor` | NO | DEC-004 D5 |
| **14. ECD returns valid again** | Recovery machine clears emergency | `RecoveryMachine` | NO | None |
| **15. Solver infeasibility (status != 0)**| Return governed zero-dispatch plan | `milp.py` | **YES** ([milp.py:L291](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py#L291)) | None |
