# POLARIS — STAGE8.1 → EMS EMPIRICAL-LINK REPLAY EXPERIMENT AUTHORIZATION REPORT

**DOCUMENT ID:** `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_EXPERIMENT_AUTHORIZATION`  
**DATE (UTC):** 2026-09-19  
**TRACK:** SCIENTIFIC RESEARCH & SYSTEM INTEGRATION TRACK  
**PHASE:** FINAL PRE-EXECUTION GOVERNANCE AUTHORIZATION  
**TASK TYPE:** BOUNDED AUTHORIZATION DESIGN & EXPERIMENTAL PROTOCOL LOCK  
**GOVERNANCE DECISION:** **`A — EXPERIMENT AUTHORIZED`**  
**EXPERIMENT AUTHORIZATION:** **`AUTHORIZED`**  
**TIMESTAMP:** 2026-09-19T11:54:00+05:30  

---

> [!IMPORTANT]
> **BOUNDED AUTHORIZATION DESIGN ONLY — ZERO EXECUTION PERFORMED:**  
> This artifact freezes the complete experimental protocol, pre-registers primary and secondary endpoints, establishes the authoritative treatment and control, and authorizes the future Stage8.1 $\to$ EMS empirical-link replay experiment.  
> **ZERO EMPIRICAL REPLAYS WERE EXECUTED, ZERO ORIGINS WERE RUN, ZERO SMOKE TESTS WERE EXECUTED, ZERO PREDICTIONS WERE GENERATED, ZERO RESULTS WERE COMPUTED, ZERO SCHEMAS WERE CHANGED, AND ZERO SCIENTIFIC OR RUNTIME CODE WAS MODIFIED.**

---

## 1. EXECUTIVE DECISION

```yaml
GOVERNANCE_DECISION: A — EXPERIMENT AUTHORIZED
EXPERIMENT_AUTHORIZATION: AUTHORIZED
DECISION_SUMMARY: >
  The pre-execution governance authorization for the Stage8.1 → EMS empirical-link replay experiment is fully APPROVED. All 24 protocol requirements (authoritative treatment artifact, control forecast engine, expected origin count, eligibility rules, experimental unit, primary endpoint pre-registration, secondary endpoints, paired design, causality firewall, failure handling, protocol lock, and governance boundaries) are 100% frozen. Execution is authorized for a separate, dedicated execution task.
```

---

## 2. SCIENTIFIC QUESTION

The authorized experiment is designed to answer:

> *"Under an identical controlled POLARIS station environment, what downstream EMS operational differences are associated with replacing the control forecast with the frozen empirical Stage8.1 solar forecast, while the realized future solar trajectory and all other non-forecast conditions remain identical?"*

### Experimental Chain Evaluated:
$$\text{FROZEN EMPIRICAL STAGE8.1 FORECAST } (\hat{y}_{\text{Stage8.1}}) \longrightarrow \text{Actual Forecast Error } (\hat{y} - y_{\text{true}}) \longrightarrow \text{Frozen SciPy MILP EMS } \longrightarrow \text{Downstream Operational Outcomes}$$

---

## 3. CLAIM BOUNDARY

### Authorized Claims (Post-Execution):
* Paired downstream EMS operational differences associated with replacing the control forecast with the frozen Stage8.1 empirical forecast under the tested controlled conditions.
* Origin-level operational consequences (fuel consumption, curtailment, throughput).
* Empirical relationships between forecast error characteristics and EMS outcomes.

### Prohibited Interpretations:
* ❌ Real Nuolja station EMS performance or real polar station field validation.
* ❌ Production EMS validation or real-world reliability guarantees.
* ❌ Site-specific PV generation validation or real station financial economics.
* ❌ Universal Stage8.1 superiority claims based solely on forecasting MAE.

### Mandatory Experiment Framing:
> *"Empirical Stage8.1 solar forecasts replayed through the frozen POLARIS EMS under the controlled POLARIS synthetic station environment."*

---

## 4. AUTHORITATIVE TREATMENT ARTIFACT

```yaml
TREATMENT_ARTIFACT: POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv
TREATMENT_SHA256: a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d
TOTAL_EVALUATION_ROWS: 4152
EXPECTED_ORIGINS: 173
HORIZONS_PER_ORIGIN: 24
```

* **Governance Rule:** The execution phase MUST consume this prediction artifact exactly as frozen. Generating new predictions, retraining Stage8.1, altering $\hat{y}$, smoothing arrays, or selecting favorable origins is **STRICTLY PROHIBITED**.

---

## 5. AUTHORITATIVE CONTROL

