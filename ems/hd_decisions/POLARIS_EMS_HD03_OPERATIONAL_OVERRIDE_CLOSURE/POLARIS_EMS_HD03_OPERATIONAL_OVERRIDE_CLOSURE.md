# POLARIS EMS — HD-03 OPERATIONAL OVERRIDE / SOURCE PRECEDENCE & CONFLICT-RESOLUTION GOVERNANCE CLOSURE

## 1. FORMAL GOVERNANCE CLOSURE STATEMENT

The human stakeholder has formally decided and approved the **HD-03 Operational Override & Source Precedence Policy** for POLARIS EMS.

### Authoritative Policy Statement:
> **"An authorized valid operational $T_{\text{required}}$ input shall be capable of overriding the deployment-configured $T_{\text{required}}$ baseline."**

### Authoritative Conflict Rule:
$$\text{HD03\_CONFLICT\_RULE} = \text{CLOSED\_OPERATIONAL\_WINS}$$

When both deployment configuration ($T_{\text{config}}$) and authorized operational input ($T_{\text{oper}}$) exist and are valid:
$$\text{resolved\_T\_required} = T_{\text{oper}}$$

---

## 2. PRECEDENCE & RESOLVER ARCHITECTURE PRINCIPLES

1. **Operational Override Precedence**: An authorized valid operational $T_{\text{required}}$ input supersedes the deployment-configured baseline.
2. **Config Baseline Role**: Deployment configuration provides the default baseline candidate when an operational override is absent, invalid, or unauthenticated.
3. **No Mathematical Manipulation**: The resolver **MUST NOT** average $T_{\text{config}}$ and $T_{\text{oper}}$, select min/max automatically, interpolate between them, or merge them.
4. **Detector Boundary**: The Emergency Condition Detector is **`CONSUMER_ONLY`**. Precedence resolution is performed exclusively upstream by the $T_{\text{required}}$ Resolver.
5. **Fail-Closed Integration**: If neither source yields a valid candidate, the closed fail-closed policy (`CLOSED_FAIL_CLOSED`) strictly applies.

---

## 3. PRESERVED GOVERNANCE BASELINE

All prior POLARIS EMS governance decisions remain fully preserved and unaltered:

- **`HD03_SOURCE_MODEL = C_PLUS_A`**: Deployment configuration baseline + Authorized operational extension.
- **`HD03_MISSING_INPUT_BEHAVIOR = CLOSED_FAIL_CLOSED`**: Detector fails closed when no valid resolved $T_{\text{required}}$ exists.
- **`HD03_DETECTOR_OWNERSHIP = CONSUMER_ONLY`**: Detector consumes resolved value only.
- **`HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`**: Numerical survival window remains unresolved.
- **HD-01A, HD-01B ($N=6\text{h}$), HD-02, HD-04 Option A ($P_{\text{solar}}=0, P_{\text{wind}}=0$), HD-05, Policy E3**.

---

## 4. AUTHORITATIVE GOVERNANCE CLASSIFICATIONS

| Governance Key | Authoritative Classification | Status / Scope |
| :--- | :--- | :--- |
| `HD03_OPERATIONAL_OVERRIDE_CAPABILITY` | `CLOSED` | Operational override enabled |
| `HD03_OVERRIDE_PRECEDENCE` | `CLOSED_OPERATIONAL_WINS_WHEN_VALID_AND_AUTHORIZED` | Operational input supersedes config |
| `HD03_CONFLICT_RULE` | `CLOSED_OPERATIONAL_WINS` | Operational input wins when valid |
| `HD03_CONFIG_BASELINE_ROLE` | `FALLBACK_CANDIDATE_WHEN_OPERATIONAL_OVERRIDE_IS_NOT_VALID` | Config serves as default candidate |
| `HD03_MISSING_INPUT_BEHAVIOR` | `CLOSED_FAIL_CLOSED` | Fails closed on zero valid inputs |
| `HD03_VALIDITY_RULE` | `GOVERNANCE_REQUIRED` | Validity criteria remain open |
| `HD03_FRESHNESS_RULE` | `GOVERNANCE_REQUIRED` | Staleness thresholds remain open |
| `HD03_OPERATIONAL_SOURCE_AUTHORITY` | `GOVERNANCE_REQUIRED` | Authentication schema remains open |
| `HD03_TIME_SEMANTICS` | `GOVERNANCE_REQUIRED` | Time representation remains open |
| `HD03_RUNTIME_VARIABILITY` | `GOVERNANCE_REQUIRED` | Step-by-step variability remains open |
| `HD03_NUMERICAL_VALUE` | `NOT_ESTABLISHED` | Numerical hours unresolved |
| `HD03_DETECTOR_OWNERSHIP` | `CONSUMER_ONLY` | Detector is consumer only |
| `HD03_IMPLEMENTATION_AUTHORIZATION` | `NOT_GRANTED` | Code modification prohibited |
| `HD03_EXECUTION_AUTHORIZATION` | `NOT_GRANTED` | Simulation execution prohibited |
