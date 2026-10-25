# POLARIS — PATH A / WIND FORECASTING TRACK
## PHASE A1.6 — SCIENTIFIC TARGET / SITE-TRANSFER QUALIFICATION REPORT

**Document ID:** `POLARIS_WIND_A1_6_SITE_TRANSFER_QUALIFICATION`  
**Date (UTC):** 2026-09-18  
**Track:** PATH A — WIND FORECASTING TRACK  
**Phase:** PHASE A1.6 (Abisko $\rightarrow$ Nuolja Target & Site-Transfer Qualification)  
**Task Type:** Controlled Scientific Target & Site-Transfer Assessment  
**Authorization Status:** Authorized Phase A1.6 Only (Model Training/Inference/Benchmarking **STRICTLY PROHIBITED**)  

---

## 1. OBJECTIVE

Phase A1.6 was initiated following Phase A1.5 closeout (`POLARIS_WIND_DATA_ACQUISITION_AND_A1_5_QUALIFICATION`) to resolve a specific scientific qualification question:

> *"Can the empirical 10m wind speed dataset measured at SMHI Station 188790 (Abisko Aut) legitimately serve as the forecasting target for the future POLARIS wind forecasting research track, specifically considering its use as a proxy target representing the Mount Nuolja research context?"*

Phase A1.6 rigorously evaluates the distinction between:
- **Fact A:** *"Measured wind data exist at Abisko Aut (Station 188790)."* (Established in Phase A1.5).
- **Fact B:** *"Those measurements are scientifically defensible as the target for the POLARIS wind forecasting task."* (Evaluated in Phase A1.6).

> [!IMPORTANT]
> **Zero Execution Mandate:** Phase A1.6 **MUST NOT** train models, run inference, produce wind forecasts, benchmark candidates, tune hyperparameters, construct forecast windows, calculate metrics, modify ForecastBundle/EMS/MPC, or apply synthetic scaling formulas.

---

## 2. STARTING EVIDENCE FROM A1.5

Phase A1.5 acquired and verified the empirical wind dataset from SMHI Station 188790 (`Abisko Aut`):

- **Station ID & Name:** `188790` (`Abisko Aut`).
- **Custodian:** Polarforskningssekretariatet (Swedish Polar Research Secretariat).
- **Geographic Coordinates:** Latitude $68.3538^\circ\text{N}$, Longitude $18.8164^\circ\text{E}$, Altitude $392.235\,\text{m}$ a.s.l.
- **Proximity:** $\sim 4.1\,\text{km}$ East-Northeast of Mount Nuolja AWS ($68.3621^\circ\text{N}, 18.7388^\circ\text{E}$, $702\,\text{m}$ a.s.l.).
- **Parameters Acquired:** 10m height 1-hour average wind speed ($v_{\text{wind}}$ in $\text{m/s}$) and wind direction ($\theta_{\text{wind}}$ in degrees).
- **Temporal Record:** $8,784$ continuous hourly observations for full 2024 benchmark period ($0$ missing values).
- **Licensing & Quality:** SMHI Quality Controlled Archive (Codes `G` / `Y`), Creative Commons CC BY 4.0.

*Governance Rule:* Phase A1.5 established that data exist at Abisko Aut, but explicitly did **NOT** establish that Abisko measurements are directly interchangeable with Mount Nuolja conditions.

---

## 3. TARGET DEFINITION

Phase A1.6 evaluates the candidate target: **10m hourly measured wind speed ($v_{\text{wind}}$ in $\text{m/s}$) at Abisko Aut**.

Three candidate interpretations were evaluated:

1. **Direct Empirical Target for POLARIS Research:**
   - *Assessment:* **UNSUPPORTED**. Abisko Aut is at $392\,\text{m}$ altitude on the valley floor; Mount Nuolja AWS is at $702\,\text{m}$ on a mountain ridge $\sim 4.1\,\text{km}$ away. Abisko wind is not directly identical to Nuolja ridge wind.

2. **Proxy Target Representing the Nuolja Context:**
   - *Assessment:* **CONDITIONALLY SUPPORTED**. Abisko Aut measurements are scientifically defensible as an empirical proxy target representing the regional Nuolja/Abisko polar microgrid context because both stations share the same microclimate basin, same institutional custodian, same 2024 benchmark timeframe, and high data quality. However, transfer limitations ($310\,\text{m}$ vertical offset, valley vs ridge topography) remain unresolved and must be carried into future research governance.

3. **Separate Abisko-Site Target Only:**
   - *Assessment:* **SUPPORTED AS FALLBACK**. If site-transfer to Nuolja is rejected by project governance, the dataset validly supports a standalone Abisko microgrid forecasting study.

