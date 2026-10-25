# Battery Physical Evidence Source Register

```yaml
PHASE_ID: battery_physical_evidence_acquisition_20260930
PREVIOUS_CAMPAIGN: FROZEN
PRODUCTION_PROMOTION: NOT_AUTHORIZED
```

## 1. Governance Starting Facts

Before recording acquired sources, the following facts from the frozen campaign are established:

- **Current Degradation Parameter**: `0.00005 $/Wh` ($0.050/kWh) — `UNVALIDATED_SYNTHETIC_PROXY`
- **Current Battery Efficiency**: `0.8464` (84.64% round-trip) — `UNVALIDATED_SYNTHETIC_ASSUMPTION`
- **Physical Degradation Model Supported**: `NO`
- **Production Parameter Change**: `NOT_AUTHORIZED`

---

## 2. Acquired Evidence Source Register

| Source ID | Title / Document | Source Type | Evidence Tier | Acquired in Workspace? | Chemistry | Directly Supports | Limitations |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **SRC-TIER-A-01** | POLARIS EMS Minimum Synthetic Engineering Fixture V1 | Synthetic Fixture | **Tier A (Target)** | **YES** | UNKNOWN | 200 kWh Capacity, 50 kW Power, 20-95% SOC | Stated `real_nuolja_data: false`; no physical wear data. |
| **SRC-TIER-B-01** | Saft Sunica.plus Technical Datasheet | Manufacturer Datasheet | **Tier B (Mfr)** | NO (Desk Verified) | Ni-Cd | Cold temp specs (-50C), 8,000 cycles @ 20% DoD | Ni-Cd chemistry; POLARIS defaults use Li-ion SOC bounds. |
| **SRC-TIER-C-01** | Wang et al. (2011) LFP Cycle-Life Model (J. Power Sources) | Peer-Reviewed Paper | **Tier C (Experimental)** | NO (Desk Verified) | LFP | Semi-empirical capacity fade vs Ah & Temperature | Requires cell-specific calibration parameters. |
| **SRC-TIER-C-02** | Schmalstieg et al. (2014) Full Lifetime Model | Peer-Reviewed Paper | **Tier C (Experimental)** | NO (Desk Verified) | NMC / LFP | Superposition of calendar & cycle aging vs DoD/SOC | Calibrated at ambient 0C-45C. |
| **SRC-TIER-C-03** | NREL BLAST Microgrid Lifetime Model (2018) | National Lab Report | **Tier C (Experimental)** | NO (Desk Verified) | LFP / NMC | Round-trip efficiency vs C-rate, degradation wear scaling | Generic stack cost ($250-400/kWh) assumption. |

---

## 3. Source Hierarchy & Provenance Evaluation

1. **Tier A (Target System Evidence)**:
   - Only synthetic fixture `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json` exists in workspace.
   - Field telemetry, station BMS logs, and physical battery cell datasheets for the target station remain **ABSENT**.
2. **Tier B (Manufacturer Evidence)**:
   - Polar-rated battery datasheets (e.g. Saft Sunica Ni-Cd, Tesla Megapack LFP) establish physical bounds, but specific OEM cell assignment for Nuolja is unconfirmed.
3. **Tier C (Peer-Reviewed Experimental Evidence)**:
   - High-fidelity semi-empirical models (Wang 2011, Schmalstieg 2014, NREL BLAST) provide validated mathematical structures for cycle aging, DoD stress, and calendar fade.
4. **Tier D & E (Lab & Literature)**:
   - Formulates the mathematical specification for research-only degradation modeling.

---

## 4. Epistemic Classification

```yaml
TARGET_BATTERY_CHEMISTRY: UNKNOWN
TARGET_BATTERY_SPECIFICATION: UNCONFIRMED_OEM
EMPIRICAL_TELEMETRY: ABSENT
EVIDENCE_CLASS: TIER_C_SEMI_EMPIRICAL_LITERATURE
PRODUCTION_PROMOTION: BLOCKED
```
