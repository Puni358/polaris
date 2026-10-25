# POLARIS EMS — HD-03 OPERATIONAL AUTHORITY, TIME SEMANTICS, AND RUNTIME VARIABILITY FORMAL GOVERNANCE CLOSURE

## 1. FORMAL GOVERNANCE CLOSURE STATEMENT

The human stakeholder has formally decided and approved the remaining three HD-03 semantic governance policies:

### Decision 1 — Operational Source Authority:
> **"Only an authenticated and explicitly authorized operational source may issue a $T_{\text{required}}$ override."**
- **Classification**: `HD03_OPERATIONAL_SOURCE_AUTHORITY = CLOSED_AUTHENTICATED_AUTHORIZED_OPERATIONAL_SOURCE`
- Cryptographic mechanism remains: `HD03_CRYPTOGRAPHIC_MECHANISM = NOT_ESTABLISHED`.

### Decision 2 — $T_{\text{required}}$ Time Semantics:
> **" $T_{\text{required}}$ is represented as a positive duration from the current decision point to the required survival/recovery point."**
- **Classification**: `HD03_TIME_SEMANTICS = CLOSED_POSITIVE_DURATION_PLUS_EXPLICIT_EXPIRY`
- $T_{\text{required}}$ is a duration ($\Delta t > 0$), not a timestamp. Payload carries explicit validity/expiry metadata for freshness.

### Decision 3 — Runtime Variability / Update Behavior:
> **" $T_{\text{required}}$ may be refreshed at MPC-cycle boundaries through a new valid, authorized, and fresh operational instruction."**
- **Classification**: `HD03_RUNTIME_VARIABILITY = CLOSED_MPC_CYCLE_REFRESH`
- Update boundary is locked to the MPC cycle. Arbitrary per-timestep mutation is strictly prohibited.

---

## 2. CONCEPTUAL RESOLVER RESOLUTION ORDER

At each MPC cycle boundary, the $T_{\text{required}}$ Resolver executes the following deterministic sequence:

```
                  ┌─────────────────────────────────────┐
                  │ 1. Evaluate Operational Authority   │
                  └──────────────────┬──────────────────┘
                                     │ Authorized & Authenticated?
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 2. Evaluate Structural Validity     │
                  └──────────────────┬──────────────────┘
                                     │ Valid (T_required > 0)?
                                     ▼
                  ┌─────────────────────────────────────┐
                  │ 3. Evaluate Freshness (F-C BOTH)    │
                  └──────────────────┬──────────────────┘
                                     │ Fresh (Not expired & Age <= TTL)?
                                     ▼
                  Is Operational Input Valid, Authorized, & Fresh?
                    ├── YES ──► RESOLVED = T_operational (Operational Wins)
                    └── NO  ──► 4. Evaluate Configured Baseline (T_config)
                                  ├── Valid ──► RESOLVED = T_config
                                  └── Invalid ──► 5. FAIL CLOSED (No Classification)
```

---

## 3. PRESERVED GOVERNANCE BASELINE

All prior POLARIS EMS governance decisions remain fully preserved and unaltered:

- `HD03_SOURCE_MODEL = C_PLUS_A`
- `HD03_OPERATIONAL_OVERRIDE_CAPABILITY = CLOSED`
- `HD03_OVERRIDE_PRECEDENCE = CLOSED_OPERATIONAL_WINS_WHEN_VALID_AND_AUTHORIZED`
- `HD03_CONFLICT_RULE = CLOSED_OPERATIONAL_WINS`
- `HD03_CONFIG_BASELINE_ROLE = FALLBACK_CANDIDATE_WHEN_OPERATIONAL_OVERRIDE_IS_NOT_VALID`
- `HD03_MISSING_INPUT_BEHAVIOR = CLOSED_FAIL_CLOSED`
- `HD03_NO_VALID_T_REQUIRED_STATE = FAIL_CLOSED`
- `HD03_LAST_VALID_FALLBACK = NOT_ALLOWED`
- `HD03_NUMERICAL_FALLBACK = NOT_ALLOWED`
- `HD03_EMERGENCY_ON_UNKNOWN = NOT_ALLOWED`
- `HD03_VALIDITY_RULE = CLOSED_BASIC_STRUCTURAL_VALIDITY`
- `HD03_BASIC_STRUCTURAL_VALIDITY = CLOSED`
- `HD03_ZERO_VALUE_STATUS = INVALID`
- `HD03_NEGATIVE_VALUE_STATUS = INVALID`
- `HD03_NAN_INF_STATUS = INVALID`
- `HD03_FRESHNESS_RULE = CLOSED_FC_BOTH`
- `HD03_FRESHNESS_MODEL = EXPLICIT_EXPIRY_PLUS_MAXIMUM_AGE_GUARD`
- `HD03_DETECTOR_OWNERSHIP = CONSUMER_ONLY`
- HD-01A, HD-01B ($N=6\text{h}$), HD-02, HD-04 Option A, HD-05, Policy E3.

---

## 4. AUTHORITATIVE GOVERNANCE CLASSIFICATIONS

| Governance Key | Authoritative Classification | Scope / Status |
| :--- | :--- | :--- |
| `HD03_OPERATIONAL_SOURCE_AUTHORITY` | `CLOSED_AUTHENTICATED_AUTHORIZED_OPERATIONAL_SOURCE` | **Closed**: Authentication & authorization required |
| `HD03_TIME_SEMANTICS` | `CLOSED_POSITIVE_DURATION_PLUS_EXPLICIT_EXPIRY` | **Closed**: $T_{\text{required}} = \text{duration} > 0$ |
| `HD03_RUNTIME_VARIABILITY` | `CLOSED_MPC_CYCLE_REFRESH` | **Closed**: Update boundary at MPC cycle |
| `HD03_CRYPTOGRAPHIC_MECHANISM` | `NOT_ESTABLISHED` | Crypto algorithm/protocol unresolved |
| `HD03_CLOCK_DRIFT_THRESHOLD` | `NOT_ESTABLISHED` | Drift tolerance unresolved |
| `HD03_TTL_VALUE` | `NOT_ESTABLISHED` | Numerical TTL duration unresolved |
| `HD03_NUMERICAL_VALUE` | `NOT_ESTABLISHED` | Survival hours unresolved |
| `HD03_DETECTOR_OWNERSHIP` | `CONSUMER_ONLY` | Detector is consumer only |
| `HD03_IMPLEMENTATION_AUTHORIZATION` | `NOT_GRANTED` | Code modification prohibited |
| `HD03_EXECUTION_AUTHORIZATION` | `NOT_GRANTED` | Simulation execution prohibited |
