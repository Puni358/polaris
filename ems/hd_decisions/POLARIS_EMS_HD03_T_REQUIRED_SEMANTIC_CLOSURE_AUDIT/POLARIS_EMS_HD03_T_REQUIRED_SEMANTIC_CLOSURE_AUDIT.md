# POLARIS EMS — HD-03 T_required INPUT VALIDITY / PRECEDENCE / MISSING-DATA GOVERNANCE AUDIT

## 1. EXECUTIVE SUMMARY & AUDIT PURPOSE

This document presents the formal **Semantic Closure Audit** for the **HD-03 $T_{\text{required}}$ Source Architecture** under model **`C_PLUS_A`**.

### Closed Governance Foundation:
- **`HD03_SOURCE_MODEL = C_PLUS_A`**:
  - **Option C**: Deployment-specific configured $T_{\text{required}}$ baseline (prototype / default source).
  - **Option A**: Authorized operational $T_{\text{required}}$ input / override (future real-station extension).
- **`HD03_DETECTOR_OWNERSHIP = CONSUMER_ONLY`**:
  - The Emergency Condition Detector **CONSUMES** the resolved $T_{\text{required}}$ value.
  - The Emergency Condition Detector **MUST NOT** derive, invent, modify, estimate, or self-select $T_{\text{required}}$.
- **`HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`**:
  - The numerical survival window (in hours or timesteps) is **UNRESOLVED**.

### Semantic Audit Scope:
This audit systematically evaluates the repository evidence regarding:
1. Missing-input behavior across 9 operational edge cases (Cases A–I)
2. Operational-vs-configured precedence options (Options P1–P4)
3. Conflict resolution when configuration and operational streams disagree
4. Validity and non-zero / finite data criteria
5. Freshness, staleness, TTL, and clock-drift semantics
6. Operational source authority and governance roles
7. Time semantics (duration relative to decision point vs absolute recovery timestamp)
8. Dynamic runtime variability across MPC steps / EMS runs
9. Reproducibility and provenance tracking requirements
10. Resolver architecture boundaries

---

## 2. PRESERVED GOVERNANCE BASELINE

All prior POLARIS EMS governance decisions remain preserved and unaltered:

- **HD-01A**: `EBR = CRITICAL_LOAD_BASED_DYNAMIC`
- **HD-01B**: `N = 6 HOURS` (Fixed normal-operation resilience target; strictly distinct from $T_{\text{required}}$)
- **HD-02**: `E_terminal_target = E_EBR_target(H)` (Terminal shortfall counted exactly once at MPC boundary $H=24\text{h}$)
- **HD-04**: Emergency Mode Detector evaluates survivability through $T_{\text{required}}$ under stress scenario ($P_{\text{solar}} = 0, P_{\text{wind}} = 0$); normal MPC continues using standard causal forecasts.
- **HD-05**: NORMAL: $F_{\text{diesel}} \le 1.05 \cdot F_{\text{diesel}}^*$; EMERGENCY: Battery degradation subordinate to critical service/resilience.
- **Policy E3**: In emergency mode, dynamically preserve whichever resource has the larger survivability margin while maintaining critical service.

---

## 3. COMPREHENSIVE SEMANTIC AUDIT FINDINGS

### Part 1 — Missing Input Behavior (Cases A–I)
Repository evidence audit across all 9 missing-input cases reveals that **NO fallback or default selection rule exists in the repository**.
- **Case A (Config Valid, Oper Absent)**: System falls back to configured baseline ONLY IF authorized precedence permits. No default code exists.
- **Case B (Config Absent, Oper Valid)**: Uses operational value ONLY IF authorized precedence permits. No fallback code exists.
- **Case C (Both Absent)**: Unresolved. Must NOT automatically assume fail-closed, fail-open, default emergency, or default normal.
- **Case D (Config Invalid, Oper Valid)**: Unresolved whether invalid config invalidates system or allows operational pass-through.
- **Case E (Config Valid, Oper Invalid)**: Unresolved whether invalid operational payload flags an error or falls back to config.
- **Case F (Both Invalid)**: Unresolved. System failure / halt behavior is not specified.
- **Case G (Operational Becomes Unavailable)**: Unresolved transition rule.
- **Case H (Operational Stale, Config Valid)**: Unresolved whether stale operational data causes fall-back to config or triggers error.
- **Case I (Operational Stale, Config Absent/Invalid)**: Unresolved catastrophic missing-data handling.
- **Result**: `HD03_MISSING_INPUT_BEHAVIOR = GOVERNANCE_REQUIRED`.

### Part 2 — Source Precedence (Options P1–P4)
Audit evaluated candidate precedence models:
- **Option P1**: Operational value overrides configuration whenever valid.
- **Option P2**: Configuration remains authoritative; operational data cannot override.
- **Option P3**: Operational input overrides configuration only under explicit authorization/validity conditions.
- **Option P4**: Configuration provides baseline; operational source dynamically replaces it only when governed resolver condition is satisfied.
- **Result**: Repository evidence does not establish any of P1–P4 as code or policy. `HD03_OVERRIDE_PRECEDENCE = GOVERNANCE_REQUIRED`.

