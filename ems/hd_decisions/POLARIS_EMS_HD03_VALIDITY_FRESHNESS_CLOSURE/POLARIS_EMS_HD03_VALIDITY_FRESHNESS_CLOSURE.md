# POLARIS EMS — HD-03 VALIDITY & FRESHNESS FORMAL GOVERNANCE CLOSURE

## 1. FORMAL GOVERNANCE CLOSURE STATEMENT

The human stakeholder has formally decided and approved the **HD-03 Validity & Freshness Governance Policies** for POLARIS EMS.

### Policy Decision 1 — Basic Structural Validity:
> **"An operational $T_{\text{required}}$ candidate is structurally valid if and only if it is present, numeric, finite, positive, expressed in the authorized unit, and unambiguously identified as $T_{\text{required}}$."**

$$\text{T\_required} > 0$$

Required Invalid States:
- Missing, null, or empty fields
- Non-numeric or non-finite values (`NaN`, `Inf`)
- Zero duration ($T_{\text{required}} = 0$)
- Negative values ($T_{\text{required}} < 0$)
- Unauthorized unit representation
- Ambiguous field identity

Upper bound status: `HD03_UPPER_BOUND = NOT_ESTABLISHED` (No $T_{\text{max}}$ is authorized).

### Policy Decision 2 — Freshness Model (F-C BOTH):
The operational $T_{\text{required}}$ freshness evaluation uses a dual-guard model (**F-C BOTH**):
$$\text{freshness\_valid} = \text{not\_expired(explicit\_expiry)} \;\text{AND}\; (\text{payload\_age} \le \text{governed\_max\_age})$$

Numerical TTL status: `HD03_TTL_VALUE = NOT_ESTABLISHED`.
Clock drift threshold status: `HD03_CLOCK_DRIFT_THRESHOLD = NOT_ESTABLISHED`.

---

## 2. COMPATIBILITY & BASELINE PRESERVATION

All prior POLARIS EMS governance decisions remain fully preserved and unaltered:

- **`HD03_SOURCE_MODEL = C_PLUS_A`**: Deployment config default baseline + Authorized operational extension.
- **`HD03_OVERRIDE_PRECEDENCE = CLOSED_OPERATIONAL_WINS_WHEN_VALID_AND_AUTHORIZED`**: Operational input supersedes config when valid.
- **`HD03_MISSING_INPUT_BEHAVIOR = CLOSED_FAIL_CLOSED`**: Detector fails closed when no valid resolved input exists.
- **`HD03_DETECTOR_OWNERSHIP = CONSUMER_ONLY`**: Detector consumes resolved value only.
- **`HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`**: Survival hours remain unresolved.
- **HD-01A, HD-01B ($N=6\text{h}$), HD-02, HD-04 Option A ($P_{\text{solar}}=0, P_{\text{wind}}=0$), HD-05, Policy E3**.

---

## 3. AUTHORITATIVE GOVERNANCE CLASSIFICATIONS

| Governance Key | Authoritative Classification | Scope / Status |
| :--- | :--- | :--- |
| `HD03_VALIDITY_RULE` | `CLOSED_BASIC_STRUCTURAL_VALIDITY` | **Closed**: Structural validity rule finalized |
| `HD03_BASIC_STRUCTURAL_VALIDITY` | `CLOSED` | **Closed**: $T_{\text{required}} > 0$ finite numeric requirement |
| `HD03_ZERO_VALUE_STATUS` | `INVALID` | **Closed**: Zero duration invalid |
| `HD03_NEGATIVE_VALUE_STATUS` | `INVALID` | **Closed**: Negative values invalid |
| `HD03_NAN_INF_STATUS` | `INVALID` | **Closed**: NaN/Inf values invalid |
| `HD03_UPPER_BOUND` | `NOT_ESTABLISHED` | No upper bound authorized |
| `HD03_UNIT_STATUS` | `GOVERNANCE_REQUIRED` | Unit definition remains open |
| `HD03_FRESHNESS_RULE` | `CLOSED_FC_BOTH` | **Closed**: F-C Dual-guard model finalized |
| `HD03_FRESHNESS_MODEL` | `EXPLICIT_EXPIRY_PLUS_MAXIMUM_AGE_GUARD` | **Closed**: Expiry + TTL guard model |
| `HD03_TTL_VALUE` | `NOT_ESTABLISHED` | Numerical TTL value unresolved |
| `HD03_CLOCK_DRIFT_THRESHOLD` | `NOT_ESTABLISHED` | Clock drift threshold unresolved |
| `HD03_OPERATIONAL_SOURCE_AUTHORITY` | `GOVERNANCE_REQUIRED` | Source authority remains open |
| `HD03_TIME_SEMANTICS` | `GOVERNANCE_REQUIRED` | Time semantics remain open |
| `HD03_RUNTIME_VARIABILITY` | `GOVERNANCE_REQUIRED` | Step-by-step variability remains open |
| `HD03_NUMERICAL_VALUE` | `NOT_ESTABLISHED` | Survival hours unresolved |
| `HD03_IMPLEMENTATION_AUTHORIZATION` | `NOT_GRANTED` | Code modification prohibited |
| `HD03_EXECUTION_AUTHORIZATION` | `NOT_GRANTED` | Simulation execution prohibited |
