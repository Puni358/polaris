# POLARIS SYSTEM D5 — FORECAST-ERROR → EMS ROBUSTNESS CONTRACT & ROADMAP (FINAL REVISED)

**Phase**: D5 — Forecast-Error → EMS Robustness  
**Governance Status**: CONTRACT / ROADMAP ONLY — IMPLEMENTATION & EXECUTION NOT AUTHORIZED  
**Phase Status**: **D5 = CONTRACT / ROADMAP ONLY**  
**Preceding Phase Status**: **D4 = CLOSED** (D4-A, D4-B, D4-C0, D4-C1 frozen; D4-C2, D4-C branch closed)  

---

## 1. PRIMARY ENGINEERING QUESTION

> *"How does downstream EMS operational behavior (unmet load, diesel consumption, renewable curtailment, and SOC boundary integrity) change as a function of systematic forecast error in solar, wind, and demand when the frozen POLARIS closed-loop MPC is supplied with perturbed forecasts under identical hidden ground-truth actual trajectories?"*

This engineering question characterizes the sensitivity of the **EXISTING, FROZEN POLARIS EMS** to forecast errors. D5 evaluates downstream operational consequences on the existing system; it does NOT attempt to improve, retrain, recalibrate, or select a forecasting model, nor does it modify, tune, or select the optimizer.

---

## 2. GOVERNANCE & PROGRESSION SEQUENCE

D5 is currently in **CONTRACT / ROADMAP ONLY** status. Implementation and execution are strictly **NOT AUTHORIZED**.

D5 adheres to the mandatory POLARIS governance sequence:
$$\text{CONTRACT} \longrightarrow \text{SCIENTIFIC / GOVERNANCE REVIEW} \longrightarrow \text{EXPLICIT IMPLEMENTATION AUTHORIZATION} \longrightarrow \text{IMPLEMENTATION} \longrightarrow \text{IMPLEMENTATION REVIEW} \longrightarrow \text{EXPLICIT EXECUTION AUTHORIZATION} \longrightarrow \text{EXECUTION} \longrightarrow \text{EVIDENCE} \longrightarrow \text{GATE-BY-GATE REVIEW} \longrightarrow \text{FREEZE OR CLOSE}$$

### Implementation Scope Boundary:
> Implementation authorization permits construction and modification of **D5 implementation code, D5-specific schemas or adapters that do not modify frozen system schemas, configuration, test infrastructure, and supporting documentation required to implement the frozen D5 contract.**
>
> It does NOT authorize modification of:
> * the frozen D5 contract;
> * frozen EMS scientific/operational logic;
> * frozen forecasting logic;
> * frozen evaluator definitions;
> * frozen D4 artifacts or governance;
> * any locked historical research artifacts.
>
> If an implementation change would require modifying a frozen artifact, STOP and report the dependency rather than modifying it.
>
> **Frozen System Schemas Immutability Rule**:
> **Frozen system schemas, including the existing ForecastBundle, DispatchPlan, and StationState schemas, MUST NOT be modified.**
>
> D5-specific validation structures, adapters, scenario representations, or metadata schemas may be added only where they do not alter the behavior, fields, validation rules, or semantics of the frozen system schemas.
>
> Implementation authorization therefore does NOT grant permission to modify `system/schemas/forecast_bundle.py`, `system/schemas/dispatch_plan.py`, `system/schemas/station_state.py`, or equivalent frozen system-schema artifacts.
>
> If D5 implementation appears to require such a modification: **STOP and report the dependency.** Do not modify the schema.

---

## 3. FROZEN DEPENDENCIES & IMMUTABLE COMPONENTS

The following components are **FROZEN & IMMUTABLE**:

