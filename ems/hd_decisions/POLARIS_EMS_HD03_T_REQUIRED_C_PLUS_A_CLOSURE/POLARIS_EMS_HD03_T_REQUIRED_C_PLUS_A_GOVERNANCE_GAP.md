# POLARIS EMS — HD-03 C+A REMAINING GOVERNANCE GAPS & OPEN ITEMS

## 1. EXECUTIVE GOVERNANCE GAP SUMMARY

The closure of **HD-03 Source Architecture Model C+A** establishes **WHERE** $T_{\text{required}}$ can come from (configured baseline + operational override).

However, it explicitly leaves all numerical parameters, operational override rules, error handling policies, and implementation permissions **OPEN**. These items require separate human governance decisions before any code implementation or simulation execution can occur.

---

## 2. DETAILED REGISTER OF REMAINING OPEN GOVERNANCE ITEMS

### 2.1 Numerical Value Selection
- **Governance Key**: `HD03_NUMERICAL_VALUE`
- **Current Status**: `NOT_ESTABLISHED`
- **Open Questions**: What exact numerical value (in hours or timesteps) should $T_{\text{required}}$ have for a given deployment?
- **Prohibited Derivations**: Do NOT substitute $N = 6\text{h}$, $H = 24\text{h}$, $30\text{d}$, $2\text{h}$, $15\text{m}$, or battery capacity calculations ($6.67\text{h}$).

### 2.2 Missing Input Behavior
- **Governance Key**: `HD03_MISSING_INPUT_BEHAVIOR`
- **Current Status**: `GOVERNANCE_REQUIRED`
- **Open Questions**: What should POLARIS EMS do if $T_{\text{required}}$ is missing, unconfigured, unreadable, or invalid?
- **Prohibited Pre-determinations**: Do NOT assume fail-open, fail-closed, default to emergency, default to normal, fallback to $24\text{h}$, or fallback to $6\text{h}$.

### 2.3 Operational Override Precedence & Conflict Resolution
- **Governance Keys**: `HD03_OVERRIDE_PRECEDENCE`, `HD03_CONFLICT_RULE`
- **Current Status**: `GOVERNANCE_REQUIRED`
- **Open Questions**: When deployment configuration and an operational input stream disagree or conflict, what is the exact deterministic precedence hierarchy?

### 2.4 Validity Criteria & Freshness Rules
- **Governance Keys**: `HD03_VALIDITY_RULE`, `HD03_FRESHNESS_RULE`
- **Current Status**: `GOVERNANCE_REQUIRED`
- **Open Questions**:
  - What timestamp semantics, clock sync requirements, and freshness windows apply to operational inputs?
  - At what point does a non-updated operational input become stale, and what state transitions occur upon staleness?

### 2.5 Source Authorization & Security Schema
- **Governance Key**: `HD03_SOURCE_AUTHORIZATION_MECHANISM`
- **Current Status**: `GOVERNANCE_REQUIRED`
- **Open Questions**: How does POLARIS cryptographically or procedurally authenticate operational input messages to prevent unauthorized override attacks?

### 2.6 Implementation & Execution Permissions
- **Governance Keys**: `HD03_IMPLEMENTATION_AUTHORIZATION`, `HD03_EXECUTION_AUTHORIZATION`
- **Current Status**: `NOT_GRANTED`
- **Directives**:
  - **NO** source code modifications to `StationState`, `ForecastBundle`, `DispatchPlan`, or detector modules are permitted.
  - **NO** solver runs, MILP executions, or EMS campaign simulations are authorized under this closure package.

---

## 3. GOVERNANCE ROADMAP TO COMPLETE EMS CLOSURE

```
[ HD-03 Source Architecture (CLOSED: C+A) ]
                  │
                  ▼
[ Step 1: Human Decision on Missing Input Behavior (OPEN) ]
                  │
                  ▼
[ Step 2: Human Decision on Override Precedence & Validity Rules (OPEN) ]
                  │
                  ▼
[ Step 3: Deployment-Specific Numerical T_required Selection (OPEN) ]
                  │
                  ▼
[ Step 4: Formal Implementation Authorization Gate (NOT GRANTED) ]
```
