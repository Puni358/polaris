# POLARIS — Target Battery Contradiction Register

> **RESEARCH SCENARIO / SYNTHETIC BATTERY BOUNDARY / NOT TARGET-HARDWARE EVIDENCE**

## 1. Overview

This register documents all identified contradictions, mismatches, and conflicting assertions across workspace files, synthetic fixtures, literature assumptions, and site documentation regarding the target battery system.

---

## 2. Contradiction Register Table

| Conflict ID | Claim A | Source A (Tier) | Claim B | Source B (Tier) | Reason for Conflict | Resolution Status |
|---|---|---|---|---|---|---|
| **CON-001** | POLARIS operates a 200.0 kWh / 50.0 kW BESS | `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json` (Synthetic) | SITES Nuolja is a weather field station with no 200 kWh BESS | SITES / Swedish Polar Research Secretariat (Tier A) | Synthetic benchmark fixture created for algorithm testing | **RESOLVED**: Claim A is synthetic engineering fixture only; Claim B is site ground truth. |
| **CON-002** | Battery degradation cost is $0.05/kWh | `milp.py` production config (Synthetic Proxy) | Degradation economics cannot be identified without procurement/logistics data | Economic Audit (Section 11) | Arbitrary wear surrogate used to prevent unconstrained cycling | **RESOLVED**: $0.05/kWh is unvalidated proxy; target economic cost remains NOT IDENTIFIABLE. |
| **CON-003** | Battery round-trip efficiency is 84.64% | POLARIS baseline config (Synthetic Assumption) | Cell efficiency varies dynamically with C-rate, SOC, and temperature (81.0–95.0%) | Physical Battery Literature (Tier C) | Static efficiency assumption simplified for linear MILP | **RESOLVED**: 84.64% is synthetic research baseline assumption. |
| **CON-004** | Nuolja battery experiences sub-zero cell degradation | Cold Climate Polar Microgrid Assumptions | Stationary batteries in Arctic installations are housed in climate-controlled containers | Polar Station Engineering Reports (Tier B) | Assuming outdoor ambient temp equals cell temp ignores container HVAC | **RESOLVED**: Cell temp log is ABSENT; cannot assume cell temp equals ambient. |

---

## 3. Disambiguation Assertion

No evidence from external demonstration projects or generic polar research stations (e.g., Troll Station, Antarctica or Svalbard microgrids) may be conflated with SITES Nuolja Middle Station. Every target claim must pass an explicit site identity check.
