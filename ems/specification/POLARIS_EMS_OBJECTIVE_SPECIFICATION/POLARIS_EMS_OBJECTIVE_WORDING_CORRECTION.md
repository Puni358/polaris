# POLARIS EMS OBJECTIVE GOVERNANCE WORDING CORRECTION
## 16,000 : 1 Fuel / Unmet-Load Ratio Interpretation Clarification

**Document Version**: 1.0.0  
**Governance Status**: WORDING_CORRECTION_COMPLETE  
**Audit Timestamp**: 2026-09-21T21:31:00Z  
**Authoritative Directory**: `POLARIS_EMS_OBJECTIVE_SPECIFICATION/`  
**Frozen Implementation SHA-256**: `ee913b68b736602ef8f50163198ae34fe59efe8e0ba852c6f4710fbe91999b35`  

---

> [!IMPORTANT]
> **GOVERNANCE CORRECTION SUMMARY**: This document records a strict read-only governance correction applied to the `POLARIS_EMS_OBJECTIVE_SPECIFICATION/` documentation package. The purpose is to eliminate an over-strong, scientifically misleading statement that interpreted the 16,000:1 objective cost coefficient ratio as a literal operational claim that the optimizer would burn up to 4,000 Liters of diesel fuel to avoid 1 kWh of unmet load.

---

## 1. Authoritative Numerical Facts

The underlying implementation parameters in `system/optimization/implementations/milp.py` and `system/config/*.yaml` are preserved without change:

- **Unmet Load Penalty ($c_{\text{unmet}}$)**: $\$10.00/\text{Wh} = \$10,000.00/\text{kWh}$
- **Marginal Diesel Fuel Cost ($c_{\text{marg}}$)**: $\$2.50/\text{L} \times 0.00025\text{ L/Wh} = \$0.000625/\text{Wh} = \$0.625/\text{kWh}$
- **Coefficient Ratio**: $\frac{\$10,000.00/\text{kWh}}{\$0.625/\text{kWh}} = 16,000 : 1$

### Correct Scientific Statement:
> "The unmet-load penalty is 16,000 times the marginal diesel-energy cost on a $\$/\text{kWh}$ basis."

---

## 2. Invalid Statement Removed

The following over-strong claim was identified and removed from current authoritative governance documentation:

> ❌ **Removed Wording**: *"The optimizer will consume up to 4,000 Liters of diesel fuel (or generate 16,000 kWh of electricity) to prevent a single kWh of unmet critical load."*

---

## 3. Required Corrected Interpretation

The misleading statement has been replaced across current authoritative specification documents with the following governed wording:

> ✅ **Governed Wording**: *"The unmet-load penalty is 16,000 times the marginal diesel-energy cost on a $\$/\text{kWh}$ basis. The realized fuel required to avoid a unit of unmet load depends on generator operating constraints, base fuel consumption, startup costs, battery state, renewable availability, curtailment, objective discounting, horizon dynamics, and overall feasibility."*

> ✅ **Clarification**: *"The 16,000:1 value is therefore an objective-cost coefficient ratio, not a claim that the optimizer will literally burn a fixed quantity of diesel to avoid one kWh of unmet load."*

---

## 4. Mathematical Distinction of Three Core Quantities

To prevent future conflation of objective weights, physical constants, and empirical outputs, the governance documentation explicitly separates three distinct concepts:

### A. Objective Coefficient Ratio
- **Formula**: $\frac{\$10,000/\text{kWh}}{\$0.625/\text{kWh}} = 16,000 : 1$
- **Nature**: Pure mathematical ratio of objective function penalty weights in `milp.py`.

### B. Physical / Configured Diesel Conversion
- **Formula**: $0.25\text{ L/kWh} \times \$2.50/\text{L} = \$0.625/\text{kWh}$
- **Nature**: Configured physical parameters (heat rate and fuel price) in `diesel.yaml`.