### Supported Target Interpretation
```
TARGET_DECISION = PROXY_TARGET_CONDITIONALLY_SUPPORTED
```

---

## 4. ABISKO STATION IDENTITY

- **Full Name:** Abisko Automatic Weather Station (`Abisko Aut`).
- **SMHI Network ID:** `188790`.
- **Operating Agency:** SMHI (Swedish Meteorological and Hydrological Institute) in collaboration with Polarforskningssekretariatet.
- **Location:** Abisko Scientific Research Station (ANS), Abisko, Kiruna Municipality, Sweden.
- **Coordinates:** $68.353787^\circ\text{N}, 18.816420^\circ\text{E}$.
- **Ground Elevation:** $392.235\,\text{m}$ above sea level.
- **Anemometer Mast Height:** $10.0\,\text{m}$ above ground level.

---

## 5. NUOLJA COMPARISON

Side-by-side scientific comparison of Abisko Aut and Mount Nuolja AWS stations:

| Attribute | Abisko Aut (Station 188790) | Mount Nuolja AWS (`SITES_MET_ANS_NMS`) | Comparison & Delta |
| :--- | :--- | :--- | :--- |
| **Latitude** | $68.3538^\circ\text{N}$ | $68.3621^\circ\text{N}$ | $\Delta = 0.0083^\circ$ ($\sim 0.9\,\text{km}$ North) |
| **Longitude** | $18.8164^\circ\text{E}$ | $18.7388^\circ\text{E}$ | $\Delta = 0.0776^\circ$ ($\sim 3.2\,\text{km}$ West) |
| **Straight-Line Distance** | Reference | $\sim 4.1\,\text{km}$ | Close spatial proximity ($\sim 4.1\,\text{km}$ ENE) |
| **Ground Elevation** | $392.2\,\text{m}$ a.s.l. | $702.0\,\text{m}$ a.s.l. | **$\Delta = +309.8\,\text{m}$ vertical offset** |
| **Terrain Context** | Low-gradient valley floor / lake shoreline | Alpine mountain ridge slope | Valley vs mountain ridge exposure |
| **Surface Category** | Torneträsk Lake basin ($341\,\text{m}$ lake) | Mountain slope tree-line | Different surface roughness ($\text{z}_0$) |
| **Station Owner** | Polarforskningssekretariatet | Polarforskningssekretariatet | **Identical institutional custodian** |
| **Wind Instrumentation** | Anemometer ($10\,\text{m}$) + Vane ($10\,\text{m}$) | **None** (`TA`, `RH`, `SW_IN`, `TS`, `PRECIP` only) | Abisko has wind; Nuolja lacks wind sensors |
| **2024 Coverage** | $8,784$ hourly records ($100\%$) | $52,704$ 10-min records ($100\%$) | Synchronous 2024 temporal benchmark period |

---

## 6. SITE-TRANSFER EVIDENCE

Evaluating the scientific validity of the Abisko $\rightarrow$ Nuolja site-transfer:

1. **Regional Synoptic Equivalence:** Both stations are situated within the exact same atmospheric grid cell and Torneträsk catchment basin in sub-arctic Lapland ($68^\circ\text{N}$). Macro-scale synoptic wind patterns (e.g., Atlantic low-pressure fronts, polar vortex incursions) affect both locations simultaneously.
2. **Institutional & Temporal Alignment:** Both stations are operated under the auspices of Polarforskningssekretariatet and share synchronous 2024 observations.
3. **Local Microclimate Divergence:**
   - *Ridge Speed-up:* Air flow over Mount Nuolja ($702\,\text{m}$) experiences topographically driven Bernoulli acceleration (ridge speed-up), resulting in higher mean wind speeds than the valley floor ($392\,\text{m}$).
   - *Boundary Layer Friction:* Abisko Aut is subject to valley floor surface friction and localized Lake Torneträsk breezes.

### Conclusion on Transfer
Available evidence supports using Abisko wind speed as a **proxy target for the Nuolja microgrid context**, provided that the altitude and ridge transfer limitations are explicitly acknowledged and carried into future research governance.

---

## 7. ALTITUDE ASSESSMENT

- **Elevation Difference:** Mount Nuolja AWS ($702\,\text{m}$) is $309.8\,\text{m}$ higher than Abisko Aut ($392.2\,\text{m}$).
- **Governance Audit:** Search of POLARIS repository governance records confirms that **NO AUTHORIZED ALTITUDE TRANSFER METHOD IS ESTABLISHED** in project contracts.

