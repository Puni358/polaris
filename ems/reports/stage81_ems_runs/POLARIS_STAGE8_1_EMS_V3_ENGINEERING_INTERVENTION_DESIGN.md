# POLARIS Stage8.1 → EMS V3 Engineering Intervention Design
## Mechanism-Specific Design / Scientific Consistency Corrected / No Implementation / No Execution

```yaml
V3_DESIGN_STATUS: DESIGN_ONLY
V3_IMPLEMENTATION_STATUS: NOT_STARTED
V3_EXECUTION_STATUS: NOT_AUTHORIZED
V2_MODIFICATION: NO
V2_RERUN: NO
V1_MODIFICATION: NO
FORECAST_MODIFICATION: NO
EMS_MODIFICATION: NO
OPTIMIZER_MODIFICATION: NO
SIMULATOR_MODIFICATION: NO
RAW_EVIDENCE_MODIFICATION: NO
```

---

## 1. Executive Governance & Scientific Consistency Statement

```yaml
V1 STATUS = ACCEPTED + FROZEN (Control: 4671.00 L, Treatment: 6447.44 L, Mean Delta: +10.2684 L)
V2 EXECUTION = VALID + COMPLETED (173 Origins, 4,152 Timesteps)
V2 RAW EVIDENCE = FROZEN (SHA256: 652a047dd272058527d0458fa32738a97cbf70d4aa8a2d59aeaa33b33183415a)
V2 FORENSIC AUDIT = ACCEPTED WITH QUALIFICATIONS (Classification B)
V2 MECHANISM WORDING = CORRECTED + LOCKED (POLARIS_STAGE8_1_EMS_V2_MECHANISM_WORDING_CORRECTION.md)
V3 DESIGN STATUS = DOCUMENTATION-ONLY SCIENTIFIC CONSISTENCY CORRECTED
EMS MODIFICATION = NOT AUTHORIZED
ENGINEERING INTERVENTION = DESIGN ONLY — NOT AUTHORIZED FOR IMPLEMENTATION OR EXECUTION
```

### Purpose of Correction:
This document updates the V3 engineering intervention design specification to ensure **complete scientific consistency** with the locked V2 forensic audit. The update removes unsupported engineering assertions (e.g., claiming specific horizons are "low-confidence" or "uncalibrated" without empirical proof, or framing hysteresis as a fix for "short-cycling" when Treatment exhibited fewer startups than Control).

---

## 2. Governance Correction Manifest

| Correction ID | Target Component | Original Assertion | Corrected Neutral Formulation | Scientific Rationale |
|---|---|---|---|---|
| **CONSISTENCY_01** | Class B | *"low-confidence morning forecast horizons (h=1..6)"* | *"candidate morning forecast horizons under evaluation"* | V2 established multi-horizon forecast-shape differences, but did not establish that horizons 1–6 are specifically low-confidence. |
| **CONSISTENCY_02** | Class E | *"optimizing against lower-bound solar quantile in receding horizon"* | *"hypothesis requiring external uncertainty estimation before implementation"* | Stage8.1 `ForecastBundle` uses degenerate point format (`lower=point=upper`). An external uncertainty estimation model is a mandatory prerequisite prior to implementation. |
| **CONSISTENCY_03** | Class F | *"distant uncalibrated horizons (h=12..24)"* | *"predeclared horizon sub-windows under experimental evaluation"* | V2 did not establish that horizons 12–24 are specifically uncalibrated. Neutral factor language enforced. |
| **CONSISTENCY_04** | Class C | *"response to treatment-side short-cycling"* | *"hypothesis testing commitment hysteresis impact under frozen forecast/truth environment"* | Raw V2 telemetry proved Treatment had 178 startups vs Control's 346 startups. Treatment did not short-cycle. |
| **CONSISTENCY_05** | Candidate Framing | *"proven remedies / solutions"* | *"future engineering hypotheses"* | All 7 candidate classes are framed explicitly as un-tested future engineering hypotheses rather than validated remedies. |
| **CONSISTENCY_06** | Framework | *"3-Arm Parallel Replay"* | *"3-Arm Paired Replay Design"* | Aligned framework terminology to 3-Arm Paired Replay Design over shared $N=173$ origin population. |