### C. Realized Dispatch Trade-off
- **Nature**: Actual fuel consumed per kWh of avoided unmet load across an execution trajectory.
- **Rule**: Trajectory-dependent operational outcome that CANNOT be derived from the 16,000:1 objective coefficient ratio alone.

---

## 5. V2 Evidence Context Preservation

The observed V2 campaign result remains locked and unchanged:
- **Treatment vs Control Aggregate Change**: $+11,350.2\text{ L}$ fuel vs $-30,543.8\text{ kWh}$ unmet load.
- **Observed Aggregate V2 Fuel / Unmet-Load Change Ratio**: $\frac{11,350.2\text{ L}}{30,543.8\text{ kWh}} \approx 0.3716\text{ L/kWh}$.
- **Label**: This value is explicitly labeled as the **Observed aggregate V2 fuel/unmet-load change ratio**. It is a trajectory-dependent empirical outcome from a representative trajectory set, NOT an objective coefficient or universal trade-off law.

---

## 6. Files Modified and Hash Audit

| File Name | Relative Path | Action |
| :--- | :--- | :--- |
| `POLARIS_EMS_GOVERNANCE_REVIEW.md` | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_GOVERNANCE_REVIEW.md` | MODIFIED (Replaced 4,000 L claim with governed clarification) |
| `POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_SPECIFICATION.md` | MODIFIED (Added ratio interpretation boundary) |
| `POLARIS_EMS_OBJECTIVE_WORDING_CORRECTION.md` | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_WORDING_CORRECTION.md` | CREATED (Master wording correction record) |
| `POLARIS_EMS_OBJECTIVE_WORDING_CORRECTION.json` | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_WORDING_CORRECTION.json` | CREATED (Machine-readable wording correction record) |
| `POLARIS_EMS_OBJECTIVE_WORDING_CORRECTION_HASH_AUDIT.csv` | `POLARIS_EMS_OBJECTIVE_SPECIFICATION/POLARIS_EMS_OBJECTIVE_WORDING_CORRECTION_HASH_AUDIT.csv` | CREATED (Wording correction cryptographic hash audit) |

---

## 7. Unchanged Governance Status

```
EMS_OBJECTIVE_WORDING_CORRECTION = PASS
OBJECTIVE_COEFFICIENT_RATIO = 16000_TO_1
RATIO_INTERPRETATION = OBJECTIVE_COST_COEFFICIENT_RATIO_ONLY
DIRECT_FUEL_PER_KWH_CLAIM = NOT_SUPPORTED
REALIZED_FUEL_TRADEOFF = TRAJECTORY_DEPENDENT
V2_EVIDENCE_LOCK = PASS
EMS_OBJECTIVE_SOURCE_AUDIT = PASS
OBJECTIVE_NUMERIC_RECONCILIATION = PASS
OBJECTIVE_REQUIREMENT_ALIGNMENT = PARTIALLY_ALIGNED
CURRENT_OBJECTIVE_STATUS = FROZEN_IMPLEMENTATION
FUEL_VS_RELIABILITY_TRADEOFF = NOT_SPECIFIED
OBJECTIVE_PRIORITY = NOT_SPECIFIED
OBJECTIVE_FORMULATION_POLICY = NOT_SPECIFIED
EMS_OBJECTIVE_SPECIFICATION = DRAFT_PENDING_AUTHORIZATION
OBJECTIVE_MODIFICATION = NOT_AUTHORIZED
EMS_MODIFICATION = NOT_AUTHORIZED
NEW_EMS_EXPERIMENT = NOT_AUTHORIZED
ANNUAL_RESULT_STATUS = REPRESENTATIVE_TRAJECTORY_SET
NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING = NOT_ESTABLISHED
NEXT_GOVERNED_STEP = HUMAN_REVIEW_OF_EXPLICIT_EMS_OBJECTIVE_SPECIFICATION
```
