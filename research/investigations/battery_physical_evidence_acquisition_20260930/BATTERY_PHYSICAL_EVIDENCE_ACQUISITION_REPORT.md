# Battery Physical Evidence Acquisition & Degradation Model Research Report

```yaml
REPORT_ID: BATTERY_PHYSICAL_EVIDENCE_ACQUISITION_REPORT_V1
DATE: 2026-09-30
RESEARCH_PHASE: BATTERY_PHYSICAL_EVIDENCE_ACQUISITION
PREVIOUS_SENSITIVITY_CAMPAIGN: FROZEN
PRODUCTION_PROMOTION: NOT_AUTHORIZED
```

---

## 1. Executive Summary

This report documents the acquisition, source verification, parameter matrix evaluation, and gap analysis for physically defensible battery degradation evidence in POLARIS.

Following the formal freezing of the previous battery sensitivity campaign, this research phase evaluated whether sufficient physical evidence exists to replace the current unvalidated synthetic degradation proxy (`deg_penalty_per_wh = 0.00005`, or $0.050/kWh) and unvalidated synthetic round-trip efficiency assumption ($\eta_{rt} = 0.8464$) with an evidence-supported physical degradation model.

```yaml
DECISION_GATE: STATE_B_PARTIAL_EVIDENCE
BATTERY_PHYSICAL_EVIDENCE_STATUS: PARTIAL
DEGRADATION_MODEL_STATUS: PARTIALLY_IDENTIFIABLE
PRODUCTION_PROMOTION_STATUS: NOT_AUTHORIZED
```

---

## 2. Answers to Section 21 Plain Questions

### Q1: What battery evidence was actually found?
- **Tier A (Target System)**: `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json` specifies a 200.0 kWh nominal capacity, 50.0 kW max power, and 20–95% SOC window. However, its provenance header explicitly states `real_nuolja_data: false`.
- **Tier B (Manufacturer)**: Polar battery datasheets (e.g. Saft Sunica.plus Ni-Cd) were desk-verified, but specific cell manufacturer/model assignment for Nuolja is unconfirmed.
- **Tier C (Peer-Reviewed Experimental)**: Wang et al. (2011), Schmalstieg et al. (2014), and NREL BLAST (2018) microgrid degradation models were identified and desk-verified.

### Q2: What was actually acquired and verified in the workspace?
- Only synthetic engineering fixture files exist in the workspace. No site BMS telemetry logs or OEM cell datasheets are present in the repository.

### Q3: What battery chemistry/model is established?
- **Target Cell Chemistry**: `STATUS: UNKNOWN`. The cell chemistry is not documented in existing repository fixtures.
- **Target Battery Model**: `STATUS: UNCONFIRMED_OEM`.

### Q4: Which degradation parameters are directly supported?
- **Zero** parameters are directly supported by measured target site field telemetry. Nominal capacity (200 kWh) and usable capacity (150 kWh) are indirectly supported by synthetic fixture specifications.

### Q5: Which parameters remain assumptions?
- Round-trip efficiency (84.64%), charge efficiency (92%), discharge efficiency (92%), and degradation cost penalty ($0.050/kWh) remain **unvalidated synthetic assumptions**.

### Q6: What does the evidence say about efficiency?
- Peer-reviewed literature (NREL BLAST, Schmalstieg 2014) indicates physical round-trip efficiency for stationary LFP/NMC batteries ranges from **85.0% to 94.0%**, depending on C-rate and temperature. The current 84.64% is a plausible synthetic engineering proxy, but unmeasured on the target hardware.

### Q7: What does the evidence say about cycle life?
- Peer-reviewed experimental data (Wang 2011, NREL BLAST) indicates LFP stationary cells yield **3,000 to 6,000 Equivalent Full Cycles (EFC)** down to 80% remaining capacity.

### Q8: What does the evidence say about Depth of Discharge (DoD)?
- Degradation is strongly non-linear with DoD ($f(\text{DoD}) \propto \text{DoD}^{1.5}$). Shallow cycles (20–40% DoD) inflict substantially less degradation per discharged kWh than deep cycles (80–95% DoD).

### Q9: What does the evidence say about temperature?
- Capacity fade follows Arrhenius kinetics ($E_a \approx 31.7 \text{ kJ/mol}$). Sub-zero operating temperatures increase lithium plating risk unless thermal management maintains cell temperatures at $\ge 15^\circ\text{C}$.

### Q10: What does the evidence say about C-rate?
- Degradation scales with power factor $C_{\text{rate}}^{0.55}$. In POLARIS (50 kW max power / 200 kWh capacity = 0.25C max rate), C-rate stress is low.

### Q11: What does the evidence say about calendar aging?
- Calendar degradation follows square-root time kinetics ($t^{0.5}$) and accelerates at high average SOC ($>80\%$) and elevated temperatures.

### Q12: Can a defensible degradation model be constructed?
- **YES**, a candidate research-only physical degradation model ($Q_{\text{loss}} = Q_{\text{cycle}} + Q_{\text{calendar}}$) was specified in `BATTERY_DEGRADATION_MODEL_RESEARCH_SPEC.md` based on Tier C literature.

### Q13: Can an economic $/kWh degradation penalty be identified?
- **NO.** Physical capacity loss ($Q_{\text{loss}}$) cannot be converted into an empirical $/kWh penalty because target site stack replacement cost and polar freight transport invoices are **MISSING** (`ECONOMIC_DEGRADATION_COST: STATUS: NOT_IDENTIFIABLE`).

### Q14: What remains unknown?
- Target site OEM battery cell model, verified chemistry, site BMS telemetry, shelter thermal profile, and stack replacement cost.

### Q15: What physical measurements should be obtained next?
1. Target site battery nameplate photo / OEM datasheet.
2. 30 days of 1-minute site BMS telemetry logs.
3. Documented stack replacement invoice and polar freight cost ($/kWh).

### Q16: Has anything been promoted into production?
- **NO.** Production `milp.py`, `router.py`, battery configuration, and governance rules remain **100% untouched and unchanged**.

---

## 3. Final Decision Gate

```yaml
BATTERY_PHYSICAL_EVIDENCE:
  STATUS: PARTIAL

DEGRADATION_MODEL:
  STATUS: PARTIALLY_IDENTIFIABLE

PRODUCTION_PROMOTION:
  STATUS: NOT_AUTHORIZED
```

---

## 4. Final Governance Assertion

```yaml
GOVERNANCE:
  PREVIOUS_SENSITIVITY_CAMPAIGN:
    STATUS: FROZEN

  PHYSICAL_EVIDENCE_RESEARCH:
    STATUS: COMPLETE_FOR_CURRENT_SCOPE

  PRODUCTION_PARAMETER_CHANGE:
    NONE

  PRODUCTION_CODE_CHANGE:
    NONE

  GOVERNANCE_CHANGE:
    NONE

  CURRENT_DEGRADATION_PARAMETER:
    0.00005 $/Wh
    STATUS: UNVALIDATED_SYNTHETIC_PROXY

  CURRENT_EFFICIENCY:
    0.8464
    STATUS: UNVALIDATED_SYNTHETIC_ASSUMPTION

  PRODUCTION_PROMOTION:
    NOT_AUTHORIZED
```
