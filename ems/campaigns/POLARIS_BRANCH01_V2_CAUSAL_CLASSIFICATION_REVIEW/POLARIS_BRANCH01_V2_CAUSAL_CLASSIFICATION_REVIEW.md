# POLARIS Branch01 V2 Causal Classification & Evidence Review Audit Report

**Governance Status**: READ_ONLY_GOVERNANCE_CORRECTION  
**Audit Timestamp**: 2026-09-21T19:49:14Z  
**Authoritative Directory**: `POLARIS_BRANCH01_V2_CAUSAL_CLASSIFICATION_REVIEW/`

---

## Executive Governance Summary

The POLARIS Branch01 V2 controlled EMS/MPC campaign is complete and frozen. This audit performs a strict read-only evaluation of persisted forensic evidence to re-evaluate causal classifications and refine scientific wording.

No code, inference, forecasts, optimization, or telemetry were modified or rerun.

### Core Governance Conclusions
1. **Forecast Intervention to Dispatch**: **ESTABLISHED**  
   The causal sequence from control/treatment solar forecast intervention -> optimizer input vector modification -> MILP dispatch plan -> physical simulator telemetry is established by persisted provenance logs.
2. **Branch01 Relative Forecast Accuracy**: **ESTABLISHED**  
   Branch01 achieves an H1 MAE of 808.121 W vs Control MAE of 9,122.961 W relative to actual SW_IN, with lower error across all persisted regimes.
3. **Control Optimism**: **ESTABLISHED**  
   Control forecast bias is positive across all regimes (+8,380.026 W overall H1 bias, +3,433.930 W at night, +11,815.619 W in low irradiance).
4. **Cloudy Deficit Mechanism**: **PARTIALLY_ESTABLISHED**  
   Persisted artifacts categorize error by irradiance levels (`LOW_IRRADIANCE`), but atmospheric attenuation / cloud fraction is not explicitly isolated.
5. **Forecast Accuracy to Operational Causality**: **PARTIALLY_ESTABLISHED**  
   The operational dispatch change (+11,350.179 L fuel, -30,543.753 kWh unmet load) is caused by lower forecast solar magnitude colliding with the MILP $10,000/kWh unmet load penalty vs $0.625/kWh marginal fuel cost, rather than forecast accuracy per se.
6. **Optimizer Consistency**: **ESTABLISHED**  
   The observed dispatch is consistent with the frozen MILP objective and constraints given the forecast inputs available to the optimizer at each MPC origin.
7. **Final Causal Classification**: **MECHANISM_PARTIALLY_ESTABLISHED**

---

## Frozen V2 Metric Verification

The following aggregate results are strictly preserved from `POLARIS_BRANCH01_REMEDIATED_CAMPAIGN_V2`:

| Metric | Control | Treatment | Difference | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Completed Trajectories** | 173 | 173 | 0 | FROZEN_MATCH |
| **H1 Horizon Steps** | 4,152 | 4,152 | 0 | FROZEN_MATCH |
| **Fuel Consumption (L)** | 22,486.701 | 33,836.880 | +11,350.179 | FROZEN_MATCH |
| **Diesel Generation (kWh)** | 62,126.805 | 95,667.521 | +33,540.716 | FROZEN_MATCH |
| **Load Served (kWh)** | 75,480.485 | 106,024.238 | +30,543.753 | FROZEN_MATCH |
| **Unmet Load (kWh)** | 40,352.215 | 9,808.462 | -30,543.753 | FROZEN_MATCH |

---

## Detailed Issue Evidence Verification

