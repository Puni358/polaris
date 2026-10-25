# POLARIS Stage8.1 → EMS V2 Execution Authorization Document

## 1. Executive Governance Authorization Decision

```yaml
V1 = ACCEPTED + FROZEN
V1 RESULT = UNCHANGED
V2 PROTOCOL = HARDENED
V2 TELEMETRY IMPLEMENTATION = COMPLETE
V2 NON-INTERVENTION CORRECTION = COMPLETE
V2 STATIC NON-INTERVENTION RE-AUDIT = A
V2 EXECUTION AUTHORIZATION = A — AUTHORIZED
V2 EMPIRICAL EXECUTION = NOT YET EXECUTED

NEXT STEP = SEPARATE V2 EMPIRICAL EXECUTION TASK
```

### Formal Decision Statement:
Following the successful completion of the V2 mechanism-observability protocol hardening, the 37-field passive telemetry logger implementation, the telemetry non-intervention exception isolation boundary correction, and the final static non-intervention re-audit (Classification A), the POLARIS Governance Body hereby **FORMALLY AUTHORIZES** the empirical execution of the 173-origin V2 Stage8.1 → EMS mechanism observability replay.

**ABSOLUTE EXECUTION FIREWALL NOTE**: No V2 origins were executed during this authorization task. Empirical execution will occur exclusively in a separate dedicated execution task.

## 2. Prerequisites & Governance Verification Checklist

| Governed Prerequisite | Verification Status | Evidence / Location |
|---|---|---|
| Treatment artifact frozen & SHA256 verified | **VERIFIED** | a4d288f9bba4a57c... (4152 rows, 173 origins) |
| Control forecast engine frozen & verified | **VERIFIED** | LocalBaselineForecastEngine (baseline.py) |
| Paired design structurally verified | **VERIFIED** | Identical initial states, ground truth, and configs |
| Eligibility rules frozen | **VERIFIED** | N = 173 origins, no result-dependent exclusions |
| Horizon continuation semantics verified | **VERIFIED** | Empirical S8.1 predictions + clear-sky extension |
| ForecastBundle v1.0 schema verified | **VERIFIED** | solar_generation = min(SW_IN * 51.0, 60000.0 W) |
| EMS scientific components unchanged | **VERIFIED** | milp.py SHA256: 274926d2..., simulator.py SHA256: 7217dc2b... |
| Telemetry implementation completed | **VERIFIED** | system/telemetry/v2_logger.py (37 fields) |
| Telemetry field set matches protocol | **VERIFIED** | 37/37 exact field match |
| Telemetry non-intervention verified | **VERIFIED** | runner.py:218-260 isolated try-except block |
| Static re-audit completed & reviewed | **VERIFIED** | Classification A in POLARIS_STAGE8_1_EMS_V2_TELEMETRY_STATIC_REAUDIT.md |
| Future-truth firewall verified | **VERIFIED** | Truth loaded on runner.py:191 strictly post-optimization |
| Failure semantics established | **VERIFIED** | EMS failures -> FAILED_TERMINATED; telemetry errors -> _telemetry_faults |
| Solver provenance limitation documented | **VERIFIED** | HiGHS interface ESTABLISHED; binary hash NOT_ESTABLISHED |
| No result-dependent stopping rule locked | **VERIFIED** | Pre-registered 173-origin complete execution requirement |
| Engineering change prohibition enforced | **VERIFIED** | V2 is 100% observational; EMS modification locked |

## 3. Mandatory Current Provenance Hash Verification

