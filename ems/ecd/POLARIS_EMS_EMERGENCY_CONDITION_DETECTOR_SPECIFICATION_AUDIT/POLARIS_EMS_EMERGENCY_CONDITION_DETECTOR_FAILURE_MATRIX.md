# POLARIS EMS — EMERGENCY CONDITION DETECTOR FAILURE MATRIX

## 1. FAILURE MODES & GOVERNANCE CLASSIFICATION MATRIX

The table below defines the required system behavior across all failure conditions, distinguishing closed governed fail-closed behavior from unresolved failure behaviors:

| Scenario # | Failure Condition Scenario | Existing Governance | Required Classification | Rationale & Policy Reference |
| :--- | :--- | :--- | :--- | :--- |
| 1 | $T_{\text{required}}$ missing | **CLOSED** | **`FAIL_CLOSED`** | Closed HD-03 policy: zero classification issued |
| 2 | $T_{\text{required}}$ invalid ($\le 0$, NaN, Inf) | **CLOSED** | **`FAIL_CLOSED`** | Closed HD-03 structural validity policy |
| 3 | $T_{\text{required}}$ stale | **CLOSED** | **`FAIL_CLOSED`** | Closed HD-03 F-C freshness policy |
| 4 | $T_{\text{required}}$ unauthorized | **CLOSED** | **`FAIL_CLOSED`** | Closed HD-03 source authority policy |
| 5 | Critical load trajectory missing | Not yet closed | **`GOVERNANCE_REQUIRED`** | Unresolved failure behavior; requires governance decision |
| 6 | Critical trajectory too short (<72h) | Not yet closed | **`GOVERNANCE_REQUIRED`** | Unresolved coverage gap; requires governance decision |
| 7 | Battery state missing (`StationState`) | Not yet closed | **`GOVERNANCE_REQUIRED`** | Unresolved state gap; requires governance decision |
| 8 | Battery model / config missing | Not yet closed | **`GOVERNANCE_REQUIRED`** | Unresolved hardware parameter gap |
| 9 | Fuel remaining missing (`StationState`) | Not yet closed | **`GOVERNANCE_REQUIRED`** | Unresolved fuel state gap; requires governance decision |
| 10 | Generator model / config missing | Not yet closed | **`GOVERNANCE_REQUIRED`** | Unresolved generator parameter gap |
| 11 | Generator fuel curve missing | Not yet closed | **`GOVERNANCE_REQUIRED`** | Unresolved fuel consumption curve gap |
| 12 | Zero-renewable scenario evaluation error | Not yet closed | **`GOVERNANCE_REQUIRED`** | Unresolved stress calculation failure |
| 13 | Timestamps misaligned | Inspect repository | **`GOVERNANCE_REQUIRED`** | Unresolved timestamp consistency rule |
| 14 | Units inconsistent | Inspect repository | **`GOVERNANCE_REQUIRED`** | Unresolved unit enforcement rule |
| 15 | Margin tie ($M_{\text{batt}} = M_{\text{diesel}}$) | Not yet closed | **`GOVERNANCE_REQUIRED`** | Unresolved tie-breaking policy |

---

## 2. FAILURE BEHAVIOR BOUNDS & NON-OVER-EXTENSION RULE

### 2.1 Governed Fail-Closed Boundaries:
- **`FAIL_CLOSED`** is explicitly CLOSED by governance **ONLY** for $T_{\text{required}}$ failure conditions (missing, invalid, stale, unauthorized).
- When $T_{\text{required}}$ is unavailable or invalid, the detector MUST NOT issue a `NORMAL` or `EMERGENCY` classification.

### 2.2 Unresolved Failure Behaviors (`GOVERNANCE_REQUIRED`):
- For all other missing or invalid detector inputs (e.g., missing fuel state, missing load trajectory, model parameter gaps), the detector MUST NOT automatically generalize or declare `FAIL_CLOSED` or `EMERGENCY`.
- These conditions are classified as **`GOVERNANCE_REQUIRED`** until explicit repository evidence or human governance establishes their behavior.
- The detector MUST NOT silently convert:
  $$\text{unknown input} \not\to \text{EMERGENCY}$$
  $$\text{unknown input} \not\to \text{FAIL\_CLOSED}$$
- No fallback or default classification shall be invented without explicit authorization.
