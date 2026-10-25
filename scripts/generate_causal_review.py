import os
import hashlib
import json

base_dir = "/home/punith-bs/01polaris (Copy)/ems/campaigns/POLARIS_BRANCH01_V2_CAUSAL_CLASSIFICATION_REVIEW"
os.makedirs(base_dir, exist_ok=True)

# 1. Evidence Matrix CSV
matrix_csv_path = os.path.join(base_dir, "POLARIS_BRANCH01_V2_CAUSAL_EVIDENCE_MATRIX.csv")
matrix_csv_content = """CLAIM_ID,CLAIM,EVIDENCE_SOURCE,EVIDENCE_PRESENT,EVIDENCE_STRENGTH,CLASSIFICATION,RATIONALE
CLAIM_A,forecast intervention -> optimizer input -> dispatch,POLARIS_BRANCH01_V2_FORECAST_PROVENANCE.csv; POLARIS_BRANCH01_V2_SOLAR_DISPATCH_FORENSIC.csv; POLARIS_BRANCH01_V2_TRAJECTORY_CAUSAL_SUMMARY.csv,YES,STRONG,ESTABLISHED,Changing solar forecast intervention changed optimizer input vectors producing distinct MILP dispatch plans and simulator telemetry (+11350.179 L fuel -30543.753 kWh unmet load).
CLAIM_B,Branch01 relative forecast accuracy,POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_HORIZON.csv; POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_REGIME.csv,YES,STRONG,ESTABLISHED,Branch01 achieves 808.121 W MAE vs Control 9122.961 W MAE at H1 across 4152 samples. Lower MAE holds across NIGHT_ZERO LOW_IRRADIANCE MODERATE_HIGH_IRRADIANCE regimes.
CLAIM_C,cloudy/attenuated deficit prediction,POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_REGIME.csv,PARTIAL,MODERATE,PARTIALLY_ESTABLISHED,Low irradiance regime shows lower error (96.033 W vs 11863.765 W MAE) but cloudiness/atmospheric attenuation index is not explicitly isolated from solar zenith angle.
CLAIM_D,control forecast optimism,POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_HORIZON.csv; POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_REGIME.csv,YES,STRONG,ESTABLISHED,Control exhibits positive bias across all persisted regimes (+8380.026 W overall H1 +3433.93 W night +11815.619 W low irradiance +10182.119 W mod/high).
CLAIM_E,forecast accuracy -> operational outcome,POLARIS_BRANCH01_V2_OBJECTIVE_AUDIT.md; POLARIS_BRANCH01_V2_TRAJECTORY_CAUSAL_SUMMARY.csv,PARTIAL,MODERATE,PARTIALLY_ESTABLISHED,Operational dispatch change is driven by lower forecast solar magnitude colliding with the $10000/kWh unmet load penalty vs $0.625/kWh fuel cost not forecast accuracy per se.
CLAIM_F,observed dispatch consistent with frozen MILP objective,POLARIS_BRANCH01_V2_OBJECTIVE_AUDIT.md,YES,STRONG,ESTABLISHED,The observed dispatch is consistent with the frozen MILP objective and constraints given the forecast inputs available to the optimizer at each MPC origin.
ISSUE1_A,Branch01 forecast error relative to actual SW_IN,POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_HORIZON.csv,YES,STRONG,ESTABLISHED,H1 MAE is 808.121 W and bias is +17.234 W relative to mean actual SW_IN of 4565.219 W across 4152 H1 steps.
ISSUE1_B,Control forecast error relative to actual SW_IN,POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_HORIZON.csv,YES,STRONG,ESTABLISHED,H1 MAE is 9122.961 W and bias is +8380.026 W relative to mean actual SW_IN of 4565.219 W across 4152 H1 steps.
ISSUE1_C,Branch01 lower error than control in relevant regimes,POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_REGIME.csv,YES,STRONG,ESTABLISHED,Branch01 MAE is lower than Control across NIGHT_ZERO (67.178 W vs 3433.930 W) LOW_IRRADIANCE (96.033 W vs 11863.765 W) and MODERATE_HIGH_IRRADIANCE (1446.770 W vs 11559.646 W).
ISSUE1_D,Control systematically optimistic,POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_REGIME.csv,YES,STRONG,ESTABLISHED,Control bias is positive across all regimes (+3433.930 W night +11815.619 W low irradiance +10182.119 W mod/high irradiance).
ISSUE1_E,Branch01 systematically pessimistic,POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_REGIME.csv,YES,STRONG,NOT_ESTABLISHED,Branch01 overall H1 bias is +17.234 W (+67.178 W night +90.299 W low irradiance -33.348 W mod/high irradiance) demonstrating near-zero overall bias.
ISSUE1_F,Difference specifically concentrated in cloudy/attenuated periods,POLARIS_BRANCH01_V2_FORECAST_ERROR_BY_REGIME.csv,PARTIAL,MODERATE,PARTIALLY_ESTABLISHED,Persisted artifacts categorize by irradiance magnitude but do not isolate atmospheric cloud cover attenuation index.
ISSUE1_G,Forecast difference temporally aligns with dispatch differences,POLARIS_BRANCH01_V2_SOLAR_DISPATCH_FORENSIC.csv; POLARIS_BRANCH01_V2_TRAJECTORY_CAUSAL_SUMMARY.csv,YES,STRONG,ESTABLISHED,Per-trajectory time-series forensic logs show tight alignment between origin forecast solar inputs and optimizer dispatch decisions.
ISSUE1_H,Evidence sufficient to attribute operational difference specifically to forecast accuracy,POLARIS_BRANCH01_V2_CAUSAL_CHAIN.md; POLARIS_BRANCH01_V2_OBJECTIVE_AUDIT.md,PARTIAL,MODERATE,PARTIALLY_ESTABLISHED,Intervention chain is established but dispatch changes stem from lower forecast magnitudes triggering MILP unmet load penalties rather than accuracy itself.
"""
with open(matrix_csv_path, "w") as f:
    f.write(matrix_csv_content)

