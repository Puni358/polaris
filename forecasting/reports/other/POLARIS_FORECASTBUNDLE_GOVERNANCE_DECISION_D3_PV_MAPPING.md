# POLARIS — FORECASTBUNDLE RESEARCH GOVERNANCE DECISION RECORD
## GOVERNANCE DECISION D3: SW_IN TO SOLAR-GENERATION MAPPING

## 1. Purpose
This document records the formal **Authoritative Research Governance Decision D3** for the POLARIS forecasting and energy management architecture. 

Following the formal recording of Decisions D1 (uncertainty bound field designation) and D2 (authorized degenerate point-only representation), project governance hereby records Decision **D3**, authorizing the representation mapping used to convert the Stage8.1 surface downwelling shortwave radiation ($SW_{\text{IN}}$ / solar irradiance) forecast into the `ForecastBundle` solar-generation field (`solar_generation`).

---

## 2. Governance Status
- **D3 Status**: **`DECISION_RECORDED`**
- **Official Value**: `D3_PV_MAPPING = AUTHORIZED_EXISTING_IRRADIANCE_TO_POWER_REPRESENTATION`
- **Implementation Status**: **`NOT_AUTHORIZED`**
- **Scope**: Governance authorization of representation mapping semantics only.

---

## 3. Authoritative Input Artifacts
This decision record builds upon the verified findings of the following control artifacts:
1. `POLARIS_FORECASTBUNDLE_GOVERNANCE_DECISION_D1_D2.md` / `.json`
2. `POLARIS_STAGE8_1_FORECASTBUNDLE_RESEARCH_GOVERNANCE_PACKAGE.md` / `.json`
3. `POLARIS_STAGE8_1_FORECASTBUNDLE_CONTRACT_RESOLUTION.md` / `.json`
4. `POLARIS_FORECASTBUNDLE_INTERVAL_SEMANTICS_AUDIT.md` / `.json`
5. `POLARIS_FORECASTBUNDLE_POINT_SEMANTICS_EVIDENCE_CHECK.md` / `.json`
6. `LocalBaselineForecastEngine` Implementation ([`system/forecasting/implementations/baseline.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/forecasting/implementations/baseline.py#L30-L37))
7. Frozen `ForecastBundle` v1.0 Schema ([`system/schemas/forecast_bundle.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py))

---

## 4. Distinction Between Existing Evidence and New Governance Decision
- **Pre-existing Implementation Evidence**: The helper method `_irradiance_to_power_w()` exists in `LocalBaselineForecastEngine` as a private implementation detail for baseline forecast generation. Prior audits verified that no existing contract or governance artifact had explicitly authorized reusing this helper method for Stage8.1 irradiance output.
- **New Governance Decision**: Decision **D3** recorded herein is a **NEW PROJECT GOVERNANCE AUTHORIZATION**. It formally authorizes reusing the existing `_irradiance_to_power_w()` representation mapping for Stage8.1 solar irradiance integration. It does NOT claim that this authorization existed prior to this decision record.

---

## 5. D3 Governance Decision

### Governance Decision Statement
For Stage8.1 solar forecast integration, the project **SHALL** use the existing `_irradiance_to_power_w()` representation mapping as the **AUTHORIZED $SW_{\text{IN}} \to \text{solar-generation}$ MAPPING**, subject to the constraints and semantic boundaries defined herein.

```
D3_PV_MAPPING = AUTHORIZED_EXISTING_IRRADIANCE_TO_POWER_REPRESENTATION
```

### Authorization Scope & Interpretation
1. **Representation Mapping**: The function is authorized strictly as a representation and engineering transformation from Stage8.1 irradiance forecasts ($\text{W/m}^2$) to `ForecastBundle` solar generation ($\text{W}$).
2. **No Model Alteration**: This decision does NOT modify the Stage8.1 champion model, its feature set, or its scientific target.
3. **No Claim of New Model**: The mapping MUST NOT be presented as a new solar forecasting model, a Stage8.1 model modification, or an empirical scientific improvement.

---

## 6. Existing `_irradiance_to_power_w()` Evidence

