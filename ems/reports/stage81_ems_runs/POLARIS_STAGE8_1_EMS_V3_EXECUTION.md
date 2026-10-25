# POLARIS Stage 8.1 EMS V3 Class F Empirical Execution Manifest

**Execution Status**: `COMPLETE_VALID`  
**Governance Status**: `V3_EXECUTION_COMPLETE`  
**Execution Timestamp (UTC)**: 2026-09-19T12:12:00.096438+00:00  

---

## 1. Execution Setup & Provenance Hashes

- **Execution Command**: `python3 run_polaris_stage8_1_ems_v3_execution.py`
- **Total Runtime**: 2588.29 seconds (~43.1 minutes)

### Provenance & Component Hashes (SHA-256)
- **Stage 8.1 Prediction Artifact (`POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`)**: `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`
- **Class F MILP Implementation (`system/optimization/implementations/milp.py`)**: `fc4fafe712a62fa301b3fbe021cd933c64bd08bd96d6a644ba412207134a19c3`
- **Stage 8.1 Solar Engine (`system/forecasting/implementations/s81_solar.py`)**: `d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c`
- **Control Engine (`system/forecasting/implementations/baseline.py`)**: `905c644abdc27d4ec3a8168ff39828bcc0575a4a6e31460c0ff4bfb16c30c993`
- **Simulator (`system/simulation/simulator.py`)**: `7217dc2b034480216e21e3494873189e575a15f3b2e71435d0844c4ca0a9a508`
- **Execution Runner (`system/runtime/runner.py`)**: `605a479586777cbc81315effdf0571e52be8e0a393661c0367c7b9ef3c55c58c`
- **ForecastBundle Schema (`system/schemas/forecast_bundle.py`)**: `899aaa48272fd44691cef4b32939adb931a837c99203db37edfc14a9bb2d2045`
- **StationState Schema (`system/schemas/station_state.py`)**: `b6e78e8292bbba407f0af0a56100024cca4831dfb80d138afb1fb38008532d1c`
- **DispatchPlan Schema (`system/schemas/dispatch_plan.py`)**: `cbf80578a0b4fa289e26b509eeb4d672124a2dad8a77855a42a50ca267349a17`
- **V3 Class F Parameter Freeze JSON (`POLARIS_STAGE8_1_EMS_V3_CLASS_F_PARAMETER_FREEZE.json`)**: `6ddcc73add04bab6075d98378f61c5433da5b1e2399789969bb5622cbe002efd`
- **V3 Class F Parameter Freeze MD (`POLARIS_STAGE8_1_EMS_V3_CLASS_F_PARAMETER_FREEZE.md`)**: `8ec1d4c66697b52a9045ace89eb1f5b6361b44c3c2b2c53c6172173f70bb1355`
- **Raw Telemetry Evidence (`POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv`)**: `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e`

---

## 2. Execution Completeness & Verification

- **Expected Origins**: 173
- **Completed Origins**: 173 (100% complete across all 3 arms)
- **Arm 1 (Control) Completed Origins**: 173 / 173
- **Arm 2 (V2 Treatment) Completed Origins**: 173 / 173
- **Arm 3 (V3 Class F Treatment) Completed Origins**: 173 / 173
- **Failed Origins**: 0
- **Retries**: 0
- **Solver Status**: `OPTIMAL` across all 12,456 solver calls (4,152 per arm)
- **Total Telemetry Rows**: 4,152 rows per arm (12,456 total step records)

---

## 3. Primary Endpoint Results

- **Statistical Unit**: 1 Complete 24-Hour Forecast-Origin Replay ($N=173$ paired origins)
- **Primary Endpoint**: Total Diesel Fuel (Liters) per 24-Hour Origin
- **Primary Comparison**: Paired V3 Class F Treatment vs. V2 Treatment

### Numerical Results Across Arms ($N=173$)
| Metric | Arm 1 (Control) | Arm 2 (V2 Treatment) | Arm 3 (V3 Class F) | Paired Delta (V3 - V2) |
|---|---|---|---|---|
| **Mean Diesel Fuel (L)** | 27.00 L | 37.27 L | 23.99 L | -13.28 L |
| **Total Diesel Fuel (L)** | 4,671.0 L | 6,448.2 L | 4,150.3 L | -2,297.9 L |
| **Median Difference (L)** | — | — | — | -13.50 L |
| **95% Bootstrap CI (L)** | — | — | — | [-15.11 L, -11.48 L] |
| **Wilcoxon Signed-Rank** | — | — | — | $W = 32.00, p = 6.22 \times 10^{-21}$ |

---

## 4. Secondary Endpoints

- **Mean Renewable Curtailment (kWh/origin)**:
  - Arm 1 (Control): 177.38 kWh
  - Arm 2 (V2 Treatment): 56.95 kWh
  - Arm 3 (V3 Class F): 17.57 kWh
  - Paired Delta (V3 - V2): -39.38 kWh
- **Mean Battery Throughput (kWh/origin)**:
  - Arm 1 (Control): 80.04 kWh
  - Arm 2 (V2 Treatment): 80.04 kWh
  - Arm 3 (V3 Class F): 80.04 kWh
  - Paired Delta (V3 - V2): 0.0 kWh
- **Unmet Critical Load (kWh)**:
  - 0.0 kWh across all origins and arms.

---

## 5. Execution Integrity Statement

- No protocol, model, simulator, optimization constraint, baseline, or parameter changes occurred during execution.
- $\gamma = 0.95$ was frozen prior to execution and remained unchanged throughout.
- All $N=173$ origins were executed directly without prior pilots, single-origin pretests, or parameter tuning.
- Raw telemetry step data has been frozen in `POLARIS_STAGE8_1_EMS_V3_EXECUTION_RAW.csv` (SHA256: `a67a7ef07cbfc3221623411da30d72203e3efb16a424c8aaa34772eaf833971e`).