# 2. Causal Classification Review JSON
review_json_path = os.path.join(base_dir, "POLARIS_BRANCH01_V2_CAUSAL_CLASSIFICATION_REVIEW.json")
review_json_data = {
  "audit_id": "POLARIS_BRANCH01_V2_CAUSAL_CLASSIFICATION_REVIEW",
  "audit_mode": "READ_ONLY_GOVERNANCE_CORRECTION",
  "timestamp": "2026-09-21T19:49:14Z",
  "governance_status": {
    "V2_RESULTS_CHANGED": "NO",
    "V2_ARTIFACTS_CHANGED": "NO",
    "MODEL_CHANGED": "NO",
    "NEW_INFERENCE": "NO",
    "NEW_OPTIMIZATION": "NO",
    "NEW_SIMULATION": "NO",
    "NEW_FORECASTS": "NO",
    "CAUSAL_CLASSIFICATION_REVIEW": "COMPLETE"
  },
  "final_causal_classifications": {
    "FINAL_CAUSAL_CLASSIFICATION": "MECHANISM_PARTIALLY_ESTABLISHED",
    "FORECAST_INTERVENTION_TO_DISPATCH": "ESTABLISHED",
    "BRANCH01_RELATIVE_FORECAST_ACCURACY": "ESTABLISHED",
    "CLOUDY_DEFICIT_MECHANISM": "PARTIALLY_ESTABLISHED",
    "CONTROL_OPTIMISM": "ESTABLISHED",
    "FORECAST_ACCURACY_TO_OPERATIONAL_CAUSALITY": "PARTIALLY_ESTABLISHED",
    "OPTIMIZER_CONSISTENCY": "ESTABLISHED"
  },
  "issue_evidence_status": {
    "ISSUE1_A_BRANCH01_ERROR_RELATIVE_TO_ACTUAL": "ESTABLISHED",
    "ISSUE1_B_CONTROL_ERROR_RELATIVE_TO_ACTUAL": "ESTABLISHED",
    "ISSUE1_C_BRANCH01_LOWER_ERROR_IN_REGIMES": "ESTABLISHED",
    "ISSUE1_D_CONTROL_SYSTEMATICALLY_OPTIMISTIC": "ESTABLISHED",
    "ISSUE1_E_BRANCH01_SYSTEMATICALLY_PESSIMISTIC": "NOT_ESTABLISHED",
    "ISSUE1_F_CLOUDY_ATTENUATION_CONCENTRATION": "PARTIALLY_ESTABLISHED",
    "ISSUE1_G_TEMPORAL_ALIGNMENT_WITH_DISPATCH": "ESTABLISHED",
    "ISSUE1_H_ATTRIBUTION_TO_ACCURACY_SPECIFICALLY": "PARTIALLY_ESTABLISHED"
  },
  "frozen_v2_results": {
    "TRAJECTORIES": 173,
    "H1_STEPS": 4152,
    "CONTROL_FUEL": 22486.701,
    "TREATMENT_FUEL": 33836.880,
    "FUEL_DIFFERENCE": 11350.179,
    "CONTROL_DIESEL": 62126.805,
    "TREATMENT_DIESEL": 95667.521,
    "DIESEL_DIFFERENCE": 33540.716,
    "CONTROL_LOAD_SERVED": 75480.485,
    "TREATMENT_LOAD_SERVED": 106024.238,
    "LOAD_SERVED_DIFFERENCE": 30543.753,
    "CONTROL_UNMET_LOAD": 40352.215,
    "TREATMENT_UNMET_LOAD": 9808.462,
    "UNMET_LOAD_DIFFERENCE": -30543.753
  },
  "annualization_boundary": {
    "ANNUAL_RESULT_STATUS": "REPRESENTATIVE_TRAJECTORY_SET",
    "NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING": "NOT_ESTABLISHED"
  },
  "next_governed_step": "EMS_OBJECTIVE_REQUIREMENTS_REVIEW"
}
with open(review_json_path, "w") as f:
    json.dump(review_json_data, f, indent=2)

