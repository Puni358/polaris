# POLARIS — FORECASTBUNDLE RESEARCH GOVERNANCE DECISION RECORD
## GOVERNANCE DECISIONS D1 & D2: LOWER/UPPER SEMANTICS & POINT-ONLY REPRESENTATION

## 1. Purpose
This document constitutes the first **Authoritative Research Governance Decision Record** for the frozen POLARIS `ForecastBundle` contract. 

Following the completion of the repository discovery phase, project governance hereby records formal design decisions **D1** (designating `lower` and `upper` array semantics) and **D2** (authorizing a contract serialization convention for point-only forecasting sources).

---

## 2. Governance Status
- **D1 Status**: **`DECISION_RECORDED`**
- **D2 Status**: **`DECISION_RECORDED`**
- **Implementation Status**: **`NOT_AUTHORIZED`**
- **Scope**: Contract semantic designation and serialization convention recording only.

---

## 3. Authoritative Input Artifacts
This decision record builds upon the verified findings of the following control artifacts:
1. `POLARIS_FORECASTBUNDLE_INTERVAL_SEMANTICS_AUDIT.md` / `.json`
2. `POLARIS_FORECASTBUNDLE_POINT_SEMANTICS_EVIDENCE_CHECK.md` / `.json`
3. `POLARIS_STAGE8_1_FORECASTBUNDLE_RESEARCH_GOVERNANCE_PACKAGE.md` / `.json`
4. `POLARIS_STAGE8_1_FORECASTBUNDLE_CONTRACT_RESOLUTION.md` / `.json`
5. Frozen `ForecastBundle` v1.0 Schema (`system/schemas/forecast_bundle.py`)

---

## 4. Distinction Between Existing Evidence and New Governance Decisions
- **Pre-existing Discovery Facts**: Prior audits established that the `ForecastBundle` v1.0 schema contained `lower`, `point`, `upper` fields with structural constraints (`lower <= point <= upper`), but contained **NO** contractual or governance definition of their semantic meaning, coverage percentage, or point-only representation rules.
- **New Governance Decisions**: Decisions **D1** and **D2** recorded herein are **NEW PROJECT GOVERNANCE DESIGNATIONS**. They do NOT claim that these semantics were established by historical repository implementations or prior discovery audits.

---

## 5. Decision D1 — Lower/Upper Semantics

### Governance Decision Statement
From this decision record onward, `ForecastBundle.lower` and `ForecastBundle.upper` **SHALL** be designated as **FORECAST-UNCERTAINTY BOUND FIELDS** surrounding the corresponding `point` forecast.

```
LOWER_UPPER_SEMANTICS = FORECAST_UNCERTAINTY_BOUNDS_WITHOUT_CLAIMED_STATISTICAL_COVERAGE
```

### Scope & Constraints
1. **No Statistical Coverage Claim**: This semantic designation does **NOT** claim or imply any specific statistical coverage, calibration, or probabilistic confidence property (e.g. 80%, 90%, 95% prediction intervals, quantile forecasts, or physical operating limits) unless separately established and explicitly authorized by future governance.
2. **Prototype Baseline Rule**: Prototype percentage multipliers in historical baseline code (e.g. `x * 0.9`, `x * 1.1` in `LocalBaselineForecastEngine`) MUST NOT be retroactively treated as validated uncertainty bounds merely because they populate `lower` and `upper`.

---

## 6. Decision D2 — Point-Only Representation

### Governance Decision Statement
A point-only forecasting source (such as the frozen Stage8.1 champion) **MAY** be represented within `ForecastBundle` using the degenerate representation convention:

```python
lower = point
point = point
upper = point
```

```
POINT_ONLY_REPRESENTATION = AUTHORIZED_DEGENERATE_POINT_REPRESENTATION
```

### Scope & Constraints
1. **Degenerate Representation Convention**: The equality `lower = point = upper` is a **SERIALIZATION / CONTRACT CONVENTION** for point-only sources.
2. **Semantic Interpretation**: `lower = point = upper` explicitly means:
   > *"No uncertainty information is represented by this point-only source."*
3. **Firewall Rule**: Equality of `lower`, `point`, and `upper` **MUST NOT** be interpreted as evidence that real-world forecast uncertainty is zero or that the forecast possesses perfect accuracy.
4. **Structural Validity**: The degenerate representation identically satisfies the existing schema structural ordering constraint ($p \le p \le p$).
5. **No Schema Alteration**: This convention does **NOT** add, remove, or modify any required `ForecastBundle` fields or metadata keys.

---

## 7. Scientific Claim Limitations

> [!WARNING]
> **SCIENTIFIC FIREWALL**:
> Decisions D1 and D2 establish **CONTRACT BOUNDARY SEMANTICS ONLY**.
> They do **NOT** establish:
> - Forecast uncertainty calibration
> - Prediction interval coverage or statistical reliability
> - Probabilistic forecast quality or skill
> - Empirical error distributions or statistical guarantees
> - Model accuracy or operational superiority
> 
> Any future uncertainty calibration or probabilistic forecasting evaluation must be separately authorized as independent scientific research.

---

## 8. D1/D2 Frozen Contract Assessment