---

## 3. Frozen V2 Mechanism Evidence Base

The design of candidate V3 interventions is grounded exclusively in the corrected, locked V2 mechanism observability findings:

- **M1 — Diesel Commitment (`Classification: B — STRONGLY SUPPORTED`)**:
  Treatment exhibited fewer startup events ($178 \text{ vs } 346$), but longer continuous commitment runs ($400 \text{ vs } 346 \text{ timesteps}$) and higher average diesel power ($33.79 \text{ kW vs } 10.0 \text{ kW}$) across active steps.
- **M2 — Battery Dispatch (`Classification: A — DIRECTLY ESTABLISHED FOR THE OBSERVED TEMPORAL PATHWAY`)**:
  Early battery discharge decisions and SOC trajectories diverge at $k=1 \dots 4$ prior to daytime solar arrival, directly preceding later diesel commitment divergence.
- **M3 — Renewable Absorption / Curtailment (`Classification: A — DIRECTLY ESTABLISHED AT THE OBSERVED DISPATCH/EVENT LEVEL`)**:
  Renewable curtailment occurs during active diesel commitment due to minimum generator output limits ($P_{\text{min}} = 15 \text{ kW}$).
- **M4 — SOC Positioning (`Classification: A — DIRECTLY ESTABLISHED FOR THE OBSERVED TEMPORAL PATHWAY`)**:
  Early morning SOC depletion persists into afternoon operating hours, coinciding with evening diesel commitment.
- **M5 — Forecast-Horizon Shape (`Classification: B — STRONGLY SUPPORTED, NOT INDIVIDUALLY ISOLATED`)**:
  Treatment and control forecast vectors differ in their multi-horizon shape at $k=0$ before $H1$ forecast error manifests at $k=5$. Individual horizon causality is un-isolated.
- **M6 — Multi-Pathway Interaction (`Classification: B — STRONGLY SUPPORTED`)**:
  Sequential multi-pathway trace: Multi-horizon forecast shape $\rightarrow$ Battery SOC positioning $\rightarrow$ Diesel commitment $\rightarrow$ Renewable curtailment.
- **M7 — Other Mechanisms (`Classification: E — NOT IDENTIFIABLE FROM AVAILABLE EVIDENCE`)**:
  No extraneous un-modeled mechanisms observed.

---

## 4. Conceptual Evaluation of Candidate Intervention Classes (A – G)

Every candidate class explicitly distinguishes:
$$\text{OBSERVED V2 EVIDENCE} \quad \text{vs} \quad \text{ENGINEERING HYPOTHESIS} \quad \text{vs} \quad \text{FUTURE INTERVENTION}$$

No candidate is ranked, declared preferred, or designated optimal.

---

### Candidate Class A: Forecast-Aware SOC Reserve / Terminal-State Policy
- **Observed V2 Evidence**: M2/M4: Early morning battery SOC divergence precedes evening diesel commitment.
- **Engineering Hypothesis**: Dynamic SOC floor reservation during morning hours prevents SOC depletion prior to un-forecasted solar drops.
- **Future Intervention**: Formally declared dynamic SOC floor constraint added to MILP formulation.
- **New Parameters**: `soc_reserve_dynamic_factor` (scalar multiplier on horizon variance).
- **Unchanged EMS Behavior**: MILP power flow conservation, physical battery limits, load serving logic.
- **Risks Introduced**: Over-conservative SOC reservation may force unnecessary diesel commitment when solar is available.
- **Required Measurements**: `soc_before`, `soc_after`, `h1_diesel_power`, `h1_renewable_curtailment`.
- **Outcomes Improving if Hypothesis Correct**: Total diesel fuel liters, minimum SOC percentage.
- **Outcomes Worsening if Hypothesis Incorrect**: Renewable curtailment kWh, diesel active timesteps.
- **Falsification Criterion**: If dynamic SOC reserve fails to reduce diesel fuel while increasing renewable curtailment, hypothesis is rejected.

---

