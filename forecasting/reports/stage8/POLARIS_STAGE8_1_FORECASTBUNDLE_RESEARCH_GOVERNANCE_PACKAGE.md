# POLARIS — STAGE8.1 → FORECASTBUNDLE RESEARCH GOVERNANCE PACKAGE

## 1. Purpose
This document constitutes the formal **Research Governance Package** for the POLARIS energy management and forecasting system. It records the authoritative handoff from the completed discovery phase into formal human/project governance. 

This package presents the verified existing facts, established contract boundaries, and specific unresolved governance decision points required before any Stage8.1 solar forecast integration can be authorized or implemented.

---

## 2. Governance Scope
- **Scope**: Governance evaluation of integrating the frozen Stage8.1 Solar Irradiance Forecasting Champion into `ForecastBundle` v1.0 and downstream EMS optimization components.
- **Firewall Guarantee**:
  - NO code modifications, schema changes, or adapter implementations are authorized by this package.
  - NO model execution, EMS simulation, or forecasting inference is authorized.
  - NO governance option is chosen, preferred, ranked, or recommended.

---

## 3. Authoritative Input Artifacts
The findings in this package are derived strictly from the following control records:
1. `POLARIS_STAGE8_1_FORECASTBUNDLE_COMPATIBILITY_AUDIT.md` / `.json`
2. `POLARIS_STAGE8_1_FORECASTBUNDLE_CONTRACT_RESOLUTION.md` / `.json`
3. `POLARIS_FORECASTBUNDLE_INTERVAL_SEMANTICS_AUDIT.md` / `.json`
4. `POLARIS_FORECASTBUNDLE_POINT_SEMANTICS_EVIDENCE_CHECK.md` / `.json`
5. Frozen `ForecastBundle` v1.0 Schema (`system/schemas/forecast_bundle.py`)
6. Frozen Stage8.1 Champion Manifest (`POLARIS_REPRODUCIBLE_BASELINE_FREEZE.json`)

---

## 4. Current Control State

```
POINT_SEMANTICS = PARTIALLY_ESTABLISHED
INTERVAL_SEMANTICS = NOT ESTABLISHED
POINT_ONLY_REPRESENTATION = NOT ESTABLISHED
PV_MAPPING = NOT ESTABLISHED
WIND_SOURCE = NOT ESTABLISHED
DEMAND_SOURCE = NOT ESTABLISHED
MULTI_SOURCE_COMPOSITION = NOT ESTABLISHED
FROZEN_CONTRACT_CHANGE_REQUIRED = NOT_ESTABLISHED
FINAL_GOVERNANCE_STATUS = DECISION_REQUIRED
IMPLEMENTATION_STATUS = NOT_AUTHORIZED
```

---

## 5. Existing Facts

1. **Stage8.1 Output Contract**: Produces 24 hourly point predictions (`y_pred`) of surface downwelling shortwave radiation ($SW_{\text{IN}}$ / solar irradiance) in $\text{W/m}^2$. It produces no prediction intervals or uncertainty bounds.
2. **ForecastBundle v1.0 Contract**: Requires a 24-step horizon across 4 channels (`solar_irradiance`, `solar_generation`, `wind_generation`, `demand`), each containing 24-element float arrays for `point`, `lower`, and `upper` satisfying `lower <= point <= upper`.
3. **`point` Semantic**: Established as a 24-step central point-forecast array (Level 3 Contract). Treating `point` as a "deterministic expected point prediction" is a reasonable inference from baseline engine header comments and MILP solver formulation, but is not explicitly declared as a probabilistic mean ($\mathbb{E}[Y]$) in the contract schema.
4. **`lower` / `upper` Semantics**: Not defined in any contract schema or governance artifact. In `LocalBaselineForecastEngine`, they are constructed via heuristic percentage multipliers marked explicitly as `PROTOTYPE_UNVALIDATED`.
5. **Downstream Optimizer Consumption**: Microgrid decision optimizers (`LocalMILPEnergyOptimizer` and `LocalRuleBasedEnergyOptimizer`) consume **ONLY** `.point` arrays. `lower` and `upper` arrays are ignored during optimization.

---

## 6. Governance Decision D1 — Lower/Upper Semantics

