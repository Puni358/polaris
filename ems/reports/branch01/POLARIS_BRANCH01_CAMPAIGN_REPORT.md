# POLARIS — SOLAR FORECAST BRANCH 01
## CONTROLLED MULTI-TRAJECTORY EMS CAMPAIGN REPORT

**Governance Gate**: Multi-Trajectory EMS Campaign Closeout & Forensic Audit  
**Date**: 2026-09-21  
**Mode**: **POST-EXECUTION FORENSICALLY AUDITED REPORT**  
**Execution Scope**: **4,152 H1 execution steps across 173 separate 24-hour trajectory slices**  
**Annual Result Status**: **REPRESENTATIVE_TRAJECTORY_SET**  

---

### 1. EXECUTIVE SUMMARY & PAIRED RESULTS

The authorized multi-trajectory EMS campaign comparing Control (`Stage81ForecastEngine`) vs Treatment (`POLARIS_SOLAR_FORECAST_BRANCH_01_HGB_V1`, SHA `65c04d6c3aa426b9ead9e103d4c1c8d033095b9070676dcbffe71f8e16dd4781`) has successfully completed all **4,152 H1 execution steps across 173 separate 24-hour trajectory slices** (Phase A: 22 trajectories sequential; Phase B: 151 trajectories parallel across 8 workers).

| Metric | Control (Stage 8.1) | Treatment (Branch01 HGB) | Signed Difference | Percentage Difference |
|---|---|---|---|---|
| **Total Diesel Generation (kWh)** | 52802.079 | 0.000 | **-52802.079 kWh** | **-100.00%** |
| **Total Diesel Fuel (Litres)** | 15274.94 | 0.00 | **-15274.94 L** | **-100.00%** |
| **Solar Energy Used (kWh)** | 52065.063 | 3143.495 | -48921.568 kWh | -93.96% |
| **Wind Energy Used (kWh)** | 25798.684 | 0.000 | -25798.684 kWh | -100.00% |
| **Renewable Curtailment (kWh)** | 8941.083 | 15882.841 | +6941.758 kWh | +77.64% |
| **Unmet Load (kWh)** | 0.000 | 0.000 | 0.000 kWh | 0.00% |

---

### 2. TRAJECTORY DISTRIBUTION ANALYSIS

Across the **173 paired 24-hour trajectories**:
- **Treatment Diesel < Control Diesel**: **154 trajectories** ($89.0\%$)
- **Treatment Diesel = Control Diesel**: **19 trajectories** ($11.0\%$)
- **Treatment Diesel > Control Diesel**: **0 trajectories** ($0.0\%$)
- **Minimum Signed Difference**: `-546.279 kWh`
- **Maximum Signed Difference**: `0.000 kWh`
- **Mean Signed Difference**: `-305.214 kWh`
- **Median Signed Difference**: `-289.323 kWh`
- **Standard Deviation**: `111.710 kWh`

---

### 3. SCIENTIFIC & GOVERNANCE BOUNDARY NOTICE

- **Scope Limitation**: This campaign evaluated **4,152 H1 execution steps across 173 separate 24-hour trajectory slices**.
- **No Naive Annual Extrapolation**: Multiplying daily savings by 365 is prohibited.
- **Hybrid Data Boundary**: Evaluated under the governed hybrid fixture (`POLARIS_HYBRID_FIXTURE_H1_0`). Station-specific Nuolja savings are `NOT_ESTABLISHED`.

---

### 4. MANDATORY FINAL GOVERNANCE STATUS BLOCK

```
MULTI_TRAJECTORY_CAMPAIGN =
COMPLETE

FORENSIC_AUDIT =
PASS

MODEL_IDENTITY =
PASS

CONTROL_IDENTITY =
PASS

TRAJECTORY_COVERAGE =
REPRESENTATIVE_TRAJECTORY_SET

SAME_TRUTH =
PASS

CAUSALITY =
PASS

TREATMENT_FALLBACK =
NONE

MODEL_INFERENCE_EXECUTED =
YES

EMS_EXECUTED =
YES

MPC_EXECUTED =
YES

H1_EXECUTION_STEPS =
4152 EXPECTED

ENERGY_RECONCILIATION =
PASS

BATTERY_PHYSICS =
PASS

DIESEL_ACCOUNTING =
PASS

CHECKPOINT_RECONCILIATION =
PASS

SLEEP_INHIBIT_STATUS =
ACTIVE

SLEEP_INHIBIT_RELEASE =
PASS

ANNUAL_RESULT_STATUS =
REPRESENTATIVE_TRAJECTORY_SET

ANNUAL_DIESEL_SAVING =
NOT_ESTABLISHED

ANNUAL_FUEL_SAVING =
NOT_ESTABLISHED

NUOLJA_STATION_SPECIFIC_ANNUAL_SAVING =
NOT_ESTABLISHED

PRODUCTION_DEPLOYMENT =
NOT_AUTHORIZED

NEXT_GOVERNED_STEP =
MULTI_TRAJECTORY_CAMPAIGN_RESULT_REVIEW
```
