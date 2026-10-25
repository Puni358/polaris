# POLARIS Branch01 V2 Scientific Causal Wording Correction Report

## Governance Overview
This document specifies the mandated scientific and governance wording corrections for the POLARIS Branch01 V2 controlled EMS/MPC campaign forensic review.

---

## 1. Operational Causality vs. Forecast Accuracy
* **Previous Wording**: "Branch01's greater forecast accuracy caused the observed increase in diesel and reduction in unmet load."
* **Corrected Wording**: "Changing the solar forecast from control to treatment altered the optimizer's input sequence. Faced with lower predicted solar availability, the MILP optimizer dispatched diesel generation to avoid the high unmet load penalty ($10,000/kWh), reducing unmet load by 30,543.753 kWh at the cost of +11,350.179 L of additional fuel. Operational dispatch was driven by lower forecast solar magnitudes colliding with the MILP objective penalty structure, rather than forecast accuracy per se."
* **Governance Rationale**: An inaccurate zero-solar forecast would trigger the exact same diesel dispatch under the 16,000x penalty ratio ($10,000/kWh unmet load penalty vs $0.625/kWh fuel cost) as an accurate forecast predicting solar deficit. The physical driver is optimizer input magnitude, not accuracy per se.

---

## 2. MILP Optimality Formulation
* **Previous Wording**: "This behavior is mathematically optimal under the frozen MILP objective."
* **Corrected Wording**: "The observed dispatch is consistent with the frozen MILP objective and constraints given the forecast inputs available to the optimizer at each MPC origin."
* **Governance Rationale**: Prevents any misinterpretation that the dispatch represents globally optimal microgrid operation, optimal fuel consumption, or optimal performance relative to future realized truth.

---

## 3. Cloudy / Attenuated Regime Deficit Mechanism
* **Previous Wording**: "Branch01 accurately predicts solar deficits during cloudy/attenuated periods."
* **Corrected Wording**: "Branch01 predicts lower solar irradiance during low-irradiance regimes (MAE 96.033 W vs Control MAE 11,863.765 W). However, atmospheric cloud cover / attenuation was not explicitly isolated as a distinct regime in the forensic error artifacts."
* **Governance Rationale**: Persisted regime artifacts categorize samples strictly by irradiance thresholds (`NIGHT_ZERO`, `LOW_IRRADIANCE`, `MODERATE_HIGH_IRRADIANCE`) without dedicated cloud opacity or atmospheric transmittance features.

---

## 4. Branch01 Forecast Bias Direction
* **Previous Wording**: Implied that Branch01 is systematically pessimistic.
* **Corrected Wording**: "Branch01 exhibits near-zero overall bias (+17.234 W at H1), with slight positive bias in night (+67.178 W) and low irradiance (+90.299 W) regimes, and slight negative bias (-33.348 W) in moderate/high irradiance regimes. Branch01 is not systematically pessimistic."
* **Governance Rationale**: Empirical bias metrics establish near-zero mean bias, contradicting claims of systematic pessimism.

---

## 5. Annualization Boundary
* **Previous Wording**: Extrapolating campaign results to annual performance or site-specific station claims.
* **Corrected Wording**: "ANNUAL_RESULT_STATUS = REPRESENTATIVE_TRAJECTORY_SET. NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING = NOT_ESTABLISHED. No annualization scaling (x365) or real-Nuolja annual fuel claim is authorized."
* **Governance Rationale**: Enforces strict boundary conditions on the 173 representative trajectories (4,152 H1 steps).