- **Governance Question**: What mathematical, statistical, or operational concept should the `lower` and `upper` fields in `ForecastBundle` represent?
- **Existing Evidence**:
  - No contract schema or governance artifact defines their semantic meaning.
  - No coverage percentage (e.g. 80%, 95%), quantile, confidence interval, or operational envelope is established.
  - Prototype percentage scaling in baseline implementations is marked `PROTOTYPE_UNVALIDATED` and is NOT an authorized contract.
- **Candidate Categories (Neutral Identification)**:
  - Category D1.A: Statistical prediction intervals / quantiles (e.g. 10th and 90th percentiles).
  - Category D1.B: Operational error bounds / envelopes.
  - Category D1.C: Physical min/max bounds.
  - Category D1.D: Deterministic boundary equality (`lower = point, upper = point`).
- **Current Status**: **`DECISION REQUIRED`** (No choice or recommendation is made).

---

## 7. Governance Decision D2 — Point-Only Representation

- **Governance Question**: How should deterministic, point-only forecasting sources (such as Stage8.1) populate the required `lower` and `upper` fields in `ForecastBundle` v1.0?
- **Existing Evidence**:
  - Stage8.1 produces point predictions (`y_pred`) only.
  - The frozen `ForecastEngine` base interface defines NO authorized rule or fallback mechanism for point-only models.
  - Setting `lower = point` and `upper = point` satisfies structural schema validation (`fl <= fp <= fu`), but is **NOT** currently authorized as an integration contract.
- **Current Status**: **`DECISION REQUIRED`** (No representation policy is selected).

---

## 8. Governance Decision D3 — SW_IN to Solar-Generation Mapping

- **Governance Question**: What physical model or transformation is authorized to map Stage8.1 solar irradiance ($SW_{\text{IN}}$ in $\text{W/m}^2$) to solar generation (`solar_generation` in $\text{W}$)?
- **Existing Evidence**:
  - `LocalBaselineForecastEngine` contains a private helper `_irradiance_to_power_w()`.
  - This helper is NOT defined in the base `ForecastEngine` contract ABC nor explicitly authorized for Stage8.1 output in any frozen artifact.
- **Current Status**: **`DECISION REQUIRED`** (No mapping model is authorized).

---

## 9. Governance Decision D4 — Wind Source

- **Governance Question**: What is the authoritative wind generation forecast source to be paired with Stage8.1 solar forecasts in `ForecastBundle` v1.0?
- **Existing Evidence**:
  - Stage8.1 predicts solar irradiance only.
  - `LocalBaselineForecastEngine` populates wind generation from persistent station observation arrays.
  - No project contract establishes how wind forecasts are supplied when Stage8.1 is active.
- **Current Status**: **`DECISION REQUIRED`** (No wind source is selected).

---

## 10. Governance Decision D5 — Demand Source

- **Governance Question**: What is the authoritative electrical demand forecast source to be paired with Stage8.1 solar forecasts in `ForecastBundle` v1.0?
- **Existing Evidence**:
  - Stage8.1 predicts solar irradiance only.
  - `LocalBaselineForecastEngine` populates demand from persistent station observation arrays.
  - No project contract establishes how demand forecasts are supplied alongside Stage8.1 solar.
- **Current Status**: **`DECISION REQUIRED`** (No demand source is selected).

---

## 11. Governance Decision D6 — Multi-Source Composition

- **Governance Question**: What composition rule/architecture is authorized to combine separate single-channel forecasts (Stage8.1 solar + wind source + demand source) into a single `ForecastBundle` v1.0?
- **Existing Evidence**:
  - Multi-channel bundle creation exists within `LocalBaselineForecastEngine` for baseline streams.
  - Composing external single-channel forecasts into a single bundle is NOT established as a contract path for Stage8.1.
- **Current Status**: **`DECISION REQUIRED`** (No composition rule is defined).

---

## 12. Governance Decision D7 — Frozen Contract Change

- **Governance Question**: Can the unresolved decisions D1–D6 be represented under the existing frozen `ForecastBundle` v1.0 schema, or will a schema/contract extension be required?
- **Existing Evidence**:
  - The existing schema (`system/schemas/forecast_bundle.py`) structurally supports array inputs.
  - However, whether future governance decisions (e.g., probabilistic quantiles or multi-source metadata) can fit within schema v1.0 depends entirely on decisions D1–D6.