### Candidate Class B: Forecast-Uncertainty-Aware Battery Dispatch Constraints
- **Observed V2 Evidence**: M2/M5: Multi-horizon forecast shape differences lead to early battery dispatch divergence.
- **Engineering Hypothesis**: Capping maximum battery discharge rate during candidate morning forecast horizons preserves SOC buffer.
- **Future Intervention**: Formally declared horizon-specific battery discharge cap constraints.
- **New Parameters**: `max_discharge_fraction_per_horizon` (vector of caps per horizon step).
- **Unchanged EMS Behavior**: Battery capacity $E_{\text{cap}} = 200 \text{ kWh}$, inverter efficiency $\eta = 0.95$, load serving priority.
- **Risks Introduced**: Discharge caps may force early diesel dispatch when battery power was sufficient to serve load.
- **Required Measurements**: `h1_battery_discharge_power`, `h1_diesel_power`, `soc_before`.
- **Outcomes Improving if Hypothesis Correct**: Total diesel fuel liters, battery equivalent cycles.
- **Outcomes Worsening if Hypothesis Incorrect**: Unmet critical load kWh, early diesel startup count.
- **Falsification Criterion**: If discharge caps increase diesel commitment steps without reducing total fuel, hypothesis is rejected.

---

### Candidate Class C: Diesel Commitment Hysteresis / Minimum-Runtime Logic
- **Observed V2 Evidence**: M1/M3: Treatment exhibited fewer startups ($178 \text{ vs } 346$) but longer continuous runs ($400 \text{ vs } 346 \text{ steps}$) at higher power ($33.79 \text{ kW vs } 10.0 \text{ kW}$).
- **Engineering Hypothesis**: Tests whether commitment hysteresis / minimum-runtime logic alters generator operating behavior under the frozen forecast/truth environment.
- **Future Intervention**: Formally declared MILP objective penalty for rapid generator state transitions.
- **New Parameters**: `min_offline_hours_penalty` (MILP objective penalty weight for rapid re-cycling).
- **Unchanged EMS Behavior**: Diesel minimum output limit $P_{\text{min}} = 15 \text{ kW}$, marginal fuel consumption slope $0.00025 \text{ L/Wh}$.
- **Risks Introduced**: Excessive hysteresis locks diesel ON unnecessarily, increasing fuel consumption and curtailment.
- **Required Measurements**: `startup_event`, `shutdown_event`, `h1_diesel_power`, `h1_renewable_curtailment`.
- **Outcomes Improving if Hypothesis Correct**: Startup event count, diesel fuel liters.
- **Outcomes Worsening if Hypothesis Incorrect**: Renewable curtailment kWh, total diesel active timesteps.
- **Falsification Criterion**: If hysteresis logic increases total diesel-active timesteps without reducing fuel, hypothesis is rejected.

---

### Candidate Class D: Renewable-Absorption-Aware Diesel Commitment Logic
- **Observed V2 Evidence**: M1/M3: Renewable curtailment occurs during active diesel commitment due to $P_{\text{min}} = 15 \text{ kW}$ constraints.
- **Engineering Hypothesis**: Adding a solar absorption credit to the MILP objective tests whether daytime diesel commitment is suppressed.
- **Future Intervention**: Formally declared daytime curtailment penalty weight in MILP objective.
- **New Parameters**: `daytime_curtailment_penalty_weight` (objective weighting factor).
- **Unchanged EMS Behavior**: Hard load-serving constraints, battery power bounds.
- **Risks Introduced**: Daytime diesel suppression may cause SOC depletion immediately before evening peak.
- **Required Measurements**: `h1_renewable_curtailment`, `h1_renewable_dispatch`, `h1_diesel_power`.
- **Outcomes Improving if Hypothesis Correct**: Renewable curtailment percentage, renewable utilization percentage.
- **Outcomes Worsening if Hypothesis Incorrect**: Evening diesel fuel consumption, unmet critical load.
- **Falsification Criterion**: If curtailment penalty shifts diesel run hours to evening without reducing total fuel, hypothesis is rejected.

---

