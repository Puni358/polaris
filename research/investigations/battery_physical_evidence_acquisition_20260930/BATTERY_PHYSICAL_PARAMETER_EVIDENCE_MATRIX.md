# Battery Physical Parameter Evidence Matrix

```yaml
PHASE_ID: battery_physical_evidence_acquisition_20260930
EVIDENCE_EVALUATION: PARTIAL
PRODUCTION_PROMOTION: NOT_AUTHORIZED
```

## 1. Parameter Evidence Assessment Matrix

| Parameter | Required? | Evidence Available? | Evidence Tier | Directly Measured? | Target-Battery Specific? | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Battery Chemistry** | **YES** | NO | NONE | NO | NO | **UNVERIFIED** |
| **Nominal Capacity (200 kWh)** | **YES** | YES | Tier A (Target) | NO | YES | **INDIRECTLY_SUPPORTED** |
| **Usable Capacity (150 kWh)** | **YES** | YES | Tier A (Target) | NO | YES | **INDIRECTLY_SUPPORTED** |
| **Round-Trip Efficiency (84.64%)** | **YES** | YES | Tier C (Experimental) | NO | NO | **MODEL_STRUCTURAL_ONLY** |
| **Charge Efficiency (92%)** | **YES** | NO | NONE | NO | NO | **UNVERIFIED** |
| **Discharge Efficiency (92%)** | **YES** | NO | NONE | NO | NO | **UNVERIFIED** |
| **Cycle Life (EFC)** | **YES** | YES | Tier C (Experimental) | NO | NO | **MODEL_STRUCTURAL_ONLY** |
| **Capacity Fade Model** | **YES** | YES | Tier C (Experimental) | NO | NO | **MODEL_STRUCTURAL_ONLY** |
| **DoD Dependence** | **YES** | YES | Tier C (Experimental) | NO | NO | **MODEL_STRUCTURAL_ONLY** |
| **Temperature Dependence** | **YES** | YES | Tier C (Experimental) | NO | NO | **MODEL_STRUCTURAL_ONLY** |
| **C-rate Dependence** | **YES** | YES | Tier C (Experimental) | NO | NO | **MODEL_STRUCTURAL_ONLY** |
| **Calendar Aging** | **YES** | YES | Tier C (Experimental) | NO | NO | **MODEL_STRUCTURAL_ONLY** |
| **SOC-Window Dependence** | NO | YES | Tier C (Experimental) | NO | NO | **MODEL_STRUCTURAL_ONLY** |
| **End-of-Life Criterion (80%)**| **YES** | YES | Tier C (Experimental) | NO | NO | **MODEL_STRUCTURAL_ONLY** |
| **Replacement Cost ($/kWh)** | **YES** | NO | NONE | NO | NO | **MISSING** |

---

## 2. Parameter Classifications Summary

- **Directly Supported (0 parameters)**: No parameters are directly measured from verified target station field telemetry.
- **Indirectly Supported (2 parameters)**: Nominal capacity (200.0 kWh) and Usable capacity (150.0 kWh) from synthetic engineering fixture `POLARIS_EMS_MINIMUM_SYNTHETIC_FIXTURE.json`.
- **Model Structural Only (9 parameters)**: Mathematical formulations for cycle fade, calendar aging, DoD stress, C-rate, temperature, and EOL thresholds derived from peer-reviewed LFP/NMC literature (Wang 2011, Schmalstieg 2014, NREL BLAST).
- **Unverified (3 parameters)**: Cell chemistry, charge efficiency, discharge efficiency.
- **Missing (1 parameter)**: Target station battery stack replacement and logistics delivery cost ($/kWh).

---

## 3. Epistemic Conclusion

```text
EVIDENCE_STATUS = PARTIAL (Tier C literature available, Tier A/B target evidence missing)
```

While peer-reviewed literature allows formulating a candidate semi-empirical physical degradation model structure, the lack of target cell chemistry, manufacturer datasheets, BMS logs, and replacement costs prevents converting physical degradation into an empirical production optimizer penalty.