### Protected Governance Artifacts & Source Components
| File Path | Expected SHA256 | Current Computed SHA256 | Verification Status |
|---|---|---|---|
| `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` | `a4d288f9bba4a57c...` | `a4d288f9bba4a57c...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_RAW.csv` | `7d9c6e7af82b6198...` | `7d9c6e7af82b6198...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.json` | `80cf3be4955da83a...` | `80cf3be4955da83a...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXECUTION.md` | `0b516787444ed5c9...` | `0b516787444ed5c9...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_DECOMPOSITION.md` | `8c2c8da41134b9b2...` | `8c2c8da41134b9b2...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_DECOMPOSITION.json` | `f3b6ecd581d6c790...` | `f3b6ecd581d6c790...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_BRANCH_CLOSURE.md` | `ac4dec9e101adc8e...` | `ac4dec9e101adc8e...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_BRANCH_CLOSURE.json` | `f8e574fb6f774b2a...` | `f8e574fb6f774b2a...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_OBSERVABILITY_V2_PROTOCOL.md` | `c9a61cd0e726e37a...` | `c9a61cd0e726e37a...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_OBSERVABILITY_V2_PROTOCOL.json` | `3c47c8a4b283aa41...` | `3c47c8a4b283aa41...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V2_FINAL_PRE_IMPLEMENTATION_CONSISTENCY_CHECK.md` | `1ff1d00ddde7ece3...` | `1ff1d00ddde7ece3...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V2_FINAL_PRE_IMPLEMENTATION_CONSISTENCY_CHECK.json` | `35b33d1eb8582f37...` | `35b33d1eb8582f37...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V2_PRE_IMPLEMENTATION_CORRECTION.md` | `e064a87a09cd2fab...` | `e064a87a09cd2fab...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V2_PRE_IMPLEMENTATION_CORRECTION.json` | `50c23683fa9a4ad7...` | `50c23683fa9a4ad7...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_TIMESTEP_MECHANISM_VERIFICATION.md` | `e6fd9974cb4fa7d3...` | `e6fd9974cb4fa7d3...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_TIMESTEP_MECHANISM_VERIFICATION.json` | `629f4731cb269cd2...` | `629f4731cb269cd2...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V1_MECHANISM_WORDING_CORRECTION_MANIFEST.md` | `2dbdf65d2c44cc37...` | `2dbdf65d2c44cc37...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V1_MECHANISM_WORDING_CORRECTION_MANIFEST.json` | `e5634d69595dee2b...` | `e5634d69595dee2b...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_V2_TELEMETRY_IMPLEMENTATION.md` | `ESTABLISHED_POST...` | `ca7ad3037be3a9ee...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_MECHANISM_V2_TELEMETRY_IMPLEMENTATION.json` | `ESTABLISHED_POST...` | `6b0d43ad26304f84...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V2_TELEMETRY_NON_INTERVENTION_CORRECTION.md` | `ESTABLISHED_POST...` | `ea3ee080d6ed0641...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V2_TELEMETRY_NON_INTERVENTION_CORRECTION.json` | `ESTABLISHED_POST...` | `7ad6fd881075a0cc...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V2_TELEMETRY_STATIC_REAUDIT.md` | `ESTABLISHED_POST...` | `300ede2ef49edcd3...` | **MATCH** |
| `POLARIS_STAGE8_1_EMS_V2_TELEMETRY_STATIC_REAUDIT.json` | `ESTABLISHED_POST...` | `544475d0a577aa53...` | **MATCH** |
| `system/telemetry/v2_logger.py` | `ESTABLISHED_POST...` | `131ff6f4dc83a2a5...` | **MATCH** |
| `system/runtime/runner.py` | `ESTABLISHED_POST...` | `605a479586777cbc...` | **MATCH** |
| `system/tests/test_v2_telemetry.py` | `ESTABLISHED_POST...` | `aad44e780a850fbb...` | **MATCH** |
| `run_polaris_stage8_1_ems_empirical_replay.py` | `c305aa8179015efb...` | `c305aa8179015efb...` | **MATCH** |
| `system/forecasting/implementations/s81_solar.py` | `d76249bb0fc78680...` | `d76249bb0fc78680...` | **MATCH** |
| `system/forecasting/implementations/baseline.py` | `ESTABLISHED_POST...` | `905c644abdc27d4e...` | **MATCH** |
| `system/schemas/forecast_bundle.py` | `ESTABLISHED_POST...` | `899aaa48272fd446...` | **MATCH** |
| `system/schemas/station_state.py` | `b6e78e8292bbba40...` | `b6e78e8292bbba40...` | **MATCH** |
| `system/schemas/dispatch_plan.py` | `cbf80578a0b4fa28...` | `cbf80578a0b4fa28...` | **MATCH** |
| `system/optimization/implementations/milp.py` | `274926d2d04a26f9...` | `274926d2d04a26f9...` | **MATCH** |
| `system/simulation/simulator.py` | `7217dc2b03448021...` | `7217dc2b03448021...` | **MATCH** |
| `system/evaluation/evaluator.py` | `ESTABLISHED_POST...` | `79af472d52aab4b6...` | **MATCH** |

