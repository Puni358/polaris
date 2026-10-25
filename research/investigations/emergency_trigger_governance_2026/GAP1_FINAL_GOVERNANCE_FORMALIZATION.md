# POLARIS — GAP 1 FINAL GOVERNANCE FORMALIZATION

## Executive Summary & Authorization Record

This document records the formal mathematical semantics of the **Authoritative GAP 1 Human Governance Decisions (G1–G6)**.

```yaml
HUMAN_POLICY_STATUS: COMPLETE & AUTHORITATIVE
FORMAL_SEMANTICS_STATUS: COMPLETE
RESEARCH_PREREQUISITES_STATUS: PENDING (G1.3-E Resource-Specific Freshness Research)
IMPLEMENTATION_AUTHORIZATION: NOT AUTHORIZED (Formalization Audit Only)
PRODUCTION_MODIFICATIONS: 0
```

---

## 1. Formal Record of Authoritative Human Decisions

### G1 — GENERATOR AVAILABILITY
- **Formal Rule**: Generator safety credit requires the generator to be:
  1. Operational OR capable of becoming operational under the validated dispatchability/start-readiness rule (G1.2);
  2. Dispatchable;
  3. Supported by validated telemetry/evidence.
- **Mandatory Distinctions**: Configured $\neq$ Operational; Running $\neq$ Dispatchable; Rated $\neq$ Available; Available $\neq$ Fuel-Sufficient.

### G2 — FUEL SUFFICIENCY & UNCERTAINTY
- **Formal Rule**: Generator contribution to 6-hour survivability requires sufficient fuel for the 6-hour interval to be demonstrated ($E_{\text{fuel\_available}} \ge E_{\text{req}}$).
- **Uncertainty Rule**: Fuel uncertainty ($\text{V}_{\text{fuel}} = \text{INVALID/UNKNOWN}$) makes generator safety contribution $0.0\text{ kWh}$.
- **Safeguard**: `UNKNOWN_INVALID != EMERGENCY`. Fuel uncertainty does not automatically trigger Emergency. Remaining verified resources determine system state.

### G3 — STARTUP TRANSIENTS
- **Formal Rule**: Startup must be explicitly accounted for. An OFF generator ($u_k(t_0) = 0$) may receive survivability credit ONLY if:
  1. Validated start-readiness exists ($\text{StartReady} = \text{VALID}$);
  2. Startup delay is validated ($\Delta t_{\text{startup}}$);
  3. Generation credit begins ONLY after the applicable startup constraint is satisfied ($t \ge \Delta t_{\text{startup}}$).
- **Zero-Evidence Rule**: No instantaneous-start assumption may be used for safety credit. If start-readiness is unverified, generator safety credit is $0.0\text{ kWh}$.

### G4 — UNKNOWN GENERATOR HEALTH
- **Formal Rule**: If generator health/status evidence is UNKNOWN or invalid:
  1. Do NOT credit generator for survivability ($E_{\text{gen\_credit}} = 0.0\text{ kWh}$);
  2. Do NOT automatically classify system as Emergency;
  3. Evaluate remaining verified resources (battery deliverable + verified renewables).
- **Emergency Entry Rule**: If remaining verified resources cannot establish 6-hour survivability ($M_{\text{surv}} < 0$), separate Emergency-entry governance applies.

### G5 — TIME-VARYING GENERATOR OUTPUT ENVELOPE
- **Formal Rule**: Generator survivability credit is represented as a dynamic time-varying power integral:
  $$E_{\text{gen\_credible\_raw}} = \int_{0}^{6.0\text{ h}} P_{\text{gen\_credible}}(t) \, dt \quad [\text{kWh}]$$
- **Dynamic Factors**: $P_{\text{gen\_credible}}(t)$ must account for availability, dispatchability, startup delay, fuel depletion, output bounds ($10\text{ kW}$ to $100\text{ kW}$), validated derating, operating limitations, and health evidence.

### G1.1 — CRITICAL-LOAD DEMAND CAP
- **Formal Rule**: Generator safety credit MUST be capped at the remaining critical-load energy requirement ($69.60\text{ kWh}$ max for $11.6\text{ kW} \times 6.0\text{ h}$):
  $$E_{\text{gen\_credible}} = \min\left( \int_{0}^{6.0} P_{\text{gen\_credible}}(t) \, dt, \, \max\left(0, \, 69.60 - E_{\text{batt\_deliverable}}\right) \right)$$
