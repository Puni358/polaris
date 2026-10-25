# POLARIS — PATH A / WIND FORECASTING TRACK
## A2 TARGET DEFINITION GOVERNANCE DECISION RECORD

**Document ID:** `POLARIS_WIND_A2_TARGET_DEFINITION_GOVERNANCE_DECISION`  
**Date (UTC):** 2026-09-18  
**Track:** PATH A — WIND FORECASTING TRACK  
**Phase:** A2 Target Definition Governance Decision  
**Decision Status:** `AUTHORIZED_CONDITIONAL_ABISKO_PROXY_TARGET`  
**Implementation Status:** `TARGET_DEFINITION_ONLY` (Model Training/Inference/Benchmarking **NOT AUTHORIZED**)  

---

## 1. DECISION OBJECTIVE

The objective of this formal governance decision record is to determine and define the authoritative empirical target specification for the future POLARIS Path A wind forecasting research track prior to any model implementation or experimental execution.

Specifically, this decision record resolves whether the future A2 wind forecasting research target is formally designated as:

$$\text{MEASURED } 10\,\text{m } \text{HOURLY WIND SPEED AT SMHI ABISKO AUT STATION } 188790$$

under the explicit governance interpretation that:

$$\text{ABISKO WIND SPEED IS USED AS A CONDITIONALLY SUPPORTED REGIONAL PROXY FOR THE MOUNT NUOLJA RESEARCH CONTEXT.}$$

---

## 2. PRIOR A1 / A1.5 / A1.6 EVIDENCE SUMMARY

This governance decision builds directly upon the locked scientific findings of the preceding qualification phases:

- **Phase A1 (`POLARIS_WIND_FORECASTING_A1_TARGET_AND_DATA_QUALIFICATION`):** Established `WIND_TARGET_STATUS = NOT_ESTABLISHED` and `WIND_DATA_STATUS = INSUFFICIENT` due to zero ground-measured wind observations at the primary Mount Nuolja AWS station mast.
- **Phase A1.5 (`POLARIS_WIND_DATA_ACQUISITION_AND_A1_5_QUALIFICATION`):** Acquired and qualified the empirical 1-hour 10m wind speed ($v_{\text{wind}}$ in $\text{m/s}$) and direction dataset from SMHI Station 188790 (`Abisko Aut`, $392.2\,\text{m}$ a.s.l., $\sim 4.1\,\text{km}$ ENE of Mount Nuolja AWS) covering the full 2024 benchmark period ($8,784$ records, $100\%$ complete, SMHI quality controlled).
- **Phase A1.6 (`POLARIS_WIND_A1_6_SITE_TRANSFER_QUALIFICATION`):** Established `TARGET_DECISION = PROXY_TARGET_CONDITIONALLY_SUPPORTED` and `A2_READINESS = CONDITIONALLY_READY_PENDING_SPECIFIED_RESOLUTION`, concluding that Abisko measured wind speed is scientifically defensible as an empirical proxy target representing the regional Nuolja microgrid context, provided site-transfer limitations are explicitly preserved.

---

## 3. AUTHORIZED TARGET DEFINITION

Project governance hereby authorizes the following target specification for future A2 wind forecasting research:

- **A2 Target Variable:** `WIND_SPEED`
- **A2 Target Units:** $\text{m/s}$
- **A2 Target Measurement Height:** $10.0\,\text{m}$ above ground level
- **A2 Target Temporal Resolution:** 1 hour
- **A2 Target Source Station:** `Abisko Aut`
- **A2 Target Station ID:** SMHI Station `188790`
- **A2 Target Empirical Status:** `MEASURED` (empirical ground-truth observation)
- **A2 Site Interpretation:** `CONDITIONAL_REGIONAL_PROXY_FOR_NUOLJA`
- **A2 Direct Nuolja Measurement Status:** `NOT_ESTABLISHED`

```
TARGET_DEFINITION_DECISION = AUTHORIZED_CONDITIONAL_ABISKO_PROXY_TARGET
```

---

## 4. PROXY INTERPRETATION — MANDATORY LIMITATIONS

The future A2 research record **MUST EXPLICITLY PRESERVE** the following mandatory proxy statements:

> [!IMPORTANT]
> *"Abisko measured wind speed is used as a conditionally supported regional proxy for the Mount Nuolja research context; it is not direct measured Nuolja wind."*
> 
> *"The proxy designation supports use of the Abisko series as the empirical forecasting target for this research track; it does not establish meteorological equivalence between Abisko and Mount Nuolja."*

### Prohibited Claims
Project governance explicitly forbids claiming any of the following:
- Abisko wind speed equals Mount Nuolja wind speed.
- Abisko station measurements are direct Mount Nuolja station measurements.
- The $310\,\text{m}$ altitude difference between Abisko and Nuolja has been mathematically corrected.
- Mount Nuolja wind conditions have been empirically reconstructed.
- A validated Abisko $\rightarrow$ Nuolja site-transfer model exists.
- Abisko and Mount Nuolja are meteorologically equivalent sites.

---

## 5. ALTITUDE LIMITATION

Phase A1.6 established that no authorized altitude transfer formula exists in project governance:

```
ALTITUDE_TRANSFER_METHOD = NOT_ESTABLISHED
```

### Directive
Project governance preserves `ALTITUDE_TRANSFER_METHOD = NOT_ESTABLISHED` unchanged. Future A2 research:
- **SHALL NOT** apply power-law or log-law boundary layer scaling formulas.
- **SHALL NOT** apply generic vertical wind scaling equations.
- **SHALL NOT** rescale the measured target values.
- **SHALL NOT** estimate Nuolja wind speed using unauthorized mathematical rescalings.

The A2 research target remains the un-scaled measured Abisko 10m value. The $309.8\,\text{m}$ unresolved altitude difference remains a documented research limitation on interpreting results for the Nuolja context.

---

## 6. WIND-SPEED VS WIND-POWER BOUNDARY

This decision authorizes **ONLY** the research target: **10m measured wind speed in $\text{m/s}$**.

For governance purposes, "A2 wind forecasting" refers strictly to predicting the measured Abisko 10m hourly wind-speed series.

```
A2_WIND_POWER_TARGET = NOT_AUTHORIZED
A2_WIND_GENERATION_FORECASTING = NOT_AUTHORIZED
```

### Strictly Non-Authorized Engineering Modifications:
- Wind power prediction or electrical generation forecasting.
- Conversion of forecasted wind speed ($\text{m/s}$) into electrical power ($\text{W}$).
- Turbine power curve implementations (e.g., IEC 61400-12-1 curves).
- Extrapolation to turbine hub height.
- Wind energy production or microgrid dispatch claims.

Any future conversion from forecast wind speed to electrical generation requires a separate representation decision and explicit governance authorization.

---

## 7. AUTHORIZATION SCOPE

This decision record authorizes **ONLY**:

> Defining the future research target as forecasting the measured 10m hourly Abisko wind-speed series ($v_{\text{wind}}$ in $\text{m/s}$) as a conditionally supported regional proxy target for the Nuolja context.

---

## 8. NON-AUTHORIZED ACTIVITIES

This decision **DOES NOT AUTHORIZE**:
1. Model training of any candidate algorithm (GBDT, Neural, Foundation Models, Persistence).
2. Model inference or synthetic forecast generation.
3. Model selection or champion recommendation.
4. Benchmark performance evaluation or metric calculation.
5. Feature engineering or predictor matrix assembly.
6. Forecast-window generation or dataset splitting.
7. Integration with `ForecastBundle` schema v1.0.
8. Integration with EMS, MPC, or Digital Twin solvers.
9. Execution of new scientific experiments.

---

## 9. GOVERNANCE PRESERVATION

The following frozen system components remain **UNTOUCHED AND UNCHANGED**:
- **Stage8.1 Artifacts:** Frozen Stage8.1 solar irradiance champion model and canonical fold assignments.
- **Governance Decisions D1–D7:** Decisions D1 through D7 remain locked.
- **ForecastBundle Schema:** Version 1.0.0 contract remains solar/wind/demand point schema intact.
- **ForecastEngine Interface:** Interface contract remains unmodified.
- **EMS / MPC Solvers:** Operational MILP/LP solvers remain frozen.
- **Baseline Prototype:** `LocalBaselineForecastEngine` prototype wind persistence heuristic remains `PROTOTYPE_UNVALIDATED_NOT_AUTHORIZED`.

