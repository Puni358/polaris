# POLARIS — STAGE8.1 → EMS V1
## CORRECTED TRAJECTORY-LEVEL FORENSIC MECHANISM AUDIT

```
============================================================
FINAL TRAJECTORY-LEVEL FORENSIC MECHANISM DETERMINATION
============================================================
FINAL_CLASSIFICATION: C — ONLY ASSOCIATIONS ESTABLISHED
V1_EXECUTION_STATUS: ACCEPTED_AND_FROZEN
V1_MECHANISM_STATUS: AGGREGATE_ASSOCIATION_ONLY
V1_CAUSAL_MECHANISM: NOT_ESTABLISHED
V2_STATUS: DESIGNED_NOT_EXECUTED
V2_ENGINEERING_STATUS: V2_ENGINEERING_LOCKED
EXPERIMENT_RERUN: NO
ORIGIN_RERUN: NO
V1_RESULT_MODIFIED: NO
V2_EXECUTED: NO
============================================================
```

---

### 1. FROZEN V1 EXPERIMENTAL RESULT CONFIRMATION

The V1 experimental baseline is formally accepted, immutable, and frozen:

- **Experimental Unit**: One complete 24-hour forecast-origin replay ($N = 173$ paired origins).
- **Primary Endpoint (`total_diesel_fuel_liters`)**:
  - **Control Total**: 4,671.00 Liters (Mean: 27.0000 L / origin)
  - **Treatment Total**: 6,447.44 Liters (Mean: 37.2684 L / origin)
  - **Mean Paired Difference ($\Delta = \text{Treatment} - \text{Control}$)**: **+10.2684 Liters / origin**
  - **95% Bootstrap CI (10,000 iter, seed=42)**: **[+5.4795 L, +15.2113 L]**
  - **Wilcoxon Signed-Rank Test**: $W = 5351.5, p = 1.3566 \times 10^{-3}$
- **Preregistered Forecast-Error Association**:
  - **Spearman $\rho$**: **-0.9198** ($p = 2.2830 \times 10^{-71}$, $N = 173$)
- **Secondary Frozen Differences**:
  - `diesel_energy_kwh`: **+58.1351 kWh/origin**
  - `renewable_energy_used_kwh`: **-79.4577 kWh/origin**
  - `renewable_curtailment_kwh`: **-120.4317 kWh/origin** (-10.12 percentage points)
  - `renewable_utilization_pct`: **+10.1204 percentage points**
  - `battery_throughput_kwh`: **-64.6521 kWh/origin** (-0.32 cycles/origin)
  - `unmet_critical_load_kwh`: **0.00 kWh**
  - `system_reliability_pct`: **0.00 percentage points**
  - `constraint_violations_count`: **0 violations**

---

### 2. CRITICAL MAE RECONCILIATION

- **Official Stage8.1 OOD Benchmark MAE ($36.1887\,\text{W/m}^2$)**: Evaluates daytime-only hours (`daytime_flag == True`) across the official OOD benchmark dataset.
- **V1 Replay Subset All-Hours MAE ($25.13\,\text{W/m}^2$ Treatment, $174.25\,\text{W/m}^2$ Control)**: Evaluates all 24 horizon hours (including 12 nighttime zero-solar hours) across the 173 mechanically eligible V1 origins.
- `MAE_DISCREPANCY_STATUS`: **`RECONCILED`** (Official benchmark $36.1887\,\text{W/m}^2$ remains the authoritative forecast accuracy baseline).

---

### 3. WHAT V1 ESTABLISHES ABOUT THE DIESEL INCREASE

- **Aggregate Outcome**: In the controlled synthetic microgrid environment, Treatment consumed an average of **+10.2684 L/origin MORE diesel fuel** than Control.
- **Secondary Operational Deltas**: This increase was accompanied by lower renewable energy used ($-79.46$ kWh/origin), lower solar curtailment ($-120.43$ kWh/origin), and lower battery throughput ($-64.65$ kWh/origin).
- **Origin Heterogeneity**:
  - **Group P ($N=95$ origins)**: Treatment consumed more fuel (Mean Delta = $+36.0633$ L).
  - **Group N ($N=77$ origins)**: Treatment saved fuel (Mean Delta = $-21.4230$ L).
  - **Group Z ($N=1$ origin)**: Equal fuel consumption ($0.00$ L).
- **Scientific Boundary Statement**:
  > *"V1 tells us WHAT happened at the aggregate outcome level, but not the complete timestep-level mechanism explaining WHY it happened."*

---

### 4. FIELD AVAILABILITY & MECHANISM CLASSIFICATION

- **Origin Summary Totals**: Preserved in `POLARIS_STAGE8_1_EMS_EMPIRICAL_REPLAY_RAW.csv`.
- **Origin Horizon Predictions**: Preserved in `POLARIS_REPRODUCIBLE_BASELINE_ODD_PREDICTIONS.csv`.
- **Hourly Timestep EMS Decision Trajectories**: `NOT_AVAILABLE_IN_PRESERVED_EVIDENCE`.
- **Final Forensic Classification**: **`C — ONLY ASSOCIATIONS ESTABLISHED`**.

---

### 5. NEXT STEP — WHY DID DIESEL USE INCREASE? (V2 HANDOFF)

Answering why the EMS produced the observed fuel outcome requires the already-designed, data-capture protocol:

$$\mathbf{STAGE8.1\_EMS\_MECHANISM\_OBSERVABILITY\_REPLAY\_V2}$$

- **V2 Status**: `DESIGNED_NOT_EXECUTED` (Execution Not Authorized).
- **Governance Mandate**: *"V2 is the mechanism-identification experiment. V1 remains frozen and is not reopened."*

---

### 6. ARTIFACT LOCATION SUMMARY

1. **Markdown Timestep Verification Report**: [`POLARIS_STAGE8_1_EMS_TIMESTEP_MECHANISM_VERIFICATION.md`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_TIMESTEP_MECHANISM_VERIFICATION.md)
2. **JSON Timestep Verification Manifest**: [`POLARIS_STAGE8_1_EMS_TIMESTEP_MECHANISM_VERIFICATION.json`](file:///home/punith-bs/01polaris%20%28Copy%29/POLARIS_STAGE8_1_EMS_TIMESTEP_MECHANISM_VERIFICATION.json)