# 3. Causal Wording Correction JSON
wording_json_path = os.path.join(base_dir, "POLARIS_BRANCH01_V2_CAUSAL_WORDING_CORRECTION.json")
wording_json_data = {
  "audit_name": "POLARIS_BRANCH01_V2_CAUSAL_WORDING_CORRECTION",
  "audit_mode": "READ_ONLY_GOVERNANCE_CORRECTION",
  "timestamp": "2026-09-21T19:49:14Z",
  "wording_corrections": [
    {
      "correction_id": "CORRECTION_OPERATIONAL_DRIVER",
      "target_claim": "Forecast Accuracy vs Operational Causality",
      "previous_wording": "Branch01's greater forecast accuracy caused the observed increase in diesel and reduction in unmet load.",
      "corrected_wording": "Changing the solar forecast from control to treatment altered the optimizer's input sequence. Faced with lower predicted solar availability, the MILP optimizer dispatched diesel generation to avoid the high unmet load penalty ($10,000/kWh), reducing unmet load by 30,543.753 kWh at the cost of +11,350.179 L of additional fuel. Operational dispatch was driven by lower forecast solar magnitudes colliding with the MILP objective penalty structure, rather than forecast accuracy per se.",
      "governance_rationale": "An inaccurate zero forecast would produce the exact same diesel dispatch as an accurate forecast predicting solar deficit. The physical cause of dispatch is input magnitude colliding with objective weights."
    },
    {
      "correction_id": "CORRECTION_MILP_OPTIMALITY",
      "target_claim": "MILP Consistency",
      "previous_wording": "This behavior is mathematically optimal under the frozen MILP objective.",
      "corrected_wording": "The observed dispatch is consistent with the frozen MILP objective and constraints given the forecast inputs available to the optimizer at each MPC origin.",
      "governance_rationale": "Avoids implying global POLARIS optimality, optimal fuel consumption, optimal reliability, or real-world optimality under future realized truth."
    },
    {
      "correction_id": "CORRECTION_CLOUDY_DEFICIT",
      "target_claim": "Cloudy/Attenuated Mechanism",
      "previous_wording": "Branch01 accurately predicts solar deficits during cloudy/attenuated periods.",
      "corrected_wording": "Branch01 predicts lower solar irradiance during low-irradiance regimes (MAE 96.033 W vs Control MAE 11,863.765 W). However, atmospheric cloud cover / attenuation was not explicitly isolated as a distinct regime in the forensic error artifacts.",
      "governance_rationale": "Regime table classifies by irradiance magnitude (NIGHT_ZERO, LOW_IRRADIANCE, MODERATE_HIGH_IRRADIANCE) without dedicated cloudiness index variables."
    },
    {
      "correction_id": "CORRECTION_BRANCH01_PESSIMISM",
      "target_claim": "Branch01 Bias Direction",
      "previous_wording": "Branch01 is systematically pessimistic.",
      "corrected_wording": "Branch01 exhibits near-zero overall bias (+17.234 W at H1), with slight positive bias in night (+67.178 W) and low irradiance (+90.299 W) regimes, and slight negative bias (-33.348 W) in moderate/high irradiance regimes. Branch01 is not systematically pessimistic.",
      "governance_rationale": "Empirical bias values do not support systematic pessimism."
    },
    {
      "correction_id": "CORRECTION_ANNUALIZATION",
      "target_claim": "Annualization Scaling",
      "previous_wording": "Annualized fuel claims or annual station-specific projections.",
      "corrected_wording": "ANNUAL_RESULT_STATUS = REPRESENTATIVE_TRAJECTORY_SET. NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING = NOT_ESTABLISHED. No annualization scaling (x365) or real-Nuolja annual fuel claim is authorized.",
      "governance_rationale": "Campaign is conducted over 173 representative trajectories (4,152 H1 steps). Extrapolation is governed as NOT_ESTABLISHED."
    }
  ]
}
with open(wording_json_path, "w") as f:
    json.dump(wording_json_data, f, indent=2)

