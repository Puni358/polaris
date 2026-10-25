# POLARIS EMS POLICY DEFINITION RESOLUTION
## CORRECTION MANIFEST — NARROW CORRECTION PASS

**Manifest Label**: `POLARIS_EMS_POLICY_DEFINITION_CORRECTION_MANIFEST`
**Correction Version**: 1.1.0 (corrects v1.0.0)
**Timestamp**: 2026-09-22T00:10:00Z
**Type**: NARROW_GOVERNANCE_WORDING_CORRECTION

---

## ABSOLUTE GOVERNANCE CONSTRAINTS (UNCHANGED)

```yaml
D1_THROUGH_D16_CHANGED:                NO
POLICY_CHOICES_REOPENED:               NO
EMS_MODIFIED:                          NO
OPTIMIZER_MODIFIED:                    NO
MODEL_MODIFIED:                        NO
EMS_EXECUTED:                          NO
MPC_EXECUTED:                          NO
MILP_EXECUTED:                         NO
DIGITAL_TWIN_EXECUTED:                 NO
NEW_EXPERIMENT:                        NO
OBJECTIVE_COEFFICIENTS_CHANGED:        NO
CURRENT_EMS_IMPLEMENTATION:            FROZEN
CURRENT_EMS_OBJECTIVE:                 FROZEN
```

---

## WHAT THIS CORRECTION DOES

This pass corrects **governance classification errors** introduced when the v1.0.0
package promoted stakeholder-proposal language (from the POLAR_STATION_RESEARCH_MANAGER
role-based proposal — advisory only) into the "POLICY_DEFINITION" block as if it were
authorized stakeholder policy or resolved definitional fact.

**No policy content is being decided, ranked, recommended, or changed.**
**All 16 stakeholder decisions remain exactly as captured.**
**No numerical values are being selected or invented.**

---

## CORRECTIONS MADE

### CORRECTION A — Emergency Operating Modes (Area 1)

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| Modes presented as `POLICY_DEFINITION — OPERATING MODES (RESOLVED)` | Modes reclassified as `CONCEPTUAL_POLICY_FRAMEWORK — REQUIRES_STAKEHOLDER_AND_ENGINEERING_VALIDATION` |
| Mode-transition entry/exit conditions specified with numerical placeholders | Entry/exit conditions removed — classified as `NEXT_SPECIFICATION_REQUIRED` |
| SOC trigger thresholds listed as `STATION_DATA_REQUIRED` within a resolved structure | Entire numerical threshold specification deferred; mode list is illustrative only |

**Reason**: The stakeholder decisions (D02, D04, D06) establish that operating modes
exist and that shedding/reliability rules differ by mode. They do NOT formally authorize
the four specific named modes or their transition conditions. These remain conceptual.

### CORRECTION B — Load Tier Structure (Area 2)

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| Five-tier structure (CRITICAL/ESSENTIAL/DEFERRABLE/INTERRUPTIBLE/NONCRITICAL) presented as `POLICY_DEFINITION` | Reclassified as `ILLUSTRATIVE_CONCEPTUAL_STRUCTURE — NOT_STAKEHOLDER_AUTHORIZED` |
| Shedding sequence NONCRITICAL→CRITICAL listed as resolved policy | Shedding sequence reclassified as `NEXT_SPECIFICATION_REQUIRED` |
| Restoration sequence stated as resolved | Restoration sequence reclassified as `NEXT_SPECIFICATION_REQUIRED` |

**Reason**: D01 (A+C) selects tiered load classification with three conceptual tiers
(Critical / Essential-Flexible / Interruptible-Noncritical). A five-tier scheme is an
illustrative example from the advisory stakeholder proposal — NOT an authorized extension
of the stakeholder decision. Actual tier mapping is `STATION_SPECIFIC_VALIDATION_REQUIRED`.

### CORRECTION C — Five-Minute Restoration Dwell (Area 2)

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| `5 minutes` dwell time listed as `HUMAN_SELECTED_POLICY` with `PROVISIONAL` qualifier | Reclassified as `NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` |
| Appeared in policy-definition block | Moved to illustrative note only, clearly flagged as advisory-proposal-only |

**Reason**: The `5 minutes` figure originates exclusively from the
POLAR_STATION_RESEARCH_MANAGER role-based **advisory proposal** — it is not in any
authoritative POLARIS document, stakeholder decision, or system configuration. It is
not established from available evidence as policy.

### CORRECTION D — 15-Minute / 2-kWh Reliability Review Triggers (Area 3)

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| 15 minutes and 2 kWh/30-day listed as `HUMAN_SELECTED_POLICY (PROVISIONAL)` | Reclassified as `PROVISIONAL_EXAMPLE_ONLY — NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` |
| Included in policy-definition block under SLA | Moved to illustrative note; explicitly excluded from Objective Specification inputs |

