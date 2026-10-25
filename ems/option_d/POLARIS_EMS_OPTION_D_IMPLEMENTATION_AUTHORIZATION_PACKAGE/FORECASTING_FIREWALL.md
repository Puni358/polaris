# FORECASTING FIREWALL

## Scientific Isolation Contract

This document defines the strict firewall isolating scientific forecasting models, training scripts, and evaluation metrics from synthetic engineering fixtures and runtime EMS control logic.

---

## Forecasting Firewall Principles

1. **Zero Modifications to Forecasting Code**:
   - `system/forecasting/` directory, Stage8.1, and Branch01 training scripts MUST NOT be modified, re-executed, or retrained during Option D implementation.
2. **Synthetic Data Isolation**:
   - Synthetic engineering fixture data (e.g., 15/10/5 kW load profiles, 500 L fuel scenarios) enter the pipeline exclusively through `SyntheticFixtureProvider` at the integration interface level.
   - Fixture values MUST NOT be used to fit, evaluate, or fine-tune neural forecasting models or statistical time-series models.
3. **Model Artifact Integrity**:
   - Saved forecasting model weights and scalar parameter files remain 100% frozen and read-only.
