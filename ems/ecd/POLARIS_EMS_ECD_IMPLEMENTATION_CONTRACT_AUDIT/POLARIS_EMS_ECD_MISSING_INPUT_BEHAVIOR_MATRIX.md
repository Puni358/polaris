# POLARIS EMS — ECD MISSING INPUT BEHAVIOR MATRIX

## 1. Overview

This document specifies the exact behavioral contract for the Emergency Condition Detector (ECD) when input parameters are missing, invalid, expired, or malformed.

Crucially, **Fail-Closed DOES NOT mean automatically declaring EMERGENCY mode or shutting down the station**. Fail-Closed means emitting `operating_mode = UNKNOWN_INVALID` with `validity_status != VALID`, preventing unauthenticated or corrupted inputs from driving dispatch decisions.

---

## 2. Missing & Invalid Input Behavioral Matrix

| Missing / Invalid Input | Required Behavior | Resulting Operating Mode | Resulting Validity Status | Governance Status |
|-------------------------|------------------|--------------------------|---------------------------|-------------------|
| `T_required` missing | Fail Closed immediately. Do NOT use fallback default. | `UNKNOWN_INVALID` | `MISSING_T_REQUIRED` | `GOVERNANCE_CLOSED` |
| `T_required` <= 0 or NaN/Inf | Fail Closed. | `UNKNOWN_INVALID` | `INVALID_T_REQUIRED` | `GOVERNANCE_CLOSED` |
| `T_required` expired | Fail Closed upon expiry timestamp. | `UNKNOWN_INVALID` | `EXPIRED_T_REQUIRED` | `GOVERNANCE_CLOSED` |
| `T_required` unauthorized source | Fail Closed upon signature mismatch. | `UNKNOWN_INVALID` | `UNAUTHORIZED_T_REQUIRED` | `GOVERNANCE_CLOSED` |
| Critical Load Trajectory missing | Fail Closed (unless prototype constant load explicit flag set). | `UNKNOWN_INVALID` | `MISSING_CRITICAL_LOAD` | `ENGINEERING_DEFINITION_REQUIRED` |
| Critical Load <= 0 or NaN/Inf | Fail Closed. | `UNKNOWN_INVALID` | `INVALID_CRITICAL_LOAD` | `ENGINEERING_DEFINITION_REQUIRED` |
| Battery SOC missing / invalid | Fail Closed battery margin calculation ($T_{\text{battery}} = 0$). | `UNKNOWN_INVALID` | `INVALID_TELEMETRY` | `GOVERNANCE_CLOSED` |
| Fuel Remaining missing / invalid | Fail Closed diesel margin calculation ($T_{\text{diesel}} = 0$). | `UNKNOWN_INVALID` | `INVALID_TELEMETRY` | `GOVERNANCE_CLOSED` |
| Generator fuel model missing | Fail Closed diesel calculations ($T_{\text{diesel}} = 0$). | `UNKNOWN_INVALID` | `MISSING_CONFIG` | `GOVERNANCE_CLOSED` |
| Invalid / ambiguous units | Fail Closed upon schema validation. | `UNKNOWN_INVALID` | `INVALID_UNITS` | `GOVERNANCE_CLOSED` |

---

## 3. Key Non-Collapsing Principles

1. **NO Silent Fallbacks**: The ECD **MUST NOT** substitute default values for missing operational inputs like $T_{\text{required}}$ at runtime.
2. **NO Auto-Emergency Promotion**: Invalid data **MUST NOT** be silently converted into an `EMERGENCY` state (which could force unneeded diesel generation or load shedding).
3. **NO Auto-Shutdown**: Fail-closed signals pass to the EMS Controller, which engages safe fail-soft or conservative baseline holding policies as dictated by top-level governance.

Status: `COMPLETE`