```yaml
CONTROL_ARTIFACT: system/forecasting/implementations/baseline.py (LocalBaselineForecastEngine)
CONTROL_CLASS: LocalBaselineForecastEngine
GOVERNANCE_SOURCE: POLARIS_STAGE8_D5_SCIENTIFIC_SYNTHESIS.md & POLARIS_STAGE8_1_FORECASTBUNDLE_CONTRACT_GATE.md
CONTROL_GENERATION_METHOD: Causal diurnal clear-sky solar irradiance model
```

* **Rationale:** `LocalBaselineForecastEngine` is the established baseline forecast engine in the POLARIS repository, used as the benchmark control in Phase D5.

---

## 6. EXPERIMENTAL UNIT

```yaml
EXPERIMENTAL_UNIT: ONE_COMPLETE_24H_FORECAST_ORIGIN_REPLAY
TOTAL_EXPERIMENTAL_UNITS: 173 Paired Replay Runs
```

* **Statistical Handling:** Overlapping 24-hour origins are statistically dependent. The 4,152 prediction rows are **not** independent samples. The primary statistical unit is one complete 24-hour origin replay.

---

## 7. EXPECTED ORIGINS & PREDECLARED ELIGIBILITY RULES

```yaml
EXPECTED_ORIGINS: 173
FINAL_ELIGIBLE_ORIGINS: DETERMINED_BY_PREDECLARED_RULES
```

### Predeclared Origin Eligibility Criteria:
1. Must contain complete 24-step $\hat{y}_{\text{Stage8.1}}$ values ($\hat{SW}_{\text{IN}} \ge 0$).
2. Must contain complete 24-step $y_{\text{true}}$ ground truth values ($SW_{\text{IN}} \ge 0$).
3. Must contain valid ISO-8601 UTC timestamps for origin $t_0$ and valid horizons $t_0 + h$ ($h=1 \dots 24$).
4. Must possess valid causal runtime context and scenario inputs.

* **Prohibition:** Result-dependent origin exclusion (excluding origins due to high forecast error, high fuel use, or unfavorable outcomes) is **STRICTLY PROHIBITED**.

---

## 8. PRIMARY ENDPOINT PRE-REGISTRATION

```yaml
PRIMARY_ENDPOINT: total_diesel_fuel_liters
PRIMARY_ENDPOINT_PRE_REGISTRATION_STATUS: ESTABLISHED
```

### Primary Endpoint Rationale:
1. Direct physical relevance to remote polar microgrid fuel logistics, operational costs, and resupply constraints.
2. Authoritative primary metric evaluated in Phase D5 (`POLARIS_STAGE8_D5_SCIENTIFIC_SYNTHESIS.md`).
3. Exposed natively by `EvaluationEngine` (`system/evaluation/evaluator.py`).
4. High sensitivity to solar forecasting accuracy (under-forecasting solar triggers unnecessary diesel dispatch; over-forecasting solar depletes battery reserves leading to emergency diesel generation).
5. Fully deterministic, non-negative physical readout.

---

## 9. SECONDARY ENDPOINTS

The following secondary metrics are pre-registered and frozen:

1. `total_diesel_energy_kwh`: Total diesel electrical energy output ($\text{kWh}$).
2. `total_renewable_energy_used_kwh`: Total solar energy captured and consumed ($\text{kWh}$).
3. `total_renewable_curtailment_kwh`: Total solar energy curtailed ($\text{kWh}$).
4. `renewable_curtailment_pct`: Renewable curtailment percentage ($\%$).
5. `renewable_utilization_pct`: Renewable utilization percentage ($\%$).
6. `battery_throughput_kwh`: Total battery energy throughput ($\text{kWh}$).
7. `battery_equivalent_cycles`: Equivalent battery cycles ($E_{\text{throughput}} / 200\,\text{kWh}$).
8. `unmet_critical_load_kwh`: Unmet critical load ($\text{kWh}$).
9. `system_reliability_pct`: Load Serving Fraction (LSF $\% = 100 \times (1 - E_{\text{unmet}} / E_{\text{demand}})$).
10. `constraint_violations_count`: Count of MILP or simulator constraint violations.

---

## 10. PAIRED EXPERIMENTAL DESIGN & INVARIANTS

For every eligible origin $i \in \{1 \dots 173\}$, the execution phase will execute two paired runs:

```
CONDITION A (Treatment): Stage81ForecastEngine (y_pred from ODD predictions CSV)
CONDITION B (Control):   LocalBaselineForecastEngine (Baseline heuristic forecast)
```

