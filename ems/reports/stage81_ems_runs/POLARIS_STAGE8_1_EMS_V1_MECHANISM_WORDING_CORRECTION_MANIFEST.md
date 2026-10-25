# POLARIS — STAGE8.1 → EMS V1
## MECHANISM WORDING CORRECTION MANIFEST & V2 HANDOFF

```
============================================================
FINAL GOVERNANCE STATUS & INTEGRITY CONFIRMATION
============================================================
V1_EXECUTION_STATUS: ACCEPTED_AND_FROZEN
V1_MECHANISM_STATUS: AGGREGATE_ASSOCIATION_ONLY
V1_CAUSAL_MECHANISM: NOT_ESTABLISHED
V1_RESULT_MODIFIED: NO
V1_RERUN: NO
V2_STATUS: DESIGNED_NOT_EXECUTED
V2_EXECUTION_AUTHORIZED: NO
NEXT_RESEARCH_TARGET: IDENTIFY_TIMESTEP_LEVEL_MECHANISM_OF_DIESEL_INCREASE
============================================================
```

---

### 1. SUMMARY OF WORDING CORRECTIONS

This manifest documents the formal precision corrections applied to the Stage8.1 → EMS V1 mechanism reports.

#### Corrected Wording Categories
1. **Removal of Overclaimed Timestep Causality**: Replaced process assertions (such as *"Control refused diesel commitment"*, *"Treatment committed diesel"*, *"Stage8.1 caused diesel commitment"*) with scientifically supportable outcome descriptions:
   > *"The preserved V1 evidence is consistent with differences in forecast input being associated with different aggregate EMS outcomes, but the timestep-level dispatch mechanism was not directly observable in V1."*
2. **Clarification of Association Language**: Clarified that V1 established paired downstream outcome differences and quantified exploratory associations between forecast errors and fuel outcomes, without providing causal proof of internal timestep dispatch sequences.
3. **Reconciliation of MAE Benchmark Figures**: Explicitly distinguished the official Stage8.1 daytime-only benchmark MAE ($36.1887\,\text{W/m}^2$) from the all-hours 173-origin replay subset metrics ($25.13\,\text{W/m}^2$ Treatment MAE, $174.25\,\text{W/m}^2$ Control MAE).

---

### 2. WHAT V1 ESTABLISHES ABOUT THE DIESEL INCREASE

- **Aggregate Outcome**: In the controlled synthetic microgrid environment, Treatment consumed an average of **+10.2684 L/origin MORE diesel fuel** than Control (Control: 4,671.00 L total, Treatment: 6,447.44 L total; 95% CI $[+5.48, +15.21]$ L).
- **Associated Outcome Metrics**: Accompanied by lower renewable energy used ($-79.46$ kWh/origin), lower solar curtailment ($-120.43$ kWh/origin / $-10.12$ percentage points), and lower battery throughput ($-64.65$ kWh/origin / $-0.32$ cycles).
- **Origin Heterogeneity**:
  - **Group P ($N=95$ origins)**: Treatment consumed more fuel (Mean Delta = $+36.0633$ L).
  - **Group N ($N=77$ origins)**: Treatment saved fuel (Mean Delta = $-21.4230$ L).
  - **Group Z ($N=1$ origin)**: Equal fuel consumption ($0.00$ L).
- **Scientific Boundary Statement**:
  > *"V1 tells us WHAT happened at the aggregate outcome level, but not the complete timestep-level mechanism explaining WHY it happened."*

---

### 3. NEXT STEP — WHY DID DIESEL USE INCREASE? (V2 HANDOFF)

Answering why the EMS produced the observed fuel outcome requires the already-designed, data-capture protocol:

$$\mathbf{STAGE8.1\_EMS\_MECHANISM\_OBSERVABILITY\_REPLAY\_V2}$$

#### Required V2 Telemetry Schema
At every MPC timestep $k \in \{0 \dots 23\}$, V2 will record:
- Treatment/Control forecast vectors and actual hidden truth.
- Optimizer status, objective values, and binary diesel commitment state.
- Diesel startup/shutdown events and dispatch power.
- Battery charge/discharge decisions and initial/final SOC.
- Reserve status and constraint states.
- Renewable available, used, and curtailed energy.
- Incremental and cumulative diesel fuel consumption.

#### Target Causal Investigation Chain
$$\text{Forecast Difference} \rightarrow \text{MPC Decision Divergence} \rightarrow \text{Diesel Dispatch} \rightarrow \text{Battery/SOC Response} \rightarrow \text{Renewable Utilization/Curtailment} \rightarrow \text{Cumulative Fuel}$$

> **Governance Principle**:
> V2 is the mechanism-identification experiment. V1 remains frozen and is not reopened.

---

### 4. MODIFIED DOCUMENTATION FILES & CRYPTOGRAPHIC PROVENANCE

| Corrected Documentation File | Status | Hash |
| :--- | :--- | :--- |
| `POLARIS_STAGE8_1_EMS_MECHANISM_DECOMPOSITION.md` | **CORRECTED** | Recorded in manifest |
| `POLARIS_STAGE8_1_EMS_MECHANISM_BRANCH_CLOSURE.md` | **CORRECTED** | Recorded in manifest |
| `POLARIS_STAGE8_1_EMS_TIMESTEP_MECHANISM_VERIFICATION.md` | **CORRECTED** | Recorded in manifest |
| `POLARIS_STAGE8_1_EMS_V1_MECHANISM_WORDING_CORRECTION_MANIFEST.md` | **CREATED** | Recorded in manifest |

**Runtime / Code Verification**: 0 python scripts, 0 schemas, 0 simulator modules, and 0 raw CSV data files were modified. All experimental outcomes and baseline metrics remain 100% frozen.