```
ALTITUDE_TRANSFER_METHOD = NOT_ESTABLISHED
```

> [!CAUTION]
> **Strict Rule Enforcement:** Phase A1.6 **MUST NOT** invent an altitude scaling equation (e.g., power-law or log-law wind profile formulas) or alter raw wind speed values. Applying unvalidated mathematical rescalings without empirical dual-station calibration violates scientific provenance.

---

## 8. MEASUREMENT-HEIGHT ASSESSMENT

- **Height Representation:** The acquired SMHI dataset represents measured wind speed at $10.0\,\text{m}$ above ground level ($v_{10\text{m}}$ in $\text{m/s}$).
- **Task Qualification:** The future POLARIS forecasting research task can legitimately evaluate $10\,\text{m}$ wind speed directly as the microgrid base station forecasting target.
- **Firewall Rule:** Phase A1.6 does **NOT** convert $10\,\text{m}$ wind speed to turbine hub height ($e.g., 30\,\text{m}$ or $50\,\text{m}$) because no height conversion model is authorized. Measured $10\,\text{m}$ wind speed **IS NOT** claimed to equal turbine inflow or hub-height wind.

---

## 9. WIND-SPEED VS WIND-POWER DISTINCTION

Phase A1.6 strictly enforces the physical boundary between meteorological and electrical quantities:

$$\text{MEASURED WIND SPEED } (v_{\text{wind}}, \text{m/s}) \quad \neq \quad \text{WIND POWER GENERATION } (P_{\text{wind}}, \text{W})$$

- **Qualified Target:** Measured 10m wind speed ($v_{\text{wind}}$ in $\text{m/s}$).
- **Unqualified Target:** Wind power generation ($P_{\text{wind}}$ in $\text{W}$). Zero empirical turbine electrical power measurements exist.
- **Firewall Rule:** Phase A1.6 **DOES NOT** introduce a turbine power curve, convert $\text{m/s}$ to $\text{W}$, or claim wind-generation forecasting capability. If future research targets electrical power, a separate turbine power curve qualification ($v \to P_{\text{wind}}$) remains necessary.

---

## 10. TEMPORAL TASK QUALIFICATION

Structural audit of the acquired 2024 Abisko hourly wind dataset for future forecasting formulation:

- **Temporal Resolution:** $1$ hour ($\Delta t = 1\,\text{h}$).
- **Duration & Completeness:** $8,784$ continuous hourly observations for 2024 ($100\%$ complete, $0$ missing steps).
- **Monotonicity & Integrity:** ISO-8601 UTC timestamps, strictly monotonic ascending.
- **Structural Compatibility:** The dataset structure is fully capable of supporting a future 24-hour receding-horizon forecasting formulation ($H = 24\,\text{h}$, $W_{\text{hist}} = 24\,\text{h}$).

> [!NOTE]
> No forecast windows or origin splits were constructed in Phase A1.6.

---

## 11. POTENTIAL FUTURE COVARIATES

Inventory of existing local datasets available for future multi-variable predictor coupling:

- **Local Weather Predictors (`data/POLARIS_v0_1_SITES_Nuolja_2024_hourly_multivariate.csv`):** Ground Air Temp (`TA`), Humidity (`RH`), Solar Irradiance (`SW_IN`), Soil Temp (`TS`), Precipitation (`PRECIP`).
- **NWP Forecast Predictors (`data/POLARIS_v0_1_future_weather_forecasts_2024.csv`):** NWP 10m Wind Speed (`fc_wind_speed_10m`), Surface Pressure (`fc_surface_pressure`), 2m Temp (`fc_temperature_2m`), Humidity (`fc_relative_humidity_2m`), Cloud Cover (`fc_cloud_cover`).

*Directive:* No feature engineering, feature matrix assembly, or dataset alignment was performed.

---

## 12. SCIENTIFIC LIMITATIONS

1. **Abisko is not Nuolja:** Proximity ($\sim 4.1\,\text{km}$) and shared microclimate do not establish identical wind speeds.
2. **Altitude Offset ($310\,\text{m}$):** No authorized altitude transfer model exists (`ALTITUDE_TRANSFER_METHOD = NOT_ESTABLISHED`).
3. **Wind Speed vs Power:** Measured $10\,\text{m}$ wind speed ($\text{m/s}$) is not measured electrical power ($\text{W}$).
4. **No Forecast Capability Claimed:** Zero models were trained, zero forecasts were generated, and zero predictive accuracy is claimed.

---

## 13. TARGET DECISION

```
TARGET_DECISION = PROXY_TARGET_CONDITIONALLY_SUPPORTED
```