- **Governance Mandate**: Generator capacity above the remaining critical-load requirement shall NOT increase survivability credit.

### G1.2 — OFF GENERATOR DISPATCHABILITY
- **Formal Rule**: "Dispatchable" includes an OFF generator ($u(t_0)=0$) ONLY when:
  1. Validated start-readiness exists;
  2. Generator can become operational under a validated startup process;
  3. Startup delay ($\Delta t_{\text{startup}}$) is explicitly represented in $P_{\text{gen\_credible}}(t)$.
- An OFF generator without validated start-readiness CANNOT receive safety credit.

### G1.3-E — TELEMETRY FRESHNESS (NO UNIVERSAL NUMERICAL THRESHOLD)
- **Formal Rule**: **DO NOT SELECT A UNIVERSAL NUMERICAL FRESHNESS THRESHOLD.**
- **Governance Mandate**: Safety-critical telemetry must be sufficiently fresh to support the specific survivability decision being made, but the acceptable freshness rule shall be defined through **resource-specific, evidence-based research** before production implementation.
- **Negative Constraints**: The system MUST NOT invent a universal number; default to 30s/300s/900s; treat arbitrary age as acceptable; or claim stale/unknown telemetry is valid merely because no threshold has been selected.

### G1.4 — TELEMETRY LOSS / EMERGENCY
- **Formal Rule**: If generator telemetry becomes invalid AND verified remaining resources can no longer establish 6-hour critical-load survivability ($M_{\text{surv}} < 0$):
  $$\rightarrow \text{Enter EMERGENCY Mode and notify operator.}$$
- Telemetry invalidity itself is **NOT** automatically equivalent to Emergency. Emergency depends strictly on resulting verified survivability state ($M_{\text{surv}} < 0$).

### G6 — STRICT EVIDENCE VALIDATION THRESHOLD
- **Formal Rule**: Every required evidence field for generator safety credit MUST validate. No optimistic defaults, nameplate substitutions, or unverified assumptions. If required evidence is missing, invalid, stale under applicable established freshness rules, or contradictory $\rightarrow$ generator receives ZERO safety credit ($0.0\text{ kWh}$).

---

## 2. Formal G1.3-E Telemetry Freshness Semantics

### 2.1 The Conceptual Validation Chain
Telemetry MUST navigate a six-stage conceptual validation chain before contributing to generator survivability energy:

```
[ Stage 1: Telemetry Existence ]
              ↓ (Data packet present in buffer)
[ Stage 2: Structural Validity ]
              ↓ (Format, checksum, range bounds check PASS)
[ Stage 3: Timestamp / Temporal Validity ]
              ↓ (Non-future timestamp, valid wall clock)
[ Stage 4: Resource-Specific Freshness Rule ]
              ↓ (Evaluates FreshnessEligible(resource, measurement, t_now, context))
[ Stage 5: Safety-Credit Eligibility ]
              ↓ (Eligible for inclusion in M_surv equation)
[ Stage 6: Generator Survivability Contribution ]
              → Enters P_gen_credible(t) integral
```

### 2.2 Policy Interface Specification (Conceptual Only — Do Not Implement)

```python
# CONCEPTUAL POLICY INTERFACE SPECIFICATION (FOR GOVERNANCE FORMALIZATION ONLY)
# DO NOT IMPLEMENT IN PRODUCTION CODE. DO NOT ASSIGN PLACEHOLDER NUMERICAL VALUES.

def FreshnessEligible(
    resource_id: str,
    measurement_type: str,
    t_now_epoch: float,
    evidence_context: dict
) -> bool:
    """
    Formal Policy Interface for G1.3-E Telemetry Freshness.
    
    SEMANTICS:
    - Returns TRUE ONLY when an established, evidence-based, resource-specific 
      freshness specification exists for (resource_id, measurement_type) AND 
      the telemetry timestamp satisfies that specific rule.
    - Returns FALSE when freshness cannot be established (including when no 
      resource-specific rule has yet been defined).
      
    GOVERNANCE MANDATE:
    - MUST NOT assign placeholder numerical thresholds (e.g. 30s, 300s, 900s).
    - MUST NOT default to TRUE when rules are missing.
    """
    rule = LookupResourceSpecificFreshnessRule(resource_id, measurement_type)
    if rule is None:
        # Resource-specific freshness specification has not yet been established
        return False
    
    return rule.evaluate(t_now_epoch, evidence_context)
```

---