# 4. Causal Wording Correction MD
wording_md_path = os.path.join(base_dir, "POLARIS_BRANCH01_V2_CAUSAL_WORDING_CORRECTION.md")
wording_md_content = """# POLARIS Branch01 V2 Scientific Causal Wording Correction Report

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
"""
with open(wording_md_path, "w") as f:
    f.write(wording_md_content)

# 5. Causal Classification Review MD
review_md_path = os.path.join(base_dir, "POLARIS_BRANCH01_V2_CAUSAL_CLASSIFICATION_REVIEW.md")
review_md_content = """# POLARIS Branch01 V2 Causal Classification & Evidence Review Audit Report

**Governance Status**: READ_ONLY_GOVERNANCE_CORRECTION  
**Audit Timestamp**: 2026-09-21T19:49:14Z  
**Authoritative Directory**: `ems/campaigns/POLARIS_BRANCH01_V2_CAUSAL_CLASSIFICATION_REVIEW/`

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
"""
with open(review_md_path, "w") as f:
    f.write(review_md_content)

# 6. Hash Audit CSV
hash_csv_path = os.path.join(base_dir, "POLARIS_BRANCH01_V2_CAUSAL_CLASSIFICATION_HASH_AUDIT.csv")
files_to_hash = [
  "POLARIS_BRANCH01_V2_CAUSAL_CLASSIFICATION_REVIEW.md",
  "POLARIS_BRANCH01_V2_CAUSAL_CLASSIFICATION_REVIEW.json",
  "POLARIS_BRANCH01_V2_CAUSAL_WORDING_CORRECTION.md",
  "POLARIS_BRANCH01_V2_CAUSAL_WORDING_CORRECTION.json",
  "POLARIS_BRANCH01_V2_CAUSAL_EVIDENCE_MATRIX.csv"
]

hash_rows = ["filename,sha256,creation_purpose,source_artifacts,read_only_status"]
for fname in files_to_hash:
    fpath = os.path.join(base_dir, fname)
    with open(fpath, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    hash_rows.append(f"{fname},{digest},Read-only governance review and scientific causal classification correction artifact,ems/campaigns/POLARIS_BRANCH01_V2_CAUSAL_FORENSIC_AUDIT/,VERIFIED_READ_ONLY")

with open(hash_csv_path, "w") as f:
    f.write("\n".join(hash_rows) + "\n")

print("Successfully generated all review files and hash audit in:", base_dir)
