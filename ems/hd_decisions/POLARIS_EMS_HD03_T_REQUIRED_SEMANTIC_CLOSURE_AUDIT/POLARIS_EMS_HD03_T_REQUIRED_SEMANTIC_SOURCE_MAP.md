# POLARIS EMS — HD-03 T_required SEMANTIC SOURCE MAP & DATA FLOW

## 1. ARCHITECTURAL DATA FLOW MAP

The following diagram maps the semantic data flow between data sources, validation components, the resolver, the Emergency Condition Detector, and the EMS/MPC optimizer.

```
┌──────────────────────────────────────┐        ┌──────────────────────────────────────┐
│  DEPLOYMENT CONFIGURATION (OPTION C) │        │ AUTHORIZED OPERATIONAL INPUT (OPT A) │
│  - configured_T_required             │        │ - operational_T_required             │
│  - static_version_hash               │        │ - issue_timestamp & ttl_seconds      │
│  - authorization_scope               │        │ - authorization_signature            │
└──────────────────┬───────────────────┘        └──────────────────┬───────────────────┘
                   │                                               │
                   │ configured payload                            │ operational payload
                   v                                               v
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                 T_required RESOLVER                                  │
│                                                                                      │
│ 1. VALIDITY EVALUATOR:                                                               │
│    - Checks schema integrity, positivity, finite bounds                              │
│ 2. FRESHNESS EVALUATOR:                                                              │
│    - Evaluates timestamp, clock drift, data age against TTL                          │
│ 3. PRECEDENCE & CONFLICT RESOLVER:                                                   │
│    - Applies governed override precedence rule (OPEN: GOVERNANCE_REQUIRED)           │
│ 4. PROVENANCE GENERATOR:                                                             │
│    - Emits resolution trace audit record                                             │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           │
                                           │ resolved_T_required (hours/timesteps)
                                           v
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                             EMERGENCY CONDITION DETECTOR                             │
│                                                                                      │
│ Role: CONSUMER ONLY                                                                  │
│ Evaluates: Fuel & Battery survivability over resolved_T_required                      │
│ Stress Scenario: P_solar = 0, P_wind = 0 (HD-04 Option A)                            │
│ Constraint: Zero internal fallback, self-selection, or horizon derivation           │
└──────────────────────────────────────────┬───────────────────────────────────────────┘
                                           │
                                           │ NORMAL / EMERGENCY Mode Flag
                                           v
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                       EMS / MPC                                      │
│                                                                                      │
│ Rolling optimization over H = 24h                                                    │
│ Normal: F_diesel <= 1.05 * F_diesel* (HD-05)                                         │
│ Emergency: Subordinates degradation to critical service (HD-05 / Policy E3)          │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. INTERFACE CONTRACTS & REPOSITORY AUDIT

| Interface / Module | Current Repository State | Semantic Requirement | Governance Status |
| :--- | :--- | :--- | :--- |
| **Option C Config Source** | Unimplemented in deployment manifests | Version-controlled deployment default | `GOVERNANCE_REQUIRED` |
| **Option A Operational Source** | Unimplemented in message streams | Signed operational control message | `GOVERNANCE_REQUIRED` |
| **Validity Evaluator** | No code exists | Validates numerical finite/positive bounds | `GOVERNANCE_REQUIRED` |
| **Freshness Evaluator** | No TTL / timestamp logic exists | Evaluates payload age and expiration | `GOVERNANCE_REQUIRED` |
| **Precedence Resolver** | No code exists | Resolves config vs operational selection | `GOVERNANCE_REQUIRED` |
| **Emergency Detector** | Unimplemented / placeholder | Consumes resolved value; zero derivation | `CONSUMER_ONLY` |
| **MPC Solver Boundary** | Standard 24h rolling MILP solver | Consumes mode flag; unpolluted causal forecasts | `ESTABLISHED` |

---

## 3. PROVENANCE RECORD SCHEMA AUDIT

To ensure 100% reproducibility for any past run, the resolver must record the following fields per execution step:

1. `resolved_T_required_value` (float/int): The exact numerical survival horizon supplied to detector.
2. `winning_source_type` (enum): `DEPLOYMENT_CONFIG` vs `OPERATIONAL_OVERRIDE`.
3. `winning_source_id` (string): Identity of config file or operational message stream.
4. `resolution_timestamp` (ISO-8601 string): Exact timestamp of resolution decision.
5. `config_version_hash` (string): Hash of active deployment configuration.
6. `operational_issue_timestamp` (ISO-8601 string): Timestamp on operational message (if active).
7. `operational_age_seconds` (float): Data age of operational payload at resolution time.
8. `validity_state` (enum): `VALID`, `STALE`, `MALFORMED`, `ABSENT`.
9. `override_active` (boolean): True if operational payload superseded deployment baseline.
10. `authority_id` (string): Identity of operational authority issuing override.

*Classification*: `HD03_PROVENANCE_REQUIREMENTS = PARTIALLY_ESTABLISHED` (Candidate Engineering Requirements defined; formal schema awaits implementation authorization).
