# Forecast Provider Trace (`FORECAST_PROVIDER_TRACE.md`)

**FORENSIC RECONCILIATION**: POLARIS EMS GAP19 — Final EBR Time-Index / Forecast-Semantics Audit  
**VERDICT**: `CONFIRMED`

---

## 1. Forecast Provider Vector Construction

- Origin $t_{\text{now}}$: Observation time of current StationState.
- Horizon Target Timestamps: $t_{\text{now}} + 1\text{h}, t_{\text{now}} + 2\text{h}, \dots, t_{\text{now}} + 24\text{h}$.
- Index $k=0$: Predictions for the upcoming first hour. Zero historical/observed actuals placed in $k=0$.

```text
FORECAST_PROVIDER_INDEXING = CAUSAL_FUTURE_PREDICTION
```
