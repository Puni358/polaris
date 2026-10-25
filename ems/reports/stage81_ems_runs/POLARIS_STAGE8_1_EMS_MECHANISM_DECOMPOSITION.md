# POLARIS — STAGE8.1 → EMS MECHANISM DECOMPOSITION INVESTIGATION
## FROZEN V1 CORRECTED DIAGNOSTIC REPORT

```
============================================================
MECHANISM DECOMPOSITION SUMMARY
============================================================
INVESTIGATION_STATUS: COMPLETE_READ_ONLY_DIAGNOSTIC
FROZEN_RESULT_STATUS: IMMUTABLE_V1_BASELINE_ACCEPTED
V1_MECHANISM_STATUS: AGGREGATE_ASSOCIATION_ONLY
V1_CAUSAL_MECHANISM: NOT_ESTABLISHED
NEXT_RESEARCH_TARGET: IDENTIFY_TIMESTEP_LEVEL_MECHANISM_OF_DIESEL_INCREASE
EXPERIMENT_RERUN: NO
ORIGIN_RERUN: NO
V1_RESULT_MODIFIED: NO
V2_STATUS: DESIGNED_NOT_EXECUTED
============================================================
```

---

### 1. FROZEN V1 RESULT BASELINE

This diagnostic report evaluates the accepted and immutable V1 experimental baseline:

- **Experimental Unit**: One complete 24-hour forecast-origin replay ($N = 173$ paired origins).
- **Primary Endpoint (`total_diesel_fuel_liters`)**:
  - **Control Total**: 4,671.00 Liters (Mean: 27.0000 L / origin)
  - **Treatment Total**: 6,447.44 Liters (Mean: 37.2684 L / origin)
  - **Mean Paired Difference ($\Delta = \text{Treatment} - \text{Control}$)**: **+10.2684 Liters / origin**
  - **95% Bootstrap CI (10,000 iter, seed=42)**: **[+5.4795 L, +15.2113 L]**
  - **Wilcoxon Signed-Rank Test**: $W = 5351.5, p = 1.3566 \times 10^{-3}$
- **Preregistered Forecast-Error Association**:
  - **Spearman $\rho$**: **-0.9198** ($p = 2.2830 \times 10^{-71}$, $N = 173$)
- **Secondary Paired Deltas**:
  - `diesel_energy_kwh`: **+58.1351 kWh/origin**
  - `renewable_energy_used_kwh`: **-79.4577 kWh/origin**
  - `renewable_curtailment_kwh`: **-120.4317 kWh/origin** (-10.12 percentage points)
  - `renewable_utilization_pct`: **+10.1204 percentage points**
  - `battery_throughput_kwh`: **-64.6521 kWh/origin** (-0.32 cycles/origin)
  - `unmet_critical_load_kwh`: **0.00 kWh**
  - `system_reliability_pct`: **0.00 percentage points**
  - `constraint_violations_count`: **0 violations**

---

### 2. WHAT V1 ESTABLISHES ABOUT THE DIESEL INCREASE

- **Aggregate Outcome**: In the controlled synthetic microgrid environment, Treatment consumed an average of **+10.2684 L/origin MORE diesel fuel** than Control.
- **Secondary Operational Deltas**: This increase was accompanied by lower renewable energy used ($-79.46$ kWh/origin), lower solar curtailment ($-120.43$ kWh/origin), and lower battery throughput ($-64.65$ kWh/origin).
- **Origin-Level Heterogeneity**:
  - **Group P ($N=95$ origins)**: Treatment consumed more fuel (Mean Delta = $+36.0633$ L).
  - **Group N ($N=77$ origins)**: Treatment saved fuel (Mean Delta = $-21.4230$ L).
  - **Group Z ($N=1$ origin)**: Equal fuel consumption ($0.00$ L).
- **Scientific Boundary Statement**:
  > *"V1 tells us WHAT happened at the aggregate outcome level, but not the complete timestep-level mechanism explaining WHY it happened."*

---

### 3. MAE RECONCILIATION

- **Official Stage8.1 OOD Benchmark MAE ($36.1887\,\text{W/m}^2$)**: Measures daytime-only hours (`daytime_flag == True`) across the official OOD benchmark evaluation dataset.
- **V1 Replay Subset All-Hours MAE ($25.13\,\text{W/m}^2$ Treatment, $174.25\,\text{W/m}^2$ Control)**: Measures all 24 horizon hours (including 12 nighttime zero-solar hours) across the 173 mechanically eligible V1 origins.
- `MAE_DISCREPANCY_STATUS`: **`RECONCILED`** (Official benchmark $36.1887\,\text{W/m}^2$ remains the authoritative forecast accuracy metric).

---

### 4. HYPOTHESIZED OPERATIONAL PATHWAYS (FOR V2 TESTING)

The observed aggregate differences motivate hypotheses regarding microgrid behavior, but cannot establish internal timestep causality without V2 telemetry:

- **HYPOTHESIS 1 [REQUIRES V2 TELEMETRY]**: Lower solar forecasts under Stage8.1 prompt earlier diesel generator commitment to maintain reserve margins.
- **HYPOTHESIS 2 [REQUIRES V2 TELEMETRY]**: Lower battery throughput is a downstream consequence of diesel supplying baseload demand directly.
- **HYPOTHESIS 3 [REQUIRES V2 TELEMETRY]**: Lower solar curtailment is a downstream consequence of lower battery SOC allowing solar energy to be absorbed directly.

---

### 5. NEXT STEP — WHY DID DIESEL USE INCREASE? (V2 HANDOFF)

Answering why the EMS produced the observed fuel outcome requires the already-designed data-capture protocol:

$$\mathbf{STAGE8.1\_EMS\_MECHANISM\_OBSERVABILITY\_REPLAY\_V2}$$

- **Telemetry Requirements**: MPC timestep logging of forecast vectors, hidden truth, optimizer status, binary diesel commitment, battery charge/discharge decisions, SOC trajectories, renewable available/used/curtailed, and cumulative fuel increments.
- **Governance Mandate**:
  > *"V2 is the mechanism-identification experiment. V1 remains frozen and is not reopened."*

---

### 6. ARTIFACT LOCATION SUMMARY

1. **Markdown Diagnostic Report**: [`POLARIS_STAGE8_1_EMS_MECHANISM_DECOMPOSITION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_MECHANISM_DECOMPOSITION.md)
2. **JSON Diagnostic Manifest**: [`POLARIS_STAGE8_1_EMS_MECHANISM_DECOMPOSITION.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_MECHANISM_DECOMPOSITION.json)
