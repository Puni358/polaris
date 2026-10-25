# POLARIS EMS — HD-03 MISSING T_required INPUT FOCUSED GOVERNANCE AUDIT

## 1. PURPOSE & AUDIT SCOPE

This document provides a focused, decision-oriented governance audit to resolve the single open blocker:

> **"What does POLARIS do when the Emergency Condition Detector does not have a valid $T_{\text{required}}$?"**

### Architectural Boundaries Preserved:
- **`HD03_SOURCE_MODEL = C_PLUS_A`** (Option C Configured Baseline + Option A Authorized Operational Override).
- **`HD03_DETECTOR_OWNERSHIP = CONSUMER_ONLY`** (Emergency Detector consumes resolved value only; does NOT derive, invent, or self-select $T_{\text{required}}$).
- **`HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`** (Numerical survival window remains unresolved).
- **Preserved Baseline**: HD-01A, HD-01B ($N=6\text{h}$), HD-02 ($E_{\text{terminal\_target}}$), HD-04 Option A ($P_{\text{solar}}=0, P_{\text{wind}}=0$), HD-05 (5% diesel slack, emergency degradation subordination), Policy E3.

---

## 2. REPOSITORY EVIDENCE AUDIT FINDINGS

1. **Existing POLARIS Fail-Closed Patterns**: POLARIS subsystems (`branch01_forecast_engine.py`, `source_validator.py`, Stage 8.1 treatment scripts) heavily enforce a `FAIL_CLOSED` pattern. Missing, malformed, or NaN inputs raise explicit exceptions (`ModelGovernanceError` / `RuntimeError`). Silent zero-placeholders or unvalidated forward-filling are strictly forbidden (`"zero_placeholder_fallback": "FORBIDDEN_FAIL_CLOSED"`).
2. **Emergency on Unknown State**: No existing POLARIS subsystem defaults to EMERGENCY mode upon encountering missing data.
3. **Last Known Good / Stale Fallback**: POLARIS governance explicitly forbids unvalidated stale data forward-filling without explicit authorization.
4. **Governed Numerical Fallback**: No default numerical fallback horizon currently exists in POLARIS for $T_{\text{required}}$. Arbitrary substitutions ($6\text{h}$, $24\text{h}$, $30\text{d}$, $2\text{h}$, $15\text{m}$, $6.67\text{h}$) remain strictly prohibited.

---

## 3. POLICY OPTIONS EVALUATION & CLASSIFICATIONS

- **Option M1 (Fail Closed / Block Decision)**: Supported by existing POLARIS software architecture (`SUPPORTED_BY_EXISTING_GOVERNANCE`). Produces an explicit fault/status, blocks ungrounded survivability claims, requires no numerical fallback.
- **Option M2 (Declare Emergency)**: Conservative regarding critical service (`NOT_ESTABLISHED`). Avoids numerical fallbacks, but introduces automatic mode triggering not currently defined in code.
- **Option M3 (Use Last Valid $T_{\text{required}}$)**: `CONFLICTS_WITH_GOVERNANCE` unless governed by an explicit freshness/TTL policy. POLARIS strictly forbids unvalidated stale forward-filling.
- **Option M4 (Governed Fallback Value)**: `NOT_ESTABLISHED`. Requires an explicit human decision on a numerical fallback value.

---

## 4. AUTHORITATIVE GOVERNANCE CLASSIFICATIONS

```
HD03_MISSING_INPUT_BEHAVIOR        = GOVERNANCE_REQUIRED
HD03_NO_VALID_T_REQUIRED_STATE    = GOVERNANCE_REQUIRED
HD03_LAST_VALID_FALLBACK           = NOT_ESTABLISHED
HD03_EMERGENCY_ON_UNKNOWN          = NOT_ESTABLISHED
HD03_FAIL_CLOSED_PATTERN           = ESTABLISHED
HD03_NUMERICAL_FALLBACK            = NOT_ESTABLISHED

HD03_IMPLEMENTATION_AUTHORIZATION  = NOT_GRANTED
HD03_EXECUTION_AUTHORIZATION       = NOT_GRANTED
```

---

## 5. EXACT HUMAN DECISION REQUIRED

`EXACT_HUMAN_DECISION_REQUIRED = The human stakeholder must select whether the Emergency Condition Detector fails closed (M-A), declares emergency mode (M-B), uses the last valid T_required (M-C), or uses a separately governed numerical fallback (M-D) when no valid T_required is available.`