- **Current Status**: **`FROZEN_CONTRACT_CHANGE_REQUIRED = NOT_ESTABLISHED`**

---

## 13. Governance vs. Engineering Separation

To maintain scientific integrity, POLARIS strictly enforces the separation of governance authority from engineering consequences:

| Domain | Governance Question | Potential Future Engineering Consequence |
|---|---|---|
| **D1: Interval Semantics** | What semantic meaning should `lower`/`upper` represent? | Forecast providers or perturbers must generate bounds matching the defined semantic. |
| **D2: Point-Only Representation** | What representation rule is authorized for point-only models? | An adapter wrapper must apply the authorized representation rule. |
| **D3: PV Mapping** | Which PV conversion model is authorized for Stage8.1? | The adapter wrapper must implement the authorized PV conversion function. |
| **D4/D5: Wind & Demand Sources** | Which wind and demand forecast sources are authorized? | The adapter must fetch and validate wind and demand forecasts from authorized sources. |
| **D6: Multi-Source Composition** | How are separate streams composite-validated? | `ForecastEngine.predict()` or an adapter must composite streams into `ForecastBundle`. |
| **D7: Contract Change** | Is a schema version update required? | Schema files and serialization tests may need updating if governance mandates contract changes. |

> [!CAUTION]
> **GOVERNANCE RULE**: Engineering convenience must NOT determine scientific contracts. An adapter cannot be designed until governance authorizes the contract rules it is meant to enforce.

---

## 14. Human Decision Table

The following decision table records the current status of all unresolved integration questions. It is presented to project governance without ranking, scoring, or recommendations.

| Decision ID | Question | Existing Evidence | Current Status |
|---|---|---|---|
| **D1** | `lower`/`upper` Semantics | No contract definition; prototype scaling is `PROTOTYPE_UNVALIDATED`. | **DECISION REQUIRED** |
| **D2** | Point-Only Representation | Stage8.1 is point-only (`y_pred`); no base interface rule exists. | **DECISION REQUIRED** |
| **D3** | $SW_{\text{IN}}$ $\to$ Solar Power Mapping | `_irradiance_to_power_w()` exists in baseline engine; no Stage8.1 contract authorization. | **DECISION REQUIRED** |
| **D4** | Wind Forecast Source | Baseline engine reads persistent array; no Stage8.1 composition source defined. | **DECISION REQUIRED** |
| **D5** | Demand Forecast Source | Baseline engine reads persistent array; no Stage8.1 composition source defined. | **DECISION REQUIRED** |
| **D6** | Multi-Source Composition | Baseline engine composes internal streams; no Stage8.1 composition path established. | **DECISION REQUIRED** |
| **D7** | `ForecastBundle` Contract Change | Schema v1.0 is frozen; necessity of extension depends on D1–D6. | **NOT_ESTABLISHED** |

---

## 15. Implementation Gate

```
IMPLEMENTATION_STATUS = NOT_AUTHORIZED
```

- NO adapter layer (`Stage81ForecastEngine`) may be written.
- NO source code or schema file may be modified.
- NO Stage8.1 $\to$ EMS experiment may be executed.
- Implementation remains strictly **NOT AUTHORIZED** until project governance formally records decisions for D1 through D6.

---

## 16. File Modification Audit

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
- `POLARIS_STAGE8_1_FORECASTBUNDLE_RESEARCH_GOVERNANCE_PACKAGE.md`
- `POLARIS_STAGE8_1_FORECASTBUNDLE_RESEARCH_GOVERNANCE_PACKAGE.json`

---

## 17. Final Governance Status

```
POINT_SEMANTICS = PARTIALLY_ESTABLISHED
INTERVAL_SEMANTICS = NOT ESTABLISHED
POINT_ONLY_REPRESENTATION = NOT ESTABLISHED
PV_MAPPING = NOT ESTABLISHED
WIND_SOURCE = NOT ESTABLISHED
DEMAND_SOURCE = NOT ESTABLISHED
MULTI_SOURCE_COMPOSITION = NOT ESTABLISHED
FROZEN_CONTRACT_CHANGE_REQUIRED = NOT_ESTABLISHED
FINAL_GOVERNANCE_STATUS = DECISION_REQUIRED
IMPLEMENTATION_STATUS = NOT_AUTHORIZED
```