### Implementation Inspection
- **File Path**: [`system/forecasting/implementations/baseline.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/forecasting/implementations/baseline.py#L30-L37)
- **Function Name**: `_irradiance_to_power_w(self, irradiance_w_m2: float) -> float`
- **Input Quantity & Unit**: `irradiance_w_m2` (Solar irradiance $SW_{\text{IN}}$ in $\text{W/m}^2$)
- **Output Quantity & Unit**: `raw_power` / capped power (Electrical power generation in $\text{W}$)

### Mathematical Transformation
The method evaluates:
$$\text{raw\_power} = \text{irradiance\_w\_m2} \times \text{array\_area\_m2} \times \text{panel\_efficiency} \times \text{performance\_ratio}$$
$$\text{output\_power} = \min(\text{raw\_power}, \text{max\_inverter\_power\_w})$$

### Default Physical Configuration Parameters
- **`array_area_m2`**: $300.0 \text{ m}^2$ (Total PV array surface area)
- **`panel_efficiency`**: $0.20$ ($20\%$ module efficiency)
- **`performance_ratio`**: $0.85$ ($85\%$ system performance ratio accounting for wiring and dirtying losses)
- **`max_inverter_power_w`**: $60000.0 \text{ W}$ ($60 \text{ kW}$ inverter AC capacity cap)

### Documented Assumptions & Limitations
- **Linear Scaling**: Assumes linear conversion between surface irradiance and DC generation up to inverter saturation.
- **Inverter Clipping**: Enforces strict upper clipping at `max_inverter_power_w` ($60 \text{ kW}$).
- **Unmodelled Dynamics**: Does NOT dynamically model thermal cell temperature coefficients, solar zenith/azimuth incidence angles, inverter efficiency curves, or partial shading.

---

## 7. Input/Output Units and Semantics

```
Stage8.1 Irradiance Forecast (SW_IN) [W/m²]
             │
             ▼  D3 Authorized Mapping (_irradiance_to_power_w)
ForecastBundle Solar Generation (solar_generation) [W]
```

- **Semantic Boundary**: The D3 mapping converts physical flux density ($\text{W/m}^2$) into total station electrical power output ($\text{W}$).
- **Non-Direct Conversion**: This transformation is an engineering PV model mapping, NOT a unit alias or scalar unit conversion.

---

## 8. Stage8.1 Scientific Boundary

The scientific scope of Stage8.1 remains strictly frozen and unchanged:
- **Target Variable**: Surface downwelling shortwave radiation ($SW_{\text{IN}}$)
- **Target Units**: $\text{W/m}^2$
- **Model Parameters**: Unchanged
- **Scientific Audit Status**: Closed / Frozen

```
STAGE8_1_TARGET_MODIFIED = NO
STAGE8_1_MODEL_MODIFIED = NO
```

---

## 9. Relationship to D1/D2

Decision D3 operates in full alignment with the already recorded decisions D1 and D2:

1. **Point Forecast Transformation**: Stage8.1 produces point irradiance forecasts ($\text{W/m}^2$). D3 transforms that point irradiance array into a point solar-generation array ($\text{W}$).
2. **Point-Only Representation (D2)**: For Stage8.1 solar generation, D2 governs how the point forecast populates `ForecastBundle`:
   ```python
   solar_generation.lower = solar_generation.point
   solar_generation.point = mapped_power_array
   solar_generation.upper = solar_generation.point
   ```
3. **Uncertainty Bound Designation (D1)**: Equality across bounds ($L = P = U$) indicates that no uncertainty information is represented by this point-only source, per D1/D2. D3 does NOT introduce synthetic or statistical uncertainty bounds.

---

## 10. Scientific Claim Limitations

> [!WARNING]
> **SCIENTIFIC FIREWALL**:
> Decision D3 authorizes an **ENGINEERING REPRESENTATION MAPPING ONLY**.
> It MUST NOT be used to claim:
> - Empirical validation of station PV generation accuracy
> - Calibration of actual Antarctic station power yield
> - Causal equivalence between irradiance forecast MAE ($\text{W/m}^2$) and power forecast MAE ($\text{W}$)
> - Superiority over complex physical or ray-tracing PV models
> - Improved EMS operational performance
> 
> Any empirical power-generation validation study must be separately authorized as scientific research.

---

## 11. D3 Frozen-Contract Assessment

- **Evaluated Target**: Can Decision D3 coexist with frozen `ForecastBundle` v1.0 schema without structural or semantic contradiction?
- **Analysis**:
  - `ForecastBundle.solar_generation` expects a `TimeseriesForecast` object with unit `"W"`.
  - `_irradiance_to_power_w()` returns float values in $\text{W}$ satisfying physical non-negativity ($\ge 0.0$).
  - Array length remains 24, and timestamps remain aligned.
  - No schema modification or field addition is required.
- **Assessment Result**:
  ```
  D3_FROZEN_CONTRACT_CHANGE_REQUIRED = NO
  ```
- *Note*: This finding applies specifically to Decision D3. Whole-system contract readiness (D7) remains dependent on resolving remaining decisions D4–D6.

---

## 12. Engineering Consequence Assessment

The following potential engineering consequences follow from Decision D3:
1. **Adapter Transformation**: A future Stage8.1 forecast adapter wrapper may invoke `_irradiance_to_power_w()` to populate `solar_generation.point`.
2. **Irradiance Preservation**: Both `solar_irradiance` ($\text{W/m}^2$) and `solar_generation` ($\text{W}$) can be represented simultaneously in `ForecastBundle` v1.0.
3. **EMS Isolation**: The EMS continues receiving `ForecastBundle` objects without direct coupling to raw Stage8.1 irradiance outputs.
4. **No Implementation Authorized**: Documenting these consequences does NOT authorize writing adapter code or modifying system files.

---

## 13. Remaining Governance Decisions

Decisions D1, D2, and D3 are now formally recorded. Decisions D4 through D7 remain **UNRESOLVED**:

| Decision ID | Domain | Status |
|---|---|---|
| **D1** | `lower`/`upper` Semantics | **`DECISION_RECORDED`** |
| **D2** | Point-Only Representation | **`DECISION_RECORDED`** |
| **D3** | $SW_{\text{IN}}$ $\to$ Solar Power Mapping | **`DECISION_RECORDED`** |
| **D4** | Wind Forecast Source | **`NOT_ESTABLISHED`** |
| **D5** | Demand Forecast Source | **`NOT_ESTABLISHED`** |
| **D6** | Multi-Source Forecast Composition | **`NOT_ESTABLISHED`** |
| **D7** | Final Whole-System Contract Change Assessment | **`NOT_ESTABLISHED`** |

---

## 14. Implementation Authorization Status

```
IMPLEMENTATION_STATUS = NOT_AUTHORIZED
```

- NO adapter implementation (`Stage81ForecastEngine`) is authorized.
- NO schema modifications or code edits are authorized.
- NO integrated Stage8.1 $\to$ EMS experiments are authorized.
- System implementation remains strictly **NOT AUTHORIZED** pending the resolution of governance decisions D4 through D6.

---

## 15. Historical Artifact Protection
The following historical control artifacts remain frozen and **UNTOUCHED**:
- `POLARIS_FORECASTBUNDLE_GOVERNANCE_DECISION_D1_D2.md` / `.json`
- `POLARIS_FORECASTBUNDLE_INTERVAL_SEMANTICS_AUDIT.md` / `.json`
- `POLARIS_FORECASTBUNDLE_POINT_SEMANTICS_EVIDENCE_CHECK.md` / `.json`
- `POLARIS_STAGE8_1_FORECASTBUNDLE_RESEARCH_GOVERNANCE_PACKAGE.md` / `.json`
- `POLARIS_STAGE8_1_FORECASTBUNDLE_CONTRACT_RESOLUTION.md` / `.json`
- `POLARIS_STAGE8_1_FORECASTBUNDLE_COMPATIBILITY_AUDIT.md` / `.json`

---

## 16. Final Control State

```
D3_STATUS = DECISION_RECORDED

D3_PV_MAPPING = AUTHORIZED_EXISTING_IRRADIANCE_TO_POWER_REPRESENTATION
D3_FROZEN_CONTRACT_CHANGE_REQUIRED = NO

STAGE8_1_TARGET_MODIFIED = NO
STAGE8_1_MODEL_MODIFIED = NO

D4_WIND_SOURCE = NOT_ESTABLISHED
D5_DEMAND_SOURCE = NOT_ESTABLISHED
D6_MULTI_SOURCE_COMPOSITION = NOT_ESTABLISHED
D7_FINAL_FROZEN_CONTRACT_CHANGE_REQUIRED = NOT_ESTABLISHED

FINAL_GOVERNANCE_STATUS = D3_RECORDED_REMAINING_DECISIONS_REQUIRED
IMPLEMENTATION_STATUS = NOT_AUTHORIZED
```

---

## 17. File Modification Audit

```
SOURCE_CODE_MODIFIED = NO
FORECASTBUNDLE_MODIFIED = NO
SCHEMA_MODIFIED = NO
STAGE8_1_MODIFIED = NO
D5_MODIFIED = NO
OPTIMIZER_MODIFIED = NO
MPC_MODIFIED = NO
ADAPTER_IMPLEMENTED = NO
EXPERIMENT_EXECUTED = NO
DATA_ACQUISITION_PERFORMED = NO
HISTORICAL_CONTROL_ARTIFACTS_MODIFIED = NO
```

**Files Created**:
- `POLARIS_FORECASTBUNDLE_GOVERNANCE_DECISION_D3_PV_MAPPING.md`
- `POLARIS_FORECASTBUNDLE_GOVERNANCE_DECISION_D3_PV_MAPPING.json`
