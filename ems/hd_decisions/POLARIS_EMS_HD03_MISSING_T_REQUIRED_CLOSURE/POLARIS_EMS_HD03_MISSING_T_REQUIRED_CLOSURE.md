# POLARIS EMS — HD-03 MISSING T_required INPUT FAIL-CLOSED FORMAL GOVERNANCE CLOSURE

## 1. FORMAL GOVERNANCE CLOSURE STATEMENT

The human stakeholder has formally decided and approved **HD-03 M-A — FAIL CLOSED** for missing $T_{\text{required}}$ input behavior in POLARIS EMS.

### Authoritative Policy Statement:
> **"If the Emergency Condition Detector cannot obtain a valid $T_{\text{required}}$, it shall fail closed and shall not issue a NORMAL or EMERGENCY survivability classification."**

---

## 2. EXACT SEMANTIC BOUNDARIES OF FAIL-CLOSED BEHAVIOR

1. **No Classification Issued**: When no valid $T_{\text{required}}$ can be produced by the resolver, the Emergency Condition Detector emits **NO** survivability classification (neither `NORMAL` nor `EMERGENCY`).
2. **Zero Substitution / Derivation**: The detector shall NOT invent a fallback horizon, forward-fill stale values, or derive $T_{\text{required}}$ from battery capacity, diesel fuel volume, generator runtimes, or MPC horizons.
3. **No Uninformed Operational Action**: `FAIL_CLOSED` means no valid survivability classification is issued. It does **NOT** automatically imply shutting down EMS, shutting down the microgrid station, forcing battery discharge, starting diesel generators, shedding loads, or triggering emergency mode, unless explicitly governed by downstream system fault handlers.
4. **Scope of Closure**: This decision closes **ONLY** the behavior when no valid $T_{\text{required}}$ exists (`HD03_MISSING_INPUT_BEHAVIOR = CLOSED_FAIL_CLOSED`). It does NOT select source precedence, freshness thresholds, validity bounds, or the numerical survival window.

---

## 3. FAIL-CLOSED TRIGGER CONDITIONS

The Emergency Condition Detector fails closed under all conditions where the resolver cannot supply a valid $T_{\text{required}}$:

1. Both configured ($T_{\text{config}}$) and operational ($T_{\text{oper}}$) values are absent.
2. Configured value is invalid and operational value is absent.
3. Operational value is invalid and configured value is absent.
4. Both configured and operational values are invalid.
5. Operational source becomes unavailable and no valid configured baseline is available.
6. Operational value is stale or invalid and no valid configured baseline is available.
7. The $T_{\text{required}}$ Resolver cannot produce a valid resolved $T_{\text{required}}$ for any other failure reason.

---

## 4. PRESERVED GOVERNANCE BASELINE

All prior POLARIS EMS governance decisions remain fully preserved and unaltered:

- **`HD03_SOURCE_MODEL = C_PLUS_A`**: Deployment configuration baseline + Authorized operational extension.
- **`HD03_DETECTOR_OWNERSHIP = CONSUMER_ONLY`**: Detector consumes resolved value only.
- **HD-01A**: `EBR = CRITICAL_LOAD_BASED_DYNAMIC`
- **HD-01B**: `N = 6 HOURS` (Fixed normal resilience window)
- **HD-02**: `E_terminal_target = E_EBR_target(H)` (Terminal target at $H=24\text{h}$)
- **HD-04**: Option A Zero-Renewable Detector Baseline ($P_{\text{solar}}=0, P_{\text{wind}}=0$)
- **HD-05**: Normal 5% diesel slack ($F_{\text{diesel}} \le 1.05 \cdot F_{\text{diesel}}^*$); emergency degradation subordination
- **Policy E3**: Dynamic resource margin preservation during emergency mode

---

## 5. AUTHORITATIVE GOVERNANCE CLASSIFICATIONS

| Governance Key | Authoritative Classification | Scope / Status |
| :--- | :--- | :--- |
| `HD03_MISSING_INPUT_BEHAVIOR` | `CLOSED_FAIL_CLOSED` | **Closed**: Detector fails closed on missing $T_{\text{required}}$ |
| `HD03_NO_VALID_T_REQUIRED_STATE` | `FAIL_CLOSED` | **Closed**: No NORMAL/EMERGENCY classification issued |
| `HD03_LAST_VALID_FALLBACK` | `NOT_ALLOWED` | **Prohibited**: Forward-filling stale data forbidden |
| `HD03_NUMERICAL_FALLBACK` | `NOT_ALLOWED` | **Prohibited**: Substituting numeric proxies forbidden |
| `HD03_EMERGENCY_ON_UNKNOWN` | `NOT_ALLOWED` | **Prohibited**: Default emergency triggering forbidden |
| `HD03_DETECTOR_OWNERSHIP` | `CONSUMER_ONLY` | Detector is consumer only |
| `HD03_NUMERICAL_VALUE` | `NOT_ESTABLISHED` | Numerical hours unresolved |
| `HD03_OVERRIDE_PRECEDENCE` | `GOVERNANCE_REQUIRED` | Precedence rule remains open |
| `HD03_CONFLICT_RULE` | `GOVERNANCE_REQUIRED` | Conflict resolution remains open |
| `HD03_VALIDITY_RULE` | `GOVERNANCE_REQUIRED` | Validity criteria remain open |
| `HD03_FRESHNESS_RULE` | `GOVERNANCE_REQUIRED` | Staleness thresholds remain open |
| `HD03_OPERATIONAL_SOURCE_AUTHORITY` | `GOVERNANCE_REQUIRED` | Operational authority remains open |
| `HD03_TIME_SEMANTICS` | `GOVERNANCE_REQUIRED` | Time semantics remain open |
| `HD03_RUNTIME_VARIABILITY` | `GOVERNANCE_REQUIRED` | Step-by-step variability remains open |
| `HD03_IMPLEMENTATION_AUTHORIZATION` | `NOT_GRANTED` | Code editing prohibited |
| `HD03_EXECUTION_AUTHORIZATION` | `NOT_GRANTED` | Simulation execution prohibited |