- **Evaluated Target**: Can D1 and D2 coexist with frozen `ForecastBundle` v1.0 without contradicting schema rules, validation rules, or interface requirements?
- **Analysis**:
  - `TimeseriesForecast` in `system/schemas/forecast_bundle.py` validates `lower[i] <= point[i] <= upper[i]`. Degenerate bounds ($p \le p \le p$) satisfy this rule without error.
  - Required fields (`solar_irradiance`, `solar_generation`, `wind_generation`, `demand`) retain 24-element float arrays and required units ($\text{W/m}^2$, $\text{W}$).
  - No existing schema rule, interface method, or serialization structure is violated.
- **Assessment Result**:
  ```
  D1_D2_FROZEN_CONTRACT_CHANGE_REQUIRED = NO
  ```
- *Note*: This finding applies specifically to D1 and D2. Whole-system contract readiness (D7) remains dependent on resolving remaining decisions D3–D6.

---

## 9. Engineering Consequence Assessment

The following potential engineering consequences follow from decisions D1 and D2:
1. **Forecast Engine / Adapter Responsibility**: Future forecast providers or adapters populating `ForecastBundle` must format arrays consistently with D1 (uncertainty bounds) or D2 (degenerate point representation).
2. **Prohibition of Fabricated Coverage**: Adapters representing point-only models using `lower = point = upper` must NOT fabricate statistical coverage metadata (e.g. labeling degenerate bounds as "95% confidence intervals").
3. **Downstream Optimizer Immunity**: Existing microgrid optimizers (`MILP` and `RuleBased`) consume `.point` arrays directly. Recording D1 and D2 does not alter optimizer execution or introduce probabilistic optimization.
4. **No Implementation Authorized**: Identifying these consequences does NOT authorize writing adapter code or modifying system interfaces.

---

## 10. Remaining Governance Decisions

Decisions D1 and D2 represent the initial phase of research governance resolution. Decisions D3 through D7 remain **UNRESOLVED**:

| Decision ID | Domain | Status |
|---|---|---|
| **D1** | `lower`/`upper` Semantics | **`DECISION_RECORDED`** |
| **D2** | Point-Only Representation | **`DECISION_RECORDED`** |
| **D3** | $SW_{\text{IN}}$ $\to$ Solar-Generation Mapping | **`NOT_ESTABLISHED`** |
| **D4** | Wind Forecast Source | **`NOT_ESTABLISHED`** |
| **D5** | Demand Forecast Source | **`NOT_ESTABLISHED`** |
| **D6** | Multi-Source Forecast Composition | **`NOT_ESTABLISHED`** |
| **D7** | Final Whole-System Contract Change Assessment | **`NOT_ESTABLISHED`** |

---

## 11. Implementation Authorization Status

```
IMPLEMENTATION_STATUS = NOT_AUTHORIZED
```

- NO adapter implementation (`Stage81ForecastEngine`) is authorized.
- NO schema modifications or code edits are authorized.
- NO integrated Stage8.1 $\to$ EMS experiments are authorized.
- System implementation remains strictly **NOT AUTHORIZED** pending the resolution of governance decisions D3 through D6.

---

## 12. Historical Artifact Protection
The following historical control artifacts remain frozen and **UNTOUCHED**:
- `POLARIS_FORECASTBUNDLE_INTERVAL_SEMANTICS_AUDIT.md` / `.json`
- `POLARIS_FORECASTBUNDLE_POINT_SEMANTICS_EVIDENCE_CHECK.md` / `.json`
- `POLARIS_STAGE8_1_FORECASTBUNDLE_RESEARCH_GOVERNANCE_PACKAGE.md` / `.json`
- `POLARIS_STAGE8_1_FORECASTBUNDLE_CONTRACT_RESOLUTION.md` / `.json`
- `POLARIS_STAGE8_1_FORECASTBUNDLE_COMPATIBILITY_AUDIT.md` / `.json`

---

## 13. Final Control State

```
D1_STATUS = DECISION_RECORDED
D2_STATUS = DECISION_RECORDED

LOWER_UPPER_SEMANTICS = FORECAST_UNCERTAINTY_BOUNDS_WITHOUT_CLAIMED_STATISTICAL_COVERAGE
POINT_ONLY_REPRESENTATION = AUTHORIZED_DEGENERATE_POINT_REPRESENTATION

D1_D2_FROZEN_CONTRACT_CHANGE_REQUIRED = NO

D3_PV_MAPPING = NOT_ESTABLISHED
D4_WIND_SOURCE = NOT_ESTABLISHED
D5_DEMAND_SOURCE = NOT_ESTABLISHED
D6_MULTI_SOURCE_COMPOSITION = NOT_ESTABLISHED

D7_FINAL_FROZEN_CONTRACT_CHANGE_REQUIRED = NOT_ESTABLISHED

FINAL_GOVERNANCE_STATUS = D1_D2_RECORDED_REMAINING_DECISIONS_REQUIRED
IMPLEMENTATION_STATUS = NOT_AUTHORIZED
```

---

## 14. File Modification Audit

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
- `POLARIS_FORECASTBUNDLE_GOVERNANCE_DECISION_D1_D2.md`
- `POLARIS_FORECASTBUNDLE_GOVERNANCE_DECISION_D1_D2.json`