**Reason**: These figures originate exclusively from the advisory stakeholder proposal,
not from authoritative POLARIS requirements or governed documents. They are not policy.

### CORRECTION E — Fuel Budget Quantity and Period (Area 5)

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| `monthly fuel ceiling` framing used throughout | Removed; replaced with `budget period = STATION_SPECIFIC_VALIDATION_REQUIRED` |
| `30-day emergency reserve` sizing listed as `HUMAN_SELECTED_POLICY (PROVISIONAL)` | Reclassified as `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| Emergency reserve sizing formula provided | Formula removed; classified as `NEXT_SPECIFICATION_REQUIRED` |

**Reason**: D08 (B+C) selects the **structure** — seasonal/resupply-cycle fuel budget
plus dynamic fuel management. It does NOT select a monthly period, a 30-day reserve
sizing, or any liter figure. The `30-day` figure comes from the advisory proposal.

### CORRECTION F — Emergency Battery Reserve Percentages (Area 6)

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| 35% baseline EBR listed as `HUMAN_SELECTED_POLICY (PROVISIONAL)` | Reclassified as `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| 45% precautionary EBR listed as `HUMAN_SELECTED_POLICY (PROVISIONAL)` | Reclassified as `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| kWh derivations (70 kWh, 90 kWh) listed as `ENGINEERING_INFERENCE` | Retained only as illustrative derivation; removed from policy-definition block |

**Reason**: D11 (B+A) selects the **structure** — dynamic emergency reserve plus a
baseline reserve floor. It does NOT select 35% or 45%. These figures originate from the
advisory proposal only. The structure is `HUMAN_SELECTED_POLICY`. The numerical values
are `NUMERICAL_CALIBRATION_REQUIRED` and `ENGINEERING_VALIDATION_REQUIRED`.

### CORRECTION G — Terminal SOC Numerical Values (Area 6)

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| 35% minimum terminal SOC listed as `HUMAN_SELECTED_POLICY (PROVISIONAL)` | Reclassified as `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| 55–65% precautionary target listed as `HUMAN_SELECTED_POLICY (PROVISIONAL)` | Reclassified as `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |

**Reason**: D12 (C+B) selects the **structure** — dynamic terminal SOC requirement plus
a minimum terminal floor. It does NOT select 35%, 55%, or 65%. These originate from the
advisory proposal. Structure = `HUMAN_SELECTED_POLICY`. Values = `NUMERICAL_CALIBRATION_REQUIRED`.

### CORRECTION H — Renewable Utilization Percentage Target (Area 7)

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| 50–70% renewable utilization KPI listed as `PROVISIONAL` in curtailment policy block | Reclassified as `NOT_STAKEHOLDER_AUTHORIZED — NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` |
| KPI specified as monthly rolling with polar-day/night split | Framing retained; percentage value removed from policy |

**Reason**: D09 (B) explicitly selects **minimize avoidable curtailment with no
arbitrary percentage target**. Introducing a 50–70% figure — even labeled provisional —
directly contradicts the "no arbitrary % target" selection. D09 is itself the rejection
of a fixed percentage. The 50–70% is from the advisory proposal only.

### CORRECTION I — Forecast Uncertainty Margin Percentages (Area 8)

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| Solar −15–25%, Wind −20–30%, Demand +10% listed as `HUMAN_SELECTED_POLICY (PROVISIONAL)` | Reclassified as `PROVISIONAL_ENGINEERING_VALUE — NOT_STAKEHOLDER_AUTHORIZED` |
| Margin values listed in policy-definition block | Moved to illustrative/advisory section; removed from policy block |

**Reason**: D13 (A+D) selects the **method** — deterministic safety margins combined
with real-time MPC rolling correction. It does NOT select any numerical margin
percentages. These originate from the advisory proposal. Method = `HUMAN_SELECTED_POLICY`.
Numerical values = `NUMERICAL_CALIBRATION_REQUIRED` pending historical station forecast
error statistics.

### CORRECTION J — "All Resolved" Governance Claim

| Before (v1.0.0) | After (v1.1.0) |
|-----------------|----------------|
| `"10 Policy-Definition Areas — All Resolved"` | `"10 Policy-Definition Areas Reviewed; Policy Logic Partially Resolved, with Station-Specific, Numerical, Engineering, and Formal-Specification Items Remaining"` |
| `POLICY_DEFINITION_RESOLVED` status | `POLICY_DEFINITION_RESOLUTION = CONDITIONAL` |
| `AREAS_RESOLVED: 10 of 10` | `AREAS_POLICY_LOGIC_RESOLVED: 10 of 10; AREAS_NUMERICALLY_COMPLETE: 0 of 10` |

**Reason**: The policy relationships and structures are conceptually resolved for all
10 areas. However, no area has its numerical parameters finalized, its station-specific
mapping completed, or its mathematical formulation produced. `CONDITIONAL` is the
accurate status.

---

## STATUS MODEL APPLIED IN v1.1.0 PACKAGE

The corrected package uses the following explicit status vocabulary:

| Status Label | Meaning |
|-------------|---------|
| `HUMAN_SELECTED_POLICY` | Directly from the 16 fixed stakeholder decisions — immutable |
| `CONCEPTUALLY_RESOLVED` | Policy relationship or structure clarified from stakeholder decisions |
| `CONCEPTUAL_POLICY_FRAMEWORK` | Illustrative organizing concept; not formally authorized |
| `PROVISIONAL_ENGINEERING_VALUE` | From advisory stakeholder proposal; not authorized; requires validation |
| `ILLUSTRATIVE_CONCEPTUAL_STRUCTURE` | Example not yet mapped to actual station; not authorized |
| `STATION_SPECIFIC_VALIDATION_REQUIRED` | Cannot be resolved without physical station data |
| `NUMERICAL_CALIBRATION_REQUIRED` | Numerical value pending empirical/engineering derivation |
| `NEXT_EMS_OBJECTIVE_SPECIFICATION` | Item to be formally produced in the Specification phase |
| `FORMAL_STAKEHOLDER_AUTHORIZATION_REQUIRED` | Requires formal governance sign-off |
| `NOT_ESTABLISHED_FROM_AVAILABLE_EVIDENCE` | Not traceable to any authoritative source in available evidence |
| `NOT_STAKEHOLDER_AUTHORIZED` | Explicitly not selected by stakeholder; must not enter future specification as policy |
| `CURRENT_IMPLEMENTATION_FACT` | What the frozen prototype software does — not policy |

---

## ITEMS NOT CHANGED

The following elements were correct in v1.0.0 and are preserved:

- All 16 stakeholder decision codes (D1=A+C through D16=C) — **UNCHANGED**
- All `CURRENT_IMPLEMENTATION_FACT` labels for frozen system values
- The lexicographic priority ordering: Reliability → Resilience → Fuel → Renewables
- The three-layer governance separation structure
- The rejection of the $10,000/kWh penalty as policy
- The rejection of the 16,000:1 coefficient ratio as policy
- The identification of the 20% technical SOC minimum as `CURRENT_IMPLEMENTATION_FACT`
- All SHA-256 frozen system hashes
- The evidence traceability matrix (with classification corrections applied)
- The tension register (with TENSION_03 reclassified per corrections H and G)
- All `NEXT_SPECIFICATION_REQUIRED` items (NS-01 through NS-11)
- All `STATION_DATA_REQUIRED` items (SD-01 through SD-13)
- The pending requirements register (additional items added per correction)

---

## VERIFICATION OF 16 STAKEHOLDER DECISIONS (UNCHANGED)

| ID | Selected | Status |
|----|---------|--------|
| D01 | A + C | UNCHANGED |
| D02 | A + B | UNCHANGED |
| D03 | A | UNCHANGED |
| D04 | A | UNCHANGED |
| D05 | A | UNCHANGED |
| D06 | D + A | UNCHANGED |
| D07 | A + B | UNCHANGED |
| D08 | B + C | UNCHANGED |
| D09 | B | UNCHANGED |
| D10 | B | UNCHANGED |
| D11 | B + A | UNCHANGED |
| D12 | C + B | UNCHANGED |
| D13 | A + D | UNCHANGED |
| D14 | A + C | UNCHANGED |
| D15 | A | UNCHANGED |
| D16 | C | UNCHANGED |

**D1_D16_CHANGED = NO**

---

## FINAL GOVERNANCE STATUS

```yaml
POLICY_DEFINITION_RESOLUTION:         CONDITIONAL
UNAUTHORIZED_NUMERICAL_POLICY_VALUES:  0
STATION_SPECIFIC_ASSUMPTIONS_INVENTED: 0
D1_D16_CHANGED:                        NO
POLICY_CHOICES_REOPENED:              NO
EMS_MODIFIED:                         NO
OPTIMIZER_MODIFIED:                   NO
MODEL_MODIFIED:                       NO
EMS_EXECUTED:                         NO
MPC_EXECUTED:                         NO
MILP_EXECUTED:                        NO
DIGITAL_TWIN_EXECUTED:                NO
NEW_EXPERIMENT:                       NO
OBJECTIVE_COEFFICIENTS_CHANGED:       NO
CURRENT_EMS_IMPLEMENTATION:           FROZEN
CURRENT_EMS_OBJECTIVE:                FROZEN
FORMAL_STAKEHOLDER_AUTHORIZATION:     PENDING
NEXT_GOVERNED_STEP:                   HUMAN_POLICY_PACKAGE_REVIEW
FOLLOWING_STEP:                       GOVERNED_EMS_OBJECTIVE_SPECIFICATION
```