### Issue 1 — Forecast-Error Evidence Verification
* **Branch01 Forecast Error**: ESTABLISHED (H1 MAE 808.121 W, Bias +17.234 W).
* **Control Forecast Error**: ESTABLISHED (H1 MAE 9,122.961 W, Bias +8,380.026 W).
* **Branch01 Lower Error in Regimes**: ESTABLISHED (Lower MAE in Night, Low Irradiance, and Mod/High Irradiance).
* **Control Systematic Optimism**: ESTABLISHED (Positive bias across all regimes).
* **Branch01 Systematic Pessimism**: NOT_ESTABLISHED (Near-zero overall bias +17.234 W).
* **Cloudy/Attenuated Concentration**: PARTIALLY_ESTABLISHED (Irradiance regimes persisted; cloudiness index not isolated).
* **Temporal Alignment**: ESTABLISHED (Per-trajectory logs confirm alignment).
* **Attribution specifically to Forecast Accuracy**: PARTIALLY_ESTABLISHED (Magnitude collision with MILP penalties drives dispatch).

### Issue 2 — Claim A: Forecast Intervention to Dispatch
* **Classification**: `FORECAST_INTERVENTION_TO_DISPATCH = ESTABLISHED`
* **Evidence**: Direct lineage from solar forecast input to MILP solve to telemetry outputs.

### Issue 3 — Claim B: Relative Forecast Accuracy
* **Classification**: `BRANCH01_RELATIVE_FORECAST_ACCURACY = ESTABLISHED`
* **Evidence**: 808.121 W vs 9,122.961 W MAE at H1 across 4,152 timesteps.

### Issue 4 — Claim C: Cloudy / Attenuated Deficit Mechanism
* **Classification**: `CLOUDY_DEFICIT_MECHANISM = PARTIALLY_ESTABLISHED`
* **Evidence**: Low irradiance regime evaluated; explicit atmospheric cloudiness state missing.

### Issue 5 — Control Optimism
* **Classification**: `CONTROL_OPTIMISM = ESTABLISHED`
* **Evidence**: Positive bias in all persisted regime records.

### Issue 6 — Claim C: Operational Causality
* **Classification**: `FORECAST_ACCURACY_TO_OPERATIONAL_CAUSALITY = PARTIALLY_ESTABLISHED`
* **Evidence**: Optimizer responds to predicted deficit magnitude under $10,000/kWh penalty, not accuracy per se.

### Issue 7 — Claim D: MILP Consistency Wording
* **Classification**: `OPTIMIZER_CONSISTENCY = ESTABLISHED`
* **Correct Wording**: "The observed dispatch is consistent with the frozen MILP objective and constraints given the forecast inputs available to the optimizer at each MPC origin."

### Issue 8 — Final Causal Classification Selection
* **Classification**: `FINAL_CAUSAL_CLASSIFICATION = MECHANISM_PARTIALLY_ESTABLISHED`

---

## Annualization Boundary Governance
* `ANNUAL_RESULT_STATUS = REPRESENTATIVE_TRAJECTORY_SET`
* `NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING = NOT_ESTABLISHED`

---

## Final Governance Status Output

```
V2_RESULTS_CHANGED = NO
V2_ARTIFACTS_CHANGED = NO
MODEL_CHANGED = NO
NEW_INFERENCE = NO
NEW_OPTIMIZATION = NO
NEW_SIMULATION = NO
NEW_FORECASTS = NO
CAUSAL_CLASSIFICATION_REVIEW = COMPLETE
FINAL_CAUSAL_CLASSIFICATION = MECHANISM_PARTIALLY_ESTABLISHED
FORECAST_INTERVENTION_TO_DISPATCH = ESTABLISHED
BRANCH01_RELATIVE_FORECAST_ACCURACY = ESTABLISHED
CLOUDY_DEFICIT_MECHANISM = PARTIALLY_ESTABLISHED
CONTROL_OPTIMISM = ESTABLISHED
FORECAST_ACCURACY_TO_OPERATIONAL_CAUSALITY = PARTIALLY_ESTABLISHED
OPTIMIZER_CONSISTENCY = ESTABLISHED
NEXT_GOVERNED_STEP = EMS_OBJECTIVE_REQUIREMENTS_REVIEW
```
