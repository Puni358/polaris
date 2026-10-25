# POLARIS — Stage 2: Cloud→GHI Candidate to PV Power Forecast Evaluation: Readiness Protocol

**Date:** 2026-10-10  
**Status:** READINESS AUDIT COMPLETE — PROXY-ONLY PHYSICAL MAPPING GOVERNED  
**Governing Context:** Follows accepted irradiance candidate validation in `cloud_to_ghi_nonlinear_experiment_20261010/` ($\gamma = 0.25$).  
**Scope:** Research-only evaluation of downstream photovoltaic electrical power consequences under authorized POLARIS D3 PV engineering transformation.

---

## 1. Readiness Audit Findings: Target Availability & Provenance

### A. Target Irradiance vs Measured PV Power
- **Target in Dataset:** `data/POLARIS_v0_1_future_weather_forecasts_2025.csv` contains meteorological forecast columns and ground-truth pyranometer global horizontal irradiance `actual_SW_IN` ($W/m^2$).
- **Instrument of Record:** Apogee SP110 Pyranometer at Nuolja Middle Station (ANS_NMS, $68.362^\circ N, 18.739^\circ E, 702\text{ m}$ elevation), SITES/Abisko Scientific Research Station.
- **Physical PV Hardware Telemetry:** **ABSENT.** The Nuolja Middle Station meteorological tower records environmental flux (solar irradiance, temperature, relative humidity, wind speed, pressure, snow depth). There is no operational grid-tied PV inverter, current shunt, or AC/DC power meter deployed at ANS_NMS.
- **Audit Conclusion:** **Actual measured PV electrical power targets DO NOT EXIST** in the POLARIS empirical dataset.

### B. Governed Evaluation Type: Proxy-Only Physical Mapping Analysis
- In accordance with Stage 2 Execution Requirements §1:
  > *"If actual PV power is unavailable, do not label a derived or synthetic value as observed power. You may perform a clearly labelled **proxy-only physical mapping analysis**, but state that actual PV power forecasting performance remains unevaluated. Do not fabricate missing inputs or silently introduce new assumptions."*
- Consequently, this evaluation is designated strictly as:
  **`PROXY-ONLY PHYSICAL MAPPING ANALYSIS`**
- Any derived values using `actual_SW_IN` transformed through the PV model are labelled as **`Modelled Proxy PV Power`**, never as empirical electrical observations.

---

## 2. Production PV Power Model Specification

Extracted directly from production reference `system/forecasting/implementations/causal_nwp_physics.py` and configuration `system/config/solar_pv.yaml`:

### Technical Parameters (D3 Engineering PV Transformation)
- **Status Label:** `PROTOTYPE_ASSUMPTION`
- **Array Surface Area ($A$):** $300.0\text{ m}^2$
- **Panel Efficiency ($\eta$):** $20.0\%$ ($0.20$)
- **System Performance Ratio ($PR$):** $85.0\%$ ($0.85$, accounting for inverter, wiring, and thermal derate)
- **Composite Linear Multiplier:**
  $$K_{\text{pv}} = A \times \eta \times PR = 300.0 \times 0.20 \times 0.85 = 51.0\text{ W per W/m}^2$$
- **Inverter Saturation Capacity ($P_{\max}$):** $60,000.0\text{ W}$ ($60.0\text{ kW}$ AC)
- **Night-Zero Handling:** If $\text{solar\_elevation} \le 0.0^\circ$ OR $\text{clear\_sky\_GHI} \le 0.0\text{ W/m}^2$, predicted GHI and power are identically $0.0\text{ W}$.
- **Mathematical Transformation:**
  $$P_{\text{pv}}(G) = \max\left(0.0, \min\left(51.0 \times G, 60000.0\right)\right)$$

---

## 3. Experimental Controls & Partition Freeze

1. **Candidate Freeze:** Nonlinear correction candidate frozen at $\gamma = 0.25$, without re-tuning:
   $$\text{GHI}_{\text{candidate}} = \text{clear\_sky\_GHI} \times (1 - \text{cloud\_fraction})^{0.25}$$
2. **Baseline Formulation:** Linear clear-sky attenuation baseline ($\gamma = 1.00$):
   $$\text{GHI}_{\text{baseline}} = \text{clear\_sky\_GHI} \times (1 - \text{cloud\_fraction})$$
3. **Data Partition:** Exactly 242 non-blind 2025 origins (5,808 hourly forecast steps; 1,873 daylight hours).
4. **Blind Window Firewall:** Exactly 123 blind origins (May 1–August 31, 2025; 2,952 hourly steps) are strictly filtered out immediately upon dataset loading prior to any metric calculation. Zero outcome values are accessed.
5. **Statistical Uncertainty:** Calendar-gap-aware segment-stratified stationary bootstrap (mean block length 10 days, $B=2,000$ replicates, seed `20261010`, percentile 95% CI).
