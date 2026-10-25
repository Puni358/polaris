# Battery Degradation Parameter Validation Matrix

```yaml
PHASE_ID: battery_degradation_model_validation_20260930
5_LAYER_SEPARATION: ENFORCED
PRODUCTION_PROMOTION: NOT_AUTHORIZED
```

## 1. Explicit 5-Layer Separation Architecture

1. **Layer 1 — Source-Derived Physical Evidence**: Wang et al. (2011), Schmalstieg et al. (2014), NREL BLAST (2018).
2. **Layer 2 — Research Model Structure**: Semi-empirical superposition $Q_{\text{loss}} = Q_{\text{cycle}} + Q_{\text{calendar}}$.
3. **Layer 3 — Research Model Parameters**: Power-law exponents ($\text{EFC}^{0.55}$, $\text{DoD}^{1.5}$, $t^{0.5}$) and activation energies ($31.7 \text{ kJ/mol}$, $24.5 \text{ kJ/mol}$).
4. **Layer 4 — Synthetic / Engineering Assumptions**: 200 kWh nominal capacity, 50 kW max power, $20^\circ\text{C}$ shelter temperature, 84.64% round-trip efficiency.
5. **Layer 5 — Production Optimizer Parameters**: `deg_penalty_per_wh = 0.00005` ($0.05/kWh) — **UNTOUCHED & FROZEN**.

---

## 2. Parameter Validation Matrix

| Parameter Symbol | Description | Value | Unit | Evidence Tier | Directly Measured? | Target Specific? | Uncertainty Range | Classification | Status |
| :--- | :--- | ---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **$M_{\text{cycle}}$** | Cycle pre-exponential factor | 0.0032 | — | Tier C | NO | NO | 0.0018 – 0.0055 | Same-Chemistry External | **PARTIALLY_VALIDATED** |
| **$\text{efc\_exp}$** | EFC power-law exponent | 0.55 | — | Tier C | NO | NO | 0.50 – 0.60 | Same-Chemistry External | **VALIDATED_BY_LITERATURE** |
| **$\text{dod\_exp}$** | DoD stress exponent | 1.50 | — | Tier C | NO | NO | 1.20 – 1.80 | Same-Chemistry External | **VALIDATED_BY_LITERATURE** |
| **$E_{a,\text{cycle}}$**| Cycle activation energy | 31.7 | kJ/mol | Tier C | NO | NO | 28.0 – 35.0 | Same-Chemistry External | **VALIDATED_BY_LITERATURE** |
| **$M_{\text{cal}}$** | Calendar pre-exponential factor | 0.0015 | day$^{-0.5}$ | Tier C | NO | NO | 0.0008 – 0.0028 | Same-Chemistry External | **PARTIALLY_VALIDATED** |
| **$\text{time\_exp}$** | SEI time exponent | 0.50 | — | Tier C | NO | NO | 0.45 – 0.55 | Generic Literature | **VALIDATED_BY_LITERATURE** |
| **$k_{\text{soc}}$** | SOC stress coefficient | 0.85 | — | Tier C | NO | NO | 0.60 – 1.10 | Generic Literature | **VALIDATED_BY_LITERATURE** |
| **$\eta_{\text{rt}}$** | Round-trip efficiency | 0.8464 | fraction | NONE | NO | NO | 0.810 – 0.940 | Model Assumption | **UNVALIDATED_SYNTHETIC_ASSUMPTION** |

---

## 3. Epistemic Conclusion

Generic literature values provide validated mathematical forms for $Q_{\text{cycle}}$ and $Q_{\text{calendar}}$, but **zero parameters are target-battery specific** due to missing site BMS telemetry and OEM datasheets.