### Strict Invariants Across Condition A and B:
* Same origin timestamp $t_0$.
* Same initial station state ($\text{SOC}_0 = 50.0\%$, $E_0 = 100\,\text{kWh}$).
* Same actual solar ground truth trajectory ($y_{\text{true}}$ from Nuolja 2024 data).
* Same station demand trajectory ($35\,\text{kW}$ synthetic load).
* Same wind power trajectory.
* Same SciPy MILP / HiGHS optimizer configuration (`LocalMILPEnergyOptimizer`).
* Same Digital Twin simulator physics (`DigitalTwinSimulator`).
* Same 24-step receding horizon MPC execution protocol.

---

## 11. FUTURE-TRUTH FIREWALL

```yaml
FUTURE_TRUTH_FIREWALL: ESTABLISHED
```

```
CONTROLLER VISIBLE:
  - StationState at t0
  - Historical observations up to t0
  - Supplied 24h forecast (y_pred for Condition A; baseline for Condition B)
  - Authorized PV conversion metadata (D3 mapping)

CONTROLLER FORBIDDEN:
  - Future actual solar ground truth (y_true at t1...t24)
  - Future actual station demand
  - Future actual wind generation

SIMULATOR / EVALUATOR VISIBLE:
  - Realized H1 dispatch action from DispatchPlan
  - Hidden actual ground truth (y_true at t1) for physical state advancement
```

* **Enforcement:** Code path in `system/runtime/runner.py` fetches `future_actuals` via `get_future_ground_truth()` **after** optimization completes.

---

## 12. FORECASTBUNDLE CONTRACT & FROZEN EMS STACK

* **ForecastBundle Schema:** Version 1.0.0 (`system/schemas/forecast_bundle.py`).
* **D3 PV Transformation:** $P_{\text{raw}} = SW_{\text{IN}} \times 300\text{ m}^2 \times 0.20 \times 0.85 = SW_{\text{IN}} \times 51.0$, $P_{\text{solar}} = \min(P_{\text{raw}}, 60000\text{ W})$.
* **D1/D2 Interval Bounds:** Degenerate point representation ($\text{lower} = \text{point} = \text{upper}$).
* **Optimizer Stack:** `LocalMILPEnergyOptimizer` (SciPy MILP / HiGHS).
* **Simulator Stack:** `DigitalTwinSimulator`.

---

## 13. FORECAST METRICS & ASSOCIATIONAL ANALYSIS

### Predefined Origin-Level Analysis:
For each eligible origin $i$, paired deltas will be calculated:
$$\Delta \text{Fuel}_i = \text{Fuel}_{\text{Stage8.1}, i} - \text{Fuel}_{\text{Control}, i}$$
$$\Delta \text{Curtailment}_i = \text{Curtailment}_{\text{Stage8.1}, i} - \text{Curtailment}_{\text{Control}, i}$$

* **Negative $\Delta \text{Fuel}$:** Stage8.1 consumed less diesel than control.
* **Positive $\Delta \text{Fuel}$:** Stage8.1 consumed more diesel than control.

---

## 14. STATISTICAL DEPENDENCE HANDLING

```yaml
STATISTICAL_DEPENDENCE_HANDLING: >
  Paired origin-level non-parametric bootstrap resampling (10,000 iterations over N=173 origins) and Wilcoxon signed-rank test; no naive n=4152 row-independence assumptions.
```

---

## 15. FAILURE HANDLING & STOPPING RULES

* **Fault Semantics:** Use existing D4-C1 governed fault rules (`GOVERNED_DEGRADED` zero dispatch, `objective_value = 1e9`).
* **Failure Preservation:** Infeasibility or solver exceptions must be recorded and classified, **not** silently retried with altered parameters or relaxed constraints.
* **Result-Dependent Stopping:** **PROHIBITED.** All eligible origins must be attempted regardless of early interim outcomes.

---

## 16. PROTOCOL LOCK & REPRODUCIBILITY

```yaml
PROTOCOL_LOCK_REQUIRED: YES
PROTOCOL_STATUS: LOCKED & FROZEN
```

* The experimental protocol defined in this document is **LOCKED**. No protocol modifications are permitted during or after execution.

---

## 17. RAW EVIDENCE REQUIREMENTS FOR FUTURE EXECUTION

The future execution task must preserve raw evidence before generating summaries:
1. `per_origin_control_results.json`: Full 24-step dispatch and evaluation readouts for Control.
2. `per_origin_stage81_results.json`: Full 24-step dispatch and evaluation readouts for Stage8.1.
3. `paired_origin_deltas.csv`: Origin-by-origin forecast errors, fuel deltas, curtailment deltas, and LSF values.
4. `execution_manifest.json`: Runtime configuration, git commit hash, and artifact SHA-256 hashes.

---