### Decision Justification
Abisko Aut 10m measured wind speed ($v_{\text{wind}}$ in $\text{m/s}$) is scientifically defensible as an empirical proxy target for the POLARIS wind forecasting research track in the Nuolja/Abisko polar context. The decision is `CONDITIONALLY_SUPPORTED` because important physical transfer limitations ($310\,\text{m}$ altitude difference, valley floor vs mountain ridge topography, and lack of authorized turbine power curve models) remain unresolved and must be carried into future research governance.

---

## 14. A2 READINESS

```
A2_READINESS = CONDITIONALLY_READY_PENDING_SPECIFIED_RESOLUTION
```

Phase A1.6 **DOES NOT** authorize Phase A2 wind model development. Phase A2 may only be considered for separate governance authorization after the following unresolved prerequisites are resolved:

1. **Base Station vs Altitude Transfer Decision:** Governance decision authorizing either (a) using Abisko 10m measured wind speed directly as the microgrid base station target, or (b) authorizing an explicit altitude boundary layer transfer model.
2. **Turbine Power Curve Contract:** Formal project governance authorization of an explicit IEC 61400-12-1 wind turbine power curve model ($v_{\text{wind}} \to P_{\text{wind}}$) to map wind speed ($\text{m/s}$) to `ForecastBundle.wind_generation` ($\text{W}$).
3. **Canonical Fold Pre-registration:** Pre-registration of canonical train/val/test temporal fold splits using the SMHI Abisko target.
4. **Baseline Pre-registration:** Pre-registration of baseline models (Naive Persistence, Raw NWP) and evaluation metrics (MAE, RMSE).
5. **Separate Governance Gate:** Formal issuance of a separate Phase A2 governance authorization.

---

## 15. GOVERNANCE STATE

```
PATH_A_SELECTION = SELECTED
WIND_TRACK_STATUS = AUTHORIZED_PHASE_A1_6
WIND_TARGET_STATUS = CONDITIONALLY_ESTABLISHED
TARGET_DECISION = PROXY_TARGET_CONDITIONALLY_SUPPORTED
A2_READINESS = CONDITIONALLY_READY_PENDING_SPECIFIED_RESOLUTION
WIND_MODEL_TRAINING = NOT_AUTHORIZED
WIND_MODEL_INFERENCE = NOT_AUTHORIZED
WIND_MODEL_SELECTION = NOT_AUTHORIZED
WIND_FORECASTBUNDLE_INTEGRATION = NOT_AUTHORIZED
EMS_INTEGRATION = NOT_AUTHORIZED
NEW_EXPERIMENT = NOT_AUTHORIZED
IMPLEMENTATION_STATUS = A1_6_ONLY
```

---

## 16. MODIFICATION FIREWALL

```
SOURCE_CODE_MODIFIED = NO
SCHEMA_MODIFIED = NO
STAGE8_1_MODIFIED = NO
D1_D7_MODIFIED = NO
FORECASTBUNDLE_MODIFIED = NO
EMS_MODIFIED = NO
MPC_MODIFIED = NO
LOCALBASELINEFORECASTENGINE_MODIFIED = NO
EXPERIMENT_EXECUTED = NO
MODEL_TRAINING_EXECUTED = NO
MODEL_INFERENCE_EXECUTED = NO
MODEL_SELECTION_EXECUTED = NO
FORECAST_WINDOWS_CREATED = NO
SYNTHETIC_SCENARIOS_MODIFIED = NO
REAL_DATA_INTEGRATED = NO
IMPLEMENTATION_STATUS = A1_6_ONLY
```

---

## 17. FINAL CONCLUSION

Phase A1.6 has established that the empirical 10m measured wind speed series from SMHI Station 188790 (Abisko Aut) can legitimately serve as a **conditionally supported proxy target** for future POLARIS wind forecasting research.

- **Data Validity:** Fully verified ($8,784$ continuous 1-hour records for 2024, SMHI quality controlled).
- **Site-Transfer Validity:** Conditionally supported ($\sim 4.1\,\text{km}$ proximity, shared microclimate basin, $310\,\text{m}$ altitude offset requiring explicit governance handling).
- **Target Validity:** Bounded to measured wind speed ($v_{\text{wind}}$ in $\text{m/s}$). Measured wind generation ($P_{\text{wind}}$ in $\text{W}$) is not established.
- **Model Execution:** **ZERO** model training, inference, forecasting, or benchmarking occurred.

**PHASE A1.6 SCIENTIFIC TARGET AND SITE-TRANSFER QUALIFICATION IS COMPLETE.**