1. **Stage8.1 Forecasting Research & Models**: Stage8.1 forecasting models, weights, and research outputs remain untouched.
2. **ForecastEngine Interface**: The frozen Python interface supplying forecast data (`ForecastEngine`).
3. **ForecastBundle Schema**: [`system/schemas/forecast_bundle.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/forecast_bundle.py) schema validation rules.
4. **MILP Optimizer**: [`system/optimization/implementations/milp.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/milp.py) formulation and solver settings.
5. **Rule-Based Optimizer**: [`system/optimization/implementations/rule_based.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/optimization/implementations/rule_based.py) logic.
6. **Digital Twin Simulator**: [`system/simulation/simulator.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/simulation/simulator.py) battery physics, diesel constraints, and SOC boundary enforcement ($20.0\% \le \text{SOC} \le 95.0\%$).
7. **StationState Schema**: [`system/schemas/station_state.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/schemas/station_state.py).
8. **D1/D2/D3/D4 Architecture & Invariants**: All physical energy conservation laws, closed-loop MPC H1 execution semantics, offline network isolation, and future-truth firewalls.
9. **D4 Execution Semantics**: Single-step MPC runner loop in [`system/runtime/runner.py`](file:///home/punith-bs/01polaris%20%28Copy%29/system/runtime/runner.py).

---

## 4. TWO-WORLD CAUSAL MODEL & FORECAST-PERTURBATION FIREWALL

D5 maintains a strict two-world separation between controller-visible data and evaluator ground truth:

```
+-------------------------------------------------------------------+
|                        CONTROLLER WORLD                           |
|  - Current observable state S_t0                                  |
|  - Historical observations available at or before t0              |
|  - Perturbed 24h ForecastBundle F' = P(F, theta, seed)            |
|  - Frozen POLARIS Configuration & MILP Optimizer                  |
|  - Prior legitimate controller state/actions                      |
|  - Output: 24h DispatchPlan C'                                    |
+-------------------------------------------------------------------+
                                 |
                                 v
+-------------------------------------------------------------------+
|                    DIGITAL TWIN / EVALUATION WORLD                |
|  - Hidden Ground-Truth Actuals A (Solar, Wind, Demand for t > t0) |
|  - Physical Battery & Diesel Simulator                            |
|  - Evaluates DispatchPlan C' (H1 action) against Actuals A        |
|  - Outputs: Realized State S_t+1, Unmet Load, Fuel, Curtailment   |
+-------------------------------------------------------------------+
```

### Mandatory Forecast-Perturbation Firewall Formula:
$$F'_t = P(F_t, \theta, \text{seed})$$

where:
* $F_t$: Baseline 24-hour `ForecastBundle` generated by the frozen forecaster at decision point $t$.
* $\theta$: Predeclared deterministic perturbation parameters (e.g., scale factor $\gamma$).
* $\text{seed}$: Predeclared deterministic random seed (required if a stochastic perturbation is explicitly specified).

### Causal Firewall & Paired Control Rules:
1. **Inputs Allowed**: The perturbation generator $P$ may inspect ONLY the baseline 24-hour `ForecastBundle` $F_t$, predeclared parameters $\theta$, deterministic scenario metadata, and the specified random seed.
2. **Prohibited Access**: The perturbation generator $P$ MUST NOT inspect, access, condition upon, calibrate against, optimize against, or select parameters using hidden future ground-truth actuals $A$.
3. **No Oracle Perturbations**: Any perturbation derived using ground-truth actuals (such as $F'_t = A_t + \epsilon$) or any equivalent oracle construction is strictly prohibited.
4. **Post-Decision Evaluation Only**: Hidden future actuals $A$ are accessed exclusively by the Digital Twin / Evaluator AFTER the controller has produced its dispatch decision $C'_t$.
5. **Fixed Parameters**: All perturbation parameters $\theta$ and scenario rules MUST be fixed prior to experimental execution.
6. **Exogenous Input Stream Provenance**: At corresponding MPC decision points, the paired control and perturbed executions must use the same predeclared exogenous observation/input provenance for generation of the baseline `ForecastBundle`. Differences in realized station state caused by previous dispatch decisions are permitted as downstream consequences of the perturbation, but must not be used to redefine or retrospectively select the paired forecast-error parameters.
7. **Hidden / Experimental Actual Trajectory Firewall**:
   > During implementation and implementation testing, hidden future actual trajectories MUST NOT be loaded or consumed as experimental inputs.
   >
   > Synthetic/mock actuals may be used solely to verify software interfaces, state transitions, evaluator wiring, or control flow.
   >
   > A real D5 experimental actual trajectory combined with a D5 perturbation scenario is sufficient to require D5 execution authorization, regardless of whether empirical metrics are ultimately saved.

---

## 5. FORECASTBUNDLE VALIDITY & INTERVAL PERTURBATION SEMANTICS

1. **Interval Scale Transformation**: Where a `ForecastBundle` forecast quantity contains lower ($L$), point ($P$), and upper ($U$) values, a multiplicative scale factor $\gamma \ge 0$ transforms all three components identically:
   $$L' = \gamma \cdot L, \quad P' = \gamma \cdot P, \quad U' = \gamma \cdot U$$
   For non-negative $\gamma \ge 0$, this transformation preserves lower $\le$ point $\le$ upper ($L' \le P' \le U'$) by construction.
2. **Validity Enforcement**: Perturbation rules MUST be designed to produce a valid `ForecastBundle` by construction. If a proposed perturbation produces non-finite values (`NaN`, `Inf`), invalid interval ordering ($L' > P'$ or $P' > U'$), schema violations, or negative power values where prohibited, the resulting scenario MUST be **REJECTED AS INVALID**.
3. **No Silent Repair**: An invalid forecast bundle MUST NOT be silently clamped, repaired, normalized, smoothed, or substituted.
4. **Rejection Logging**: Any rejected scenario must be explicitly logged as invalid rather than reported as an executed robustness result.

---

## 6. UNITS AND FORECAST SEMANTICS

D5 perturbations are applied strictly to the actual forecast quantities consumed by the frozen POLARIS EMS:
* **Solar Electrical Generation**: Watts ($W$)
* **Wind Electrical Generation**: Watts ($W$)
* **Station Demand Load**: Watts ($W$)

If irradiance ($\text{W/m}^2$) forecasts exist in the upstream pipeline, perturbations apply to irradiance while preserving existing downstream conversion semantics. D5 does NOT introduce new solar conversion models.

---

## 7. CLOSED-LOOP MPC PERTURBATION SEMANTICS

D5 is a closed-loop MPC simulation experiment. The frozen runtime execution model remains strictly unchanged:
* **Simulation Duration**:
  * For D5-1 through D5-5, exactly **$N = 24$ closed-loop iterations**.
  * For D5-6, exactly **$N = 168$ closed-loop iterations**.
  * These durations are frozen by the corresponding D5 gate definitions and MUST NOT be changed during implementation or execution.
* **Forecast Horizon per Iteration**: Exactly 24 hours.
* **Executed Action per Iteration**: Exactly the first timestep ($H1$).

### Step-by-Step MPC Decision Loop:
At each closed-loop decision step $t \in \{1 \dots N\}$:
1. The frozen forecasting interface generates a new 24-hour baseline `ForecastBundle` $F_t$ available at decision point $t$.
2. The predetermined perturbation rule $P$ is applied to $F_t$, yielding perturbed 24-hour `ForecastBundle` $F'_t = P(F_t, \theta, \text{seed})$.
3. $F'_t$ is validated against the schema and supplied to the unchanged frozen optimizer.
4. The optimizer generates a 24-hour horizon `DispatchPlan` $C'_t$.
5. **ONLY the first timestep ($H1$)** of $C'_t$ is executed by the station runner.
6. The Digital Twin simulator advances station state to $t+1$ using the hidden actual ground-truth $A_t$.
7. The closed-loop process repeats for step $t+1$.

---

## 8. JUSTIFIED FORECAST-ERROR SCENARIO DEFINITIONS & D5 GATE-FIXTURE IMMUTABILITY

> **D5 Gate-Fixture Immutability**:
> D5-1 through D5-6 scenario definitions are frozen contract inputs.
>
> Antigravity MUST NOT alter their:
> * perturbation factors;
> * scenario composition;
> * horizon;
> * iteration count;
> * persistence;
> * evaluation definitions;
> * causality rules.
>
> Implementation may create software representations of these scenarios, but must not execute them against experimental trajectories before separate D5 execution authorization.

### Retained Scenario Definitions:

* **S1 — Solar Underprediction**: $L' = 0.70 L, P' = 0.70 P, U' = 0.70 U$. Tests EMS response when available solar generation is systematically underrepresented in the forecast.
* **S2 — Solar Overprediction Sensitivity**: $L' = 1.30 L, P' = 1.30 P, U' = 1.30 U$. Tests EMS response when available solar generation is systematically overrepresented in the forecast.
* **S3 — Wind Underprediction**: $L' = 0.70 L, P' = 0.70 P, U' = 0.70 U$. Tests EMS response when available wind generation is systematically underrepresented in the forecast.
* **S4 — Wind Overprediction**: $L' = 1.30 L, P' = 1.30 P, U' = 1.30 U$. Tests EMS response when available wind generation is systematically overrepresented in the forecast.
* **S5 — Demand Overprediction**: $L' = 1.20 L, P' = 1.20 P, U' = 1.20 U$. Tests EMS response when station demand is systematically overrepresented in the forecast.
* **S6 — Compound Over-Optimistic Forecast Stress**: Solar $\times 1.30$, Wind $\times 1.30$, Demand $\times 0.80$ applied to $L, P, U$ fields. Specified compound stress scenario; not classified as a "worst case".

---

## 9. PERTURBATION LEVELS & RESPONSE CHARACTERIZATION

The core gates D5-1 through D5-6 are specified as fixed single-point characterization experiments.

Full response trajectories across sweeps of scale factors $\gamma$ are NOT required for D5-1 through D5-6. A full response trajectory requirement applies ONLY to a gate or scenario explicitly designated and authorized as a perturbation sweep.

---

## 10. PRIMARY D5 EVALUATION CRITERION & REPRODUCIBLE LSF DEFINITION

For D5 evaluation purposes, a forecast-error perturbation meets the predefined response criterion when:
1. Execution completes with `SUCCESS_CLEAN` or `SUCCESS_WITH_GOVERNED_FAULTS`.
2. Zero `FAILED_STATE_VIOLATION` events occur.
3. Energy-balance residuals remain within the predefined physical tolerance ($< 0.1\text{ W}$).
4. Load-Served Fraction (LSF) satisfies $\text{LSF} \ge 95.0\%$.

### Reproducible LSF Metric Definition:
$$\text{LSF} = 100 \times \left(1 - \frac{E_{\text{unmet}}}{E_{\text{demand\_total}}}\right)$$
LSF shall be computed using the frozen POLARIS evaluator definition; no new D5-specific LSF definition is introduced.

> [!IMPORTANT]
> **EVALUATION THRESHOLD DISCLAIMER**:  
> The $95\%$ LSF value is a **predeclared D5 evaluation threshold only**. It MUST NOT be represented as a validated operational requirement or universal definition of EMS robustness unless independently established by a prior POLARIS requirement. Where LSF falls below $95\%$, the outcome shall be reported as a threshold crossing for that specific perturbation level, not as proof that the entire POLARIS EMS is non-robust.

---

## 11. REQUIRED EMS OPERATIONAL METRICS

For every executed scenario, the following distinct metric categories MUST be reported separately without combining them into a composite score:

### Physical Outcome Metrics:
* Unmet Load Energy ($E_{\text{unmet}}$, Wh)
* Load-Served Fraction ($\text{LSF}$, %)
* Diesel Fuel Consumption ($V_{\text{fuel}}$, Liters)
* Diesel Operating Hours ($T_{\text{diesel}}$, Hours)
* Renewable Curtailment ($E_{\text{curt}}$, Wh)
* Renewable Utilization ($\text{RU}$, %)
* Minimum SOC ($\text{SOC}_{\min}$, %) and Maximum SOC ($\text{SOC}_{\max}$, %)
* SOC Boundary Contacts (count at $20.0\%$ or $95.0\%$)
* Physical Constraint Violations (count and Wh magnitude)
* Bus-Bar Energy Balance Residual (W), Demand Balance Residual (W), Renewable Balance Residual (W)

### Execution & Fault Metrics (Separated):
* Mathematical MILP Infeasibility Events (count of genuine infeasibility solver returns)
* Solver/Optimization Runtime Failure Events (count of caught solver exceptions/crashes)
* Governed Zero-Dispatch Responses (count of executed $P=0$ degraded responses)
* Optimizer Execution Status (`SUCCESS_CLEAN`, `SUCCESS_WITH_GOVERNED_FAULTS`, `FAILED_TERMINATED`)
* Array of `FaultEvent` records
* Execution Termination Reason (if terminated)
* Deterministic Replay Verification Result

### Perturbation Parameters:
* Predeclared perturbation rule, scale factor $\gamma$, and seed $S_{\text{seed}}$.

---

## 12. CONTROL / COUNTERFACTUAL EXPERIMENTAL DESIGN

Every D5 experiment executes a strict paired comparison:

$$\begin{array}{rccccccc}
\text{Control:} & \text{Baseline } F_t & \longrightarrow & \text{Frozen EMS} & \longrightarrow & \text{Dispatch } D_t & \stackrel{\text{Actuals } A_t}{\longrightarrow} & \text{Outcome } O_{\text{control}} \\
\text{Perturbed:} & \text{Perturbed } F'_t & \longrightarrow & \text{Frozen EMS} & \longrightarrow & \text{Dispatch } D'_t & \stackrel{\text{SAME Actuals } A_t}{\longrightarrow} & \text{Outcome } O_{\text{pert}}
\end{array}$$

### Invariance Constraints:
The initial station state $S_0$, physical configuration, hidden actual trajectory $A$, simulation duration $N$, timestep $\Delta t$, and solver configuration remain **100% IDENTICAL** between control and counterfactual executions.

---

## 13. PROPOSED ACCEPTANCE GATES (D5-1 THROUGH D5-6)

All gates below represent **PROPOSED GOVERNANCE SPECIFICATIONS ONLY**. Implementation and execution are strictly **NOT AUTHORIZED**.

| Gate ID | Engineering Assertion | Deterministic Setup | Forecast Perturbation Rule | Control Condition | Counterfactual Condition | Horizon & Duration | Primary Metrics | Pass / Characterization Criterion | Current Evidence State | Provenance Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **D5-1** | Solar Underprediction Sensitivity | `demo_scenario.json` 24h closed-loop run. | Solar scaled down: $\gamma_{\text{solar}} = 0.70$. | Baseline forecast $F_t$, actuals $A$. | Perturbed forecast $F'_t$, SAME actuals $A$. | 24h horizon, 24 MPC steps. | $E_{\text{unmet}}, V_{\text{fuel}}, \text{LSF}, \text{SOC}_{\min}$. | Characterize downstream EMS response; report $95\%$ LSF evaluation threshold status. | None (Execution not authorized) | **PROPOSED — NOT YET EXECUTED** |
| **D5-2** | Solar Overprediction Sensitivity | `demo_scenario.json` 24h closed-loop run. | Solar scaled up: $\gamma_{\text{solar}} = 1.30$. | Baseline forecast $F_t$, actuals $A$. | Perturbed forecast $F'_t$, SAME actuals $A$. | 24h horizon, 24 MPC steps. | $E_{\text{unmet}}, \text{LSF}, \text{SOC}_{\min}$, state violations. | Characterize response; report $95\%$ LSF evaluation threshold status. | None (Execution not authorized) | **PROPOSED — NOT YET EXECUTED** |
| **D5-3** | Wind Underprediction Sensitivity | `demo_scenario.json` 24h closed-loop run. | Wind scaled down: $\gamma_{\text{wind}} = 0.70$. | Baseline forecast $F_t$, actuals $A$. | Perturbed forecast $F'_t$, SAME actuals $A$. | 24h horizon, 24 MPC steps. | $E_{\text{unmet}}, V_{\text{fuel}}, \text{LSF}, T_{\text{diesel}}$. | Measure EMS response to systematic wind underrepresentation. | None (Execution not authorized) | **PROPOSED — NOT YET EXECUTED** |
| **D5-4** | Demand Overprediction Impact | `demo_scenario.json` 24h closed-loop run. | Demand scaled up: $\gamma_{\text{demand}} = 1.20$. | Baseline forecast $F_t$, actuals $A$. | Perturbed forecast $F'_t$, SAME actuals $A$. | 24h horizon, 24 MPC steps. | $V_{\text{fuel}}, E_{\text{curt}}, \text{SOC}_{\max}$. | Characterize downstream EMS response to demand overprediction. | None (Execution not authorized) | **PROPOSED — NOT YET EXECUTED** |
| **D5-5** | Compound Over-Optimistic Stress | `demo_scenario.json` 24h closed-loop run. | Solar & Wind $\times 1.30$, Demand $\times 0.80$. | Baseline forecast $F_t$, actuals $A$. | Perturbed forecast $F'_t$, SAME actuals $A$. | 24h horizon, 24 MPC steps. | $E_{\text{unmet}}, \text{LSF}, \text{SOC}_{\min}$, fault events. | Characterize response, including any infeasibility or governed degraded state. | None (Execution not authorized) | **PROPOSED — NOT YET EXECUTED** |
| **D5-6** | 168-Hour Persistent Error | `synthetic_168h_endurance_scenario.json` 168h run. | Persistent $+15\%$ solar & wind overprediction ($\gamma = 1.15$). | Baseline 24h forecast $F_t$, actuals $A$. | Perturbed 24h forecast $F'_t$, SAME actuals $A$. | 24h horizon, 168 MPC steps. | Total $V_{\text{fuel}}, T_{\text{diesel}}$, 168h LSF, $\text{SOC}$ bounds. | Characterize cumulative operational and state effects across 168 closed-loop iterations. | None (Execution not authorized) | **PROPOSED — NOT YET EXECUTED** |

---

## 14. IMPLEMENTATION COMPLETION, REVIEW & EXECUTION TRIGGER BOUNDARIES

### Implementation Completion & Review Boundary:
After implementation and authorized implementation-level testing:

```text
D5 IMPLEMENTATION = COMPLETE / AWAITING REVIEW
D5 EXECUTION = NOT AUTHORIZED
```

Implementation completion is **NOT** acceptance. The implementation-review checkpoint must record:
* what was implemented;
* what was tested;
* the exact scope of those tests;
* what was NOT executed;
* any unresolved issues;
* whether the implementation conforms to the frozen contract.

The review determines implementation readiness only. A successful implementation review does NOT authorize D5 execution. After review:

```text
D5 IMPLEMENTATION = REVIEWED / EXECUTION NOT AUTHORIZED
```

A separate explicit **D5 EXECUTION AUTHORIZATION** is required before any D5 experimental scenario is executed.

### Experimental-Execution Trigger:
> A test that executes the frozen EMS using a D5 experimental scenario against an experimental actual trajectory constitutes D5 experimental execution, regardless of whether it is invoked through a test, script, integration test, smoke test, or diagnostic command.

### Supporting-Documentation Boundary:
> **New implementation documentation may be created where required to implement or review D5. Existing frozen governance/checkpoint artifacts MUST NOT be rewritten, amended, or regenerated during implementation merely for documentation convenience.**
>
> New implementation documentation must not alter or supersede the frozen scientific contract.
>
> This governance cleanup is an explicitly authorized controlled revision of the current D5 contract/checkpoint provenance artifacts. After this cleanup is completed and the revised artifacts are frozen, they become authoritative and MUST NOT be amended or rewritten for implementation convenience.
>
> Any future implementation dependency requiring modification of a frozen governance/checkpoint artifact is a STOP-and-report condition.

### Implementation-Test Firewall:
> Implementation-level tests may verify software/contract correctness using isolated synthetic, mock, unit-test, or equivalent non-experimental fixtures, but MUST NOT:
> * execute D5-1 through D5-6;
> * consume D5 experimental actual trajectories;
> * use D5 experimental actual trajectories to generate results;
> * generate empirical EMS forecast-error response metrics;
> * perform baseline-versus-perturbed experimental comparisons;
> * partially execute a D5 experimental scenario;
> * produce D5 empirical evidence;
> * use D5 gate fixtures together with experimental actual trajectories in a way that constitutes experimental execution.
>
> Implementation tests may verify, using synthetic/mock inputs where applicable: perturbation arithmetic, schema validation, interval ordering, deterministic transformation, configuration parsing, firewall/interface isolation, H1 orchestration, metric-schema construction, fault classification, deterministic replay mechanics.
>
> If an implementation-level test would require actual D5 experimental execution: **STOP and report that D5 execution authorization is required.**

---

## 15. DETERMINISM & REPRODUCIBILITY STANDARDS

1. Perturbation scenarios must be deterministic unless a seeded pseudo-random component is explicitly predeclared.
2. Any stochastic component must specify random seed $S_{\text{seed}}$, generation rule, scope, and deterministic inputs.
3. Replayed executions shall be compared against baseline runs using frozen POLARIS C11 numerical tolerances.
4. Claims of "mathematical guarantees" of determinism are prohibited. The document shall state: *"Repeated execution produced results within the predefined C11 numerical tolerances."*

---

## 16. FAILURE HANDLING & INVARIANT PRESERVATION

D5 preserves the frozen D4-C1 failure contract without alteration:
* **No Fallback / No Retries**: Automatic Rule-Based fallback, previous-action persistence, solver relaxation, or retry mechanisms are strictly prohibited.
* **Execution Statuses**: Enforces exact 3-state enum (`SUCCESS_CLEAN`, `SUCCESS_WITH_GOVERNED_FAULTS`, `FAILED_TERMINATED`).
* **Infeasibility**: Genuine MILP infeasibility triggers `GOVERNED_ZERO_DISPATCH` ($P=0$), records `FaultEvent(GOVERNED_DEGRADED)`, and completes as `SUCCESS_WITH_GOVERNED_FAULTS`.
* **State Violation**: SOC excursion below $20.0\%$ or above $95.0\%$ rejects state transition and immediately halts with `FAILED_TERMINATED`.
* **Schema Validation**: Invalid `ForecastBundle` or `DispatchPlan` immediately halts execution with `FAILED_TERMINATED`.

---

## 17. RESEARCH FIREWALL & D4 PROTECTION

* **Research Firewall**: D5 MUST NOT reopen Stage8.1, Phase A, Phase B, Phase C-1, Phase C-2, ABC2, PARD-C, PARD-C3, feature engineering, NWP research, forecasting model selection/tuning, neural network research, spatial/advection research, or ODD experiments.
* **D4 Protection**: All D4 artifacts, fixtures (`demo_scenario.json`, `synthetic_168h_endurance_scenario.json`), configurations, test suites, and checkpoints (D4-A, D4-B, D4-C0, D4-C1, D4-C2) remain frozen, untouched, and immutable.

---

## 18. KILL SWITCH

```
============================================================
D5 KILL SWITCH CONDITION
============================================================
D5 SHALL BE IMMEDIATELY CLOSED WITHOUT IMPLEMENTATION OR EXECUTION IF:
1. Governance review establishes that existing D3/D4 evaluation data
   already sufficiently characterizes the proposed question; OR
2. No meaningful new robustness/sensitivity question remains without
   modifying the frozen architecture; OR
3. Proposed forecast-error scenarios fail to yield distinct, actionable
   engineering information; OR
4. An experiment would require violating the forecast-perturbation firewall; OR
5. Required forecast semantics cannot be defined without inventing unspecified
   lifecycle behavior; OR
6. The study would require reopening frozen forecasting or optimizer research.
============================================================
```

---

## 19. CHECKPOINT & ARTIFACT METADATA

* Markdown Contract File: [`POLARIS_SYSTEM_D5_FORECAST_ERROR_ROBUSTNESS_CONTRACT.md`](file:///home/punith-bs/.gemini/antigravity/brain/b9cc3ac2-a7df-48c7-8c1d-a5d4fcf6e617/POLARIS_SYSTEM_D5_FORECAST_ERROR_ROBUSTNESS_CONTRACT.md)
* Machine-Readable JSON Schema: [`POLARIS_SYSTEM_D5_FORECAST_ERROR_ROBUSTNESS_CONTRACT.json`](file:///home/punith-bs/.gemini/antigravity/brain/b9cc3ac2-a7df-48c7-8c1d-a5d4fcf6e617/POLARIS_SYSTEM_D5_FORECAST_ERROR_ROBUSTNESS_CONTRACT.json)

---

## 20. FINAL GOVERNANCE STATUS

```text
D4 = CLOSED
D5 = CONTRACT / ROADMAP ONLY
D5 IMPLEMENTATION = NOT AUTHORIZED
D5 EXECUTION = NOT AUTHORIZED
D6 = NOT INITIATED
```

---

> [!CAUTION]
> **ABSOLUTE HARD STOP**  
> D5 contract specification cleanup is complete.  
> **No D5 implementation, no D5 test execution, no forecaster modifications, no optimizer modifications, and no D6 work will be performed.**
