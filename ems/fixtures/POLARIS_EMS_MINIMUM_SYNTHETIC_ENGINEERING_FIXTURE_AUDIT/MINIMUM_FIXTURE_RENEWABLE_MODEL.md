# POLARIS EMS — MINIMUM FIXTURE RENEWABLE MODEL

## 1. Executive Summary

This document specifies the minimum synthetic renewable generation model (Solar PV + Wind Generation + Zero-Renewable Stress Episode).

---

## 2. Renewable Generation Specifications

1. **Solar PV Generation ($P_{\text{solar}}(t)$)**: Diurnal half-sine profile peaking at $25,000\text{ W}$ during midday ($t=6\dots 18$), zero at night.
2. **Wind Generation ($P_{\text{wind}}(t)$)**: Synthetic generation curve averaging $10,000\text{ W}$.
3. **Zero-Renewable Stress Episode**: For timesteps $t=12\dots 18$, renewable generation is set to $P_{\text{solar}}=0, P_{\text{wind}}=0$ to exercise ECD resource endurance evaluation under zero-renewable baseline.

---

## 3. Provenance & Claim Boundary

```yaml
RENEWABLE_MODEL_CLASSIFICATION: SYNTHETIC_ENGINEERING_ASSUMPTION
STATION_IDENTITY: NONE
CLAIM_FIREWALL: Tests solver and ECD interface handling under renewable fluctuations. Does NOT establish Nuolja renewable yield.
```
