# POLARIS EMS — HD-03 VALIDITY & FRESHNESS DECISION TABLE

## 1. COMPACT CANDIDATE DECISION TABLE

| Candidate | Repository Evidence | Technically Compatible | Governance Status |
| :--- | :--- | :--- | :--- |
| **V-A Basic Structural Validity** | `FAIL_CLOSED` pattern rejects NaN/Inf/missing values. Structurally requires finite positive number ($T_{\text{required}} > 0$). | Yes | `SUPPORTED_BY_ARCHITECTURE` (Can be adopted immediately) |
| **V-B Bounded Validity** | No upper bound ($T_{\text{max}}$) exists in repository code or governance records. | Yes (If bound selected) | `GOVERNANCE_REQUIRED` (Requires human policy upper bound) |
| **V-C Schema Validity** | Additive schema parameters (`config_version`, payload signature) supported by general design. | Yes | `SUPPORTED_BY_FUTURE_ARCHITECTURE` (Requires additive schema) |
| **F-A Fixed TTL** | No numeric TTL (seconds/hours) exists in repository for $T_{\text{required}}$. | Yes | `GOVERNANCE_REQUIRED` (Requires selecting numerical TTL) |
| **F-B Explicit Expiry** | No `valid_until` ISO timestamp field exists in current payload specifications. | Yes | `GOVERNANCE_REQUIRED` (Requires adding payload timestamp field) |
| **F-C Both (TTL + Expiry)** | Combines fixed TTL guard with payload `valid_until` expiration. | Yes | `SUPPORTED_BY_FUTURE_ARCHITECTURE` (Recommended complete design) |
| **F-D No Freshness** | Allows stale operational overrides to persist indefinitely. | No | `CONFLICTS_WITH_GOVERNANCE` (Unsafe for operational overrides) |

---

## 2. EXACT HUMAN DECISIONS REQUIRED FOR CLOSURE

1. **Validity Rule Selection**:
   - Approve **V-A (Basic Structural Validity)** ($T_{\text{required}} > 0$, finite float, non-NaN/Inf).
   - Decide whether an explicit upper bound ($T_{\text{max}}$) is required (Option V-B).
2. **Freshness Rule Selection**:
   - Select between **F-A (Fixed TTL)**, **F-B (Explicit Expiry Timestamp)**, or **F-C (Both)** for Option A operational overrides.
   - Select numerical TTL duration (if F-A or F-C selected) and clock-drift tolerance.
