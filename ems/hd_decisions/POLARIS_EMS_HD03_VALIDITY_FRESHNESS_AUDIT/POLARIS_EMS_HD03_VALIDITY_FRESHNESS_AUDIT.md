# POLARIS EMS — HD-03 VALIDITY & FRESHNESS EVIDENCE / GOVERNANCE AUDIT

## 1. PURPOSE & AUDIT SCOPE

This document presents the **Validity and Freshness Evidence Audit** for HD-03 $T_{\text{required}}$ in POLARIS EMS.

### Scope:
- **Part A — Validity Rule Audit**: Evaluates structural, numerical, and bounds validity criteria.
- **Part B — Freshness Rule Audit**: Evaluates TTL, payload timestamps, expiry semantics, and clock drift evidence.
- **Preserved Decisions**: HD-03 C+A model, operational-wins precedence, fail-closed policy, `CONSUMER_ONLY` detector ownership, HD-01A, HD-01B ($N=6\text{h}$), HD-02, HD-04 Option A ($P_{\text{solar}}=0, P_{\text{wind}}=0$), HD-05, Policy E3.
- **Numerical Protection**: $T_{\text{required}}$ survival hours remain `NOT_ESTABLISHED`. No proxy values ($6\text{h}$, $24\text{h}$, $30\text{d}$, $2\text{h}$, $15\text{m}$) are repurposed as bounds or TTL values.

---

## 2. PART A — VALIDITY RULE AUDIT

### 2.1 Repository Evidence Audit:
- **Type & Representation**: In existing POLARIS forecasting and validation modules (e.g. `source_validator.py`), inputs must be finite numeric scalars. Non-numeric types, `NaN`, and `Inf` raise `ModelGovernanceError` / `RuntimeError` (`FAIL_CLOSED`).
- **Positivity Requirement**: $T_{\text{required}}$ represents the operational survival duration until resupply. Structurally, negative values ($\le 0$) are non-physical and invalid. Zero duration ($T_{\text{required}} = 0$) provides zero survival window and is invalid.
- **Upper Bounds Evidence**: **ABSENT**. The repository contains NO authoritative maximum upper bound for $T_{\text{required}}$. No generic values ($24\text{h}$, $30\text{d}$) may be assumed as code bounds.
- **Unit Specification**: **GOVERNANCE_REQUIRED**. Unresolved whether inputs are passed as continuous float hours or integer timesteps ($\Delta t = 1\text{h}$).

### 2.2 Evaluation of Validity Candidates:
- **V-A (Basic Structural Validity)**: `SUPPORTED_BY_ARCHITECTURE`. Requires $T_{\text{required}}$ to be present, numeric, finite, positive ($T_{\text{required}} > 0$), and expressed in authorized units.
- **V-B (Bounded Validity)**: `GOVERNANCE_REQUIRED`. Requires an explicit human decision on an upper bound.
- **V-C (Schema Validity)**: `SUPPORTED_BY_FUTURE_ARCHITECTURE`. Combines V-A with additive schema verification (`config_version`, payload hash).

---

## 3. PART B — FRESHNESS RULE AUDIT

### 3.1 Repository Evidence Audit:
- **TTL / Message Expiry Evidence**: **ABSENT**. The repository contains NO numeric TTL (seconds or hours) for operational $T_{\text{required}}$ payloads.
- **Payload Timestamp Evidence**: **ABSENT**. No message headers or timestamp fields exist yet for Option A payloads.
- **Clock Drift / Max Age**: **ABSENT**. No drift threshold exists in the repository.

### 3.2 Evaluation of Freshness Candidates:
- **F-A (Fixed TTL)**: `GOVERNANCE_REQUIRED`. Operational payload valid for a governed maximum duration after issuance. Requires selecting a numeric TTL.
- **F-B (Explicit Expiry)**: `GOVERNANCE_REQUIRED`. Payload contains explicit `valid_until` ISO-8601 timestamp.
- **F-C (Both)**: `SUPPORTED_BY_FUTURE_ARCHITECTURE`. Combines issuance timestamp, fixed TTL guard, and explicit `valid_until` timestamp.
- **F-D (No Freshness / Indefinite)**: `CONFLICTS_WITH_GOVERNANCE`. Allows stale overrides to persist indefinitely; unsafe for real-station operations.

---

## 4. AUTHORITATIVE GOVERNANCE CLASSIFICATIONS

```
HD03_VALIDITY_RULE                 = GOVERNANCE_REQUIRED
HD03_FRESHNESS_RULE                = GOVERNANCE_REQUIRED

HD03_BASIC_STRUCTURAL_VALIDITY     = SUPPORTED_BY_ARCHITECTURE
HD03_UPPER_BOUND_EVIDENCE          = ABSENT
HD03_ZERO_VALUE_STATUS             = INVALID
HD03_NEGATIVE_VALUE_STATUS         = INVALID
HD03_NAN_INF_STATUS                = INVALID
HD03_UNIT_STATUS                   = GOVERNANCE_REQUIRED

HD03_TTL_EVIDENCE                  = ABSENT
HD03_EXPIRY_EVIDENCE               = ABSENT
HD03_TIMESTAMP_EVIDENCE            = ABSENT
HD03_CLOCK_DRIFT_EVIDENCE          = ABSENT

HD03_NUMERICAL_VALUE               = NOT_ESTABLISHED
HD03_IMPLEMENTATION_AUTHORIZATION  = NOT_GRANTED
HD03_EXECUTION_AUTHORIZATION       = NOT_GRANTED
```