### Candidate Class E: Robust MPC / Conservative Treatment of Forecast Uncertainty
- **Observed V2 Evidence**: M2/M5/M6: Multi-horizon forecast optimism drives early battery dispatch divergence.
- **Engineering Hypothesis**: Tests whether conservative forecast quantile evaluation reduces over-optimistic dispatch decisions.
- **Prerequisite Note**: Stage8.1 `ForecastBundle` uses degenerate point format (`lower=point=upper`) with zero statistical coverage claims. An external uncertainty-estimation methodology is a mandatory prerequisite prior to any implementation of Class E. (Not created here).
- **Future Intervention**: External uncertainty estimation model + quantile-constrained MILP formulation.
- **New Parameters**: `solar_forecast_conservatism_quantile` (quantile parameter $q \in [0.1, 0.5]$).
- **Unchanged EMS Behavior**: MILP cost objective weights, simulator physics.
- **Risks Introduced**: Excessive conservatism causes systematic over-generation and unnecessary diesel commitment.
- **Required Measurements**: `treatment_forecast_vector_24`, `h1_diesel_power`, `soc_before`.
- **Outcomes Improving if Hypothesis Correct**: Total diesel fuel liters, SOC trajectory stability.
- **Outcomes Worsening if Hypothesis Incorrect**: Total diesel active timesteps, renewable curtailment.
- **Falsification Criterion**: If quantile conservatism increases mean diesel fuel across 173 origins, hypothesis is rejected.

---

### Candidate Class F: Horizon-Weighted MPC Objective or Constraint Treatment
- **Observed V2 Evidence**: M5/M6: Multi-horizon forecast shape vector differences precede $H1$ error manifestations.
- **Engineering Hypothesis**: Tests whether discounting objective weights for predeclared distant forecast horizons aligns MILP decisions with forecast decay.
- **Future Intervention**: Formally declared horizon-decay weighting factor applied to MILP objective horizons.
- **New Parameters**: `horizon_discount_factor_gamma` ($\gamma \in [0.90, 0.99]$).
- **Unchanged EMS Behavior**: Physical conservation of energy constraints, H1 action execution.
- **Risks Introduced**: Heavy horizon discounting makes MPC myopic, causing failure to prepare for known multi-hour load peaks.
- **Required Measurements**: `objective_value`, `h1_diesel_power`, `h1_battery_charge_power`.
- **Outcomes Improving if Hypothesis Correct**: Total diesel fuel liters, battery throughput.
- **Outcomes Worsening if Hypothesis Incorrect**: Unmet critical load, late-horizon diesel power spikes.
- **Falsification Criterion**: If horizon discounting causes late-horizon energy deficits or constraint violations, hypothesis is rejected.

---

### Candidate Class G: Combined Battery-SOC + Diesel Commitment Policy
- **Observed V2 Evidence**: M1/M2/M3/M4: Interacting sequence between SOC depletion, generator commitment, and curtailment.
- **Engineering Hypothesis**: Tests whether a state-dependent coupling constraint linking minimum SOC floor to generator commitment state optimizes dispatch.
- **Future Intervention**: Formally declared joint reserve coupling constraint in MILP formulation.
- **New Parameters**: `joint_reserve_coupling_coefficient` (coupling scalar).
- **Unchanged EMS Behavior**: Digital twin simulator physical transition equations.
- **Risks Introduced**: Increased formulation complexity could increase MILP solve times or cause numerical infeasibilities.
- **Required Measurements**: `soc_before`, `diesel_commitment`, `optimizer_status`, `solve_time_ms`.
- **Outcomes Improving if Hypothesis Correct**: Total diesel fuel liters, renewable utilization percentage, battery equivalent cycles.
- **Outcomes Worsening if Hypothesis Incorrect**: MILP optimizer solve time, constraint violation count.
- **Falsification Criterion**: If joint policy triggers MILP infeasibilities or fails to reduce diesel fuel, hypothesis is rejected.

---

## 5. Proposed V3 Experimental 3-Arm Paired Replay Design

To evaluate any authorized V3 intervention without bias, the experimental framework specifies a **3-Arm Paired Replay Design** over the shared $N=173$ origin population:

```
                              ┌─────────────────────────────────────────┐
                              │  N = 173 Paired Forecast Origins        │
                              └────────────────────┬────────────────────┘
                                                   │
        ┌──────────────────────────────────────────┼──────────────────────────────────────────┐
        ▼                                          ▼                                          ▼
┌──────────────┐                           ┌──────────────┐                           ┌──────────────┐
│    ARM 1     │                           │    ARM 2     │                           │    ARM 3     │
│   CONTROL    │                           │   BASELINE   │                           │ INTERVENTION │
│ (Baseline    │                           │  TREATMENT   │                           │     ARM      │
│  Forecast)   │                           │  (Stage8.1)  │                           │(Stage8.1 +   │
└───────┬──────┘                           └───────┬──────┘                           │ Intervention)│
        │                                          │                                  └───────┬──────┘
        ▼                                          ▼                                          ▼
┌──────────────┐                           ┌──────────────┐                           ┌──────────────┐
│ Frozen MILP  │                           │ Frozen MILP  │                           │ Modified EMS │
│  Optimizer   │                           │  Optimizer   │                           │ (Declared    │
└───────┬──────┘                           └───────┬──────┘                           │ Intervention)│
        │                                          │                                  └───────┬──────┘
        ▼                                          ▼                                          ▼
┌──────────────┐                           ┌──────────────┐                           ┌──────────────┐
│ Digital Twin │                           │ Digital Twin │                           │ Digital Twin │
│  Simulator   │                           │  Simulator   │                           │  Simulator   │
└──────────────┘                           └──────────────┘                           └──────────────┘
```

### Arm Definitions:
1. **ARM 1 — CONTROL**: Frozen LocalBaselineForecastEngine + Frozen MILP Optimizer.
2. **ARM 2 — BASELINE TREATMENT**: Frozen Stage8.1 Empirical Forecast + Frozen MILP Optimizer.
3. **ARM 3 — INTERVENTION ARM**: Frozen Stage8.1 Empirical Forecast + Formally Declared EMS Intervention Component.

### Strict Intervention Isolation Rule:
The **Intervention Arm** differs from the **Baseline Treatment Arm** in *exactly one declared engineering component*. Simultaneous modifications to forecast engines, simulator physics, battery models, or diesel parameters are strictly prohibited.

---

## 6. Safety & Hard Constraints

Any future V3 intervention must strictly enforce the following **non-negotiable safety rules**:
1. **Zero Unmet Critical Load**: $P_{\text{unmet},k} = 0.0 \text{ W}$ for all $k$. Any run producing $P_{\text{unmet}} > 0$ is classified as **FAILED/UNSAFE**.
2. **Hard Physical Constraints**:
   - $0.20 \le \text{SOC}_k \le 0.95$
   - $0.0 \le P_{\text{charge},k} \le 50.0 \text{ kW}$
   - $0.0 \le P_{\text{discharge},k} \le 50.0 \text{ kW}$
   - $P_{\text{diesel},k} = 0.0 \text{ W}$ OR $15.0 \text{ kW} \le P_{\text{diesel},k} \le 60.0 \text{ kW}$
3. **No Constraint Relaxation**: Relaxing physical constraints or safety bounds to achieve lower fuel numbers is **STRICTLY PROHIBITED**.

---

## 7. Governed Implementation Sequence (Gates 1 – 9)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ GATE 1: V3 Intervention Design Review (COMPLETED BY THIS ARTIFACT)     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ GATE 2: Formal Implementation Authorization Review                       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ GATE 3: Static Source-Level Implementation Audit                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ GATE 4: V2-Equivalence / Non-Intervention Verification                  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ GATE 5: Bounded Mechanical Validation (No scientific outcome eval)      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ GATE 6: Formal V3 Empirical Execution Authorization                     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ GATE 7: V3 Empirical Replay Execution                                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ GATE 8: Post-Execution Forensic Audit                                   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│ GATE 9: Mechanism & Outcome Reconciliation Analysis                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Non-Execution Declaration

- **V3 Code Created**: NONE.
- **EMS Code Modified**: NONE.
- **Experiments Executed**: NONE.
- **Outcome Claims Made**: NONE.

---
**Authoritative Corrected Design Artifacts**:
- [`POLARIS_STAGE8_1_EMS_V3_ENGINEERING_INTERVENTION_DESIGN.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_V3_ENGINEERING_INTERVENTION_DESIGN.md)
- [`POLARIS_STAGE8_1_EMS_V3_ENGINEERING_INTERVENTION_DESIGN.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_V3_ENGINEERING_INTERVENTION_DESIGN.json)
