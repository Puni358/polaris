# POLARIS Stage8.1 -> EMS V4.G Empirical Execution Summary Report
## Authoritative Empirical Replay Execution Record / 3-Arm Paired Replay (N=173 Origins)

```yaml
V4G_EXECUTION_AUTHORIZED: TRUE
V4G_CLASSIFICATION: A
V4G_SPECIFICATION: FROZEN
V4G_IMPLEMENTATION: COMPLETE
V4G_STATIC_AUDIT: PASSED
MAX_WORKERS: 2
THERMAL_MONITORING_MODE: MANUAL
V4G_EMPIRICAL_EXECUTION: COMPLETE
```

---

## 1. Execution Summary & Status

The authorized POLARIS V4.G empirical experiment has been **DIRECTLY EXECUTED** across the full N=173 eligible paired origin population (4,152 timesteps per arm, total 12,456 timesteps evaluated across 3 arms).

- **Execution Status**: `COMPLETE_VALID`
- **Total Origins Evaluated**: 173 / 173 (100% Completeness)
- **Control Arm Completed**: 173 / 173
- **V3 Reference Arm Completed**: 173 / 173
- **V4.G Candidate Arm Completed**: 173 / 173
- **Failed Origins**: 0
- **Retries**: 0
- **Total Runtime**: 3144.35 seconds
- **Max Workers**: 2
- **Thermal Monitoring Mode**: MANUAL (No thermal halts required)
- **Raw Telemetry File**: [`POLARIS_STAGE8_1_EMS_V4G_EXECUTION_RAW.csv`](file:///home/punith-bs/01polaris (Copy)/POLARIS_STAGE8_1_EMS_V4G_EXECUTION_RAW.csv) (SHA256: `61389d23a307dcb1bbc5ea90f9bf43843b52d88f66d5ff1d03bb1dea55199788`)
- **Execution Manifest**: [`POLARIS_STAGE8_1_EMS_V4G_EXECUTION.json`](file:///home/punith-bs/01polaris (Copy)/POLARIS_STAGE8_1_EMS_V4G_EXECUTION.json) (SHA256: `620d8add38c8146c15e7646c0793f74a34437dbd2c9d719759b16b2be1e6934e`)

---

## 2. Experimental Setup & Arm Verification

1. **Arm 1 — Control**: `LocalBaselineForecastEngine` (SHA256: `905c644abdc27d4ec3a8168ff39828bcc0575a4a6e31460c0ff4bfb16c30c993`), `gamma = 1.0`.
2. **Arm 2 — V3 Reference**: Frozen Stage8.1 empirical solar forecast artifact (SHA256: `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`), `gamma = 0.95`, w_t = 0.95^t for t in 0..23.
3. **Arm 3 — V4.G Candidate**: EXACT SAME Stage8.1 empirical solar forecast artifact (SHA256: `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d`), isolated single-horizon weight at h=14 <-> t=13 with w_13 = 0.5133, w_t = 1.0 otherwise.

### Scientific Isolation & Firewall Verification:
- **Initial Station State (S_i,0)**: 100% identical across all 3 arms for every origin i in 1..173.
- **Realized Ground Truth Trajectory**: 100% identical across all 3 arms for every origin.
- **Future-Truth Firewall**: Ground truth strictly isolated to digital twin simulator step evaluations; zero leakage to forecasts or MILP optimizer.
- **Protocol & Code Modifications**: Zero (0) protocol, model, or parameter changes occurred during execution.
- **Unmet Load Weight**: w_unmet,t = 1.0 strictly unweighted across all timesteps.

---

## 3. Primary Endpoint Results Summary

- **Primary Endpoint**: Total diesel fuel consumption (liters) per 24-hour origin.
- **Primary Comparison**: V4.G Candidate minus V3 Reference ($\delta_i = \text{fuel}_{\text{V4G}, i} - \text{fuel}_{\text{V3}, i}$).
- **Statistical Unit**: `ORIGIN` (N=173 paired 24-hour origins).

| Arm | Mean Diesel Fuel (Liters / Origin) | Total Fuel across 173 Origins (Liters) |
|---|---|---|
| **Arm 1 — Control** | 27.00 L | 4671.0 L |
| **Arm 2 — V3 Reference** | 23.99 L | 4150.0 L |
| **Arm 3 — V4.G Candidate** | 32.25 L | 5580.0 L |

### Primary Intervention Paired Comparison (V4.G Candidate vs. V3 Reference):
- **Mean Difference (V4.G - V3)**: +8.2660 L / origin
- **Median Difference (V4.G - V3)**: +5.1300 L / origin
- **95% Bootstrap Confidence Interval**: [+6.7356 L, +9.8166 L]
- **Wilcoxon Signed-Rank Test**: W = 15.00, p = 8.645153e-18
- **Paired Difference Counts**:
  - Positive ($\delta_i > 0$, V4.G consumed more fuel): 96
  - Negative ($\delta_i < 0$, V4.G consumed less fuel): 3
  - Zero ($\delta_i = 0$, identical fuel): 74
  - Total Paired Origins ($N$): 173

---

## 4. Protected Artifact Inventory & SHA256 Hashes

| Protected Artifact | SHA256 Hash | Provenance Status |
|---|---|---|
| `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` | `a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d` | MATCH |
| `POLARIS_COMPLETE_MODEL_PREDICTION_INDEX.csv` | `b86f19476a9c5fa97df406cedf399a40c33496dc085cb077ab829afa9dd79b3c` | MATCH |
| `system/forecasting/implementations/s81_solar.py` | `d76249bb0fc78680f0ea6723fbec62a234511d181e0a091b2f80fa06838aca7c` | MATCH |
| `system/optimization/implementations/milp.py` | `a22c4b7812ca61b8a5e5990e01f49aba929e37e954b9233d7e4e66e823c9c0b5` | MATCH |
| `system/simulation/simulator.py` | `7217dc2b034480216e21e3494873189e575a15f3b2e71435d0844c4ca0a9a508` | MATCH |
| `POLARIS_STAGE8_1_EMS_V4G_SPECIFICATION_FREEZE.md` | `f476fb86c6e0a923f72ff1ae689859e767d17474019df50c66f1e60fdd1861f6` | MATCH |
| `POLARIS_STAGE8_1_EMS_V4G_IMPLEMENTATION.md` | `393dde4db0d093a67fb2e6e14b05c7a85691f9a2ec9340728aaf10f25770b11d` | MATCH |
| `POLARIS_STAGE8_1_EMS_V4G_EXECUTION_AUTHORIZATION.md` | `d2fa6c4c6523dd7322c645751cd8c2399397244760198a530a218513125e9523` | MATCH |

### Generated Execution Outputs:
- **Raw Telemetry CSV**: [`POLARIS_STAGE8_1_EMS_V4G_EXECUTION_RAW.csv`](file:///home/punith-bs/01polaris (Copy)/POLARIS_STAGE8_1_EMS_V4G_EXECUTION_RAW.csv) (SHA256: `61389d23a307dcb1bbc5ea90f9bf43843b52d88f66d5ff1d03bb1dea55199788`)
- **Execution Manifest JSON**: [`POLARIS_STAGE8_1_EMS_V4G_EXECUTION.json`](file:///home/punith-bs/01polaris (Copy)/POLARIS_STAGE8_1_EMS_V4G_EXECUTION.json) (SHA256: `620d8add38c8146c15e7646c0793f74a34437dbd2c9d719759b16b2be1e6934e`)

---

## 5. Governance Declarations & Next Step

```yaml
V4G_EXECUTION_AUTHORIZED: TRUE
V4G_SPECIFICATION: FROZEN
V4G_IMPLEMENTATION: COMPLETE
V4G_STATIC_AUDIT: PASSED
MAX_WORKERS: 2
THERMAL_MONITORING_MODE: MANUAL
V4G_EMPIRICAL_EXECUTION: COMPLETE
```

**HARD STOP AFTER EXECUTION.**  
*Mechanism interpretation, causal attribution, and engineering assessment are reserved for the subsequent governed task:*  
`POLARIS_STAGE8_1_EMS_V4G_POST_EXECUTION_FORENSIC_AUDIT`
