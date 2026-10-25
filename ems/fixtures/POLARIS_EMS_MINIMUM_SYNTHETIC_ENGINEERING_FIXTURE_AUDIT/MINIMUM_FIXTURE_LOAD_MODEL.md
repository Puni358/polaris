# POLARIS EMS — MINIMUM FIXTURE LOAD MODEL

## 1. Executive Summary

This document specifies the minimum synthetic load model required for software architecture demonstration.

---

## 2. Load Model Structure

```
Total Synthetic Demand P_total(t) = P_critical(t) + P_noncritical(t)
  ├── Protected Critical Load P_critical(t): 30,000 W (Synthetic Baseline)
  └── Noncritical Load P_noncritical(t): 15,000 W (Synthetic Flexible Load)
```

- **Protected Critical Load ($P_{\text{critical}}(t)$)**: $30,000\text{ W}$ constant. Exercises Rule D1/D2 protected service priority.
- **Noncritical Load ($P_{\text{noncritical}}(t)$)**: $15,000\text{ W}$ curtailable/deferrable load. Exercises Option D load shedding and proves battery energy is NOT spent on noncritical loads during safe-state fallback.

---

## 3. Provenance & Claim Boundary

```yaml
LOAD_MODEL_CLASSIFICATION: SYNTHETIC_ENGINEERING_ASSUMPTION
STATION_IDENTITY: NONE
EMPIRICAL_STATUS: NOT_ESTABLISHED
CLAIM_FIREWALL: Must NOT be reported as Nuolja station demand. Used solely for software control-flow demonstration.
```
