import json
import os

md_content = """# POLARIS SYSTEM D5 — FINAL SCIENTIFIC INTERPRETATION & FORECAST-TO-EMS TRACE

**Phase**: D5 — Forecast-Error → EMS Robustness  
**Governance Action**: FINAL DOCUMENTATION-LEVEL SCIENTIFIC INTERPRETATION CORRECTION  
**Timestamp**: 2026-09-17T09:05:00+05:30  
**Artifact ID**: `POLARIS_SYSTEM_D5_SCIENTIFIC_INTERPRETATION_20260917_CORRECTED`  

---

> [!IMPORTANT]  
> **THIS IS A READ-ONLY SCIENTIFIC INTERPRETATION CORRECTION AND PROVENANCE RECONCILIATION.**  
> **NO EXPERIMENTS WERE RERUN. NO CODE, SCHEMAS, OPTIMIZERS, DIGITAL TWIN, OR RAW EVIDENCE WERE MODIFIED.**  
> **ALL NUMERICAL METRICS ARE RETRIEVED DIRECTLY FROM THE PRESERVED D5 RESULTS CHECKPOINT.**  

---

## 1. PRIMARY SCIENTIFIC QUESTION & PROVENANCE TRACE

This study analyzes:

> *"How does downstream POLARIS EMS operational behavior change as a function of systematic forecast error in solar, wind, and demand when the frozen closed-loop MPC is supplied with perturbed forecasts under identical hidden ground-truth actual trajectories?"*

### Executable Forecast Data-Flow Trace

Tracing executable runtime code from `LocalDataProvider` to physical state evolution:

```text
LocalDataProvider (system/data/provider.py)
        ↓
LocalBaselineForecastEngine (system/forecasting/implementations/baseline.py)
        ↓
ForecastBundle (system/schemas/forecast_bundle.py)
        ↓
ForecastPerturber (system/robustness/perturbation.py)
        ↓
LocalMILPEnergyOptimizer (system/optimization/implementations/milp.py)
        ↓
DispatchPlan (system/schemas/dispatch_plan.py)
        ↓
DigitalTwinSimulator (system/simulation/simulator.py)
        ↓
physical outcomes & D5MetricsCalculator (system/robustness/metrics.py)
```

At the exact point where D5 supplies the `ForecastBundle` to the EMS MILP optimizer, the forecast values originate as follows:

| Forecast Channel | Producer | Source Code Path | Producer Type | Stage8.1 ML Output Used? | Target / Semantics | Point of Entry into ForecastBundle |
| --- | --- | --- | --- | --- | --- | --- |
| **Solar Irradiance (`SW_IN`)** | `LocalBaselineForecastEngine` | `system/forecasting/implementations/baseline.py:65-74` | Deterministic baseline / clear-sky heuristic | **NO (FALSE)** | Surface downwelling shortwave radiation ($W/m^2$) | `ForecastBundle.solar_irradiance` |
| **Solar Generation (`P_solar`)** | `LocalBaselineForecastEngine` | `system/forecasting/implementations/baseline.py:75` | Deterministic baseline / physical PV conversion | **NO (FALSE)** | Downstream electrical generation ($W$) derived via $P_{solar} = SW\_IN \cdot A_{PV} \cdot \eta_{PV} \cdot PR / 1000$ | `ForecastBundle.solar_power` |
| **Wind Generation (`P_wind`)** | `LocalBaselineForecastEngine` | `system/forecasting/implementations/baseline.py:78-79` | Deterministic baseline / diurnal sine heuristic | **NO (FALSE)** | Non-solar electrical generation ($W$) via `last_obs_wind + 5000 * sin(...)` | `ForecastBundle.wind_power` |
| **Demand (`P_demand`)** | `LocalBaselineForecastEngine` | `system/forecasting/implementations/baseline.py:82-83` | Deterministic baseline / diurnal cosine heuristic | **NO (FALSE)** | Station load demand ($W$) via `last_obs_demand + 3000 * cos(...)` | `ForecastBundle.load_demand` |

> [!NOTE]  
> `LocalBaselineForecastEngine` is a **deterministic prototype baseline / heuristic forecast engine**. It is NOT an ML forecasting model, and NO Stage8.1 ML model artifacts (such as Chronos or TimesFM) generated any forecast values used in the D5 runtime.

---

## 2. CRITICAL DISTINCTION: STAGE8.1 VS D5

The project maintains two distinct scientific paths:

### STAGE8.1 RESEARCH PATH (Forecasting Model Research)
```text
Historical / meteorological inputs
        ↓
Stage8.1 solar forecasting research
        ↓
Chronos / TimesFM / evaluated forecasting models
        ↓
solar forecasting accuracy evaluation on SW_IN
```

### D5 EXECUTION PATH (Downstream EMS Sensitivity)
```text
LocalDataProvider
        ↓
LocalBaselineForecastEngine (prototype baseline)
        ↓
baseline ForecastBundle
        ↓
controlled multiplicative perturbation (ForecastPerturber)
        ↓
frozen MILP EMS optimizer
        ↓
Digital Twin simulator
        ↓
operational outcomes (fuel, curtailment, LSF, SOC)
```

**D5 did not directly evaluate the Stage8.1 ML forecasting model.**

The fact that both Stage8.1 and D5 involve solar forecast quantities does NOT establish that D5 evaluated the Stage8.1 ML model. Stage8.1 evaluated forecasting model performance on its defined target ($SW\_IN$) and evaluation protocol. D5 evaluated downstream EMS operational response when forecast inputs are systematically perturbed under the frozen closed-loop architecture.

---

## 3. FORECASTING TARGET HIERARCHY

The POLARIS project target hierarchy is structured as:

```text
Stage8.1 forecasting target
        ↓
SW_IN / solar irradiance (surface downwelling shortwave radiation in W/m²)
        ↓
existing physical / PV conversion semantics (P_solar = SW_IN * PV_area * PV_eff / 1000)
        ↓
P_solar electrical generation (kW)
        ↓
EMS solar forecast channel
```

* `SW_IN` is the primary Stage8.1 solar forecasting prediction target.
* `P_solar` is the downstream electrical generation quantity derived through existing physical conversion semantics.
* Chronos and TimesFM were trained and evaluated on `SW_IN`, not directly on `P_solar`. `P_solar` was not an independently trained Stage8.1 ML target.

---

## 4. INPUT FEATURE ≠ PREDICTION TARGET ≠ FORECAST CHANNEL

These three concepts are distinct and not interchangeable:

* **Input Feature**: A variable provided as context to a model (e.g. historical wind or temperature used during forecasting research).
* **Prediction Target**: The specific variable an ML model is trained to predict (e.g. `SW_IN` irradiance in Stage8.1).
* **Forecast Channel**: A stream in the `ForecastBundle` supplied to the EMS optimizer (e.g. `P_solar`, `P_wind`, `P_demand`).

For wind, the executable code trace proves that `P_wind` in the D5 runtime is generated by a heuristic persistence rule (`last_obs_wind + 5000 * sin(...)`). Wind is **NOT** a prediction target of the solar forecasting model, nor is it generated by the solar ML model. Wind performance must not be attributed to the solar model.

---

## 5. CONTROLLED D5 PERTURBATION ≠ EMPIRICAL MODEL ERROR

The following distinction is preserved throughout this scientific interpretation:

```text
Stage8.1 model error  ≠  D5 baseline forecast error  ≠  D5 injected perturbation
```

* D5 evaluates: `controlled forecast perturbation → EMS response`.
* D5 does **NOT** measure: empirical forecast-error distribution, model bias distribution, calibration, confidence interval coverage, real-world ±30% error frequency, Chronos/TimesFM generalization error, or the probability of a real forecast being ±30% wrong.
* Terms such as *"observed model error"*, *"actual model bias"*, or *"empirical forecasting error"* are **prohibited** when referring to D5 injected perturbations. The proper terminology is **controlled forecast perturbation**, **synthetic forecast bias**, or **specified multiplicative perturbation**.

---

## 6. AUTHORITATIVE SCENARIO CLASSIFICATION TABLE

| Scenario | Perturbed Channel | D5 Forecast Source | Stage8.1 ML Output Actually Used? | Direct ML Accuracy Evaluation? | Primary Scientific Purpose |
| --- | --- | --- | --- | --- | --- |
| **D5-1** | Solar ($0.70\times$) | `LocalBaselineForecastEngine` | **NO** | **NO** | Solar-channel EMS sensitivity; indirectly relevant to Stage8.1 |
| **D5-2** | Solar ($1.30\times$) | `LocalBaselineForecastEngine` | **NO** | **NO** | Solar-channel EMS sensitivity; indirectly relevant to Stage8.1 |
| **D5-3** | Wind ($0.70\times$) | `LocalBaselineForecastEngine` | **NO** | **NO** | Wind-channel EMS sensitivity; EMS system-level sensitivity only |
| **D5-4** | Demand ($1.20\times$) | `LocalBaselineForecastEngine` | **NO** | **NO** | Demand-channel EMS sensitivity; EMS system-level sensitivity only |
| **D5-5** | Solar ($1.30\times$) + Wind ($1.30\times$) + Demand ($0.80\times$) | `LocalBaselineForecastEngine` | **NO** | **NO** | Compound EMS sensitivity; EMS system-level compound sensitivity |
| **D5-6** | Solar ($1.15\times$) + Wind ($1.15\times$) persistent 168h | `LocalBaselineForecastEngine` | **NO** | **NO** | Persistent multi-channel EMS sensitivity; EMS persistent-bias/endurance sensitivity |

> [!IMPORTANT]  
> **"Indirectly relevant to Stage8.1" does NOT mean "evaluates Stage8.1."** D5-1 and D5-2 manipulate the solar forecast channel, which corresponds conceptually to the Stage8.1 domain, but they use the baseline forecast engine and do not measure Stage8.1 ML model accuracy.

---

## 7. PRESERVED NUMERICAL RESULTS SUMMARY

All numerical D5 results remain strictly unmodified from `ems/reports/system_integration/POLARIS_SYSTEM_D5_RESULTS_CHECKPOINT.json`:

| Scenario | Perturbation ($\gamma$) | Horizon ($N$) | Control LSF | Perturbed LSF | Control Fuel | Perturbed Fuel | $\Delta$ Fuel (L) | $\Delta$ Fuel (%) | Control Curtailment | Perturbed Curtailment | $\Delta$ Curtailment (kWh) | $\Delta$ Curtailment (%) | SOC Range (%) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **D5-1** | Solar $0.70\times$ | 24 | 100.00% | 100.00% | 85.92 L | 88.07 L | +2.15 L | +2.50% | 147.33 kWh | 57.22 kWh | -90.11 kWh | -61.16% | 20.00% – 88.03% |
| **D5-2** | Solar $1.30\times$ | 24 | 100.00% | 100.00% | 85.92 L | 44.02 L | -41.90 L | -48.77% | 147.33 kWh | 165.29 kWh | +17.96 kWh | +12.19% | 20.00% – 83.30% |
| **D5-3** | Wind $0.70\times$ | 24 | 100.00% | 100.00% | 85.92 L | 131.96 L | +46.04 L | +53.58% | 147.33 kWh | 13.13 kWh | -134.20 kWh | -91.09% | 20.79% – 93.10% |
| **D5-4** | Demand $1.20\times$ | 24 | 100.00% | 100.00% | 85.92 L | 135.72 L | +49.81 L | +57.97% | 147.33 kWh | 25.19 kWh | -122.15 kWh | -82.91% | 20.00% – 86.29% |
| **D5-5** | Compound S5 | 24 | 100.00% | 100.00% | 85.92 L | 0.00 L | -85.92 L | -100.00% | 147.33 kWh | 483.47 kWh | +336.14 kWh | +228.16% | 20.00% – 75.46% |
| **D5-6** | Persistent S6 | 168 | 100.00% | 100.00% | 241.48 L | 144.82 L | -96.66 L | -40.03% | 1574.53 kWh | 2265.89 kWh | +691.36 kWh | +43.91% | 20.00% – 95.00% |

---

## 8. EVIDENTIARY AUDIT OF DISPATCH-LEVEL MECHANISMS

Each operational mechanism claim is classified into one of three rigor tiers:

1. **OBSERVED**: Directly demonstrated by preserved dispatch-level evidence.
2. **INFERRED**: Reasonable interpretation consistent with evidence, but not directly demonstrated as an isolated cause.
3. **UNIDENTIFIABLE**: Insufficient evidence to isolate the exact mechanism.

### 8.1 Rigorous 100% LSF Interpretation
* **Statement**: **"All six tested scenarios maintained 100% Load-Served Fraction under the specified experimental conditions."**
* **Scope Boundary**: **"This demonstrates no unmet load in the tested trajectories; it does not establish universal robustness, safety, or immunity to forecast error."**
* **Impact Reality**: **"Forecast perturbations nevertheless materially changed diesel consumption, diesel operating hours, renewable curtailment, and SOC behavior."**
* **Status**: `OBSERVED` (LSF metrics = 100.00%, fuel/curtailment differences preserved).

### 8.2 Resource Headroom Scope (Battery & Diesel)
* **Correct Claim**: **"Under the tested station configuration, hidden actual trajectories, perturbation magnitudes, and durations, the configured resources maintained load service without recorded physical constraint violations."**
* **Prohibited Claim**: Do *not* claim "The 200 kWh battery and 100 kW diesel generator absorbed 20–30% forecast errors" as an isolated capacity generalization.
* **Status**: `INFERRED` (System flexibility is consistent with capacity headroom, but specific component isolation requires single-variable physical ablation).

### 8.3 MPC Endurance (D5-6)
* **Correct Claim**: **"D5-6 completed 168 consecutive closed-loop MPC decision points under the specified persistent perturbation without unmet load, state-violation termination, or recorded execution fault."**
* **Prohibited Claim**: Do *not* claim "D5-6 proves MPC stability." Finite 168-hour execution does not prove infinite-horizon stability, universal control stability, long-term field reliability, or guaranteed operational stability.
* **Status**: `OBSERVED` (168-step execution completed without failure); `INFERRED` (MPC closed-loop stability over 168 steps under test profile); `UNIDENTIFIABLE` (Infinite-horizon stability).

### 8.4 Compound Optimistic Forecast Perturbation (D5-5)
* **Correct Terminology**: **compound optimistic forecast perturbation** (solar = $1.30\times$, wind = $1.30\times$, demand = $0.80\times$).
* **Prohibited Terminology**: Avoid calling this "extreme forecast optimism" as if it represented an empirically observed real-world error combination.
* **Status**: `OBSERVED` (0.00 L fuel, 483.47 kWh curtailment); `INFERRED` (Optimizer completely uncommits diesel due to expected renewable surplus).

### 8.5 Persistent Renewable Perturbation (D5-6)
* **Correct Terminology**: **persistent +15% renewable forecast perturbation over 168 sequential closed-loop iterations**.
* **Structure Note**: **D5-6 is one 168-iteration persistent scenario, not 168 independent replicates.**
* **Status**: `OBSERVED` (-96.66 L fuel, +691.36 kWh curtailment over 168 steps).

---

## 9. FORECASTING CONTRIBUTION VS. EMS CONTRIBUTION

```text
Forecasting quality (Stage8.1)
        ↓  (Arrow 1: Forecast uncertainty / error distribution)
Forecast inputs to EMS
        ↓  (Arrow 2: Injected perturbation / baseline engine)
EMS sensitivity (D5)
        ↓  (Arrow 3: MILP optimization & dispatch)
Dispatch consequences
        ↓  (Arrow 4: Digital Twin execution)
Operational outcomes (fuel, curtailment, SOC, LSF)
```

* **Stage8.1 Contribution**: Evaluates Arrow 1 (solar forecasting model accuracy on $SW\_IN$ target using historical/meteorological data).
* **D5 Contribution**: Evaluates Arrow 2 $\rightarrow$ Arrow 4 (downstream EMS operational response when forecast inputs are systematically perturbed under frozen closed-loop MPC).
* **Scientific Firewall Statement**: **D5 alone does not quantitatively establish Arrow 1 using Stage8.1 model error, because Stage8.1 model output was not used in the D5 runtime.**

---

## 10. THREE-TIER EVIDENCE HIERARCHY

| Rigor Tier | Scientific Findings & Claims |
| --- | --- |
| **LEVEL 1 — DIRECTLY DEMONSTRATED** | • 100% LSF maintained in all six tested scenarios under specified test conditions.<br>• Forecast perturbations materially change fuel burn (-100.00% to +57.97%) and curtailment (-91.09% to +228.16%).<br>• Solar overprediction (D5-2) reduces diesel fuel by 41.90 L (-48.77%) and increases curtailment by 17.96 kWh (+12.19%).<br>• Wind underprediction (D5-3) increases diesel fuel by 46.04 L (+53.58%) and reduces curtailment by 134.20 kWh (-91.09%).<br>• Demand overprediction (D5-4) increases diesel fuel by 49.81 L (+57.97%) and reduces curtailment by 122.15 kWh (-82.91%).<br>• Compound optimistic perturbation (D5-5) reduces fuel by 85.92 L (-100.00%) and increases curtailment by 336.14 kWh (+228.16%).<br>• Persistent +15% renewable perturbation (D5-6) reduces 7-day fuel by 96.66 L (-40.03%) and increases curtailment by 691.36 kWh (+43.91%) over 168 closed-loop steps. |
| **LEVEL 2 — REASONABLE SYSTEM INTERPRETATION** | • Under tested station configuration, hidden actual trajectories, perturbation magnitudes, and durations, configured battery (200 kWh) and diesel (100 kW) resources maintained load service without recorded physical constraint violations.<br>• Optimistic forecast bias causes the MILP solver to defer diesel commitment, increasing reliance on battery storage.<br>• Pessimistic forecast bias forces precautionary diesel commitment, increasing fuel burn and reducing curtailment. |
| **LEVEL 3 — NOT ESTABLISHED** | • Stage8.1 empirical model-error distribution or empirical forecast accuracy.<br>• Stage8.1 model calibration or generalization beyond its benchmark.<br>• Real-world forecast-error frequency or probability of ±30% error.<br>• Global EMS robustness or safety under arbitrary extreme weather.<br>• Infinite-horizon stability or universal control stability.<br>• Field reliability under physical component aging.<br>• Wind forecasting performance of the solar model.<br>• Demand forecasting performance. |

---

## 11. CENTRAL D5 SCIENTIFIC RESULT

The core conclusion of the D5 evaluation is:

> **"Under the tested conditions, the frozen POLARIS EMS maintained load service despite the specified systematic forecast perturbations, while its economic and resource-dispatch behavior remained materially sensitive to forecast bias."**

> **"D5 therefore characterizes forecast-to-EMS operational sensitivity rather than forecasting-model accuracy."**

---

## 12. REQUIRED FINAL QUESTION-BY-QUESTION CONCLUSION

### Q1 — What did D5 test?
Controlled systematic forecast perturbations ($\gamma = 0.70 \dots 1.30$) across solar, wind, and demand channels and their downstream EMS operational consequences in a closed-loop MPC environment.

### Q2 — What did D5 observe?
100% Load-Served Fraction across all six tested scenarios, accompanied by material changes in diesel fuel consumption (-100.00% to +57.97%), diesel operating hours, renewable curtailment (-91.09% to +228.16%), and SOC trajectory dynamics.

### Q3 — Did D5 test Stage8.1 ML accuracy?
**No. D5 did not directly evaluate Stage8.1 ML forecasting accuracy.** The D5 runtime used `LocalBaselineForecastEngine` (a prototype baseline / heuristic forecast engine) and did not ingest Chronos or TimesFM prediction outputs.

### Q4 — What is D5-1/D5-2's relationship to Stage8.1?
They are solar-channel EMS sensitivity experiments that are conceptually relevant to the Stage8.1 solar forecasting problem (modifying the solar channel), but they do NOT evaluate Stage8.1 model accuracy or empirical model error.

### Q5 — What are D5-3/D5-4?
EMS system-level sensitivity experiments for wind and demand forecast channels, evaluating operational sensitivity to non-solar forecast perturbations.

### Q6 — What are D5-5/D5-6?
D5-5 is a compound optimistic forecast perturbation experiment ($1.30\times / 1.30\times / 0.80\times$). D5-6 is a persistent multi-channel forecast perturbation experiment ($1.15\times / 1.15\times$) evaluated over 168 sequential closed-loop MPC steps.

### Q7 — What remains unproven?
Empirical model error distributions, real-world error frequency, field performance under extreme unmodeled weather, global EMS robustness, universal safety, infinite-horizon stability, wind model accuracy, and demand model accuracy.

### Q8 — Where does wind come from?
Wind generation (`P_wind`) is populated in the D5 runtime via a heuristic persistence rule (`last_obs_wind + 5000 * sin(...)`) in `LocalBaselineForecastEngine`. It is NOT an output or prediction target of the solar forecasting model.

---

## 13. GOVERNANCE BOUNDARY & FIREWALL

* **D5 Execution**: COMPLETE.
* **Interpretation Correction**: COMPLETE.
* **Frozen Checkpoints & Raw Evidence**: UNTOUCHED.
* **D6 State**: **NOT AUTHORIZED and NOT INITIATED.**
"""