## 3. Formal Survivability Semantics & Mathematics

### 3.1 Reconciled Survivability Equation
The Critical Load Survivability Margin ($M_{\text{surv}}$) is strictly defined in **bus-delivered kWh**:

$$M_{\text{surv}}(t) = E_{\text{batt\_deliverable}}(t) + E_{\text{gen\_credible\_total}}(t) + E_{\text{ren\_credible\_total}}(t) - E_{\text{critical\_delivered\_req}}(6\text{h})$$

Where:
- $E_{\text{batt\_deliverable}}(t) = \max\left(0, \, (SOC(t) - 0.20) \times 200.0\text{ kWh} \times 0.92\right)$ [kWh delivered]
- $E_{\text{critical\_delivered\_req}}(6\text{h}) = 11.6\text{ kW} \times 6.0\text{ h} = 69.60\text{ kWh delivered}$
- $E_{\text{gen\_credible\_total}}(t) = \min\left( \int_{0}^{6.0} P_{\text{gen\_credible}}(\tau) d\tau, \, \max(0, 69.60 - E_{\text{batt\_deliverable}}(t)) \right)$

### 3.2 Proof of Decoupling (Generator Credit $= 0 \neq$ Emergency)
If generator evidence fails any stage of the G6 validation threshold or G1.3-E freshness rule:
$$P_{\text{gen\_credible}}(\tau) = 0.0 \implies E_{\text{gen\_credible\_total}} = 0.0\text{ kWh}$$

The survivability margin re-evaluates strictly on remaining verified resources:
$$M_{\text{surv}}(t) = E_{\text{batt\_deliverable}}(t) + E_{\text{ren\_credible\_total}}(t) - 69.60\text{ kWh}$$

- **Case 3.2.A ($M_{\text{surv}} \ge 0$)**: If battery deliverable energy + renewables $\ge 69.60\text{ kWh}$, state remains `NORMAL` or `RESERVE_DEFICIT`. **NO EMERGENCY ENTRY.**
- **Case 3.2.B ($M_{\text{surv}} < 0$)**: If battery deliverable energy + renewables $< 69.60\text{ kWh}$, state transitions to `EMERGENCY` under Rule G1.4.

---

## 4. Policy / Assumption / Implementation Separation Table

| ID | Decision / Parameter | Type | Authoritative? | Numerical? | Evidence Basis | Implementation Status | Remaining Research Required |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **G1** | Generator Availability Rule | `HUMAN POLICY` | **YES** | No | Governed Policy | Formalized | None |
| **G2** | Fuel Sufficiency Requirement | `HUMAN POLICY` | **YES** | No | Governed Policy | Formalized | None |
| **G3** | Startup Transients Rule | `HUMAN POLICY` | **YES** | No | Governed Policy | Formalized | Define synthetic $\Delta t_{\text{start}}$ |
| **G4** | Unknown Health Governance | `HUMAN POLICY` | **YES** | No | Governed Policy | Formalized | None |
| **G5** | Time-Varying Integral Model | `HUMAN POLICY` | **YES** | No | Governed Policy | Formalized | None |
| **G1.1**| Critical-Load Demand Cap | `HUMAN POLICY` | **YES** | $69.60\text{ kWh}$ | Governed Policy | Formalized | None |
| **G1.2**| OFF Generator Dispatchability | `HUMAN POLICY` | **YES** | No | Governed Policy | Formalized | None |
| **G1.3-E**| Telemetry Freshness Rule | `HUMAN POLICY` | **YES** | **NO** (Intentionally Absent) | Research Pending | **NOT READY FOR CODE** | Resource-specific freshness research |
| **G1.4**| Telemetry Loss / Emergency Rule | `HUMAN POLICY` | **YES** | No | Governed Policy | Formalized | None |
| **G6** | Strict Evidence Validation | `HUMAN POLICY` | **YES** | No | Governed Policy | Formalized | None |

---

## 5. Governance Readiness & Readiness Breakdown

```text
[A] HUMAN POLICY COMPLETE           : YES (G1–G6, G1.1, G1.2, G1.3-E, G1.4, G6 fully recorded)
[B] FORMAL SEMANTICS COMPLETE       : YES (Decoupling, integrals, and M_surv math verified)
[C] RESEARCH PREREQUISITES COMPLETE : NO  (G1.3-E resource-specific freshness research pending)
[D] IMPLEMENTATION AUTHORIZED       : NO  (Production code lock active)
```