### Part 3 — Conflict Resolution
- When $T_{\text{config}} \ne T_{\text{operational}}$ (e.g., $30\text{h}$ vs $24\text{h}$), repository evidence contains no conflict tolerance, manual approval gate, or automated tie-breaker rule.
- **Result**: `HD03_CONFLICT_RULE = GOVERNANCE_REQUIRED`.

### Part 4 — Validity Rules
- Repository evidence requires numerical values to be finite and numeric, but does not define min/max duration bounds, schema bounds, or authorization validation logic.
- **Result**: `HD03_VALIDITY_RULE = GOVERNANCE_REQUIRED`.

### Part 5 — Freshness / Staleness Rules
- No TTL, max message age, or clock-drift threshold exists in the repository for operational inputs.
- **Result**: `HD03_FRESHNESS_RULE = GOVERNANCE_REQUIRED`.

### Part 6 — Source Authority
- No specified role matrix or authentication contract exists identifying authorized operational message senders.
- **Result**: `HD03_OPERATIONAL_SOURCE_AUTHORITY = GOVERNANCE_REQUIRED`.

### Part 7 — Time Semantics
- $T_{\text{required}}$ is defined as: *"The operational survival window from the current decision point until the next authorized recovery/resupply opportunity."*
- Unresolved whether operational inputs represent relative duration $\Delta t$, absolute timestamp $t_{\text{recovery}}$, or both.
- **Result**: `HD03_TIME_SEMANTICS = GOVERNANCE_REQUIRED`.

### Part 8 — Dynamic Runtime Variability
- Unresolved whether $T_{\text{required}}$ may change step-by-step during an active EMS run or is locked per run / per horizon.
- **Result**: `HD03_RUNTIME_VARIABILITY = GOVERNANCE_REQUIRED`.

### Part 9 — Reproducibility & Provenance
- Existing POLARIS provenance patterns (e.g. `BRANCH01_CAMPAIGN_PROVENANCE.json`) establish structural conventions. Candidate fields (`resolved_T_required`, `source_type`, `source_id`, `config_hash`, timestamps, `override_active`) are established as **Candidate Engineering Requirements**.
- **Result**: `HD03_PROVENANCE_REQUIREMENTS = PARTIALLY_ESTABLISHED`.

### Part 10 — Resolver Architecture Boundary
- Because Emergency Condition Detector is established as `CONSUMER_ONLY`, the $T_{\text{required}}$ Resolver is **ESTABLISHED** as a separate upstream data resolution component.
- **Result**: `HD03_RESOLVER_BOUNDARY = ESTABLISHED`.

### Part 11 — Numerical Value Unresolved
- `HD03_NUMERICAL_VALUE = NOT_ESTABLISHED`.
- Confirmed invalid as automatic substitutions: $6\text{h}$ (HD-01B EBR), $24\text{h}$ (MPC horizon), $30\text{d}$ (provisional budget cycle), $2\text{h}$ (generator min runtime), $15\text{m}$ (UPS hold-up), $6.67\text{h}$ (battery/load calculation).

### Part 12 — Prototype vs Future Real Station
- **Prototype**: Relies strictly on offline, deployment-configured baseline (Option C). No operational input provider currently exists.
- **Future Real Station**: Option A extension will consume dynamic operational inputs when online, valid, and authenticated.

---

## 4. AUTHORITATIVE GOVERNANCE CLASSIFICATIONS

```
HD03_SOURCE_MODEL                  = C_PLUS_A
HD03_NUMERICAL_VALUE               = NOT_ESTABLISHED

HD03_MISSING_INPUT_BEHAVIOR        = GOVERNANCE_REQUIRED
HD03_OVERRIDE_PRECEDENCE           = GOVERNANCE_REQUIRED
HD03_CONFLICT_RULE                 = GOVERNANCE_REQUIRED
HD03_VALIDITY_RULE                 = GOVERNANCE_REQUIRED
HD03_FRESHNESS_RULE                = GOVERNANCE_REQUIRED
HD03_OPERATIONAL_SOURCE_AUTHORITY  = GOVERNANCE_REQUIRED
HD03_TIME_SEMANTICS                = GOVERNANCE_REQUIRED
HD03_RUNTIME_VARIABILITY           = GOVERNANCE_REQUIRED

HD03_RESOLVER_BOUNDARY             = ESTABLISHED
HD03_PROVENANCE_REQUIREMENTS       = PARTIALLY_ESTABLISHED
HD03_DETECTOR_OWNERSHIP            = CONSUMER_ONLY

HD03_IMPLEMENTATION_AUTHORIZATION  = NOT_GRANTED
HD03_EXECUTION_AUTHORIZATION       = NOT_GRANTED
```