json_data = {
    "artifact_id": "POLARIS_SYSTEM_D5_SCIENTIFIC_INTERPRETATION_20260917_CORRECTED",
    "timestamp": "2026-09-17T09:05:00+05:30",
    "governance_state": {
        "D4": "CLOSED",
        "D5_CONTRACT": "FROZEN",
        "D5_IMPLEMENTATION": "COMPLETE",
        "D5_IMPLEMENTATION_REVIEW": "PASSED",
        "D5_EXECUTION": "COMPLETED_AS_AUTHORIZED",
        "D5_EVIDENCE_PROVENANCE": "RECONCILED_AND_CORRECTED",
        "D5_RESULTS": "PRESERVED_UNMODIFIED",
        "D6": "NOT_INITIATED"
    },
    "correction_type": "FINAL_DOCUMENTATION_LEVEL_SCIENTIFIC_INTERPRETATION_CORRECTION",
    "primary_scientific_question": "How does downstream POLARIS EMS operational behavior change as a function of systematic forecast error in solar, wind, and demand when the frozen closed-loop MPC is supplied with perturbed forecasts under identical hidden ground-truth actual trajectories?",
    "central_scientific_conclusion": "Under the tested conditions, the frozen POLARIS EMS maintained load service despite the specified systematic forecast perturbations, while its economic and resource-dispatch behavior remained materially sensitive to forecast bias. D5 therefore characterizes forecast-to-EMS operational sensitivity rather than forecasting-model accuracy.",
    "runtime_forecast_provenance": {
        "chain": [
            "LocalDataProvider (system/data/provider.py)",
            "LocalBaselineForecastEngine (system/forecasting/implementations/baseline.py)",
            "ForecastBundle (system/schemas/forecast_bundle.py)",
            "ForecastPerturber (system/robustness/perturbation.py)",
            "LocalMILPEnergyOptimizer (system/optimization/implementations/milp.py)",
            "DispatchPlan (system/schemas/dispatch_plan.py)",
            "DigitalTwinSimulator (system/simulation/simulator.py)",
            "D5MetricsCalculator (system/robustness/metrics.py)"
        ],
        "channels": {
            "solar_irradiance": {
                "producer": "LocalBaselineForecastEngine",
                "producer_type": "DETERMINISTIC_BASELINE",
                "code_path": "system/forecasting/implementations/baseline.py:65-74",
                "target_variable": "SW_IN (W/m^2)",
                "Stage8_1_ML_output": False,
                "is_input_feature": False,
                "is_observed": False,
                "is_synthetic": True,
                "point_of_entry": "ForecastBundle.solar_irradiance"
            },
            "solar_generation": {
                "producer": "LocalBaselineForecastEngine",
                "producer_type": "DETERMINISTIC_BASELINE",
                "code_path": "system/forecasting/implementations/baseline.py:75",
                "target_variable": "P_solar (W)",
                "Stage8_1_ML_output": False,
                "is_input_feature": False,
                "is_observed": False,
                "is_synthetic": True,
                "point_of_entry": "ForecastBundle.solar_power"
            },
            "wind_generation": {
                "producer": "LocalBaselineForecastEngine (Heuristic persistence rule)",
                "producer_type": "HEURISTIC",
                "code_path": "system/forecasting/implementations/baseline.py:78-79",
                "target_variable": "P_wind (W)",
                "Stage8_1_ML_output": False,
                "is_input_feature": False,
                "is_observed": False,
                "is_synthetic": True,
                "point_of_entry": "ForecastBundle.wind_power"
            },
            "demand": {
                "producer": "LocalBaselineForecastEngine (Heuristic persistence rule)",
                "producer_type": "HEURISTIC",
                "code_path": "system/forecasting/implementations/baseline.py:82-83",
                "target_variable": "P_demand (W)",
                "Stage8_1_ML_output": False,
                "is_input_feature": False,
                "is_observed": False,
                "is_synthetic": True,
                "point_of_entry": "ForecastBundle.load_demand"
            }
        }
    },
    "stage8_1_vs_d5": {
        "stage8_1_direct_evaluation_in_d5": False,
        "explicit_statement": "D5 did not directly evaluate the Stage8.1 ML forecasting model.",
        "target_hierarchy": [
            "Stage8.1 forecasting target: SW_IN (solar irradiance in W/m^2)",
            "Physical / PV conversion semantics: P_solar = SW_IN * PV_area * PV_eff / 1000",
            "Downstream electrical generation quantity: P_solar (kW)",
            "EMS solar forecast channel: ForecastBundle.solar_power"
        ],
        "distinction": "Input feature != prediction target != forecast channel. Injected D5 perturbation != empirical ML model error."
    },
    "scenario_classification_matrix": [
        {
            "scenario": "D5-1",
            "perturbed_channel": "Solar (0.70x)",
            "d5_forecast_source": "LocalBaselineForecastEngine",
            "stage8_1_ml_output_used": False,
            "direct_ml_accuracy_evaluation": False,
            "primary_scientific_purpose": "Solar-channel EMS sensitivity; indirectly relevant to Stage8.1"
        },
        {
            "scenario": "D5-2",
            "perturbed_channel": "Solar (1.30x)",
            "d5_forecast_source": "LocalBaselineForecastEngine",
            "stage8_1_ml_output_used": False,
            "direct_ml_accuracy_evaluation": False,
            "primary_scientific_purpose": "Solar-channel EMS sensitivity; indirectly relevant to Stage8.1"
        },
        {
            "scenario": "D5-3",
            "perturbed_channel": "Wind (0.70x)",
            "d5_forecast_source": "LocalBaselineForecastEngine (Heuristic)",
            "stage8_1_ml_output_used": False,
            "direct_ml_accuracy_evaluation": False,
            "primary_scientific_purpose": "Wind-channel EMS sensitivity; EMS system-level sensitivity only"
        },
        {
            "scenario": "D5-4",
            "perturbed_channel": "Demand (1.20x)",
            "d5_forecast_source": "LocalBaselineForecastEngine (Heuristic)",
            "stage8_1_ml_output_used": False,
            "direct_ml_accuracy_evaluation": False,
            "primary_scientific_purpose": "Demand-channel EMS sensitivity; EMS system-level sensitivity only"
        },
        {
            "scenario": "D5-5",
            "perturbed_channel": "Solar (1.30x) + Wind (1.30x) + Demand (0.80x)",
            "d5_forecast_source": "LocalBaselineForecastEngine",
            "stage8_1_ml_output_used": False,
            "direct_ml_accuracy_evaluation": False,
            "primary_scientific_purpose": "Compound EMS sensitivity; EMS system-level compound sensitivity"
        },
        {
            "scenario": "D5-6",
            "perturbed_channel": "Solar (1.15x) + Wind (1.15x) persistent 168h",
            "d5_forecast_source": "LocalBaselineForecastEngine",
            "stage8_1_ml_output_used": False,
            "direct_ml_accuracy_evaluation": False,
            "primary_scientific_purpose": "Persistent multi-channel EMS sensitivity; EMS persistent-bias/endurance sensitivity"
        }
    ],
    "preserved_numerical_results": {
        "D5-1": {"lsf_pct": 100.0, "delta_fuel_l": 2.15, "delta_fuel_pct": 2.50, "delta_curtailment_kwh": -90.11, "delta_curtailment_pct": -61.16, "min_max_soc_pct": [20.0, 88.03]},
        "D5-2": {"lsf_pct": 100.0, "delta_fuel_l": -41.90, "delta_fuel_pct": -48.77, "delta_curtailment_kwh": 17.96, "delta_curtailment_pct": 12.19, "min_max_soc_pct": [20.0, 83.30]},
        "D5-3": {"lsf_pct": 100.0, "delta_fuel_l": 46.04, "delta_fuel_pct": 53.58, "delta_curtailment_kwh": -134.20, "delta_curtailment_pct": -91.09, "min_max_soc_pct": [20.79, 93.10]},
        "D5-4": {"lsf_pct": 100.0, "delta_fuel_l": 49.81, "delta_fuel_pct": 57.97, "delta_curtailment_kwh": -122.15, "delta_curtailment_pct": -82.91, "min_max_soc_pct": [20.0, 86.29]},
        "D5-5": {"lsf_pct": 100.0, "delta_fuel_l": -85.92, "delta_fuel_pct": -100.00, "delta_curtailment_kwh": 336.14, "delta_curtailment_pct": 228.16, "min_max_soc_pct": [20.0, 75.46]},
        "D5-6": {"lsf_pct": 100.0, "delta_fuel_l": -96.66, "delta_fuel_pct": -40.03, "delta_curtailment_kwh": 691.36, "delta_curtailment_pct": 43.91, "min_max_soc_pct": [20.0, 95.00], "steps": 168}
    },
    "evidence_hierarchy": {
        "level_1_directly_demonstrated": [
            "All six tested scenarios maintained 100% Load-Served Fraction under the specified experimental conditions.",
            "Forecast perturbations materially change diesel consumption (-100.00% to +57.97%), diesel operating hours, renewable curtailment (-91.09% to +228.16%), and SOC trajectory behavior.",
            "Solar overprediction (D5-2) reduces diesel fuel by 41.90 L (-48.77%) and increases curtailment by 17.96 kWh (+12.19%).",
            "Wind underprediction (D5-3) increases diesel fuel by 46.04 L (+53.58%) and reduces curtailment by 134.20 kWh (-91.09%).",
            "Demand overprediction (D5-4) increases diesel fuel by 49.81 L (+57.97%) and reduces curtailment by 122.15 kWh (-82.91%).",
            "Compound optimistic perturbation (D5-5) reduces diesel fuel by 85.92 L (-100.00%) and increases curtailment by 336.14 kWh (+228.16%).",
            "Persistent +15% renewable perturbation (D5-6) reduces 7-day fuel by 96.66 L (-40.03%) and increases curtailment by 691.36 kWh (+43.91%) over 168 closed-loop steps."
        ],
        "level_2_reasonable_system_interpretation": [
            "Under the tested station configuration, hidden actual trajectories, perturbation magnitudes, and durations, the configured resources maintained load service without recorded physical constraint violations.",
            "Optimistic forecast bias causes the MILP solver to defer diesel commitment, increasing reliance on battery storage.",
            "Pessimistic forecast bias forces precautionary diesel commitment, increasing fuel burn and reducing curtailment."
        ],
        "level_3_not_established": [
            "Stage8.1 empirical model-error distribution or empirical forecast accuracy.",
            "Stage8.1 model calibration or generalization beyond its benchmark.",
            "Real-world forecast-error frequency or probability of +/-30% error.",
            "Global EMS robustness or safety under arbitrary extreme weather.",
            "Infinite-horizon stability or universal control stability.",
            "Field reliability under physical component aging.",
            "Wind forecasting performance of the solar model.",
            "Demand forecasting performance."
        ]
    },
    "required_question_answers": {
        "q1_what_d5_tested": "Controlled systematic forecast perturbations (gamma = 0.70 ... 1.30) across solar, wind, and demand channels and their downstream EMS operational consequences in a closed-loop MPC environment.",
        "q2_what_d5_observed": "100% Load-Served Fraction across all six tested scenarios, accompanied by material changes in diesel fuel consumption (-100.00% to +57.97%), diesel operating hours, renewable curtailment (-91.09% to +228.16%), and SOC trajectory dynamics.",
        "q3_did_d5_test_stage8_1_ml_accuracy": "No. D5 did not directly evaluate Stage8.1 ML forecasting accuracy. The D5 runtime used LocalBaselineForecastEngine (a prototype baseline / heuristic forecast engine) and did not ingest Chronos or TimesFM prediction outputs.",
        "q4_d5_1_d5_2_relationship_to_stage8_1": "They are solar-channel EMS sensitivity experiments that are conceptually relevant to the Stage8.1 solar forecasting problem (modifying the solar channel), but they do NOT evaluate Stage8.1 model accuracy or empirical model error.",
        "q5_what_are_d5_3_d5_4": "EMS system-level sensitivity experiments for wind and demand forecast channels, evaluating operational sensitivity to non-solar forecast perturbations.",
        "q6_what_are_d5_5_d5_6": "D5-5 is a compound optimistic forecast perturbation experiment (1.30x / 1.30x / 0.80x). D5-6 is a persistent multi-channel forecast perturbation experiment (1.15x / 1.15x) evaluated over 168 sequential closed-loop MPC steps.",
        "q7_what_remains_unproven": "Empirical model error distributions, real-world error frequency, field performance under extreme unmodeled weather, global EMS robustness, universal safety, infinite-horizon stability, wind model accuracy, and demand model accuracy.",
        "q8_where_does_wind_come_from": "Wind generation (P_wind) is populated in the D5 runtime via a heuristic persistence rule (last_obs_wind + 5000 * sin(...)) in LocalBaselineForecastEngine. It is NOT an output or prediction target of the solar forecasting model."
    }
}

with open("ems/reports/system_integration/POLARIS_SYSTEM_D5_SCIENTIFIC_INTERPRETATION.md", "w") as f:
    f.write(md_content)

with open("ems/reports/system_integration/POLARIS_SYSTEM_D5_SCIENTIFIC_INTERPRETATION.json", "w") as f:
    json.dump(json_data, f, indent=2)

print("Successfully regenerated both POLARIS_SYSTEM_D5_SCIENTIFIC_INTERPRETATION artifacts!")