---

## 10. FINAL DECISION

```
TARGET_DEFINITION_DECISION = AUTHORIZED_CONDITIONAL_ABISKO_PROXY_TARGET
A2_READINESS = READY_PENDING_A2_RESEARCH_AUTHORIZATION
```

The measured 10m hourly wind speed series from SMHI Station 188790 (`Abisko Aut`) is formally authorized as the empirical forecasting target for future Path A wind research, explicitly interpreted as a conditionally supported regional proxy for the Nuolja research context.

---

## 11. REQUIRED MACHINE-READABLE STATE

```
PATH_A_SELECTION = SELECTED
WIND_TRACK_STATUS = A2_TARGET_DEFINED_PENDING_A2_RESEARCH_AUTHORIZATION
TARGET_DEFINITION_DECISION = AUTHORIZED_CONDITIONAL_ABISKO_PROXY_TARGET
A2_READINESS = READY_PENDING_A2_RESEARCH_AUTHORIZATION
A2_TARGET_VARIABLE = WIND_SPEED
A2_TARGET_UNITS = M/S
A2_TARGET_HEIGHT = 10M
A2_TARGET_RESOLUTION = HOURLY
A2_TARGET_STATION = ABISKO_AUT_188790
A2_TARGET_EMPIRICAL_STATUS = MEASURED
A2_SITE_INTERPRETATION = CONDITIONAL_REGIONAL_PROXY_FOR_NUOLJA
A2_DIRECT_NUOLJA_MEASUREMENT = NOT_ESTABLISHED
ALTITUDE_TRANSFER_METHOD = NOT_ESTABLISHED
A2_WIND_POWER_TARGET = NOT_AUTHORIZED
A2_WIND_GENERATION_FORECASTING = NOT_AUTHORIZED
A2_MODEL_TRAINING = NOT_AUTHORIZED
A2_MODEL_INFERENCE = NOT_AUTHORIZED
A2_MODEL_SELECTION = NOT_AUTHORIZED
A2_BENCHMARKING = NOT_AUTHORIZED
FORECASTBUNDLE_INTEGRATION = NOT_AUTHORIZED
EMS_INTEGRATION = NOT_AUTHORIZED
NEW_EXPERIMENT = NOT_AUTHORIZED
REAL_DATA_INTEGRATION = NOT_AUTHORIZED
IMPLEMENTATION_STATUS = TARGET_DEFINITION_ONLY
```

---

## 12. MODIFICATION FIREWALL

```
SOURCE_CODE_MODIFIED = NO
SCHEMA_MODIFIED = NO
STAGE8_1_MODIFIED = NO
D1_D7_MODIFIED = NO
FORECASTBUNDLE_MODIFIED = NO
FORECASTENGINE_MODIFIED = NO
EMS_MODIFIED = NO
MPC_MODIFIED = NO
DIGITAL_TWIN_MODIFIED = NO
LOCALBASELINEFORECASTENGINE_MODIFIED = NO
A1_MODIFIED = NO
A1_5_MODIFIED = NO
A1_6_MODIFIED = NO
MODEL_TRAINING_EXECUTED = NO
MODEL_INFERENCE_EXECUTED = NO
BENCHMARKING_EXECUTED = NO
FORECAST_WINDOWS_CREATED = NO
NEW_EXPERIMENT_EXECUTED = NO
REAL_DATA_INTEGRATED = NO
A2_MODEL_CREATED = NO
IMPLEMENTATION_STATUS = TARGET_DEFINITION_ONLY
```

---

## 13. HARD STOP CHECK

- Altitude-transfer model invented? **NO**
- Turbine power curve introduced? **NO**
- Model trained? **NO**
- Inference executed? **NO**
- Forecasts generated? **NO**
- Benchmarking executed? **NO**
- Data acquired? **NO**
- ForecastBundle changed? **NO**
- ForecastEngine changed? **NO**
- EMS / MPC changed? **NO**
- Stage8.1 changed? **NO**
- D1–D7 modified? **NO**
- Synthetic Nuolja wind constructed? **NO**
- Meteorological equivalence claimed? **NO**

**A2 TARGET DEFINITION GOVERNANCE DECISION IS COMPLETE.**