## 4. Telemetry Field-Set & Non-Intervention Verification

- **Authoritative Protocol Field Count**: 37
- **Implemented Telemetry Field Count**: 37
- **Field-Set Match**: **100% EXACT MATCH** (0 missing fields, 0 extra fields)
- **Non-Intervention Exception Isolation**: Telemetry collection in `system/runtime/runner.py:218-260` is isolated in a dedicated `try...except Exception as te:` block. Telemetry failures are logged to `_telemetry_faults` without altering EMS execution status (`SUCCESS_CLEAN`) or state trajectories.
- **Future-Truth Firewall**: Ground truth `actual_solar_truth` is accessed on `runner.py:191` strictly **after** optimizer dispatch generation.

## 5. Locked V2 Execution Protocol Specification

1. **Experimental Unit**: One complete 24-hour forecast-origin replay ($N = 173$ origins, $173 \times 24 = 4152$ MPC timesteps).
2. **Treatment Input**: Exact raw float predictions from `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv` (SHA256: `a4d288f9bba4a57c...`).
3. **Control Input**: `LocalBaselineForecastEngine` (`system/forecasting/implementations/baseline.py`).
4. **Paired Design**: Identical origin, timestamp, initial `StationState`, realized solar/demand trajectory, simulator config, and MILP optimizer config.
5. **Horizon Protocol**: Empirical Stage8.1 predictions for remaining origin hours ($h \le 24 - k$) + baseline clear-sky diurnal continuation ($h > 24 - k$).
6. **PV Mapping**: `solar_generation = min(SW_IN * 300 * 0.20 * 0.85, 60000.0 W)`.
7. **EMS Codebase**: Frozen MILP optimizer (`milp.py`) and simulator (`simulator.py`).
8. **Observational Telemetry**: 37-field passive telemetry logged for both Treatment and Control replays.
9. **Failure Containment**: D4-C1 governed failure containment for EMS errors; isolated `_telemetry_faults` for telemetry errors.
10. **Statistical Endpoints**: Primary endpoint `total_diesel_fuel_liters` (Mean paired difference, 10,000 bootstrap resamples, Wilcoxon signed-rank test, Spearman correlation).
11. **Mechanism Analysis Plan**: Timestep-level evaluation of M1 (Diesel Commitment), M2 (Battery Dispatch), M3 (Renewable Absorption/Curtailment), M4 (SOC Positioning), M5 (Forecast Shape), M6 (Multi-Pathway), and M7 (Other Mechanisms).
12. **Engineering Change Prohibition**: **LOCKED** — No EMS parameter tuning, cost weight adjustments, or heuristic modifications permitted during V2 execution.

## 6. Required Final Governance Statement

```yaml
V1 = ACCEPTED + FROZEN
V1 RESULT = UNCHANGED
V2 PROTOCOL = HARDENED
V2 TELEMETRY IMPLEMENTATION = COMPLETE
V2 NON-INTERVENTION CORRECTION = COMPLETE
V2 STATIC NON-INTERVENTION RE-AUDIT = A
V2 EXECUTION AUTHORIZATION = A — AUTHORIZED
V2 EMPIRICAL EXECUTION = NOT YET EXECUTED

NEXT STEP = SEPARATE V2 EMPIRICAL EXECUTION TASK
```
