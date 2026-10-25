# Battery Degradation Uncertainty & Applicability Analysis

```yaml
PHASE_ID: battery_degradation_model_validation_20260930
UNCERTAINTY_BOUNDS: PROPAGATED
PRODUCTION_PROMOTION: NOT_AUTHORIZED
```

## 1. Uncertainty Quantification & Bounded Envelope

Uncertainty ranges reported in Tier C peer-reviewed literature were propagated through the candidate physical degradation model across the 8,784-hour annual trajectory:

| Parameter | Central Value | Lower Bound | Upper Bound | Impact on Annual $Q_{\text{loss}}$ |
| :--- | ---: | ---: | ---: | :--- |
| **$M_{\text{cycle}}$** | 0.0032 | 0.0018 | 0.0055 | $\pm 0.00005\%$ capacity loss |
| **$\text{dod\_exp}$** | 1.50 | 1.20 | 1.80 | $\pm 0.00003\%$ capacity loss (low DoD cycling) |
| **$M_{\text{cal}}$** | 0.0015 | 0.0008 | 0.0028 | **$\pm 0.04400\%$ capacity loss (primary driver)** |
| **$E_{a,\text{cal}}$** | 24.5 kJ/mol | 20.0 kJ/mol | 30.0 kJ/mol | $\pm 0.03500\%$ capacity loss |
| **Total $Q_{\text{loss}}$ Range** | **0.0961% / yr** | **0.0540% / yr** | **0.2850% / yr** | **Bounded Envelope** |

---

## 2. Applicability Limits & Extrapolation Warnings

### A. Temperature Extrapolation Risk
- **Validated Domain**: $15^\circ\text{C}$ to $45^\circ\text{C}$ controlled ambient.
- **Unheated Shelter Risk ($-10^\circ\text{C}$ to $-30^\circ\text{C}$)**: While Arrhenius equations mathematically predict negligible chemical aging at freezing temperatures, **lithium plating** becomes the dominant degradation mechanism during charging. Applying the candidate Arrhenius model below $0^\circ\text{C}$ without thermal enclosure heating is classified as **EXTRAPOLATION_RISK**.

### B. Chemistry Transferability Risk
- **Chemistry Status**: `STATUS: UNKNOWN`. Applying an LFP-derived model (Wang 2011) to an unconfirmed cell chemistry introduces structural model uncertainty.

### C. Economic Conversion Gap
- Physical degradation (0.054% to 0.285% capacity fade per year) cannot be converted into an empirical $/kWh penalty without target site stack replacement invoices and polar transport cost data.