## 18. DOWNSTREAM ENVIRONMENT PROVENANCE

```yaml
DOWNSTREAM_ENVIRONMENT: MIXED / SYNTHETIC CONTROLLED
```
* **Irradiance:** Real Stage8.1 ODD forecasts + real Nuolja 2024 actual ground truth.
* **Demand & Wind:** Controlled synthetic demand ($35\,\text{kW}$) and synthetic wind proxy.
* **Hardware:** Synthetic demonstration parameters ($200\,\text{kWh}$ BESS, $100\,\text{kW}$ GenSet).

---

## 19. RELATIONSHIP TO PHASE D5

* **D5 (Frozen):** Tested EMS control sensitivity to *controlled multiplicative forecast scaling perturbations* ($\gamma = 0.70 \dots 1.30$).
* **Stage8.1 Replay (Authorized):** Tests EMS operational outcomes under *empirical Stage8.1 forecast error propagation*.
* **D5 Status:** D5 remains closed and frozen.

---

## 20. LIMITATIONS

1. Stage8.1 OOD benchmark ($36.19\text{ W/m}^2$) remains frozen.
2. D3 PV mapping remains an authorized engineering representation.
3. Degenerate bounds ($\text{lower} = \text{point} = \text{upper}$) carry no statistical coverage claim.
4. Downstream EMS environment remains synthetic/controlled.
5. Real station electrical demand is DATA BLOCKED.
6. Empirical forecast error $\to$ EMS outcome relationship remains **NOT YET ESTABLISHED** until the authorized execution task runs.

---

## 21. INTEGRITY REGISTER

```yaml
SOURCE_FILES_MODIFIED: NONE
SCIENTIFIC_MODEL_MODIFIED: NO
EMS_MODIFIED: NO
FORECASTBUNDLE_SCHEMA_MODIFIED: NO
DISPATCHPLAN_SCHEMA_MODIFIED: NO
STATIONSTATE_SCHEMA_MODIFIED: NO
SIMULATOR_MODIFIED: NO
UI_MODIFIED: NO
D5_MODIFIED: NO
STAGE8_1_BENCHMARK_MODIFIED: NO
EXPERIMENT_EXECUTED: NO
MODEL_RETRAINED: NO
NEW_PREDICTIONS_GENERATED: NO
NEW_DATASET_CREATED: NO
SMOKE_TEST_EXECUTED: NO
```

---

## 22. FINAL REQUIRED STATUS & DECISION

```yaml
GOVERNANCE_DECISION: A — EXPERIMENT AUTHORIZED
EXPERIMENT_AUTHORIZATION: AUTHORIZED
TREATMENT_ARTIFACT: POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv
TREATMENT_SHA256: a4d288f9bba4a57c045f3671c1a4a78f2be11de7829af6e78103da97fa836a2d
CONTROL_ARTIFACT: system/forecasting/implementations/baseline.py (LocalBaselineForecastEngine)
EXPECTED_ORIGINS: 173
FINAL_ELIGIBLE_ORIGINS: DETERMINED_BY_PREDECLARED_RULES
INELIGIBLE_ORIGINS: NONE
EXPERIMENTAL_UNIT: ONE_COMPLETE_24H_FORECAST_ORIGIN_REPLAY
PRIMARY_ENDPOINT: total_diesel_fuel_liters
PRIMARY_ENDPOINT_RATIONALE: Direct physical relevance to polar microgrid fuel logistics, non-negative, high sensitivity to solar forecasting accuracy, and exposed natively by EvaluationEngine.
PRIMARY_ENDPOINT_PRE_REGISTRATION_STATUS: ESTABLISHED
SECONDARY_ENDPOINTS:
  - total_diesel_energy_kwh
  - total_renewable_energy_used_kwh
  - total_renewable_curtailment_kwh
  - renewable_curtailment_pct
  - renewable_utilization_pct
  - battery_throughput_kwh
  - battery_equivalent_cycles
  - unmet_critical_load_kwh
  - system_reliability_pct
  - constraint_violations_count
STATISTICAL_DEPENDENCE_HANDLING: Paired origin-level non-parametric bootstrap resampling and Wilcoxon signed-rank test over N=173 origins; no naive n=4152 independence assumptions.
FUTURE_TRUTH_FIREWALL: ESTABLISHED
RESULT_DEPENDENT_STOPPING: PROHIBITED
PROTOCOL_LOCK_REQUIRED: YES
EXPERIMENT_EXECUTED: NO
NEXT_AUTHORIZED_STEP: SEPARATE_EXECUTION_TASK_FOR_STAGE8.1_EMS_EMPIRICAL_REPLAY_EXPERIMENT
```
